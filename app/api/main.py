import time
from datetime import datetime, timedelta, timezone

from app.api.router import router
from app.custom_logging import CustomLogger
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

JST = timezone(timedelta(hours=9), "JST")
logger = CustomLogger.getLogger("application")

app = FastAPI(
    title="Bow API",
    description="Animals event management tool",
    version="1.0.0",
    redoc_url=None,
)
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=router, prefix="")


@app.get("/", include_in_schema=False)
def root():
    return {}


@app.get("/status", include_in_schema=False)
def get_status():
    return {}


@app.middleware("http")
async def access_log(request: Request, call_next):
    start_time = time.time()
    response = Response(
        "Internal Server Error", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
    try:
        response = await call_next(request)
    finally:
        args = {
            "remote_addr": request.scope["client"][0],
            "time": datetime.now(JST).isoformat(),
            "method": request.method,
            "path": request.scope["path"],
            "protocol": request.scope["scheme"],
            "status": response.status_code,
            "duration": round(time.time() - start_time, 3),
        }
        CustomLogger.getLogger("access_log").info(
            '{remote_addr} - - [{time}] "{method} {path} {protocol}" {status} {duration} -'.format(
                **args
            ),
            extra={"data": args},
        )

    return response


handler = Mangum(app, lifespan="auto")
