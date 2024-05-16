import torch
from transformers import PaliGemmaForConditionalGeneration, AutoProcessor
from PIL import Image
import requests
from transformers import BitsAndBytesConfig
from swarms import BaseMultiModalModel


class PaliGemma(BaseMultiModalModel):
    """
    PaliGemma is a class that represents a model for conditional generation using the PaliGemma model.

    Args:
        model_id (str): The identifier of the PaliGemma model to be used. Default is "google/paligemma-3b-mix-224".
        max_new_tokens (int): The maximum number of new tokens to be generated. Default is 20.
        skip_special_tokens (bool): Whether to skip special tokens during decoding. Default is True.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        model_id (str): The identifier of the PaliGemma model.
        model (PaliGemmaForConditionalGeneration): The PaliGemma model for conditional generation.
        processor (AutoProcessor): The processor for the PaliGemma model.
        max_new_tokens (int): The maximum number of new tokens to be generated.
        skip_special_tokens (bool): Whether to skip special tokens during decoding.

    Methods:
        run: Runs the PaliGemma model for conditional generation.

    """

    def __init__(
        self,
        model_id: str = "google/paligemma-3b-mix-224",
        max_new_tokens: int = 1000,
        skip_special_tokens: bool = True,
        *args,
        **kwargs
    ):
        bnb_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16,
        )

        self.model_id = model_id
        self.model = PaliGemmaForConditionalGeneration.from_pretrained(
            model_id,
            quantization_config=bnb_config,
            device_map={"": 0},
            *args,
            **kwargs
        )
        self.processor = AutoProcessor.from_pretrained(model_id)
        self.max_new_tokens = max_new_tokens
        self.skip_special_tokens = skip_special_tokens

    def run(self, task: str = None, image_url: str = None, *args, **kwargs):
        """
        Runs the PaliGemma model for conditional generation.

        Args:
            task (str): The task or prompt for conditional generation.
            image_url (str): The URL of the image to be used as input.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            str: The generated output text.

        """
        raw_image = Image.open(requests.get(image_url, stream=True).raw)
        inputs = self.processor(task, raw_image, return_tensors="pt")
        output = self.model.generate(
            **inputs, max_new_tokens=self.max_new_tokens, **kwargs
        )
        return self.processor.decode(
            output[0], skip_special_tokens=self.skip_special_tokens
        )[len(task) :]
