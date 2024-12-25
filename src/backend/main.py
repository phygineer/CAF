from typing import Union

import time

from fastapi import FastAPI, Request
from routers import mock,docker,selenium,file
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mock.router,prefix="/api",tags=["mock"])
app.include_router(docker.router,prefix="/api",tags=["docker"])
app.include_router(selenium.router,prefix="/api",tags=["selenium"])
app.include_router(file.router,prefix="/api",tags=["file"])
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    process_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
def _():
    return {"Message": "CAF you know for automation."}
