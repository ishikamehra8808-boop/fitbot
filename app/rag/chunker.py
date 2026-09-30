import os
import re

def load_and_chunk_documents(kb_dir: str, chunk_size: int, chunk_overlap: int) -> list[dict]:
    """Reads markdown files, splits them into chunks with metadata."""
    chunks = []
    if not os.path.exists(kb_dir):
        return chunks
        
    for filename in os.listdir(kb_dir):
        if not filename.endswith('.md'):
            continue
            
        filepath = os.path.join(kb_dir, filename)
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
                
            current_section = ""
            paragraphs = text.split('\n\n')
            
            current_chunk = []
            current_length = 0
            chunk_index = 0
            
            def add_chunk(chunk_text, section, idx):
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text.strip(),
                        "metadata": {
                            "source": filename,
                            "chunk_index": idx,
                            "section": section
                        }
                    })
            
            for p in paragraphs:
                header_match = re.match(r'^(#{1,6})\s+(.+)$', p.strip(), re.MULTILINE)
                if header_match:
                    current_section = header_match.group(2)
                    
                if current_length + len(p) > chunk_size and current_length > 0:
                    add_chunk('\n\n'.join(current_chunk), current_section, chunk_index)
                    chunk_index += 1
                    overlap_text = ""
                    if chunk_overlap > 0 and current_chunk:
                        overlap_text = current_chunk[-1][-chunk_overlap:]
                    current_chunk = [overlap_text + p] if overlap_text else [p]
                    current_length = len(current_chunk[0])
                else:
                    current_chunk.append(p)
                    current_length += len(p)
                    
            if current_chunk:
                add_chunk('\n\n'.join(current_chunk), current_section, chunk_index)
                
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            
    return chunks
