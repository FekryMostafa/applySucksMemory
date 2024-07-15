from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from qdrant_client import QdrantClient
from qdrant_client.http import models
from langchain_together import TogetherEmbeddings
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Qdrant setup
client = QdrantClient(
    url=os.getenv("QDRANT_LINK"),
    api_key=os.getenv("QDRANT_API_KEY")
)
embeddings = TogetherEmbeddings(model="togethercomputer/m2-bert-80M-8k-retrieval")

class MemoryResponse(BaseModel):
    id: str
    question: str
    answer: str
    company: str
    date: str

@app.get("/memories/{user_id}", response_model=List[MemoryResponse])
async def get_memories(user_id: str):
    print(f"Fetching memories for user: {user_id}")
    collection_name = "memories"  # Use a fixed collection name
    
    search_result = client.scroll(
        collection_name=collection_name,
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
    
    print(f"Found {len(memories)} memories")
    return memories

@app.delete("/memories/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    collection_name = "memories"  # Use a fixed collection name
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=models.PointIdsList(points=[memory_id]),
            wait=True
        )
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Memory not found or couldn't be deleted: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)