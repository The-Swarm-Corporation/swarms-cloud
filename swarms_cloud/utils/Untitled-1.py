# %%
# Create a config
import requests

url = "http://35.222.137.183:30001/collections"

data = {"name": "my_collection"}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())


# %%
import requests

collection_id = "my_collection"  # Replace with the actual collection ID

url = f"http://127.0.0.1:8000/collections/{collection_id}/documents"
data = {
    "documents": [
        "This is a document about pineapples",
        "This is a document about oranges",
    ],
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())


# %%
import requests

collection_id = "my_collection"  # Replace with the actual collection ID

url = f"http://127.0.0.1:8000/collections/{collection_id}/documents"
data = {"query_texts": ["This is a query document about Hawaii"], "n_results": 2}

response = requests.get(url, json=data)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())

# %%
import requests

collection_id = "my_collection"  # Replace with the actual collection ID

document_id = "your_document_id_here"  # Replace with the actual document ID
url = f"http://127.0.0.1:8000/collections/{collection_id}/documents/{document_id}"

response = requests.delete(url)

print("Status Code:", response.status_code)
print("Response JSON:", response.json())


# %% [markdown]
#
