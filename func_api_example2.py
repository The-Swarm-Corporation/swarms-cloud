from swarms_cloud.func_api_wrapper import FuncAPIWrapper

api = FuncAPIWrapper(
    port=8001,
)


@api.add("/agent", method="post")
def check():
    return "Hello World"


api.run()
