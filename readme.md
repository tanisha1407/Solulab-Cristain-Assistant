# Christian AI Assistant

A scripture-grounded Christian AI assistant built using FastAPI, Streamlit, Gemini, and ChromaDB.

## Features

* RAG-based scripture retrieval
* Bible verse grounding
* Hallucination prevention
* Denomination-aware responses
* Safety moderation
* Christian image prompt generation
* FastAPI backend
* Streamlit frontend

## Tech Stack

* FastAPI
* Streamlit
* Gemini API
* ChromaDB
* Sentence Transformers
* Python

## Architecture

User Query → Moderation → RAG Retrieval → Gemini Generation → Validation → Response

## Setup

### Backend

```bash
cd backend
pip install -r requirements.txt
python ingest_bible.py
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
streamlit run app.py
```

## Evaluation

Includes:

* adversarial prompts
* hallucination tests
* denomination tests

## Author

Tanisha
