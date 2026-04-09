"""PDF 工具函数"""
from pathlib import Path
from typing import List, Optional
from pypdf import PdfReader, PdfWriter
import pdfplumber
from src.utils.logger import get_logger
from src.utils.exceptions import FileProcessingError

logger = get_logger(__name__)


def split_pdf(input_path: str, output_dir: str, chapters: List, max_pages: int = 50) -> List[str]:
    """拆分 PDF 文件
    
    Args:
        input_path: 输入 PDF 文件路径
        output_dir: 输出目录
        chapters: 章节信息列表
        max_pages: 最大页数（用于兜底拆分）
        
    Returns:
        拆分后的文件路径列表
    """
    output_files = []
    
    try:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        with open(input_path, 'rb') as f:
            reader = PdfReader(f)
            total_pages = len(reader.pages)
            
            # 如果有章节信息，按章节拆分
            if chapters:
                for i, chapter in enumerate(chapters):
                    start_page = chapter.start_page - 1  # PDF 索引从 0 开始
                    end_page = chapter.end_page  # 结束页（不包含）
                    
                    # 处理最后一章
                    if i == len(chapters) - 1:
                        end_page = total_pages
                    
                    # 创建输出文件
                    output_path = Path(output_dir) / f"chapter_{i+1}_{chapter.title.replace(' ', '_')[:50]}.pdf"
                    output_path = output_path.with_suffix('.pdf')
                    
                    writer = PdfWriter()
                    for page_num in range(start_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(str(output_path))
                    logger.info(
                        "pdf_split_by_chapter",
                        chapter=chapter.title,
                        start_page=start_page + 1,
                        end_page=end_page,
                        output=str(output_path)
                    )
            else:
                # 按页数兜底拆分
                current_page = 0
                part = 1
                
                while current_page < total_pages:
                    end_page = min(current_page + max_pages, total_pages)
                    
                    output_path = Path(output_dir) / f"part_{part}.pdf"
                    
                    writer = PdfWriter()
                    for page_num in range(current_page, end_page):
                        writer.add_page(reader.pages[page_num])
                    
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(str(output_path))
                    logger.info(
                        "pdf_split_by_pages",
                        part=part,
                        start_page=current_page + 1,
                        end_page=end_page,
                        output=str(output_path)
                    )
                    
                    current_page = end_page
                    part += 1
        
        return output_files
        
    except Exception as e:
        logger.error("pdf_split_error", input=input_path, error=str(e))
        raise FileProcessingError(f"Failed to split PDF: {e}")


def merge_pdfs(input_files: List[str], output_path: str) -> str:
    """合并 PDF 文件
    
    Args:
        input_files: 输入 PDF 文件路径列表
        output_path: 输出文件路径
        
    Returns:
        输出文件路径
    """
    try:
        writer = PdfWriter()
        
        for input_file in input_files:
            with open(input_file, 'rb') as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)
                
            logger.info("pdf_added_to_merge", file=input_file, pages=len(reader.pages))
        
        # 确保输出目录存在
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            writer.write(f)
        
        logger.info("pdf_merged", output=output_path, files=len(input_files))
        return output_path
        
    except Exception as e:
        logger.error("pdf_merge_error", output=output_path, error=str(e))
        raise FileProcessingError(f"Failed to merge PDF: {e}")


def extract_text_from_pdf(pdf_path: str, page_range: Optional[List[int]] = None) -> str:
    """提取 PDF 文本
    
    Args:
        pdf_path: PDF 文件路径
        page_range: 页码范围 [start, end]（从 1 开始）
        
    Returns:
        提取的文本
    """
    try:
        text = ""
        
        with pdfplumber.open(pdf_path) as pdf:
            if page_range:
                start, end = page_range
                pages = pdf.pages[start-1:end]
            else:
                pages = pdf.pages
            
            for page in pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        
        return text
        
    except Exception as e:
        logger.error("pdf_text_extraction_error", file=pdf_path, error=str(e))
        raise FileProcessingError(f"Failed to extract text: {e}")