from dotenv import load_dotenv
import os

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from fastapi.responses import FileResponse

from swarms_cloud.schema.text_to_video import TextToVideoRequest, TextToVideoResponse

# from exa.structs.parallelize_models_gpus import prepare_model_for_ddp_inference

# Load environment variables from .env file
load_dotenv()

# Create a FastAPI app
app = FastAPI(debug=True)


# Load the middleware to handle CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
    import torch
    from diffusers import (
        AnimateDiffPipeline,
        MotionAdapter,
        EulerDiscreteScheduler,
    )
    from diffusers.utils import export_to_gif, export_to_video
    from huggingface_hub import hf_hub_download
    from safetensors.torch import load_file

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
    pipe.scheduler = EulerDiscreteScheduler.from_config(
        pipe.scheduler.config,
        timestep_spacing="trailing",
        beta_schedule="linear",
    )

    outputs = []
    for i in range(n):
        output = pipe(
            prompt=task,
            guidance_scale=guidance_scale,
            num_inference_steps=inference_steps,
        )
        outputs.append(output)
        if output_type == ".gif":
            out = export_to_gif([output], f"{output_path}_{i}.gif")
        else:
            out = export_to_video([output], f"{output_path}_{i}.mp4")

    return out


@app.post("/v1/chat/completions", response_model=TextToVideoResponse)
async def create_chat_completion(
    request: TextToVideoRequest,  # token: str = Depends(authenticate_user)
):
    try:
        logger.info(f"Request: {request}")
        
        
        # Validate input parameters
        # if not isinstance(request.model_name, str) or not request.model_name:
        #     raise HTTPException(status_code=400, detail="Invalid model_name")
        # if not isinstance(request.task, str) or not request.task:
        #     raise HTTPException(status_code=400, detail="Invalid task")
        # if not isinstance(request.resolution, int) or request.resolution <= 0:
        #     raise HTTPException(status_code=400, detail="Invalid resolution")
        # if not isinstance(request.length, int) or request.length <= 0:
        #     raise HTTPException(status_code=400, detail="Invalid length")
        # if not isinstance(request.style, str) or not request.style:
        #     raise HTTPException(status_code=400, detail="Invalid style")
        # if not isinstance(request.n, int) or request.n <= 0:
        #     raise HTTPException(status_code=400, detail="Invalid n")
        # if not isinstance(request.output_type, str) or not request.output_type:
        #     raise HTTPException(status_code=400, detail="Invalid output_type")
        # if not isinstance(request.output_path, str) or not request.output_path:
        #     raise HTTPException(status_code=400, detail="Invalid output_path")

        # print(f"Request: {request}")

        gen_params = dict(
            model_name=request.model_name,
            task=request.task,
            resolution=request.resolution,
            length=request.length,
            style=request.style,
            n=request.n,
            output_type=request.output_type,
            output_path=request.output_path,
        )

        logger.info(f"Running text_to_video model with params: {gen_params}")
        response = text_to_video(**gen_params)

        out = TextToVideoResponse(
            status="success",
            request_details=request,
            video_url=response,
            error=None,
        )

        logger.info(f"Response: {out}")

        logger.info(f"Downloading the file: {response}")
        download_save = FileResponse(
            path=response,
            filename=request.output_path,
            media_type="application/octet-stream",
        )

        return out, download_save
    except Exception as e:
        logger.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("MODEL_API_PORT", 8000)),
        log_level="info",
        use_colors=True,
    )
