from swarms_cloud.schema.openai_spec import OpenAIAPIWrapper


def test_set_input_spec():
    wrapper = OpenAIAPIWrapper()
    wrapper.set_input_spec(prompt="Hello, world!")
    assert wrapper.input_spec.prompt == "Hello, world!"


def test_set_output_spec():
    wrapper = OpenAIAPIWrapper()
    wrapper.set_output_spec(status="completed")
    assert wrapper.output_spec.status == "completed"


def test_get_input_spec():
    wrapper = OpenAIAPIWrapper()
    wrapper.set_input_spec(prompt="Hello, world!")
    assert (
        wrapper.get_input_spec()
        == '{"model": "gpt-3.5-turbo", "max_new_tokens": 100, "prompt": "Hello, world!", "stream": false, "sampling_params": null, "best_of": 1, "echo": false, "frequency_penalty": 0.0, "logit_bias": null, "logprobs": null, "max_tokens": null, "n": 1, "presence_penalty": 0.0, "seed": null, "stop": null, "suffix": null, "temperature": 0.0, "top_k": 0, "top_p": 1.0, "user": null}'
    )


def test_get_output_spec():
    wrapper = OpenAIAPIWrapper()
    wrapper.set_output_spec(status="completed")
    assert '"status": "completed"' in wrapper.get_output_spec()
