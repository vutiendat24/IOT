
from pydantic import BaseModel
from typing import List


class FaceEmbedding(BaseModel):
    identity: str
    embedding: List[float]
    confidence: float = 0.0