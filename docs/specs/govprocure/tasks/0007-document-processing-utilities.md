# Task 0007: Document Processing Utilities

## Overview
Implement utilities for parsing PDF and DOCX documents, file validation, and data validators.

## Subtasks

### 7.1 Implement PDF parsing utility
- Create `app/utils/pdf_parser.py` using PyMuPDF or pdfplumber
- Extract text, tables, and sections from PDF documents
- Reference: Section 3.3 (AI/ML Stack)

### 7.2 Implement DOCX parsing utility
- Create `app/utils/docx_parser.py` using python-docx
- Extract text and structured content from DOCX files
- Reference: Section 3.3 (AI/ML Stack)

### 7.3 Create file utilities
- Create `app/utils/file_utils.py` with file validation, size checking
- Implement file type detection (PDF, DOCX, TXT)
- Validate max 50MB upload size
- Reference: Section 6.1 (Backend Structure)

### 7.4 Create validators
- Create `app/utils/validators.py` with GSTIN validation, phone number validation
- Add financial year format validation
- Reference: Section 7.3 (Data Normalization Rules)

## References
- Section 3.3 (AI/ML Stack)
- Section 6.1 (Backend Structure)
- Section 7.3 (Data Normalization Rules)
