import pytest
from swarms_cloud.calculate_pricing import calculate_pricing
from transformers import AutoTokenizer


@pytest.mark.asyncio
async def test_calculate_pricing():
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    texts = ["This is the first example text.", "This is the second example text."]
    (
        total_tokens,
        cost,
    ) = await calculate_pricing(texts, tokenizer)

    assert total_tokens == 20
    assert cost == 0.00002


@pytest.mark.asyncio
async def test_calculate_pricing_empty_text():
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    texts = [""]
    (
        total_tokens,
        cost,
    ) = await calculate_pricing(texts, tokenizer)

    assert total_tokens == 2  # Special tokens
    assert cost == 0.000002


@pytest.mark.asyncio
async def test_calculate_pricing_no_text():
    tokenizer = AutoTokenizer.from_pretrained("gpt2")
    texts = []
    (
        total_tokens,
        cost,
    ) = await calculate_pricing(texts, tokenizer)

    assert total_tokens == 0
    assert cost == 0
