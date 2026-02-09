from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI application instance
app = FastAPI()

# Configure CORS middleware to allow requests from specified origins
# Vue runs on http://localhost:5173
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a POST endpoint at /api/query that returns a simple JSON response
@app.post("/api/query")
def read_api_query():
    return {"Hello": "World"}
