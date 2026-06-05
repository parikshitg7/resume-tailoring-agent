import re
from docx import Document
from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

class BlockType(Enum):
    STATIC = "static"      # Name, email, education — never changes
    DYNAMIC = "dynamic"    # Experience bullets — AI replaces these

@dataclass
class ResumeBlock:
    block_type: BlockType
    section_name: str
    paragraphs: list            # Actual python-docx paragraph objects
    text_content: str           # Raw text for AI context
    job_title: Optional[str] = None  
    company: Optional[str] = None
    date_range: Optional[str] = None

@dataclass
class ResumeStructure:
    raw_doc: Document           # The original Document object (preserves ALL formatting)
    static_blocks: List[ResumeBlock] = field(default_factory=list)
    dynamic_blocks: List[ResumeBlock] = field(default_factory=list)
    section_order: List[str] = field(default_factory=list)

# AI uses these to guess which sections are which
STATIC_SECTIONS = {"education", "contact", "certifications", "languages", "personal", "skills"}
DYNAMIC_SECTIONS = {"experience", "work experience", "projects", "internships"}

# --- CRITICAL REGEX CONFIGURATION ---
# This looks for dates (e.g., "Jan 2020 - Present")
DATE_PATTERN = re.compile(
    r'\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|january|february|'
    r'march|april|june|july|august|september|october|november|december)'
    r'[\s,]*\d{4}\s*[-–—]\s*(present|\w+\s*\d{4})\b',
    re.IGNORECASE
)
# This looks for how you separate your Job Title and Company. 
# CURRENTLY SET TO LOOK FOR: "Job Title | Company" OR "Job Title @ Company"
JOB_TITLE_PATTERN = re.compile(r'^(.*?)\s*[|@]\s*(.*?)$', re.IGNORECASE)
# ------------------------------------

def parse_resume_structure(docx_path: str) -> ResumeStructure:
    """Scans the Word doc and separates static content from dynamic experience blocks."""
    doc = Document(docx_path)
    structure = ResumeStructure(raw_doc=doc)
    
    current_section = None
    current_section_type = None
    current_block_paragraphs = []
    current_block_texts = []
    
    def flush_block():
        """Save accumulated paragraphs as a block."""
        nonlocal current_block_paragraphs, current_block_texts
        if not current_block_paragraphs or not current_section:
            return
        
        combined_text = "\n".join(current_block_texts)
        block = ResumeBlock(
            block_type=current_section_type,
            section_name=current_section,
            paragraphs=current_block_paragraphs.copy(),
            text_content=combined_text
        )
        
        # Extract job title/company/dates for dynamic blocks
        if current_section_type == BlockType.DYNAMIC:
            for text in current_block_texts[:4]:  # Check first 4 lines of the block
                date_match = DATE_PATTERN.search(text)
                if date_match:
                    block.date_range = date_match.group(0)
                title_match = JOB_TITLE_PATTERN.search(text)
                if title_match and not date_match:
                    block.job_title = title_match.group(1).strip()
                    block.company = title_match.group(2).strip()
        
        if current_section_type == BlockType.STATIC:
            structure.static_blocks.append(block)
        elif current_section_type == BlockType.DYNAMIC:
            structure.dynamic_blocks.append(block)
        
        current_block_paragraphs.clear()
        current_block_texts.clear()
    
    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue
        
        # Detect section headers (all caps or heading styles)
        is_header = (
            para.style.name.startswith('Heading') or
            (text.isupper() and len(text.split()) <= 4) or
            (para.runs and all(run.bold for run in para.runs if run.text.strip()))
        )
        
        if is_header:
            flush_block()
            current_section = text.lower().strip()
            structure.section_order.append(current_section)
            
            if any(s in current_section for s in DYNAMIC_SECTIONS):
                current_section_type = BlockType.DYNAMIC
            else:
                current_section_type = BlockType.STATIC
            continue
        
        if current_section:
            current_block_paragraphs.append(para)
            current_block_texts.append(text)
    
    flush_block() 
    return structure