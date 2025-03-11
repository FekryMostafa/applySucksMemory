from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_together import TogetherEmbeddings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Apply.Sucks Memory API",
    description="API for retrieving previously answered job application questions for autofilling",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Qdrant setup for vector storage
client = QdrantClient(
    url=os.getenv("QDRANT_LINK"),
    api_key=os.getenv("QDRANT_API_KEY")
)
# Initialize embedding model for semantic matching of questions
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")

# Collection name for job application memories
COLLECTION_NAME = "memories"

class MemoryResponse(BaseModel):
    """Model for job application question memory data."""
    id: str
    question: str  # The job application question
    answer: str    # The user's previous answer
    company: str   # Company where the application was submitted
    date: str      # Date when the application was submitted


@app.get("/memories/{user_id}", response_model=List[MemoryResponse])
async def get_memories(user_id: str) -> List[MemoryResponse]:
    """
    Retrieve all previously answered job application questions for a specific user.
    These can be used to autofill similar questions in future job applications.
    
    Args:
        user_id: The unique identifier for the user
        
    Returns:
        List of memory objects containing job application questions and their previous answers
    """
    print(f"Fetching job application memories for user: {user_id}")
    
    search_result = client.scroll(
        collection_name=COLLECTION_NAME,
        scroll_filter=models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.userID",
                    match=models.MatchValue(value=user_id)
                )
            ]
        ),
        limit=100
    )
    
    memories = []
    for point in search_result[0]:
        payload = point.payload
        metadata = payload.get('metadata', {})
        page_content = payload.get('page_content', '')
        
        # Split page_content into question and answer
        content_parts = page_content.split("\n", 1)
        question = content_parts[0].replace("Question: ", "") if len(content_parts) > 0 else ""
        answer = content_parts[1].replace("Answer: ", "") if len(content_parts) > 1 else ""
        
        memories.append(MemoryResponse(
            id=str(point.id),
            question=question,
            answer=answer,
            company=metadata.get('company', ''),
            date=metadata.get('date', '')
        ))
    
    print(f"Found {len(memories)} job application memories")
    return memories


@app.delete("/memories/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str) -> Dict[str, str]:
    """
    Delete a specific job application memory for a user.
    
    Args:
        user_id: The unique identifier for the user
        memory_id: The unique identifier for the memory to delete
        
    Returns:
        A message indicating success
        
    Raises:
        HTTPException: If the memory cannot be found or deleted
    """
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=models.PointIdsList(points=[memory_id]),
            wait=True
        )
        return {"message": "Job application memory deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Job application memory not found or couldn't be deleted: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)