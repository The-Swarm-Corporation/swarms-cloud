import os

import torch
import uvicorn
from diffusers import (
    AnimateDiffPipeline,
    EulerDiscreteScheduler,
    MotionAdapter,
)
from diffusers.utils import export_to_gif
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from huggingface_hub import hf_hub_download
from loguru import logger
from safetensors.torch import load_file
from fastapi.responses import FileResponse, JSONResponse
from swarms_cloud.schema.text_to_video import TextToVideoRequest, TextToVideoResponse

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

        logger.info(f"Output ready: {output}")

        out = export_to_gif(output.frames[0], output_path)
        logger.info(f"Exported to GIF: {out}")
        return out
    except Exception as e:
        logger.error(f"Error: {e}")
        return None


@app.post("/v1/chat/completions", response_model=TextToVideoResponse)
async def create_chat_completion(
    request: TextToVideoRequest,  # token: str = Depends(authenticate_user)
):
    try:
        logger.info(f"Request: {request}")

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

        # try:
        response = text_to_video(**gen_params)
        logger.info(f"Response: {response}")
        # except Exception as e:
        #     logger.error(f"Error: {e}")
        #     raise HTTPException(status_code=500, detail="Internal Server Error")

        log = TextToVideoResponse(
            status="success",
            request_details=request,
            output_path=response,
        )

        # logger.info(f"Response: {out}")
        logger.info(f"Downloading the file: {response}")
        
        FileResponse(
            response,
            media_type="image/gif",
            filename=request.output_path
        )

        return JSONResponse(content=log.model_dump(), status_code=200)
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
