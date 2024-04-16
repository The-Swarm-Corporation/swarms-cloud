curl -X POST http://localhost:8000/v1/chat/completions \
-H "Content-Type: application/json" \
-d '{
    "model_name": "ByteDance/AnimateDiff-Lightning",
    "task": "Beautiful girl studying with hijab",
    "resolution": "720",
    "length": 60,
    "style": "example_style",
    "n": 1,
    "output_type": "mp4",
    "output_path": "example_output_path"
}'