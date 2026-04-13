"""分块管理器测试"""
import pytest
import tempfile
from pathlib import Path
from src.processors import ChunkManager, Chunk
from src.parsers.base import ParseResult, Chapter


def test_chunk_manager_init():
    """测试分块管理器初始化"""
    config = {
        "size_threshold_pages": 100,
        "size_threshold_mb": 50.0,
        "chunk_size": 50
    }
    
    manager = ChunkManager(config)
    
    assert manager.size_threshold_pages == 100
    assert manager.size_threshold_mb == 50.0
    assert manager.chunk_size == 50


def test_should_chunk_small_file():
    """测试小文件不需要分块"""
    manager = ChunkManager({
        "size_threshold_pages": 100,
        "size_threshold_mb": 50.0
    })
    
    parse_result = ParseResult(
        text="Test content",
        page_count=50,
        metadata={},
        format_type="txt"
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content")
        temp_file = f.name
    
    try:
        needs_chunking = manager.should_chunk(temp_file, parse_result)
        assert needs_chunking == False
    finally:
        Path(temp_file).unlink()


def test_should_chunk_large_file_by_pages():
    """测试大文件需要分块（按页数）"""
    manager = ChunkManager({
        "size_threshold_pages": 100,
        "size_threshold_mb": 50.0
    })
    
    parse_result = ParseResult(
        text="Test content",
        page_count=150,
        metadata={},
        format_type="pdf"
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.pdf', delete=False) as f:
        f.write("Test content")
        temp_file = f.name
    
    try:
        needs_chunking = manager.should_chunk(temp_file, parse_result)
        assert needs_chunking == True
    finally:
        Path(temp_file).unlink()


def test_create_text_chunks():
    """测试创建文本块"""
    manager = ChunkManager({
        "chunk_size": 1,
        "temp_dir": ".test_chunks"
    })
    
    long_text = "A" * 5000
    parse_result = ParseResult(
        text=long_text,
        page_count=1,
        metadata={},
        format_type="txt"
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(long_text)
        temp_file = f.name
    
    try:
        chunks = manager.create_chunks(temp_file, parse_result)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.status == "pending" for chunk in chunks)
        assert all(len(chunk.text) > 0 for chunk in chunks)
        
    finally:
        Path(temp_file).unlink()
        manager.cleanup_chunks([c.chunk_id for c in chunks])


def test_create_document_chunks():
    """测试创建文档块"""
    manager = ChunkManager({
        "chunk_size": 1,
        "temp_dir": ".test_chunks"
    })
    
    long_text = "Test paragraph.\n\n" * 1000
    parse_result = ParseResult(
        text=long_text,
        page_count=50,
        metadata={},
        format_type="docx"
    )
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
        f.write(long_text)
        temp_file = f.name
    
    try:
        chunks = manager.create_chunks(temp_file, parse_result)
        
        assert len(chunks) > 1
        assert all(isinstance(chunk, Chunk) for chunk in chunks)
        assert all(chunk.status == "pending" for chunk in chunks)
        
    finally:
        Path(temp_file).unlink()
        manager.cleanup_chunks([c.chunk_id for c in chunks])


def test_get_chunk_info():
    """测试获取块信息"""
    manager = ChunkManager()
    
    chunk_info = manager.get_chunk_info("test_chunk_id")
    
    assert "chunk_id" in chunk_info
    assert "status" in chunk_info


def test_cleanup_chunks():
    """测试清理块"""
    manager = ChunkManager({"temp_dir": ".test_chunks"})
    
    chunk_ids = ["chunk1", "chunk2", "chunk3"]
    
    manager.cleanup_chunks(chunk_ids)
    
    assert True


def test_chunk_dataclass():
    """测试块数据类"""
    chunk = Chunk(
        chunk_id="test_id",
        file_path="/test/file.pdf",
        start_page=1,
        end_page=10,
        text="Test content",
        metadata={"test": "data"}
    )
    
    assert chunk.chunk_id == "test_id"
    assert chunk.file_path == "/test/file.pdf"
    assert chunk.start_page == 1
    assert chunk.end_page == 10
    assert chunk.text == "Test content"
    assert chunk.status == "pending"
    assert chunk.translation_result is None
    assert chunk.quality_score is None
    assert chunk.metadata["test"] == "data"


def test_chunk_status_update():
    """测试块状态更新"""
    chunk = Chunk(
        chunk_id="test_id",
        file_path="/test/file.pdf",
        start_page=1,
        end_page=10,
        text="Test content"
    )
    
    chunk.status = "completed"
    chunk.translation_result = "Translated content"
    chunk.quality_score = 85.0
    
    assert chunk.status == "completed"
    assert chunk.translation_result == "Translated content"
    assert chunk.quality_score == 85.0
