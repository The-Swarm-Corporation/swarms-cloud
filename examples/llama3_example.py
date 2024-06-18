from swarms import llama3Hosted

llama3 = llama3Hosted(
    model="meta-llama/Meta-Llama-3-8B",
    base_url="http://199.204.135.78:8090/v1/chat/completions",
    temperature=0.1,
)

out = llama3.run("what is your name?")
print(out)
