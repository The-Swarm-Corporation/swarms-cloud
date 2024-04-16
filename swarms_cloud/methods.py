from fastapi import FastAPI
from fastapi.responses import Response
from starlette_exporter import PrometheusMiddleware, handle_metrics


TIMEOUT_KEEP_ALIVE = 5  # seconds
app = FastAPI(
    debug=True,
)
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)


@app.get("/health")
async def health() -> Response:
    """Health check."""
    return Response(status_code=200)


# # Add prometheus asgi middleware to route /metrics requests
# metrics_app = make_asgi_app()
# app.mount("/metrics", metrics_app)
