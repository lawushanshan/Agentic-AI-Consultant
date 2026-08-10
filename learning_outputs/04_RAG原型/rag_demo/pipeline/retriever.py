from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from config import Config


def retrieve(
    query: str, vector_store: Chroma, config: Config
) -> list[tuple[Document, float]]:
    results = vector_store.similarity_search_with_score(
        query, k=config.TOP_K
    )
    filtered = [
        (doc, score)
        for doc, score in results
        if score <= (1 - config.RELEVANCE_THRESHOLD)
    ]
    print(f"[retriever] 检索到 {len(results)} 个片段，过滤后保留 {len(filtered)} 个")
    return filtered
