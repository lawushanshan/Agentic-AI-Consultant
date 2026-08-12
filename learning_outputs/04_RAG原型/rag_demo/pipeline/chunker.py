from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


CHINESE_MARKDOWN_SEPARATORS = [
    "\n## ",
    "\n### ",
    "\n\n",
    "\n",
    "。",
    "；",
    "，",
    " ",
    "",
]


def create_splitter(
    chunk_size: int = 300, chunk_overlap: int = 50
) -> RecursiveCharacterTextSplitter:
    return RecursiveCharacterTextSplitter(
        separators=CHINESE_MARKDOWN_SEPARATORS,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )


def chunk_documents(
    docs: list[Document],
    chunk_size: int = 300,
    chunk_overlap: int = 50,
) -> list[Document]:
    # 创建中文分割器
    splitter = create_splitter(chunk_size, chunk_overlap)
    chunks = splitter.split_documents(docs)
    print(f"[chunker] 切分完成: {len(docs)} 篇文档 -> {len(chunks)} 个片段")
    return chunks
