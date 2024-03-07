import os
from fastapi import FastAPI, File, Form, UploadFile, HTTPException
import uvicorn
from typing import Optional, List
from PIL import Image
import torchvision.transforms as transforms
import torch
from run import QWenInfer, vit_process  # Adjust import paths as necessary

app = FastAPI()
# Directory to save pre-processed images as tensors
TENSOR_DIR = "./tensor_images"
os.makedirs(TENSOR_DIR, exist_ok=True)
temp_dir = "./tempfiles"
# Configuration for model and inference
vit_engine_dir = "./plan"
qwen_infer = QWenInfer(
    tokenizer_dir="./Qwen-VL-Chat",
    qwen_engine_dir="./trt_engines/Qwen-VL-7B-Chat-int4-gptq",
    log_level="info",
    output_csv=None,
    output_npy=None,
    num_beams=1
)
qwen_infer.qwen_model_init()

def load_and_transform_image(image_file: UploadFile):
    """Load an image file, transform it, and save as a tensor."""
    image = Image.open(image_file.file).convert("RGB")
    transform = transforms.Compose([
        transforms.Resize((448, 448)),  # Resize image to expected dimensions
        transforms.ToTensor(),  # Convert to tensor
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),  # Normalize
    ])
    image_tensor = transform(image).unsqueeze(0)  # Add batch dimension
    print(f'image_tensor {image_tensor.shape}')
    # Save the tensor for inference
    tensor_file_path = os.path.join(TENSOR_DIR, f'{image_file.filename}.pt')
    
    # file = f'{image_file.filename}.pt'
    torch.save(image_tensor, tensor_file_path)
    
    return tensor_file_path

@app.post("/infer/")
async def infer(
    image: UploadFile = File(...),
    input_text: str = Form(...),
    max_new_tokens: int = Form(1024),
    history: Optional[List[str]] = Form(None)
):
    try:
        temp_image_path = os.path.join(temp_dir, image.filename)
        with open(temp_image_path, 'wb') as f:
                contents = await image.read()
                f.write(contents)
        print(input_text)
        print(type(input_text))
        transformed_img_path = load_and_transform_image(image)
        images = [{'image': transformed_img_path}]
        stream = torch.cuda.current_stream().cuda_stream
        image_embeds = vit_process(images, vit_engine_dir, stream)
        print(temp_image_path)
        history = []
        content_list = images
        content_list.append({'text': input_text})
        print("content list")
        output_text = qwen_infer.qwen_infer(
            input_vit=image_embeds,
            images_path=images,
            input_text=input_text,
            max_new_tokens=max_new_tokens,
            history=history
        )
        print(output_text)
        os.remove(temp_image_path)
        os.remove(transformed_img_path)
        return {"output_text": output_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
