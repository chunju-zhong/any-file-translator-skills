"""大文件处理器测试"""
import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch
from src.processors import LargeFileProcessor, ProcessingResult, ChunkManager, Chunk
from src.parsers.base import ParseResult


def test_large_file_processor_init():
    """测试大文件处理器初始化"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    mock_improver = Mock()
    
    config = {
        "max_parallel_chunks": 4,
        "progress_tracking": True
    }
    
    processor = LargeFileProcessor(
        translator=mock_translator,
        evaluator=mock_evaluator,
        improver=mock_improver,
        config=config
    )
    
    assert processor.max_parallel_chunks == 4
    assert processor.progress_tracking == True
    assert processor.translator == mock_translator
    assert processor.evaluator == mock_evaluator
    assert processor.improver == mock_improver


def test_processing_result_dataclass():
    """测试处理结果数据类"""
    result = ProcessingResult(
        final_text="Final translated text",
        overall_quality_score=85.0,
        chunks_processed=5,
        chunks_failed=0,
        processing_time=10.5,
        chunk_details=[
            {"chunk_id": "chunk1", "status": "completed", "quality_score": 85.0}
        ],
        metadata={"test": "data"}
    )
    
    assert result.final_text == "Final translated text"
    assert result.overall_quality_score == 85.0
    assert result.chunks_processed == 5
    assert result.chunks_failed == 0
    assert result.processing_time == 10.5
    assert len(result.chunk_details) == 1
    assert result.metadata["test"] == "data"


@patch('src.processors.large_file_processor.ChunkManager')
@patch('src.processors.large_file_processor.ResultMerger')
def test_process_large_file(mock_merger_class, mock_manager_class):
    """测试处理大文件"""
    mock_translator = Mock()
    mock_translator.translate.return_value = Mock(
        text="Translated text",
        model="gpt-4",
        usage={"total_tokens": 100}
    )
    
    mock_evaluator = Mock()
    mock_evaluator.evaluate.return_value = Mock(
        overall_score=85.0,
        fluency_score=85.0,
        accuracy_score=85.0,
        format_score=85.0,
        completeness_score=85.0,
        human_score=85.0,
        issues=[],
        suggestions=[],
        metadata={}
    )
    
    mock_improver = Mock()
    
    mock_manager = Mock()
    mock_chunk1 = Chunk(
        chunk_id="chunk1",
        file_path="/test/file.pdf",
        start_page=1,
        end_page=10,
        text="Test content 1",
        metadata={"chunk_index": 0}
    )
    mock_chunk1.status = "completed"
    mock_chunk1.translation_result = "Translated 1"
    mock_chunk1.quality_score = 85.0
    
    mock_chunk2 = Chunk(
        chunk_id="chunk2",
        file_path="/test/file.pdf",
        start_page=11,
        end_page=20,
        text="Test content 2",
        metadata={"chunk_index": 1}
    )
    mock_chunk2.status = "completed"
    mock_chunk2.translation_result = "Translated 2"
    mock_chunk2.quality_score = 90.0
    
    mock_manager.create_chunks.return_value = [mock_chunk1, mock_chunk2]
    mock_manager_class.return_value = mock_manager
    
    mock_merger = Mock()
    mock_merger.merge_translations.return_value = "Merged translated text"
    mock_merger.merge_quality_scores.return_value = 87.5
    mock_merger_class.return_value = mock_merger
    
    processor = LargeFileProcessor(
        translator=mock_translator,
        evaluator=mock_evaluator,
        improver=mock_improver,
        config={"max_parallel_chunks": 2}
    )
    
    parse_result = ParseResult(
        text="Original text",
        page_count=150,
        metadata={},
        format_type="pdf"
    )
    
    result = processor.process_large_file(
        file_path="/test/file.pdf",
        parse_result=parse_result,
        source_language="en",
        target_language="zh"
    )
    
    assert isinstance(result, ProcessingResult)
    assert result.final_text == "Merged translated text"
    assert result.overall_quality_score == 87.5
    assert result.chunks_processed >= 0
    assert result.processing_time > 0


def test_process_chunk():
    """测试处理单个块"""
    mock_translator = Mock()
    mock_translator.translate.return_value = Mock(
        text="Translated chunk",
        model="gpt-4",
        usage={"total_tokens": 50}
    )
    
    mock_evaluator = Mock()
    mock_evaluator.evaluate.return_value = Mock(
        overall_score=90.0,
        fluency_score=90.0,
        accuracy_score=90.0,
        format_score=90.0,
        completeness_score=90.0,
        human_score=90.0,
        issues=[],
        suggestions=[],
        metadata={}
    )
    
    mock_improver = Mock()
    
    processor = LargeFileProcessor(
        translator=mock_translator,
        evaluator=mock_evaluator,
        improver=mock_improver,
        config={}
    )
    
    chunk = Chunk(
        chunk_id="test_chunk",
        file_path="/test/file.pdf",
        start_page=1,
        end_page=10,
        text="Test content"
    )
    
    processed_chunk = processor._process_chunk(
        chunk=chunk,
        source_language="en",
        target_language="zh"
    )
    
    assert processed_chunk.status == "completed"
    assert processed_chunk.translation_result == "Translated chunk"
    assert processed_chunk.quality_score == 90.0


def test_track_progress():
    """测试进度跟踪"""
    mock_translator = Mock()
    mock_evaluator = Mock()
    mock_improver = Mock()
    
    processor = LargeFileProcessor(
        translator=mock_translator,
        evaluator=mock_evaluator,
        improver=mock_improver,
        config={"progress_tracking": True}
    )
    
    processor._track_progress("chunk1", "processing")
    processor._track_progress("chunk1", "completed")
    
    assert "chunk1" in processor.progress
    assert processor.progress["chunk1"]["status"] == "completed"


def test_process_chunk_failure():
    """测试块处理失败"""
    mock_translator = Mock()
    mock_translator.translate.side_effect = Exception("Translation failed")
    
    mock_evaluator = Mock()
    mock_improver = Mock()
    
    processor = LargeFileProcessor(
        translator=mock_translator,
        evaluator=mock_evaluator,
        improver=mock_improver,
        config={}
    )
    
    chunk = Chunk(
        chunk_id="test_chunk",
        file_path="/test/file.pdf",
        start_page=1,
        end_page=10,
        text="Test content"
    )
    
    processed_chunk = processor._process_chunk(
        chunk=chunk,
        source_language="en",
        target_language="zh"
    )
    
    assert processed_chunk.status == "failed"
