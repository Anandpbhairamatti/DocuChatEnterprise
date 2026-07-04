from typing import List, Dict, Any
import re

def structure_aware_chunking(text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict[str, Any]]:
    """
    Very basic structure-aware chunking.
    Splits by paragraphs, then groups them to fit chunk_size.
    Returns metadata alongside text.
    """
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_length = 0
    char_start = 0
    
    for idx, para in enumerate(paragraphs):
        para = para.strip()
        if not para:
            continue
            
        token_estimate = len(para.split())
        
        if current_length + token_estimate > chunk_size and current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "metadata": {
                    "token_count": current_length,
                    "paragraph_start": idx - len(current_chunk),
                    "paragraph_end": idx - 1,
                    "char_start": char_start,
                    "char_end": char_start + len(chunk_text)
                }
            })
            # Overlap handling (simplistic)
            char_start += len(" ".join(current_chunk[:-1])) + 1 if len(current_chunk) > 1 else len(chunk_text)
            current_chunk = current_chunk[-1:] if overlap > 0 else []
            current_length = len(current_chunk[0].split()) if current_chunk else 0
            
        current_chunk.append(para)
        current_length += token_estimate
        
    if current_chunk:
        chunk_text = " ".join(current_chunk)
        chunks.append({
            "text": chunk_text,
            "metadata": {
                "token_count": current_length,
                "paragraph_start": len(paragraphs) - len(current_chunk),
                "paragraph_end": len(paragraphs) - 1,
                "char_start": char_start,
                "char_end": char_start + len(chunk_text)
            }
        })
        
    return chunks
