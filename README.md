[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Swarms Cloud
- Swarms-as-a-service
- 100% uptime
- Bleeding-Edge Performance
- Production-Grade Reliability
  
# Install
`pip install swarms-cloud`

# Models

## `CogVLM`
```python
import requests
import base64
from PIL import Image
from io import BytesIO


# Convert image to Base64
def image_to_base64(image_path):
    with Image.open(image_path) as image:
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    return img_str


# Replace 'image.jpg' with the path to your image
base64_image = image_to_base64("images/3897e80dcb0601c0.jpg")
text_data = {"type": "text", "text": "Describe what is in the image"}
image_data = {
    "type": "image_url",
    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
}

# Construct the request data
request_data = {
    "model": "cogvlm-chat-17b",
    "messages": [{"role": "user", "content": [text_data, image_data]}],
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 1024,
}

# Specify the URL of your FastAPI application
url = "https://api.swarms.world/v1/chat/completions"

# Send the request
response = requests.post(url, json=request_data)
# Print the response from the server
print(response.text)
```

## CogVLM in Node
```js
const fs = require('fs');
const https = require('https');
const sharp = require('sharp');

// Convert image to Base64
async function imageToBase64(imagePath) {
    try {
        const imageBuffer = await sharp(imagePath).jpeg().toBuffer();
        return imageBuffer.toString('base64');
    } catch (error) {
        console.error('Error converting image to Base64:', error);
    }
}

// Main function to execute the workflow
async function main() {
    const base64Image = await imageToBase64("images/3897e80dcb0601c0.jpg");
    const textData = { type: "text", text: "Describe what is in the image" };
    const imageData = {
        type: "image_url",
        image_url: { url: `data:image/jpeg;base64,${base64Image}` },
    };

    // Construct the request data
    const requestData = JSON.stringify({
        model: "cogvlm-chat-17b",
        messages: [{ role: "user", content: [textData, imageData] }],
        temperature: 0.8,
        top_p: 0.9,
        max_tokens: 1024,
    });

    const options = {
        hostname: 'api.swarms.world',
        path: '/v1/chat/completions',
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Content-Length': requestData.length,
        },
    };

    const req = https.request(options, (res) => {
        let responseBody = '';

        res.on('data', (chunk) => {
            responseBody += chunk;
        });

        res.on('end', () => {
            console.log('Response:', responseBody);
        });
    });

    req.on('error', (error) => {
        console.error(error);
    });

    req.write(requestData);
    req.end();
}

main();
```



## Calculate Pricing
```python
from transformers import AutoTokenizer
from swarms_cloud import calculate_pricing

# Initialize the tokenizer
tokenizer = AutoTokenizer.from_pretrained("gpt2")

# Define the example texts
texts = ["This is the first example text.", "This is the second example text."]

# Calculate pricing and retrieve the results
total_tokens, total_sentences, total_words, total_characters, total_paragraphs, cost = calculate_pricing(texts, tokenizer)

# Print the total tokens processed
print(f"Total tokens processed: {total_tokens}")

# Print the total cost
print(f"Total cost: ${cost:.5f}")
```


## Generate an API key
```python
from swarms_cloud.api_key_generator import generate_api_key

out = generate_api_key(prefix="sk", length=30)

print(out)

```

# Stack
- Backend: FastAPI
- Skypilot for container management
- Stripe for payment tracking
- Postresql for database
- TensorRT for inference
- Docker for cluster management
- Kubernetes for managing and autoscaling docker containers
- Terraform


# Example

scripts/send_request_to_cogvlm.py
```
url = "https://api.swarms.world/v1/chat/completions"

response = requests.post(url, json=request_data)

print(response.text)
```
# License
MIT
