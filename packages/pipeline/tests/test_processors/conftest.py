"""Test fixtures for processors module."""

from pathlib import Path

import pytest

from src.processors import DoclingChunker, ChunkerConfig


@pytest.fixture
def chunker() -> DoclingChunker:
    """Create a default DoclingChunker instance."""
    return DoclingChunker()


@pytest.fixture
def chunker_small_size() -> DoclingChunker:
    """Create a chunker with small chunk size for testing splits."""
    return DoclingChunker(ChunkerConfig(chunk_size=100))


@pytest.fixture
def sample_markdown_for_chunking(tmp_path: Path) -> Path:
    """Create a markdown file with enough content to generate multiple chunks."""
    content = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that provides systems
the ability to automatically learn and improve from experience without being
explicitly programmed. This field has seen tremendous growth in recent years.

## Types of Machine Learning

There are three main types of machine learning algorithms:

### Supervised Learning

In supervised learning, the algorithm learns from labeled training data.
Examples include classification and regression tasks. The algorithm tries
to learn the mapping between input features and output labels.

Common supervised learning algorithms include:
- Linear Regression
- Logistic Regression
- Decision Trees
- Random Forests
- Support Vector Machines
- Neural Networks

### Unsupervised Learning

Unsupervised learning works with unlabeled data. The algorithm tries to
find hidden patterns or intrinsic structures in the input data without
any explicit guidance about what to look for.

Popular unsupervised learning techniques:
- K-Means Clustering
- Hierarchical Clustering
- Principal Component Analysis (PCA)
- Autoencoders
- Generative Adversarial Networks (GANs)

### Reinforcement Learning

Reinforcement learning is about taking suitable actions to maximize reward
in a particular situation. It is employed by various software and machines
to find the best possible behavior or path in a specific environment.

Key concepts in reinforcement learning:
- Agent and Environment
- State and Action
- Reward and Policy
- Value Function
- Q-Learning

## Applications

Machine learning has numerous applications across industries:

### Healthcare
- Disease diagnosis
- Drug discovery
- Patient monitoring
- Medical image analysis

### Finance
- Fraud detection
- Algorithmic trading
- Credit scoring
- Risk assessment

### Technology
- Natural language processing
- Computer vision
- Recommendation systems
- Autonomous vehicles

## Conclusion

Machine learning continues to evolve and impact various aspects of our lives.
Understanding the fundamentals is essential for anyone working in technology.
"""
    file_path = tmp_path / "ml_guide.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_short_markdown(tmp_path: Path) -> Path:
    """Create a short markdown file that fits in a single chunk."""
    content = """# Quick Note

This is a brief note that should fit in a single chunk.
It contains just a few sentences of text.
"""
    file_path = tmp_path / "short_note.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_pdf_for_chunking(tmp_path: Path) -> Path:
    """Create a PDF with content for chunking tests."""
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
<< /Length 400 >>
stream
BT
/F1 18 Tf
50 750 Td
(RAG Architecture Guide) Tj
/F1 12 Tf
0 -30 Td
(Chapter 1: Introduction to RAG) Tj
0 -20 Td
(Retrieval-Augmented Generation combines retrieval with generation.) Tj
0 -20 Td
(This approach enhances LLM responses with external knowledge.) Tj
0 -30 Td
(Chapter 2: Components) Tj
0 -20 Td
(The main components are the retriever and the generator.) Tj
0 -20 Td
(The retriever finds relevant documents from a knowledge base.) Tj
0 -20 Td
(The generator creates responses using the retrieved context.) Tj
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
0000000718 00000 n
trailer
<< /Size 6 /Root 1 0 R >>
startxref
795
%%EOF"""
    file_path = tmp_path / "rag_guide.pdf"
    file_path.write_bytes(pdf_content)
    return file_path
