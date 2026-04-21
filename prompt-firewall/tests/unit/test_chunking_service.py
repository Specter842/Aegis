from app.services.chunking_service import ChunkingService

def test_chunking_service():
    chunker = ChunkingService(chunk_size=10, chunk_overlap=2)
    text = "0123456789abcdefghij"
    chunks = chunker.chunk_text(text)
    assert len(chunks) == 3
    assert chunks[0] == "0123456789"
    assert chunks[1] == "89abcdefgh"
    assert chunks[2] == "ghij"
