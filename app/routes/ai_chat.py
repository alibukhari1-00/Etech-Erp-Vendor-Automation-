from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import asyncio
from typing import Optional

from app.core.config import settings
from app.core.dependencies import get_current_user

# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------
router = APIRouter(prefix="/ai-chat", tags=["AI Chat"])


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[list[dict]] = None


class ChatResponse(BaseModel):
    reply: str


from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import MessagesPlaceholder

# Lazy-initialised agents (cached per role + name)
_agents_cache = {}


def get_agent_for_role(role: str, user_name: str):
    """Build (or return cached) SQL agent specific to the user's role and name."""
    cache_key = f"{role}_{user_name}"
    global _agents_cache
    if cache_key in _agents_cache:
        return _agents_cache[cache_key]

    api_key = settings.OPENAI_API_KEY
    if not api_key or api_key == "your-openai-api-key-here":
        raise HTTPException(
            status_code=503,
            detail="OpenAI API key is not configured. Add OPENAI_API_KEY to your .env file.",
        )

    # LangChain imports
    from langchain_openai import ChatOpenAI
    from langchain_community.utilities import SQLDatabase
    from langchain_community.agent_toolkits import create_sql_agent

    db = SQLDatabase.from_uri(
        settings.DATABASE_URL,
        sample_rows_in_table_info=0, # Strict zero-leak policy
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.2, # Lower for SQL stability
        api_key=api_key,
    )

    # Role-specific instructions (human-friendly)
    if role == "purchaser":
        role_note = "You are helping a Purchaser. Access to system user accounts is restricted. Focus on Vendors and Procurement."
    else:
        role_note = "You are helping an Admin. You have full access to all business records, including system accounts."

    prefix = f"""You are the warm and professional "ETSolar ERP Assistant". 
You help {user_name} manage the business smoothly.

---
PERSONALITY & TONE:
1. **Friendly Colleague**: Speak like a helpful assistant, not a database. Use simple, clear language.
2. **NO TECHNICAL JARGON**: NEVER use words like "ID", "Table", "Schema", "Primary Key", "Column", or "Null". Use "Details", "Records", "Reference Number", or "Information".
3. **Concise Answers**: Provide direct answers. 
4. **ZERO SQL LEAKAGE**: NEVER output SQL queries, database internals, or triple backticks. If you need to search data, do it silently using your tools.
5. **Business Context**: Understand that "Sabir Sultan Floor Mills" or "Fast National University" are PROJECTS. "SolarTech" or "PowerMax" are VENDORS.

OPERATING RULES:
1. **ERP Only**: You only answer questions about ETSolar business data (Vendors, Items, Projects, Demands). 
2. **Rejection**: For non-ERP questions, stay professional.
3. **Branded Formatting**: Use "Clean Lists" with **Bold Headers**. Add a ☀️ or 🚀 where it feels encouraging.
4. **Security**: {role_note}
---

You have access to information regarding:
- Vendors and their Contact Persons
- Items, Brands, and Categories
- Active Projects and their Locations (e.g., Sabir Sultan Floor Mills)
- Purchase Demands and their current Statuses
- System User Accounts (Admin only)
"""

    agent = create_sql_agent(
        llm=llm,
        db=db,
        agent_type="openai-tools",
        verbose=False,
        handle_parsing_errors=True,
        prefix=prefix,
        extra_prompt_messages=[MessagesPlaceholder(variable_name="chat_history")],
    )
    _agents_cache[cache_key] = agent
    return agent


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/ask")
async def ask_question_stream(
    body: ChatRequest,
    current_user=Depends(get_current_user),
):
    """Streaming endpoint for the AI Chatbot."""
    user_display_name = current_user.full_name.split(" ")[0] if current_user.full_name else "there"
    msg_lower = body.message.lower().strip().strip("?!.")

    # [GREETING BYPASS] Intercept simple greetings
    greetings = ["hi", "hello", "salam", "hey", "a o a", "assalam o alaikum", "good morning", "good evening"]
    if msg_lower in greetings:
        async def greeting_generator():
            reply = f"Hi {user_display_name}! 👋 I'm your ETSolar Assistant. I can help you find vendor details, check item stock, or track purchase demands. What would you like to check today? ☀️"
            yield f"data: {json.dumps({'reply': reply})}\n\n"
            yield "data: [DONE]\n\n"
        return StreamingResponse(greeting_generator(), media_type="text/event-stream")

    # Convert conversation history to LangChain messages
    history = []
    if body.conversation_history:
        for msg in body.conversation_history:
            if msg.get("role") == "user":
                history.append(HumanMessage(content=msg.get("content", "")))
            elif msg.get("role") == "assistant":
                history.append(AIMessage(content=msg.get("content", "")))

    agent = get_agent_for_role(current_user.role, user_display_name)

    async def event_generator():
        try:
            # We filter out any accidental SQL or technical blocks from the stream
            in_code_block = False
            
            async for event in agent.astream_events(
                {"input": body.message, "chat_history": history},
                version="v1"
            ):
                if event["event"] == "on_chat_model_stream":
                    content = event["data"]["chunk"].content
                    if not content:
                        continue
                    
                    # Basic protection against leaking code blocks
                    if "```" in content:
                        in_code_block = not in_code_block
                        continue
                        
                    if not in_code_block:
                        yield f"data: {json.dumps({'reply': content})}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
