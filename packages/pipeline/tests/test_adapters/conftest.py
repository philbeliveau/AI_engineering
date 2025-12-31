"""Test fixtures for adapters module."""

from pathlib import Path

import pytest

from src.adapters import AdapterConfig, AdapterResult, SourceAdapter


class ConcreteTestAdapter(SourceAdapter):
    """Minimal concrete adapter for testing purposes."""

    SUPPORTED_EXTENSIONS = [".txt", ".text"]

    def extract_text(self, file_path: Path) -> AdapterResult:
        self._validate_file_exists(file_path)
        self._validate_file_extension(file_path)
        return AdapterResult(
            text=file_path.read_text(),
            metadata=self.get_metadata(file_path),
        )

    def get_metadata(self, file_path: Path) -> dict:
        return {
            "title": self._extract_title_from_path(file_path),
            "path": str(file_path),
            "type": "text",
        }

    def supports_file(self, file_path: Path) -> bool:
        return file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS


class MinimalTestAdapter(SourceAdapter):
    """Minimal adapter with stub implementations for utility testing."""

    SUPPORTED_EXTENSIONS = [".txt"]

    def extract_text(self, file_path: Path) -> AdapterResult:
        return AdapterResult(text="", metadata={})

    def get_metadata(self, file_path: Path) -> dict:
        return {}

    def supports_file(self, file_path: Path) -> bool:
        return True


@pytest.fixture
def concrete_adapter() -> ConcreteTestAdapter:
    """Create a concrete test adapter instance."""
    return ConcreteTestAdapter()


@pytest.fixture
def minimal_adapter() -> MinimalTestAdapter:
    """Create a minimal test adapter for utility method testing."""
    return MinimalTestAdapter()


@pytest.fixture
def sample_text_file(tmp_path: Path) -> Path:
    """Create a sample text file for testing."""
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello, World!\n\nThis is a test document.")
    return file_path


@pytest.fixture
def custom_config() -> AdapterConfig:
    """Create a custom adapter config for testing."""
    return AdapterConfig(
        preserve_structure=False,
        include_metadata=True,
        max_section_depth=2,
    )


# ============================================================================
# Docling Adapter Fixtures
# ============================================================================


@pytest.fixture
def sample_markdown(tmp_path: Path) -> Path:
    """Create a sample markdown file with headings and code blocks."""
    content = """# Main Title

This is an introduction paragraph.

## Section One

Some content in section one.

### Subsection 1.1

More detailed content here.

```python
def hello_world():
    print("Hello, World!")
```

## Section Two

| Column A | Column B | Column C |
|----------|----------|----------|
| Value 1  | Value 2  | Value 3  |
| Value 4  | Value 5  | Value 6  |

This is section two content with a table above.
"""
    file_path = tmp_path / "sample.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_markdown_with_code(tmp_path: Path) -> Path:
    """Create a markdown file with code blocks for testing."""
    content = """# Code Examples

Here is a Python example:

```python
def calculate_sum(a, b):
    return a + b

result = calculate_sum(5, 3)
print(f"Result: {result}")
```

And here is JavaScript:

```javascript
function greet(name) {
    console.log(`Hello, ${name}!`);
}
```
"""
    file_path = tmp_path / "code_example.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_html(tmp_path: Path) -> Path:
    """Create a sample HTML file for testing."""
    content = """<!DOCTYPE html>
<html>
<head>
    <title>Test HTML Document</title>
</head>
<body>
    <h1>Main Heading</h1>
    <p>This is a paragraph of text.</p>
    <h2>Section Heading</h2>
    <ul>
        <li>Item one</li>
        <li>Item two</li>
        <li>Item three</li>
    </ul>
    <table>
        <tr><th>Name</th><th>Value</th></tr>
        <tr><td>Alpha</td><td>100</td></tr>
        <tr><td>Beta</td><td>200</td></tr>
    </table>
</body>
</html>
"""
    file_path = tmp_path / "sample.html"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def corrupted_file(tmp_path: Path) -> Path:
    """Create a file that will fail to parse as a document."""
    file_path = tmp_path / "corrupted.pdf"
    # Write random bytes that aren't a valid PDF
    file_path.write_bytes(b"\x00\x01\x02\x03invalid content\xff\xfe")
    return file_path


@pytest.fixture
def missing_file(tmp_path: Path) -> Path:
    """Return a path to a file that doesn't exist."""
    return tmp_path / "nonexistent.pdf"


@pytest.fixture
def sample_pdf_with_table(tmp_path: Path) -> Path:
    """Create a minimal PDF file with table content for testing.

    Note: Creates a simple text-based PDF that Docling can parse.
    """
    # Minimal valid PDF with text content including table-like structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 200 >>
stream
BT
/F1 12 Tf
50 700 Td
(Table of Values) Tj
0 -20 Td
(Column A | Column B | Column C) Tj
0 -15 Td
(Value 1  | Value 2  | Value 3) Tj
0 -15 Td
(Value 4  | Value 5  | Value 6) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000518 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
595
%%EOF"""
    file_path = tmp_path / "table_document.pdf"
    file_path.write_bytes(pdf_content)
    return file_path


@pytest.fixture
def sample_pdf_with_headings(tmp_path: Path) -> Path:
    """Create a PDF file with heading structure for testing."""
    pdf_content = b"""%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792]
   /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>
endobj
4 0 obj
<< /Length 300 >>
stream
BT
/F1 18 Tf
50 750 Td
(Main Document Title) Tj
/F1 14 Tf
0 -30 Td
(Chapter 1: Introduction) Tj
/F1 12 Tf
0 -20 Td
(This is the introduction paragraph with some content.) Tj
/F1 14 Tf
0 -30 Td
(Chapter 2: Details) Tj
/F1 12 Tf
0 -20 Td
(This section contains more detailed information.) Tj
ET
endstream
endobj
5 0 obj
<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>
endobj
xref
0 6
0000000000 65535 f
0000000009 00000 n
0000000058 00000 n
0000000115 00000 n
0000000266 00000 n
0000000618 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
695
%%EOF"""
    file_path = tmp_path / "headings_document.pdf"
    file_path.write_bytes(pdf_content)
    return file_path


@pytest.fixture
def sample_docx(tmp_path: Path) -> Path:
    """Create a minimal DOCX file for testing.

    DOCX is a ZIP archive containing XML files. This creates
    a minimal valid DOCX that Docling can parse.
    """
    import zipfile

    docx_path = tmp_path / "sample.docx"

    # Minimal DOCX structure
    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    document = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading1"/></w:pPr>
      <w:r><w:t>DOCX Test Document</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>This is a test paragraph in a DOCX file.</w:t></w:r>
    </w:p>
    <w:p>
      <w:pPr><w:pStyle w:val="Heading2"/></w:pPr>
      <w:r><w:t>Section One</w:t></w:r>
    </w:p>
    <w:p>
      <w:r><w:t>Content in section one with important information.</w:t></w:r>
    </w:p>
  </w:body>
</w:document>"""

    with zipfile.ZipFile(docx_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("word/document.xml", document)

    return docx_path


@pytest.fixture
def sample_pptx(tmp_path: Path) -> Path:
    """Create a minimal PPTX file for testing.

    PPTX is a ZIP archive containing XML files for presentations.
    """
    import zipfile

    pptx_path = tmp_path / "sample.pptx"

    content_types = """<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slides/slide1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="ppt/presentation.xml"/>
</Relationships>"""

    presentation = """<?xml version="1.0" encoding="UTF-8"?>
<p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
                xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships">
  <p:sldIdLst>
    <p:sldId id="256" r:id="rId2"/>
  </p:sldIdLst>
</p:presentation>"""

    pres_rels = """<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/slide" Target="slides/slide1.xml"/>
</Relationships>"""

    slide1 = """<?xml version="1.0" encoding="UTF-8"?>
<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"
       xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr/>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="2" name="Title"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr/>
        <p:txBody>
          <a:bodyPr/>
          <a:p><a:r><a:t>Presentation Title Slide</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
      <p:sp>
        <p:nvSpPr><p:cNvPr id="3" name="Content"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>
        <p:spPr/>
        <p:txBody>
          <a:bodyPr/>
          <a:p><a:r><a:t>This is slide content for testing PPTX extraction.</a:t></a:r></a:p>
        </p:txBody>
      </p:sp>
    </p:spTree>
  </p:cSld>
</p:sld>"""

    with zipfile.ZipFile(pptx_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types)
        zf.writestr("_rels/.rels", rels)
        zf.writestr("ppt/presentation.xml", presentation)
        zf.writestr("ppt/_rels/presentation.xml.rels", pres_rels)
        zf.writestr("ppt/slides/slide1.xml", slide1)

    return pptx_path
