llm = LLM(
    model="llava-hf/llava-1.5-7b-hf",
    image_input_type="pixel_values",
    image_token_id=32000,
    image_input_shape="1,3,336,336",
    image_feature_size=576,
)

prompt = "<image>" * 576 + "What is the content of this image?"

images=torch.load("xxx")  # This should be generated offline or by another online component. See tests/images/ for samples

from vllm.sequence import MultiModalData
llm.generate(prompt, multi_modal_data=MultiModalData(type=MultiModalData.Type.IMAGE, data=images))