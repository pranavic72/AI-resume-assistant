from google import genai
import os
from dotenv import load_dotenv
from retriever1 import get_relevant_context

load_dotenv()

client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))

def get_response(user_question, chat_history, mode="recruiter", filenames=None):
    # Get relevant context from uploaded files
    context = get_relevant_context(user_question, filenames)
    
#     if mode == "recruiter":
#         system_prompt = """You are an expert recruitment assistant helping recruiters 
# evaluate candidates. Answer questions based ONLY on the uploaded candidate documents.
# When comparing candidates, be specific about which document each point comes from.
# Be professional, concise and objective."""

#     else:  # candidate mode
#         system_prompt = """You are an expert career coach helping a candidate tailor 
# their resume and prepare for job applications. Be encouraging, specific and actionable.
# Help them identify gaps, improve their resume, and write cover letters."""

    system_prompt = """You are an expert recruitment assistant helping recruiters 
evaluate candidates. Answer questions based ONLY on the uploaded candidate documents.
When comparing candidates, be specific about which document each point comes from.
Be professional, concise and objective."""

    # Build conversation history string
    history_text = ""
    for msg in chat_history[-6:]:  # last 6 messages for context
        role = "Recruiter" if msg["role"] == "user" else "Assistant"
        history_text += f"{role}: {msg['content']}\n"

    prompt = f"""{system_prompt}

UPLOADED DOCUMENTS:
{context}

CONVERSATION SO FAR:
{history_text}

CURRENT QUESTION:
{user_question}

Answer:"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text