from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import List, Annotated
from google import genai
import os

# in case the env var isn't set, use YOUR_<VARIABLE> as the default
# to help with debugging
project_id = os.getenv("PROJECT_ID", "YOUR_PROJECT_ID")
region = os.getenv("REGION", "YOUR_REGION")
gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-001")

app = FastAPI(title="FastAPI HTMX Chat")

templates = Jinja2Templates(directory="templates")

genai_client = genai.Client(
    vertexai=True, project=project_id, location=region
)

system_prompt = f"""
You're a chatbot that helps pass the time with small talk, that is
polite conversation about unimportant or uncontroversial matters
that allows people to pass the time. Please keep your answers short.
"""

chat_messages: List[str] = []

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def get_chat_ui(request: Request):
    """Serves the main chat page."""
    print("Serving index.html")
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "messages": chat_messages} # Pass existing messages
    )

@app.post("/ask", response_class=HTMLResponse)
async def ask_gemini_and_respond(
    request: Request,
    # Use Annotated for dependency injection with Form data
    message: Annotated[str, Form()]
):
    
    user_msg_html = templates.get_template('message.html').render({'message': message})
    
    print("asking gemini...")
    response = genai_client.models.generate_content(
        model=gemini_model,
        contents=[message],
        config=genai.types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.7,
        ),
    )
    
    print("Gemini responded with: " + response.text)
    
    ai_response_html = templates.get_template('ai_message.html').render({'ai_response_text': response.text})

    combined_html = user_msg_html + ai_response_html

    return HTMLResponse(content=combined_html)
