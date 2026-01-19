import os
from fastapi import APIRouter
from google import genai
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
router = APIRouter()

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


class PromptRequest(BaseModel):
    prompt: str


def send_task_to_gemini(request: PromptRequest):
    response = client.models.generate_content(
        model="gemini-2.5-flash", 
        contents=request.prompt
    )
    return {"result": response.text}
