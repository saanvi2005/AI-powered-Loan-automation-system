from fastapi import FastAPI
from .api.sales_routes import router as sales_router
from .api.underwriter_router import router as underwriter_router
from .api.document_router import router as document_router
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:8000", "http://127.0.0.1:8000", "file://", "null"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(sales_router, prefix="/sales_agent")
app.include_router(underwriter_router, prefix="/underwriter")
app.include_router(document_router, prefix="/documents")

@app.get("/")
def read_root():
    return {
        "message": "Loan Application System API",
        "status": "running",
        "endpoints": {
            "chat": "/sales_agent/message",
            "underwriting": "/underwriter/analyze",
            "documents": "/documents/verify"
        }
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Serve static files
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
