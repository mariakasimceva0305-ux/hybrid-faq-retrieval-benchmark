from faq_bench.data import Document
from faq_bench.retrievers.bm25 import BM25Retriever


def test_bm25_returns_password_doc_first() -> None:
    docs = [
        Document(doc_id="d1", title="Password reset", text="Reset password through account email", category="security"),
        Document(doc_id="d2", title="Billing", text="Refund requests and disputes", category="billing"),
    ]
    retriever = BM25Retriever(docs)
    results = retriever.search("How do I reset my password?", top_k=2)
    assert results[0].doc_id == "d1"
