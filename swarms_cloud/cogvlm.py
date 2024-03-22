import base64
import os
from io import BytesIO
from typing import List, Optional, Tuple

import torch
from loguru import logger
from PIL import Image
from transformers import (
    AutoModelForCausalLM,
    BitsAndBytesConfig,
    LlamaTokenizer,
    PreTrainedModel,
    PreTrainedTokenizer,
    TextIteratorStreamer,
)

from swarms_cloud.schema.cog_vlm_schemas import (
    ChatCompletionResponse,
    ChatCompletionResponseStreamChoice,
    ChatMessageInput,
    DeltaMessage,
    ImageUrlContent,
    TextContent,
)

# Environment variables
MODEL_PATH = os.environ.get("COGVLM_MODEL_PATH", "THUDM/cogvlm-chat-hf")
TOKENIZER_PATH = os.environ.get("TOKENIZER_PATH", "lmsys/vicuna-7b-v1.5")
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
QUANT_ENABLED = os.environ.get("QUANT_ENABLED", True)


class CogVLMModel:
    def __init__(
        self,
        model_name: str = MODEL_PATH,
        tokenizer_name: str = TOKENIZER_PATH,
        quant_enabled: bool = QUANT_ENABLED,
        device: str = DEVICE,
    ):
        # Load the tokenizer and model
        self.tokenizer = LlamaTokenizer.from_pretrained(
            TOKENIZER_PATH, trust_remote_code=True
        )

        if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8:
            torch_type = torch.bfloat16
        else:
            torch_type = torch.float16

        self.torch_type = torch_type

        print(
            f"========Use torch type as:{torch_type} with device:{DEVICE}========\n\n"
        )

        quantization_config = {
            "load_in_4bit": True,
            "bnb_4bit_use_double_quant": True,
            "bnb_4bit_compute_dtype": torch_type,
        }

        bnb_config = BitsAndBytesConfig(**quantization_config)

        AutoModelForCausalLM.from_pretrained(
            MODEL_PATH,
            trust_remote_code=True,
            torch_dtype=torch_type,
            low_cpu_mem_usage=True,
            quantization_config=bnb_config,
        ).eval()

        # Torch type
        if torch.cuda.is_available() and torch.cuda.get_device_capability()[0] >= 8:
            torch_type = torch.bfloat16
        else:
            torch_type = torch.float16

    def run(self, task: str, *args, **kwargs):
        pass


async def predict(model_id: str, params: dict):
    """
    Handle streaming predictions. It continuously generates responses for a given input stream.
    This is particularly useful for real-time, continuous interactions with the model.
    """

    choice_data = ChatCompletionResponseStreamChoice(
        index=0, delta=DeltaMessage(role="assistant"), finish_reason=None
    )

    chunk = ChatCompletionResponse(
        model=model_id, choices=[choice_data], object="chat.completion.chunk"
    )

    # Log to supabase
    # supabase_logger.log(chunk)

    yield f"{chunk.model_dump_json(exclude_unset=True)}"

    previous_text = ""
    for new_response in generate_stream_cogvlm(model, tokenizer, params):
        decoded_unicode = new_response["text"]
        delta_text = decoded_unicode[len(previous_text) :]
        previous_text = decoded_unicode
        delta = DeltaMessage(
            content=delta_text,
            role="assistant",
        )
        choice_data = ChatCompletionResponseStreamChoice(
            index=0,
            delta=delta,
        )

        chunk = ChatCompletionResponse(
            model=model_id, choices=[choice_data], object="chat.completion.chunk"
        )

        yield f"{chunk.model_dump_json(exclude_unset=True)}"

    choice_data = ChatCompletionResponseStreamChoice(
        index=0,
        delta=DeltaMessage(),
    )

    chunk = ChatCompletionResponse(
        model=model_id, choices=[choice_data], object="chat.completion.chunk"
    )

    yield f"{chunk.model_dump_json(exclude_unset=True)}"


def generate_cogvlm(
    model: PreTrainedModel, tokenizer: PreTrainedTokenizer, params: dict
):
    """
    Generates a response using the CogVLM model. It processes the chat history and image data, if any,
    and then invokes the model to generate a response.
    """

    for response in generate_stream_cogvlm(model, tokenizer, params):
        pass
    return response


def process_history_and_images(
    messages: List[ChatMessageInput],
) -> Tuple[Optional[str], Optional[List[Tuple[str, str]]], Optional[List[Image.Image]]]:
    """
    Process history messages to extract text, identify the last user query,
    and convert base64 encoded image URLs to PIL images.

    Args:
        messages(List[ChatMessageInput]): List of ChatMessageInput objects.
    return: A tuple of three elements:
             - The last user query as a string.
             - Text history formatted as a list of tuples for the model.
             - List of PIL Image objects extracted from the messages.
    """
    formatted_history = []
    image_list = []
    last_user_query = ""

    for i, message in enumerate(messages):
        role = message.role
        content = message.content

        if isinstance(content, list):  # text
            text_content = " ".join(
                item.text for item in content if isinstance(item, TextContent)
            )
        else:
            text_content = content

        if isinstance(content, list):  # image
            for item in content:
                if isinstance(item, ImageUrlContent):
                    image_url = item.image_url.url
                    if image_url.startswith("data:image/jpeg;base64,"):
                        base64_encoded_image = image_url.split(
                            "data:image/jpeg;base64,"
                        )[1]
                        image_data = base64.b64decode(base64_encoded_image)
                        image = Image.open(BytesIO(image_data)).convert("RGB")
                        image_list.append(image)

        if role == "user":
            if i == len(messages) - 1:  # 最后一条用户消息
                last_user_query = text_content
            else:
                formatted_history.append((text_content, ""))
        elif role == "assistant":
            if formatted_history:
                if formatted_history[-1][1] != "":
                    assert (
                        False
                    ), f"the last query is answered. answer again. {formatted_history[-1][0]}, {formatted_history[-1][1]}, {text_content}"
                formatted_history[-1] = (formatted_history[-1][0], text_content)
            else:
                assert False, "assistant reply before user"
        else:
            assert False, f"unrecognized role: {role}"

    return last_user_query, formatted_history, image_list


@torch.inference_mode()
def generate_stream_cogvlm(
    model: PreTrainedModel, tokenizer: PreTrainedTokenizer, params: dict
):
    """
    Generates a stream of responses using the CogVLM model in inference mode.
    It's optimized to handle continuous input-output interactions with the model in a streaming manner.
    """
    messages = params["messages"]
    temperature = float(params.get("temperature", 1.0))
    repetition_penalty = float(params.get("repetition_penalty", 1.0))
    top_p = float(params.get("top_p", 1.0))
    max_new_tokens = int(params.get("max_tokens", 256))
    query, history, image_list = process_history_and_images(messages)

    logger.debug(f"==== request ====\n{query}")

    input_by_model = model.build_conversation_input_ids(
        tokenizer, query=query, history=history, images=[image_list[-1]]
    )
    inputs = {
        "input_ids": input_by_model["input_ids"].unsqueeze(0).to(DEVICE),
        "token_type_ids": input_by_model["token_type_ids"].unsqueeze(0).to(DEVICE),
        "attention_mask": input_by_model["attention_mask"].unsqueeze(0).to(DEVICE),
        "images": [[input_by_model["images"][0].to(DEVICE).to(torch_type)]],
    }
    if "cross_images" in input_by_model and input_by_model["cross_images"]:
        inputs["cross_images"] = [
            [input_by_model["cross_images"][0].to(DEVICE).to(torch_type)]
        ]

    input_echo_len = len(inputs["input_ids"][0])
    streamer = TextIteratorStreamer(
        tokenizer=tokenizer, timeout=60.0, skip_prompt=True, skip_special_tokens=True
    )
    gen_kwargs = {
        "repetition_penalty": repetition_penalty,
        "max_new_tokens": max_new_tokens,
        "do_sample": True if temperature > 1e-5 else False,
        "top_p": top_p if temperature > 1e-5 else 0,
        "streamer": streamer,
    }
    if temperature > 1e-5:
        gen_kwargs["temperature"] = temperature

    total_len = 0
    generated_text = ""
    with torch.no_grad():
        model.generate(**inputs, **gen_kwargs)
        for next_text in streamer:
            generated_text += next_text
            yield {
                "text": generated_text,
                "usage": {
                    "prompt_tokens": input_echo_len,
                    "completion_tokens": total_len - input_echo_len,
                    "total_tokens": total_len,
                },
            }
    ret = {
        "text": generated_text,
        "usage": {
            "prompt_tokens": input_echo_len,
            "completion_tokens": total_len - input_echo_len,
            "total_tokens": total_len,
        },
    }
    yield ret
