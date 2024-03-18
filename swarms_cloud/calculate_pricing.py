from transformers import PreTrainedTokenizer
from PIL import Image
from typing import Any, List


# Function to calculate tokens and pricing
def calculate_pricing(
    texts: List[str] = None,
    tokenizer: PreTrainedTokenizer = None,
    images: List[str] = None,
    rate_per_million: float = 0.01,
    img_model: Any = None,
    rate_img: float = 0.003,
):
    """
    Calculate containtaining for otal number of  texts based on the number of tokens, sentences, words, characters, and paragraphs.

    Args:
        texts (list): A list of texts to calculate pricing for.
        tokenizer (PreTrainedTokenizer): A pre-trained tokenizer object used to tokenize the texts.
        rate_per_million (float, optional): The rate per million tokens used to calculate the cost. Defaults to 0.01.

    Returns:
        tuple: A tuple containing the total number of tokens, sentences, words, characters, paragraphs, and the calculated cost.

    Example usage:
    >>> tokenizer = AutoTokenizer.from_pretrained("gpt2")
    >>> texts = ["This is the first example text.", "This is the second example text."]
    >>> total_tokens, total_sentences, total_words, total_characters, total_paragraphs, cost = calculate_pricing(texts, tokenizer)
    >>> print(f"Total tokens processed: {total_tokens}")
    >>> print(f"Total cost: ${cost:.5f}")

    """
    total_tokens = 0
    total_sentences = 0
    total_words = 0
    total_characters = 0
    total_paragraphs = 0
    total_images_processed = 0
    image_processing_cost = 0

    for text in texts:
        # Tokenize the text and count tokens
        tokens = tokenizer.encode(text, add_special_tokens=True)
        total_tokens += len(tokens)

        # Count sentences
        sentences = text.count(".") + text.count("!") + text.count("?")
        total_sentences += sentences

        # Count words
        words = len(text.split())
        total_words += words

        # Count characters
        characters = len(text)
        total_characters += characters

        # Count paragraphs
        paragraphs = text.count("\n\n") + 1
        total_paragraphs += paragraphs

    if images and img_model:
        for img_path in images:
            # Load the image
            Image.open(img_path)
            # Process the image
            image_processing_cost += rate_img
            total_images_processed += 1

        # Calculate the image processing cost
        total_images_processed + rate_img

    # Calculate total cost with high precision
    cost = (total_tokens / 1_000_000) * rate_per_million
    print(f"Total cost: ${float(cost):.10f}")

    return (
        total_tokens,
        total_sentences,
        total_words,
        total_characters,
        total_paragraphs,
        cost,
    )
