from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import csv
import ast
from pathlib import Path
import torch
from utils import (
    DEFAULT_HF_MODEL_DIRS,
    DEFAULT_PROMPT_TEMPLATES,
    load_tokenizer,
    read_model_name,
    throttle_generator,
)
import tensorrt_llm
from tensorrt_llm.runtime import ModelRunner
from typing import List

import numpy as np

runtime_rank = tensorrt_llm.mpi_rank()
lora_dir = None  # Adjust as necessary
debug_mode = False  # Adjust based on your needs
use_py_session = True  # Assuming Python session usage; adjust based on your needs
lora_ckpt_source = "source_of_your_choice"  # Adjust as necessary
tokenizer_dir = "./dolphin-2.6-mistral-7b-dpo-laser"
# Assuming global variables for model components
model_runner = None
engine_dir = "./tmp/mistral/7B-16k/trt_engines/fp16/1-gpu"
model_name, model_version = read_model_name(engine_dir)
tokenizer, pad_id, end_id = load_tokenizer(
    tokenizer_dir=tokenizer_dir,
    # vocab_file=vocab_file,
    model_name=model_name,
    model_version=model_version
    # tokenizer_type=tokenizer_type,
)
runner_cls = ModelRunner
model_runner = runner_cls.from_dir(
    engine_dir=engine_dir,
    # Include other necessary arguments for your runner initialization
)
runner_kwargs = dict(
    engine_dir=engine_dir,
    lora_dir=lora_dir,
    rank=runtime_rank,
    debug_mode=debug_mode,
    lora_ckpt_source=None,
)
runner = model_runner.from_dir(**runner_kwargs)
print("Model and tokenizer have been initialized.")

app = FastAPI()


class GenerateRequest(BaseModel):
    max_output_len: int = 16384
    input_text: List[str]
    # input_text: list = ["Born in north-east France, Soyer trained as a"]
    max_attention_window_size: int = None
    sink_token_length: int = None
    use_py_session: bool = False
    max_input_length: int = 32256
    output_csv: str = None
    output_npy: str = None
    output_logits_npy: str = None
    # tokenizer_dir = "./llama/dolphin-2.6-mistral-7b-dpo-laser"
    num_beams: int = 1
    temperature: float = 1.0
    top_k: int = 1
    top_p: float = 0.0
    length_penalty: float = 1.0
    repetition_penalty: float = 1.0
    presence_penalty: float = 0.0
    frequency_penalty: float = 0.0


def parse_input(
    tokenizer,
    input_text=None,
    prompt_template=None,
    input_file=None,
    add_special_tokens=True,
    max_input_length=16384,
    pad_id=None,
    num_prepend_vtokens=[],
    model_name=None,
    model_version=None,
):
    if pad_id is None:
        pad_id = tokenizer.pad_token_id

    batch_input_ids = []
    if input_file is None:
        for curr_text in input_text:
            if prompt_template is not None:
                curr_text = prompt_template.format(input_text=curr_text)
            input_ids = tokenizer.encode(
                curr_text,
                add_special_tokens=add_special_tokens,
                truncation=True,
                max_length=max_input_length,
            )
            batch_input_ids.append(input_ids)
    else:
        if input_file.endswith(".csv"):
            with open(input_file, "r") as csv_file:
                csv_reader = csv.reader(csv_file, delimiter=",")
                for line in csv_reader:
                    input_ids = np.array(line, dtype="int32")
                    batch_input_ids.append(input_ids[-max_input_length:])
        elif input_file.endswith(".npy"):
            inputs = np.load(input_file)
            for row in inputs:
                input_ids = row[row != pad_id]
                batch_input_ids.append(input_ids[-max_input_length:])
        elif input_file.endswith(".txt"):
            with open(input_file, "r", encoding="utf-8", errors="replace") as txt_file:
                input_text = txt_file.read()
                input_ids = tokenizer.encode(
                    input_text,
                    add_special_tokens=add_special_tokens,
                    truncation=True,
                    max_length=max_input_length,
                )
                batch_input_ids.append(input_ids)
        else:
            print("Input file format not supported.")
            raise SystemExit

    if num_prepend_vtokens:
        assert len(num_prepend_vtokens) == len(batch_input_ids)
        base_vocab_size = tokenizer.vocab_size - len(
            tokenizer.special_tokens_map.get("additional_special_tokens", [])
        )
        for i, length in enumerate(num_prepend_vtokens):
            batch_input_ids[i] = (
                list(range(base_vocab_size, base_vocab_size + length))
                + batch_input_ids[i]
            )

    if model_name == "ChatGLMForCausalLM" and model_version == "glm":
        for ids in batch_input_ids:
            ids.append(tokenizer.sop_token_id)

    batch_input_ids = [torch.tensor(x, dtype=torch.int32) for x in batch_input_ids]
    return batch_input_ids


def print_output(
    tokenizer,
    output_ids,
    input_lengths,
    sequence_lengths,
    output_csv=None,
    output_npy=None,
    context_logits=None,
    generation_logits=None,
    output_logits_npy=None,
):
    batch_size, num_beams, _ = output_ids.size()
    if output_csv is None and output_npy is None:
        for batch_idx in range(batch_size):
            inputs = output_ids[batch_idx][0][: input_lengths[batch_idx]].tolist()
            input_text = tokenizer.decode(inputs)
            print(f'Input [Text {batch_idx}]: "{input_text}"')
            for beam in range(num_beams):
                output_begin = input_lengths[batch_idx]
                output_end = sequence_lengths[batch_idx][beam]
                outputs = output_ids[batch_idx][beam][output_begin:output_end].tolist()
                output_text = tokenizer.decode(outputs)
                print(f'Output [Text {batch_idx} Beam {beam}]: "{output_text}"')

    output_ids = output_ids.reshape((-1, output_ids.size(2)))

    if output_csv is not None:
        output_file = Path(output_csv)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        outputs = output_ids.tolist()
        with open(output_file, "w") as csv_file:
            writer = csv.writer(csv_file, delimiter=",")
            writer.writerows(outputs)

    if output_npy is not None:
        output_file = Path(output_npy)
        output_file.parent.mkdir(exist_ok=True, parents=True)
        outputs = np.array(output_ids.cpu().contiguous(), dtype="int32")
        np.save(output_file, outputs)

    # Save context logits
    if context_logits is not None and output_logits_npy is not None:
        context_logits = torch.cat(context_logits, axis=0)
        vocab_size_padded = context_logits.shape[-1]
        context_logits = context_logits.reshape([1, -1, vocab_size_padded])

        output_context_logits_npy = output_logits_npy.split(".npy")[0] + "_context"
        output_context_logits_file = Path(output_context_logits_npy)
        context_outputs = np.array(
            context_logits.squeeze(0).cpu().contiguous(), dtype="float32"
        )  # [promptLengthSum, vocabSize]
        np.save(output_context_logits_file, context_outputs)

    # Save generation logits
    if (
        generation_logits is not None
        and output_logits_npy is not None
        and num_beams == 1
    ):
        output_generation_logits_npy = (
            output_logits_npy.split(".npy")[0] + "_generation"
        )
        output_generation_logits_file = Path(output_generation_logits_npy)
        generation_outputs = np.array(
            generation_logits.cpu().contiguous(), dtype="float32"
        )
        np.save(output_generation_logits_file, generation_outputs)
    return output_text


def main(args):
    model_name, model_version = read_model_name(args.engine_dir)
    if args.tokenizer_dir is None:
        args.tokenizer_dir = DEFAULT_HF_MODEL_DIRS[model_name]

    tokenizer, pad_id, end_id = load_tokenizer(
        tokenizer_dir=args.tokenizer_dir,
        vocab_file=args.vocab_file,
        model_name=model_name,
        model_version=model_version,
        tokenizer_type=args.tokenizer_type,
    )

    # # An example to stop generation when the model generate " London" on first sentence, " eventually became" on second sentence
    # stop_words_list = [[" London"], ["eventually became"]]
    # stop_words_list = tensorrt_llm.runtime.to_word_list_format(stop_words_list, tokenizer)
    # stop_words_list = torch.Tensor(stop_words_list).to(torch.int32).to("cuda").contiguous()
    stop_words_list = None

    # # An example to prevent generating " chef" on first sentence, " eventually" and " chef before" on second sentence
    # bad_words_list = [[" chef"], [" eventually, chef before"]]
    # bad_words_list = tensorrt_llm.runtime.to_word_list_format(bad_words_list, tokenizer)
    # bad_words_list = torch.Tensor(bad_words_list).to(torch.int32).to("cuda").contiguous()
    bad_words_list = None

    prompt_template = None
    if args.use_prompt_template and model_name in DEFAULT_PROMPT_TEMPLATES:
        prompt_template = DEFAULT_PROMPT_TEMPLATES[model_name]
    batch_input_ids = parse_input(
        tokenizer=tokenizer,
        input_text=args.input_text,
        prompt_template=prompt_template,
        input_file=args.input_file,
        add_special_tokens=args.add_special_tokens,
        max_input_length=args.max_input_length,
        pad_id=pad_id,
        num_prepend_vtokens=args.num_prepend_vtokens,
        model_name=model_name,
        model_version=model_version,
    )
    input_lengths = [x.size(0) for x in batch_input_ids]

    if not PYTHON_BINDINGS and not args.use_py_session:
        args.use_py_session = True
    if args.debug_mode and not args.use_py_session:
        args.use_py_session = True
    runner_cls = ModelRunner if args.use_py_session else ModelRunnerCpp
    runner_kwargs = dict(
        engine_dir=args.engine_dir,
        lora_dir=args.lora_dir,
        rank=runtime_rank,
        debug_mode=args.debug_mode,
        lora_ckpt_source=args.lora_ckpt_source,
    )
    if args.medusa_choices is not None:
        args.medusa_choices = ast.literal_eval(args.medusa_choices)
        assert args.use_py_session, "Medusa is only supported by py_session"
        assert args.temperature == 0, "Medusa should use temperature == 0"
        assert args.num_beams == 1, "Medusa should use num_beams == 1"
        runner_kwargs.update(medusa_choices=args.medusa_choices)
    if not args.use_py_session:
        runner_kwargs.update(
            max_batch_size=len(batch_input_ids),
            max_input_len=max(input_lengths),
            max_output_len=args.max_output_len,
            max_beam_width=args.num_beams,
            max_attention_window_size=args.max_attention_window_size,
            sink_token_length=args.sink_token_length,
        )
    runner = runner_cls.from_dir(**runner_kwargs)

    with torch.no_grad():
        outputs = runner.generate(
            batch_input_ids,
            max_new_tokens=args.max_output_len,
            max_attention_window_size=args.max_attention_window_size,
            sink_token_length=args.sink_token_length,
            end_id=end_id,
            pad_id=pad_id,
            temperature=args.temperature,
            top_k=args.top_k,
            top_p=args.top_p,
            num_beams=args.num_beams,
            length_penalty=args.length_penalty,
            repetition_penalty=args.repetition_penalty,
            presence_penalty=args.presence_penalty,
            frequency_penalty=args.frequency_penalty,
            stop_words_list=stop_words_list,
            bad_words_list=bad_words_list,
            lora_uids=args.lora_task_uids,
            prompt_table_path=args.prompt_table_path,
            prompt_tasks=args.prompt_tasks,
            streaming=args.streaming,
            output_sequence_lengths=True,
            return_dict=True,
            medusa_choices=args.medusa_choices,
        )
        torch.cuda.synchronize()
    if runtime_rank == 0:
        output_ids = outputs["output_ids"]
        sequence_lengths = outputs["sequence_lengths"]
        context_logits = None
        generation_logits = None
        if runner.gather_context_logits:
            context_logits = outputs["context_logits"]
        if runner.gather_generation_logits:
            generation_logits = outputs["generation_logits"]
        print_output(
            tokenizer,
            output_ids,
            input_lengths,
            sequence_lengths,
            output_csv=args.output_csv,
            output_npy=args.output_npy,
            context_logits=context_logits,
            generation_logits=generation_logits,
            output_logits_npy=args.output_logits_npy,
        )
    if args.run_profiling:
        ite = 10
        # warmup
        for _ in range(ite):
            with torch.no_grad():
                outputs = runner.generate(
                    batch_input_ids,
                    max_new_tokens=args.max_output_len,
                    max_attention_window_size=args.max_attention_window_size,
                    end_id=end_id,
                    pad_id=pad_id,
                    temperature=args.temperature,
                    top_k=args.top_k,
                    top_p=args.top_p,
                    num_beams=args.num_beams,
                    length_penalty=args.length_penalty,
                    repetition_penalty=args.repetition_penalty,
                    presence_penalty=args.presence_penalty,
                    frequency_penalty=args.frequency_penalty,
                    stop_words_list=stop_words_list,
                    bad_words_list=bad_words_list,
                    lora_uids=args.lora_task_uids,
                    prompt_table_path=args.prompt_table_path,
                    prompt_tasks=args.prompt_tasks,
                    streaming=args.streaming,
                    output_sequence_lengths=True,
                    return_dict=True,
                )
                torch.cuda.synchronize()
        for _ in range(ite):
            with torch.no_grad():
                outputs = runner.generate(
                    batch_input_ids,
                    max_new_tokens=args.max_output_len,
                    max_attention_window_size=args.max_attention_window_size,
                    end_id=end_id,
                    pad_id=pad_id,
                    temperature=args.temperature,
                    top_k=args.top_k,
                    top_p=args.top_p,
                    num_beams=args.num_beams,
                    length_penalty=args.length_penalty,
                    repetition_penalty=args.repetition_penalty,
                    presence_penalty=args.presence_penalty,
                    frequency_penalty=args.frequency_penalty,
                    stop_words_list=stop_words_list,
                    bad_words_list=bad_words_list,
                    lora_uids=args.lora_task_uids,
                    prompt_table_path=args.prompt_table_path,
                    prompt_tasks=args.prompt_tasks,
                    streaming=args.streaming,
                    output_sequence_lengths=True,
                    return_dict=True,
                )
                torch.cuda.synchronize()


@app.post("/generate")
async def generate(request: GenerateRequest):
    # Use `input_text` directly in the function logic
    input_text = request.input_text
    print(f"Received input text: {input_text}")
    batch_input_ids = parse_input(tokenizer, input_text, pad_id=pad_id)
    # Assume `run_model` is your refactored model execution function.
    # You will need to implement `run_model` to call your model with the request parameters.
    input_lengths = [x.size(0) for x in batch_input_ids]
    with torch.no_grad():
        outputs = runner.generate(
            batch_input_ids,
            max_new_tokens=16384,
            max_attention_window=4096,
            sink_token_length=None,
	    end_id=end_id,
            pad_id=pad_id,
	    temperature=0.7,
            top_k=1,
            top_p=0.0,
            length_penalty=1.0,
            repetition_penalty=1.0,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            stop_words_list=None,
            bad_words_list=None,
            lora_uids=None,
            prompt_table_path=None,
            prompt_tasks=None,
            streaming=False,
            output_sequence_lengths=True,
            return_dict=True,
        )
        torch.cuda.synchronize()
    if runtime_rank == 0:
        output_ids = outputs["output_ids"]
        sequence_lengths = outputs["sequence_lengths"]
        context_logits = None
        generation_logits = None
        if runner.gather_context_logits:
            context_logits = outputs["context_logits"]
        if runner.gather_generation_logits:
            generation_logits = outputs["generation_logits"]
        read_output = print_output(
            tokenizer,
            output_ids,
            input_lengths,
            sequence_lengths,
            context_logits=context_logits,
            generation_logits=generation_logits,
        )
    print(f'output: {read_output}')
    output = {"output": read_output}
    return output


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
