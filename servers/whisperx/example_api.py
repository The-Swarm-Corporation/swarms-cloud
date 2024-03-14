from pydantic import BaseModel
from typing import List, Optional
import requests


# Single BaseModel for the entire API request structure
class WhisperTranscription(BaseModel):
    file: Optional[str] = None
    model: Optional[str] = "whisperx-large-v2"
    language: Optional[str] = "en"
    prompt: Optional[str] = None
    response_format: Optional[str] = "json"
    temperature: Optional[int] = 0
    timestamp_granularities: Optional[List[str]] = ["sentence"]


# Construct the request data
request_data = WhisperTranscription(file="song.mp3")

# Specify the URL of your FastAPI application
url = "https://localhost:8000/v1/audio/transcriptions"

# Send the request
response = requests.post(url, json=request_data.dict(), verify=False)
# Print the response from the server
print(response.text)
