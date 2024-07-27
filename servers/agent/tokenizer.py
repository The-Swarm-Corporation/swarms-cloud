import tiktoken


def count_tokens(text: str):
    # Get the encoding for the specific model
    enc = tiktoken.encoding_for_model("gpt-4o")

    # Encode the text
    tokens = enc.encode(text)

    # Count the tokens
    token_count = len(tokens)

    return token_count


out = count_tokens("Hello, how are you?")
print(out)
