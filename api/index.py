from fastapi import FastAPI

app = FastAPI()

@app.get("/api/health")
def health_check():
    return {"status": "healthy", "mode": "minimal_test"}

@app.get("/api/collections")
def collections_test():
    return [{"id": 1, "name": "HR & Policy"}]

@app.get("/api/documents")
def documents_test():
    return [{"id": 1, "filename": "sample_document.pdf"}]
