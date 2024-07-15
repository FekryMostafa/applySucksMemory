from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient
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
    os.getenv("QDRANT_LINK"),
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
    print(user_id)
    collection_name = str(user_id)
    vector_store = Qdrant(
        client=client,
        collection_name=collection_name,
        embeddings=embeddings,
    )
    
    results = vector_store.similarity_search("", k=100)  # Adjust k as needed
    
    memories = []
    for doc in results:
        content_parts = doc.page_content.split("\n", 1)
        question = content_parts[0].replace("Question: ", "") if len(content_parts) > 0 else ""
        answer = content_parts[1].replace("Answer: ", "") if len(content_parts) > 1 else ""
        memories.append(MemoryResponse(
            id=str(doc.metadata.get('_id', '')),
            question=question,
            answer=answer,
            company=doc.metadata.get('company', ""),
            date=doc.metadata.get('date', "")
        ))
        
        return memories

@app.delete("/memories/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    collection_name = str(user_id)
    try:
        client.delete(
            collection_name=collection_name,
            points_selector=[memory_id]
        )
        return {"message": "Memory deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Memory not found or couldn't be deleted: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)