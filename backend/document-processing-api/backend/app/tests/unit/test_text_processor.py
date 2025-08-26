import pytest
from ...utils.text_processor import chunk_text

def test_chunk_text():
    """
    Unit test for the text chunking utility.
    """
    long_text = "a" * 2000
    chunks = chunk_text(long_text, chunk_size=500, chunk_overlap=100)

    assert len(chunks) > 1
    assert all(len(chunk) <= 500 for chunk in chunks)
    # Check for overlap
    assert chunks[0][-100:] == chunks[1][:100]
