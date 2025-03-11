# Apply.Sucks Memory API

A FastAPI-based backend service for the Apply.Sucks platform that manages job application memories. This API allows users to retrieve previously answered job application questions so they can be autofilled in future applications, saving time and reducing repetitive work.

## Features

- Retrieve previously answered job application questions for autofilling
- Store job application questions and answers for future use
- Delete specific memories when no longer needed
- Vector-based storage using Qdrant for efficient retrieval and semantic matching
- Embedding generation using Together AI's embedding model for better question matching

## Purpose

The Apply.Sucks Memory API serves as the backend for storing and retrieving job application questions and answers. When a user encounters a question they've previously answered while filling out a job application, the system can automatically retrieve and suggest the previous answer, making the job application process faster and more efficient. This eliminates the need to repeatedly type the same answers to common application questions.

## Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **Qdrant**: Vector database for storing and retrieving memories with semantic search capabilities
- **LangChain**: Framework for working with language models and vector stores
- **Together AI**: Embedding model provider for converting text to vector representations
- **Docker**: Containerization for easy deployment

## Environment Variables

The application requires the following environment variables:

```
QDRANT_LINK=your_qdrant_instance_url
QDRANT_API_KEY=your_qdrant_api_key
```

A `.env.example` file is provided in the repository. Copy this file to create your own `.env` file:

```bash
cp .env.example .env
```

Then edit the `.env` file with your actual credentials.

## API Endpoints

### Get Memories

```
GET /memories/{user_id}
```

Retrieves all previously answered job application questions for a specific user.

**Response:**
```json
[
  {
    "id": "memory_id",
    "question": "Describe a challenging situation at work and how you handled it.",
    "answer": "User's previous answer to this question",
    "company": "Company name",
    "date": "Application date"
  }
]
```

### Delete Memory

```
DELETE /memories/{user_id}/{memory_id}
```

Deletes a specific memory when it's no longer needed.

**Response:**
```json
{
  "message": "Job application memory deleted successfully"
}
```

## Running Locally

1. Clone the repository
2. Create a `.env` file with the required environment variables:
   ```
   cp .env.example .env
   ```
   Then edit the `.env` file with your actual credentials.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Run the application:
   ```
   uvicorn main:app --reload
   ```

## Docker Deployment

Build and run the Docker container:

```bash
docker build -t apply-sucks-memory .
docker run -p 8080:8080 --env-file .env apply-sucks-memory
```

## API Documentation

When running, the API documentation is available at:
- Swagger UI: `http://localhost:8080/docs`
- ReDoc: `http://localhost:8080/redoc` 