from fastapi import FastAPI
from app.api.v1 import auth, user, pismo, analiza, opcja

app = FastAPI(
    title="Pisma App API",
    description="API for managing legal documents and analysis.",
    version="1.0.0"
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(user.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(pismo.router, prefix="/api/v1/pisma", tags=["Pisma"])
app.include_router(analiza.router, prefix="/api/v1/analizy", tags=["Analizy"])
app.include_router(opcja.router, prefix="/api/v1/opcje", tags=["Opcje"])

@app.get("/")
def read_root():
    return {"message": "Welcome to Pisma App API"}
