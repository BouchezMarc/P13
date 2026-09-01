from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router


app = FastAPI(
    title="Chess AI Agent API",
    version="0.2.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/healthcheck")
def healthcheck():
    return {"status": "ok"}


app.include_router(router)