import os

os.environ["HF_HUB_OFFLINE"] = "1"
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_DATASETS_OFFLINE"] = "1"

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

from config import Config


def build_vector_store(chunks: list[Document], config: Config) -> Chroma:
    print(f"[indexer] 正在加载 Embedding 模型: {config.EMBEDDING_MODEL}")
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )

    print(f"[indexer] 正在向量化 {len(chunks)} 个片段并写入 ChromaDB...")
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=config.CHROMA_PERSIST_DIR,
        collection_name="kb_docs",
    )
    print(f"[indexer] 索引构建完成，持久化到: {config.CHROMA_PERSIST_DIR}")
    return vector_store


def load_vector_store(config: Config) -> Chroma:
    embeddings = HuggingFaceEmbeddings(
        model_name=config.EMBEDDING_MODEL,
        encode_kwargs={"normalize_embeddings": True},
    )
    vector_store = Chroma(
        persist_directory=config.CHROMA_PERSIST_DIR,
        embedding_function=embeddings,
        collection_name="kb_docs",
    )
    return vector_store
