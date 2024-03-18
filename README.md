[![Multi-Modality](agorabanner.png)](https://discord.gg/qUtxnK2NMf)

# Swarms Cloud
Infrastructure for scalable, reliable, and economical Multi-Modal Model API serving and deployment. We're using terraform to orchestrate infrastructure, FastAPI to host the models. If you're into deploying models for millions of people, join our discord and help contribute.


# Install
`pip install swarms-cloud`

# Examples

### Example Python
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

### Example API Request in Node
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

### Example API Request in Go

```go
package main

import (
    "bytes"
    "encoding/base64"
    "encoding/json"
    "fmt"
    "image"
    "image/jpeg"
    _ "image/png" // Register PNG format
    "io"
    "net/http"
    "os"
)

// imageToBase64 converts an image to a Base64-encoded string.
func imageToBase64(imagePath string) (string, error) {
    file, err := os.Open(imagePath)
    if err != nil {
        return "", err
    }
    defer file.Close()

    img, _, err := image.Decode(file)
    if err != nil {
        return "", err
    }

    buf := new(bytes.Buffer)
    err = jpeg.Encode(buf, img, nil)
    if err != nil {
        return "", err
    }

    return base64.StdEncoding.EncodeToString(buf.Bytes()), nil
}

// main is the entry point of the program.
func main() {
    base64Image, err := imageToBase64("images/3897e80dcb0601c0.jpg")
    if err != nil {
        fmt.Println("Error converting image to Base64:", err)
        return
    }

    requestData := map[string]interface{}{
        "model": "cogvlm-chat-17b",
        "messages": []map[string]interface{}{
            {
                "role":    "user",
                "content": []map[string]string{{"type": "text", "text": "Describe what is in the image"}, {"type": "image_url", "image_url": {"url": fmt.Sprintf("data:image/jpeg;base64,%s", base64Image)}}},
            },
        },
        "temperature": 0.8,
        "top_p":       0.9,
        "max_tokens":  1024,
    }

    requestBody, err := json.Marshal(requestData)
    if err != nil {
        fmt.Println("Error marshaling request data:", err)
        return
    }

    url := "https://api.swarms.world/v1/chat/completions"
    request, err := http.NewRequest("POST", url, bytes.NewBuffer(requestBody))
    if err != nil {
        fmt.Println("Error creating request:", err)
        return
    }

    request.Header.Set("Content-Type", "application/json")

    client := &http.Client{}
    response, err := client.Do(request)
    if err != nil {
        fmt.Println("Error sending request:", err)
        return
    }
    defer response.Body.Close()

    responseBody, err := io.ReadAll(response.Body)
    if err != nil {
        fmt.Println("Error reading response body:", err)
        return
    }

    fmt.Println("Response:", string(responseBody))
}
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


# License
MIT
