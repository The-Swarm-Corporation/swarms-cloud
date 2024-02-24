import argparse
import os

import torch
import tensorrt as trt

# isort: on
import tensorrt_llm


def get_engine_name(rank):
    return f"rank{rank}.engine"


def trt_dtype_to_torch(dtype):
    if dtype == trt.float16:
        return torch.float16
    elif dtype == trt.float32:
        return torch.float32
    elif dtype == trt.int32:
        return torch.int32
    else:
        raise TypeError(f"{dtype} is not supported")


def TRTOPT(args, config):
    dtype = config["pretrained_config"]["dtype"]
    world_size = config["pretrained_config"]["mapping"]["world_size"]
    assert (
        world_size == tensorrt_llm.mpi_world_size()
    ), f"Engine world size ({world_size}) != Runtime world size ({tensorrt_llm.mpi_world_size()})"

    use_gpt_attention_plugin = bool(
        config["build_config"]["plugin_config"]["gpt_attention_plugin"]
    )

    num_heads = config["pretrained_config"]["num_attention_heads"] // world_size
    hidden_size = config["pretrained_config"]["hidden_size"] // world_size
    vocab_size = config["pretrained_config"]["vocab_size"]
    max_batch_size = config["build_config"]["max_batch_size"]
    num_layers = config["pretrained_config"]["num_hidden_layers"]
    remove_input_padding = config["build_config"]["plugin_config"][
        "remove_input_padding"
    ]
    max_prompt_embedding_table_size = config["build_config"].get(
        "max_prompt_embedding_table_size", 0
    )

    model_config = tensorrt_llm.runtime.ModelConfig(
        max_batch_size=max_batch_size,
        vocab_size=vocab_size,
        num_layers=num_layers,
        num_heads=num_heads,
        num_kv_heads=num_heads,
        hidden_size=hidden_size,
        gpt_attention_plugin=use_gpt_attention_plugin,
        remove_input_padding=remove_input_padding,
        max_prompt_embedding_table_size=max_prompt_embedding_table_size,
        dtype=dtype,
    )

    runtime_rank = tensorrt_llm.mpi_rank()
    runtime_mapping = tensorrt_llm.Mapping(world_size, runtime_rank)
    torch.cuda.set_device(runtime_rank % runtime_mapping.gpus_per_node)

    engine_name = get_engine_name(runtime_rank)
    serialize_path = os.path.join(args.opt_engine_dir, engine_name)

    tensorrt_llm.logger.set_level(args.log_level)

    with open(serialize_path, "rb") as f:
        engine_buffer = f.read()
    decoder = tensorrt_llm.runtime.GenerationSession(
        model_config, engine_buffer, runtime_mapping
    )

    max_input_len = config["build_config"]["max_input_len"]
    return decoder, model_config, world_size, dtype, max_input_len


def ptuning_setup(
    prompt_table,
    dtype,
    hidden_size,
    tasks,
    input_ids,
    input_lengths,
    remove_input_padding,
):
    if prompt_table is not None:
        task_vocab_size = torch.tensor(
            [prompt_table.shape[1]], dtype=torch.int32, device="cuda"
        )
        prompt_table = prompt_table.view(
            (prompt_table.shape[0] * prompt_table.shape[1], prompt_table.shape[2])
        )
        prompt_table = prompt_table.cuda().to(
            dtype=tensorrt_llm._utils.str_dtype_to_torch(dtype)
        )
    else:
        prompt_table = torch.empty([1, hidden_size]).cuda()
        task_vocab_size = torch.zeros([1]).cuda()

    num_sequences = input_lengths.size(0) if remove_input_padding else input_ids.size(0)

    if tasks is not None:
        tasks = torch.tensor(
            [int(t) for t in tasks.split(",")], dtype=torch.int32, device="cuda"
        )
        assert (
            tasks.shape[0] == num_sequences
        ), "Number of supplied tasks must match input batch size"
    else:
        tasks = torch.zeros([num_sequences], dtype=torch.int32).cuda()

    return [prompt_table, tasks, task_vocab_size]


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_output_len", type=int, default=30)
    parser.add_argument("--log_level", type=str, default="info")
    parser.add_argument("--engine_dir", type=str, default="./plan")
    parser.add_argument("--input_dir", type=str, default="image.pt")
    parser.add_argument("--query_tokens", type=str, default="query_tokens.pt")
    parser.add_argument(
        "--opt_engine_dir", type=str, default="trt_engine/blip-2-opt-2.7b/fp16/1-gpu/"
    )
    parser.add_argument("--hf_model_location", type=str, default="facebook/opt-2.7b")
    parser.add_argument(
        "--input_text", type=str, default="Question: which city is this? Answer:"
    )
    parser.add_argument(
        "--num_beams", type=int, help="Use beam search if num_beams >1", default=1
    )
    parser.add_argument(
        "--max_txt_len", type=int, help="Max text prompt length", default=32
    )
    parser.add_argument("--top_k", type=int, default=1)

    return parser.parse_args()
