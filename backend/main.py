from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.pipeline import verify_response




app = FastAPI(
    title="Halora",
    description="Hallucination Detection Framework",
    version="1.0.0",
)




app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class ResponseVerificationRequest(BaseModel):

    response: str = Field(
        ...,
        min_length=1,
        description="Complete AI-generated response including references",
    )

    top_k: int = Field(
        default=2,
        ge=1,
        le=5,
        description="Number of evidence passages to retrieve",
    )




@app.get("/")
def root():

    return {
        "status": "online",
        "service": "Citation Checker API",
        "version": "3.0.0",
        "mode": "full_response_verification",
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }




@app.post("/api/verify-response")
def verify_ai_response(
    request: ResponseVerificationRequest,
):

    try:

        result = verify_response(
            response=request.response,
            top_k=request.top_k,
        )

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e),
        )




if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )