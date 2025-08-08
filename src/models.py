# src/models.py
from pydantic import BaseModel, Field
from typing import List

class HackRxRunRequest(BaseModel):
    documents: str = Field(
        ...,
        description="URL of the policy PDF document to be processed.",
        example="https://hackrx.blob.core.windows.net/assets/policy.pdf?sv=..."
    )
    questions: List[str] = Field(
        ...,
        description="A list of questions to ask about the document.",
        example=["What is the grace period for premium payment?"]
    )

class HackRxRunResponse(BaseModel):
    answers: List[str] = Field(
        ...,
        description="A list of answers corresponding to the questions asked.",
        example=["A grace period of thirty days is provided..."]
    )