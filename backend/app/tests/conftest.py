"""Shared test fixtures."""

import uuid
from datetime import datetime, timezone

import pytest


@pytest.fixture
def sample_openalex_work():
    """A realistic OpenAlex work response."""
    return {
        "id": "https://openalex.org/W12345",
        "title": "Attention Is All You Need",
        "doi": "https://doi.org/10.48550/arXiv.1706.03762",
        "publication_date": "2017-06-12",
        "abstract_inverted_index": {
            "We": [0],
            "propose": [1],
            "a": [2, 12],
            "new": [3],
            "simple": [4],
            "network": [5],
            "architecture": [6],
            "the": [7],
            "Transformer": [8],
            "based": [9],
            "solely": [10],
            "on": [11],
            "attention": [13],
            "mechanism": [14],
        },
        "authorships": [
            {
                "author": {
                    "id": "https://openalex.org/A1",
                    "display_name": "Ashish Vaswani",
                },
                "institutions": [
                    {"id": "https://openalex.org/I123", "display_name": "Google Brain"}
                ],
            },
            {
                "author": {
                    "id": "https://openalex.org/A2",
                    "display_name": "Noam Shazeer",
                },
                "institutions": [],
            },
        ],
        "primary_location": {
            "pdf_url": "https://arxiv.org/pdf/1706.03762",
        },
        "open_access": {"oa_url": None},
        "concepts": [
            {"display_name": "Transformer"},
            {"display_name": "Attention"},
            {"display_name": "Machine Learning"},
        ],
    }


@pytest.fixture
def sample_openalex_work_minimal():
    """An OpenAlex work with minimal fields."""
    return {
        "id": "https://openalex.org/W99999",
        "title": "Minimal Paper",
        "doi": None,
        "publication_date": None,
        "abstract_inverted_index": None,
        "authorships": [],
        "primary_location": None,
        "open_access": {},
        "concepts": [],
    }


@pytest.fixture
def sample_openalex_work_no_title():
    """An OpenAlex work with no title (should be rejected)."""
    return {
        "id": "https://openalex.org/W00000",
        "title": None,
    }


@pytest.fixture
def sample_arxiv_xml():
    """A realistic arXiv API Atom entry as XML string."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2301.12345v1</id>
    <title>  A Novel Approach to
    Robot Learning  </title>
    <summary>  We present a novel approach to robot learning
    that uses transformers for policy generation.  </summary>
    <author><name>Jane Smith</name></author>
    <author><name>John Doe</name></author>
    <published>2023-01-15T00:00:00Z</published>
    <link title="pdf" href="http://arxiv.org/pdf/2301.12345v1" />
    <arxiv:primary_category term="cs.RO" />
    <category term="cs.RO" />
    <category term="cs.AI" />
    <arxiv:doi>10.1234/test.doi</arxiv:doi>
  </entry>
</feed>"""


@pytest.fixture
def sample_arxiv_xml_minimal():
    """An arXiv entry with minimal fields."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2302.99999v1</id>
    <title>Minimal arXiv Paper</title>
  </entry>
</feed>"""


@pytest.fixture
def sample_arxiv_xml_no_title():
    """An arXiv entry with no title."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/0000.00000v1</id>
  </entry>
</feed>"""


@pytest.fixture
def sample_embedding():
    """A sample embedding vector (truncated for tests)."""
    import numpy as np
    np.random.seed(42)
    return np.random.randn(1536).tolist()


@pytest.fixture
def sample_embedding_2():
    """A second distinct embedding vector."""
    import numpy as np
    np.random.seed(123)
    return np.random.randn(1536).tolist()


@pytest.fixture
def sample_paper_text():
    """Sample paper text for evidence extraction."""
    return """
    We evaluated our method on the ImageNet dataset and the CIFAR-10 benchmark.
    Our model achieves an accuracy of 95.3% and F1 of 0.92 on ImageNet.
    Compared to ResNet and VGG baselines, our approach shows significant improvement.
    The code is available at https://github.com/example/model-repo.
    Limitations include the high computational cost and the need for large datasets.
    """
