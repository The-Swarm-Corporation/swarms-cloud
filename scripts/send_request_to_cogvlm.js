const fs = require("fs");

// Convert image to Base64
function imageToBase64(imagePath) {
  return new Promise((resolve, reject) => {
    fs.readFile(imagePath, (err, data) => {
      if (err) {
        reject(err);
        return;
      }
      const base64Image = Buffer.from(data).toString("base64");
      resolve(base64Image);
    });
  });
}

// Replace 'image.jpg' with the path to your image
imageToBase64("images/3897e80dcb0601c0.jpg")
  .then((base64Image) => {
    const textData = { type: "text", text: "Describe what is in the image" };
    const imageData = {
      type: "image_url",
      image_url: { url: `data:image/jpeg;base64,${base64Image}` },
    };

    // Construct the request data
    const requestData = {
      model: "cogvlm-chat-17b",
      messages: [{ role: "user", content: [textData, imageData] }],
      temperature: 0.8,
      top_p: 0.9,
      max_tokens: 1024,
    };

    // Specify the URL of your FastAPI application
    const url = "http://api.swarms.world/v1/chat/completions";

    // Send the request
    fetch(url, {
      method: "POST",
      body: JSON.stringify(requestData),
      headers: {
        "Content-Type": "application/json",
      },
    })
      .then((response) => response.json())
      .then((data) => {
        // Print the response from the server
        console.log(data);
      })
      .catch((error) => {
        console.error("Error:", error);
      });
  })
  .catch((error) => {
    console.error("Error:", error);
  });
