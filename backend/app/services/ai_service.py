import json
from uuid import UUID
from sqlalchemy.orm import Session
from app.ai.vector_db import vector_db_provider
from app.ai.llm import llm_provider
from app.ai.prompts import RAG_SYSTEM_PROMPT, build_context_string
from app.models.user import User
from app.core.config import settings

class AIService:
    def handle_question(self, db: Session, user: User, query: str, history_messages: list) -> dict:
        # 1. RETRIEVAL
        # We rely on ChromaDB's ONNX embedding function.
        
        # We need to enforce RBAC using ChromaDB's where filter.
        
        user_id_str = str(user.id)
        dept_id_str = str(user.department_id) if user.department_id else ""
        
        or_conditions = [
            {"visibility": "ORGANIZATION"},
            {"owner_id": user_id_str}
        ]
        
        if dept_id_str:
            or_conditions.append({
                "$and": [
                    {"visibility": "DEPARTMENT"},
                    {"department_id": dept_id_str}
                ]
            })
            
        from app.core.permissions import has_permission, Permission
        if has_permission(user.role, Permission.READ_RESTRICTED_DOCUMENTS):
            if has_permission(user.role, Permission.READ_ALL_DOCUMENTS):
                or_conditions.append({"visibility": "RESTRICTED"})
            elif dept_id_str:
                or_conditions.append({
                    "$and": [
                        {"visibility": "RESTRICTED"},
                        {"department_id": dept_id_str}
                    ]
                })
            
        where_filter = {"$or": or_conditions}
        
        results = vector_db_provider.search(
            collection_name="docuchat_collection",
            query_text=query,
            n_results=5,
            where=where_filter
        )
        
        # Map Chroma results to our chunk format
        chunks = []
        if results and 'documents' in results and len(results['documents']) > 0:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            ids = results['ids'][0]
            for doc, meta, c_id in zip(docs, metas, ids):
                chunks.append({
                    "id": c_id,
                    "text": doc,
                    "metadata": meta
                })
                
        if not chunks:
            # Enforce hard fallback if no authorized documents exist
            return {
                "parsed_response": {
                    "answer": "I couldn't find enough information in the documents you are authorized to access.",
                    "confidence_score": 0.0,
                    "citations": []
                },
                "metrics": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "response_time_ms": 0,
                    "retrieved_chunks": []
                }
            }
                
        # 2. PROMPT CONSTRUCTION
        context_str = build_context_string(chunks)
        system_prompt = RAG_SYSTEM_PROMPT.format(context=context_str)
        
        # Map history for LLM
        messages = [{"role": "assistant" if m.role == "ai" else m.role, "content": m.content} for m in history_messages]
        messages.append({"role": "user", "content": query})
        
        # 3. GENERATION
        llm_response = llm_provider.generate_response(
            system_prompt=system_prompt,
            messages=messages
        )
        
        # 4. PARSE JSON
        try:
            parsed = json.loads(llm_response["content"])
        except json.JSONDecodeError:
            # Fallback if model hallucinates non-JSON despite instructions
            parsed = {
                "answer": llm_response["content"],
                "confidence_score": 0.0,
                "citations": []
            }
            
        return {
            "parsed_response": parsed,
            "metrics": {
                "prompt_tokens": llm_response.get("prompt_tokens"),
                "completion_tokens": llm_response.get("completion_tokens"),
                "response_time_ms": llm_response.get("response_time_ms"),
                "retrieved_chunks": [c["id"] for c in chunks]
            }
        }

ai_service = AIService()
