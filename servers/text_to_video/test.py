import torch
from diffusers import (
    AnimateDiffPipeline,
    EulerDiscreteScheduler,
    MotionAdapter,
)
from diffusers.utils import export_to_gif
from dotenv import load_dotenv
from huggingface_hub import hf_hub_download
from safetensors.torch import load_file
from loguru import logger

# Load environment variables from .env file
load_dotenv()


def text_to_video(
    task: str,
    model_name: str = "ByteDance/AnimateDiff-Lightning",
    guidance_scale: float = 1.0,
    inference_steps: int = 4,
    output_type: str = ".gif",
    output_path: str = "animation.gif",
    n: int = 1,
    length: int = 60,
    *args,
    **kwargs,
):
    """
    Converts a given text task into an animated video.

    Args:
        task (str): The text task to be converted into a video.

    Returns:
        str: The path to the exported GIF file.
    """
    try:
        device = "cuda"
        dtype = torch.float16

        repo = model_name
        ckpt = f"animatediff_lightning_{inference_steps}step_diffusers.safetensors"
        base = "emilianJR/epiCRealism"  # Choose to your favorite base model.
        adapter = MotionAdapter().to(device, dtype)
        adapter.load_state_dict(load_file(hf_hub_download(repo, ckpt), device=device))

        pipe = AnimateDiffPipeline.from_pretrained(
            base, motion_adapter=adapter, torch_dtype=dtype
        ).to(device)

        logger.info(f"Initialized Model: {model_name}")

        pipe.scheduler = EulerDiscreteScheduler.from_config(
            pipe.scheduler.config,
            timestep_spacing="trailing",
            beta_schedule="linear",
        )

        # outputs = []
        # for i in range(n):
        #     output = pipe(
        #         prompt=task,
        #         guidance_scale=guidance_scale,
        #         num_inference_steps=inference_steps,
        #     )
        #     outputs.append(output)
        #     out = export_to_gif([output], f"{output_path}_{i}.gif")
        # else:
        #     out = export_to_video([output], f"{output_path}_{i}.mp4")
        output = pipe(
            prompt=task,
            guidance_scale=guidance_scale,
            num_inference_steps=inference_steps,
        )
        out = export_to_gif(output.frames[0], output_path)
        return out
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


out = text_to_video(task="A girl in hijab studying in a library")
print(out)
