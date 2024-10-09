import warnings

# Suppress all warnings


# Suppress specific warnings (if you want to keep this)
def cleanup_logs():
    warnings.filterwarnings("ignore")
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="pydantic._internal._fields"
    )
    warnings.filterwarnings(
        "ignore", category=SyntaxWarning, module="swarms_cloud.cli.main"
    )
    warnings.filterwarnings(
        "ignore", category=UserWarning, module="pydantic._internal._fields"
    )
