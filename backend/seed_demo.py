"""Seed the database with demo papers for testing.

Usage:
    cd backend
    python seed_demo.py
"""

import uuid
from datetime import datetime, timedelta, timezone

import numpy as np
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config import settings
from app.db import Base
from app.models import Paper, Institution

# Demo papers with realistic data
DEMO_PAPERS = [
    {
        "title": "Attention Is All You Need",
        "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks. We propose a new architecture, the Transformer, based solely on attention mechanisms. Experiments on machine translation show superior quality while being more parallelizable. We evaluated on the WMT 2014 English-to-German dataset. Our model achieves BLEU of 28.4, improving over the best results by over 2 BLEU. Code is available at https://github.com/tensorflow/tensor2tensor",
        "authors": [{"name": "Ashish Vaswani"}, {"name": "Noam Shazeer"}, {"name": "Niki Parmar"}],
        "doi": "10.48550/arXiv.1706.03762",
        "arxiv_id": "1706.03762",
        "source": "openalex",
        "categories": ["Machine Learning", "Attention"],
        "institution_ids": ["https://openalex.org/I4210112789"],
    },
    {
        "title": "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
        "abstract": "We introduce BERT, a language representation model. BERT is designed to pre-train deep bidirectional representations. The model achieves accuracy of 93.5% on GLUE benchmark. Compared to GPT and ELMo baselines, our approach shows significant improvement. Limitations include the high computational cost.",
        "authors": [{"name": "Jacob Devlin"}, {"name": "Ming-Wei Chang"}],
        "doi": "10.48550/arXiv.1810.04805",
        "arxiv_id": "1810.04805",
        "source": "openalex",
        "categories": ["Natural Language Processing", "Transformers"],
        "institution_ids": ["https://openalex.org/I4210112789"],
    },
    {
        "title": "A Survey of Large Language Models",
        "abstract": "This survey provides an overview of recent advances in large language models (LLMs). We review GPT-4, LLaMA, and PaLM architectures. The survey covers training methodology, evaluation on MMLU benchmark, and discusses limitations of current approaches including hallucination and alignment.",
        "authors": [{"name": "Wayne Xin Zhao"}, {"name": "Kun Zhou"}, {"name": "Ji-Rong Wen"}],
        "arxiv_id": "2303.18223",
        "source": "arxiv",
        "categories": ["Machine Learning", "Natural Language Processing"],
        "institution_ids": ["https://openalex.org/I205783295"],
    },
    {
        "title": "Denoising Diffusion Probabilistic Models",
        "abstract": "We present high-quality image synthesis results using diffusion probabilistic models. We trained on the CIFAR-10 dataset and LSUN benchmark. Our model achieves FID of 3.17 on CIFAR-10. Code available at https://github.com/hojonathanho/diffusion",
        "authors": [{"name": "Jonathan Ho"}, {"name": "Ajay Jain"}, {"name": "Pieter Abbeel"}],
        "doi": "10.48550/arXiv.2006.11239",
        "arxiv_id": "2006.11239",
        "source": "arxiv",
        "categories": ["Generative Models", "Computer Vision"],
        "institution_ids": ["https://openalex.org/I95457486"],
    },
    {
        "title": "Graph Neural Networks: A Review of Methods and Applications",
        "abstract": "Graph neural networks (GNNs) have received growing attention. We review GCN, GraphSAGE, and GAT architectures. Evaluated on Cora, CiteSeer, and PubMed datasets. Accuracy of 81.5% on Cora. Limitations include scalability and over-smoothing.",
        "authors": [{"name": "Jie Zhou"}, {"name": "Ganqu Cui"}],
        "source": "openalex",
        "categories": ["Graph Neural Networks", "Machine Learning"],
        "institution_ids": ["https://openalex.org/I136199984"],
    },
    {
        "title": "Proximal Policy Optimization Algorithms",
        "abstract": "We propose PPO, a family of policy gradient methods for reinforcement learning. Compared to TRPO and A2C baselines, PPO is simpler and achieves better sample complexity. Evaluated on Atari benchmark with reward of 7215 on Breakout. Code at https://github.com/openai/baselines",
        "authors": [{"name": "John Schulman"}, {"name": "Filip Wolski"}],
        "arxiv_id": "1707.06347",
        "source": "arxiv",
        "categories": ["Reinforcement Learning", "Optimization"],
        "institution_ids": ["https://openalex.org/I4200000001"],
    },
    {
        "title": "Masked Autoencoders Are Scalable Vision Learners",
        "abstract": "We show that masked autoencoders (MAE) are scalable self-supervised learners for computer vision. We trained on the ImageNet dataset and achieve accuracy of 87.8%. Compared to BEiT and ViT baselines, MAE is more efficient and uses less compute.",
        "authors": [{"name": "Kaiming He"}, {"name": "Xinlei Chen"}],
        "doi": "10.48550/arXiv.2111.06377",
        "arxiv_id": "2111.06377",
        "source": "openalex",
        "categories": ["Computer Vision", "Self-Supervised Learning"],
        "institution_ids": ["https://openalex.org/I4210112789"],
    },
    {
        "title": "Neural Radiance Fields for Novel View Synthesis",
        "abstract": "We present NeRF for synthesizing novel views of complex scenes. Evaluated on LLFF and Synthetic datasets. PSNR of 31.0 on Synthetic. Limitations include slow rendering and the need for dense views.",
        "authors": [{"name": "Ben Mildenhall"}, {"name": "Pratul P. Srinivasan"}],
        "arxiv_id": "2003.08934",
        "source": "arxiv",
        "categories": ["Computer Vision", "3D Vision"],
        "institution_ids": ["https://openalex.org/I95457486"],
    },
    {
        "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
        "abstract": "We explore RAG models which combine pre-trained parametric and non-parametric memory. Evaluated on Natural Questions benchmark. Accuracy of 44.5% on open-domain QA. Compared to T5 and DPR baselines.",
        "authors": [{"name": "Patrick Lewis"}, {"name": "Ethan Perez"}],
        "doi": "10.48550/arXiv.2005.11401",
        "arxiv_id": "2005.11401",
        "source": "openalex",
        "categories": ["Natural Language Processing", "Information Retrieval"],
        "institution_ids": ["https://openalex.org/I4210112789"],
    },
    {
        "title": "Decision Transformer: Reinforcement Learning via Sequence Modeling",
        "abstract": "We introduce Decision Transformer, which casts RL as a sequence modeling problem. Evaluated on Atari and D4RL benchmark datasets. Our approach matches or exceeds TD-based methods. Limitations include reliance on offline data quality.",
        "authors": [{"name": "Lili Chen"}, {"name": "Kevin Lu"}, {"name": "Aravind Rajeswaran"}],
        "arxiv_id": "2106.01345",
        "source": "arxiv",
        "categories": ["Reinforcement Learning", "Transformers"],
        "institution_ids": ["https://openalex.org/I95457486"],
    },
    {
        "title": "Segment Anything",
        "abstract": "We present SAM, a foundation model for image segmentation. Trained on 11M images with 1B mask annotations. Evaluated on 23 diverse segmentation datasets. Compared to SEEM and SegGPT baselines. Code at https://github.com/facebookresearch/segment-anything",
        "authors": [{"name": "Alexander Kirillov"}, {"name": "Eric Mintun"}],
        "arxiv_id": "2304.02643",
        "source": "openalex",
        "categories": ["Computer Vision", "Segmentation"],
        "institution_ids": ["https://openalex.org/I4210112789"],
    },
    {
        "title": "Multi-Agent Reinforcement Learning: A Review",
        "abstract": "This review covers multi-agent RL methods including QMIX, MAPPO, and independent learning approaches. Evaluated on StarCraft Multi-Agent Challenge benchmark. Limitations include non-stationarity and scalability.",
        "authors": [{"name": "Lukas Schäfer"}, {"name": "Filippos Christianos"}],
        "source": "arxiv",
        "categories": ["Multi-Agent Systems", "Reinforcement Learning"],
        "institution_ids": ["https://openalex.org/I114027177"],
    },
]

DEMO_INSTITUTIONS = [
    {"openalex_id": "https://openalex.org/I4210112789", "name": "Google", "country": "US"},
    {"openalex_id": "https://openalex.org/I95457486", "name": "University of California, Berkeley", "country": "US"},
    {"openalex_id": "https://openalex.org/I136199984", "name": "Tsinghua University", "country": "CN"},
    {"openalex_id": "https://openalex.org/I205783295", "name": "Renmin University of China", "country": "CN"},
    {"openalex_id": "https://openalex.org/I114027177", "name": "University of Edinburgh", "country": "GB"},
    {"openalex_id": "https://openalex.org/I4200000001", "name": "OpenAI", "country": "US"},
]


def main():
    from app.services.evidence import extract_evidence

    engine = create_engine(settings.database_url_sync)

    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    Base.metadata.create_all(engine)
    print("✓ Tables ready")

    with Session(engine) as session:
        # Seed institutions
        for inst_data in DEMO_INSTITUTIONS:
            existing = session.query(Institution).filter_by(openalex_id=inst_data["openalex_id"]).first()
            if not existing:
                inst = Institution(**inst_data)
                session.add(inst)
        session.commit()
        print(f"✓ Seeded {len(DEMO_INSTITUTIONS)} institutions")

        # Seed papers with random embeddings and evidence
        np.random.seed(42)
        seeded = 0
        for paper_data in DEMO_PAPERS:
            existing = session.query(Paper).filter_by(title=paper_data["title"]).first()
            if existing:
                continue

            # Generate a deterministic pseudo-embedding
            embedding = np.random.randn(settings.embedding_dim).tolist()
            norm = np.linalg.norm(embedding)
            embedding = [x / norm for x in embedding]

            # Extract evidence from abstract
            evidence = None
            if paper_data.get("abstract"):
                evidence = extract_evidence(paper_data["abstract"])

            paper = Paper(
                title=paper_data["title"],
                abstract=paper_data.get("abstract"),
                authors=paper_data.get("authors", []),
                doi=paper_data.get("doi"),
                arxiv_id=paper_data.get("arxiv_id"),
                source=paper_data["source"],
                categories=paper_data.get("categories", []),
                institution_ids=paper_data.get("institution_ids", []),
                embedding=embedding,
                evidence=evidence,
                published_date=datetime.now(timezone.utc) - timedelta(days=np.random.randint(0, 14)),
            )
            session.add(paper)
            seeded += 1

        session.commit()
        print(f"✓ Seeded {seeded} papers ({len(DEMO_PAPERS) - seeded} already existed)")

    engine.dispose()
    print("\n✓ Demo data ready. Start the backend with: uvicorn app.main:app --reload --port 8000")


if __name__ == "__main__":
    main()
