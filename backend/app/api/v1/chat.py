from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.api import dependencies
from app.models.user import User
from app.repositories.chat_repo import chat_repo
from app.services.ai_service import ai_service
from app.schemas.chat import ChatCreate, ChatRead, QuestionRequest, MessageCreate, MessageRead, Citation
from app.core.config import settings
from app.ai.llm import llm_provider # to get provider name

router = APIRouter()

@router.get("/", response_model=List[ChatRead])
def get_user_chats(
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    return chat_repo.get_user_chats(db, current_user.id)

@router.post("/", response_model=ChatRead)
def create_chat(
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    chat_in = ChatCreate(user_id=current_user.id, title="New Conversation")
    return chat_repo.create_chat(db, chat_in)

@router.get("/{chat_id}/messages", response_model=List[MessageRead])
def get_chat_messages(
    chat_id: UUID,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    chat = chat_repo.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat_repo.get_all_chat_messages(db, chat_id)

@router.post("/message", response_model=MessageRead)
def ask_question(
    request: QuestionRequest,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
) -> Any:
    chat_id = request.chat_id
    if not chat_id:
        chat = chat_repo.create_chat(db, ChatCreate(user_id=current_user.id, title=request.query[:50]))
        chat_id = chat.id
    else:
        chat = chat_repo.get_chat(db, chat_id)
        if not chat or chat.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Chat not found")
            
    # Save User message
    user_msg_in = MessageCreate(chat_id=chat_id, role="user", content=request.query)
    chat_repo.add_message(db, user_msg_in)
    
    # Get history
    history = chat_repo.get_chat_history(db, chat_id, limit=settings.CHAT_HISTORY_WINDOW)
    
    # AI Service handles Retrieval + Generation
    result = ai_service.handle_question(db, current_user, request.query, history)
    
    parsed = result["parsed_response"]
    metrics = result["metrics"]
    
    citations_data = []
    for c in parsed.get("citations", []):
        try:
            # Handle LLM hallucinating string values for optional integer
            if isinstance(c.get("page_number"), str):
                if not c["page_number"].isdigit():
                    c["page_number"] = None
                else:
                    c["page_number"] = int(c["page_number"])
            citations_data.append(Citation(**c))
        except Exception:
            pass # Skip invalid citations rather than crashing the chat
    
    # Save AI message
    ai_msg_in = MessageCreate(
        chat_id=chat_id,
        role="ai",
        content=parsed.get("answer", "Error generating response."),
        citations=citations_data
    )
    ai_msg = chat_repo.add_message(db, ai_msg_in)
    
    # Save AI Log
    chat_repo.create_ai_log(
        db,
        user_id=current_user.id,
        chat_id=chat_id,
        provider="Groq",
        model_name="llama3-8b-8192",
        prompt_tokens=metrics.get("prompt_tokens"),
        completion_tokens=metrics.get("completion_tokens"),
        total_tokens=(metrics.get("prompt_tokens") or 0) + (metrics.get("completion_tokens") or 0),
        response_time_ms=metrics.get("response_time_ms"),
        retrieval_metadata={"retrieved_chunks": metrics.get("retrieved_chunks")}
    )
    
    return ai_msg

@router.delete("/{chat_id}", status_code=204)
def delete_chat(
    chat_id: UUID,
    db: Session = Depends(dependencies.get_db),
    current_user: User = Depends(dependencies.get_current_active_user)
):
    chat = chat_repo.get_chat(db, chat_id)
    if not chat or chat.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Chat not found")
        
    chat_repo.delete_chat(db, chat_id)
    return None
