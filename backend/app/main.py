from fastapi import FastAPI
from app.routes.health import router as health_router
from app.routes.upload import router as upload_router

app = FastAPI(title="Celebrity Face Recognition API")

app.include_router(health_router)
app.include_router(upload_router)

@app.get("/")
def root():
    return {"message": "API is running"}    