from eduone_cdn.app.core.views import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(openapi_url="/cdn/openapi.json", docs_url="/cdn/docs", redoc_url=None)
app.include_router(router)

origins = ["http://172.21.0.1:8080", "http://127.0.0.1:8080"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
