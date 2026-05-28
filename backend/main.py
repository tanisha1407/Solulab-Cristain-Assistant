from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import base64

from google import genai
from google.genai import types

from fastapi.middleware.cors import CORSMiddleware

from rag import retrieve_scripture
from moderation import moderate_input
from prompts import SYSTEM_PROMPT
from validator import validate_references

from memory import (
    save_chat,
    clear_memory,
    format_chat_history
)

# ==========================================
# LOAD ENV VARIABLES
# ==========================================

load_dotenv()

# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="Christian AI Assistant",
    description="Scripture-grounded Christian AI assistant",
    version="1.0.0"
)

# ==========================================
# ENABLE CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# GEMINI CONFIGURATION
# ==========================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY not found in .env"
    )

# Single client for both text and image generation
gemini_client = genai.Client(
    api_key=GEMINI_API_KEY
)

# ==========================================
# REQUEST MODELS
# ==========================================

class ChatRequest(BaseModel):

    question: str

    denomination: str = (
        "Non-denominational"
    )


class ImageRequest(BaseModel):

    prompt: str

# ==========================================
# ROOT ROUTE
# ==========================================

@app.get("/")
def root():

    return {
        "message": (
            "Christian AI Assistant "
            "API Running"
        )
    }

# ==========================================
# HEALTH CHECK
# ==========================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }

# ==========================================
# CHAT ENDPOINT
# ==========================================

@app.post("/chat")
def chat(request: ChatRequest):

    user_question = (
        request.question.strip()
    )

    # =========================
    # MODERATION CHECK
    # =========================

    is_safe = moderate_input(
        user_question
    )

    if not is_safe:

        return {
            "success": False,
            "response": (
                "I cannot assist with "
                "hateful, extremist, "
                "or harmful religious "
                "content."
            )
        }

    # =========================
    # RETRIEVE SCRIPTURE
    # =========================

    verses = retrieve_scripture(
        user_question
    )

    scripture_context = ""

    valid_refs = []

    for verse in verses:

        reference = verse["reference"]

        text = verse["text"]

        valid_refs.append(reference)

        scripture_context += (
            f"{reference}: {text}\n\n"
        )

    # =========================
    # MEMORY CONTEXT
    # =========================

    history_text = (
        format_chat_history()
    )

    # =========================
    # FINAL PROMPT
    # =========================

    final_prompt = f"""
{SYSTEM_PROMPT}

USER DENOMINATION:
{request.denomination}

PREVIOUS CONVERSATION:
{history_text}

RETRIEVED SCRIPTURE:
{scripture_context}

USER QUESTION:
{user_question}

INSTRUCTIONS:
- Answer naturally
- Stay Biblically grounded
- Use ONLY retrieved scripture
- Never invent Bible verses
- Respect theological differences
- Cite scripture clearly
- Avoid extremist theology
- Be compassionate and helpful

FINAL RESPONSE:
"""

    # =========================
    # GEMINI GENERATION
    # =========================

    try:

        response = gemini_client.models.generate_content(
            model="gemini-2.0-flash-lite",
            contents=final_prompt
        )

        assistant_response = (
            response.text
        )

    except Exception as e:

        return {
            "success": False,
            "response": (
                f"Generation error: "
                f"{str(e)}"
            )
        }

    # =========================
    # VALIDATE REFERENCES
    # =========================

    invalid_refs = (
        validate_references(
            assistant_response,
            valid_refs
        )
    )

    if invalid_refs:

        assistant_response += (
            "\n\n⚠ Some scripture "
            "references could not "
            "be verified."
        )

    # =========================
    # SAVE MEMORY
    # =========================

    save_chat(
        user_question,
        assistant_response
    )

    # =========================
    # RETURN RESPONSE
    # =========================

    return {

        "success": True,

        "response": assistant_response,

        "verses": verses,

        "denomination": (
            request.denomination
        )
    }

# ==========================================
# IMAGE GENERATION ENDPOINT
# ==========================================

@app.post("/generate-image")
def generate_image(
    request: ImageRequest
):

    user_prompt = (
        request.prompt.strip()
    )

    # =========================
    # MODERATION CHECK
    # =========================

    is_safe = moderate_input(
        user_prompt
    )

    if not is_safe:

        return {
            "success": False,
            "error": (
                "Unsafe or harmful "
                "image request detected."
            )
        }

    # =========================
    # ENHANCED PROMPT
    # =========================

    enhanced_prompt = f"""
Create a respectful Christian-themed image.

Scene:
{user_prompt}

Style:
- cinematic lighting
- realistic
- reverent
- inspirational Christian artwork
- highly detailed
- peaceful atmosphere
- Biblical accuracy

Avoid:
- offensive imagery
- extremist symbolism
- hateful depictions
"""

    try:

        response = gemini_client.models.generate_content(
            model=(
                "gemini-2.0-flash-preview-image-generation"
            ),
            contents=enhanced_prompt,
            config=types.GenerateContentConfig(
                response_modalities=[
                    "TEXT",
                    "IMAGE"
                ]
            )
        )

        image_base64 = None

        text_response = ""

        for part in (
            response.candidates[0]
            .content.parts
        ):

            # Text response
            if hasattr(part, "text"):

                if part.text:

                    text_response += (
                        part.text
                    )

            # Image response
            elif hasattr(
                part,
                "inline_data"
            ):

                if part.inline_data:

                    image_base64 = (
                        base64.b64encode(
                            part.inline_data.data
                        ).decode("utf-8")
                    )

        if not image_base64:

            return {
                "success": False,
                "error": (
                    "Image generation failed."
                )
            }

        return {

            "success": True,

            "image_base64": (
                image_base64
            ),

            "description": (
                text_response
            )
        }

    except Exception as e:

        return {
            "success": False,
            "error": str(e)
        }

# ==========================================
# CLEAR MEMORY ENDPOINT
# ==========================================

@app.post("/clear-memory")
def clear_chat_memory():

    clear_memory()

    return {
        "success": True,
        "message": (
            "Conversation memory "
            "cleared."
        )
    }

# ==========================================
# TEST SCRIPTURE ENDPOINT
# ==========================================

@app.get("/test-scripture")
def test_scripture():

    sample_query = (
        "What does Bible say "
        "about love?"
    )

    verses = retrieve_scripture(
        sample_query
    )

    return {

        "query": sample_query,

        "retrieved_verses": verses
    }

# ==========================================
# START COMMAND
# ==========================================

"""
RUN SERVER:

uvicorn main:app --reload

API DOCS:

http://127.0.0.1:8000/docs
"""