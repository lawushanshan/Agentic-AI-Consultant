import re
from langchain_core.documents import Document


def clean_document(doc: Document) -> Document:
    text = doc.page_content
    # 清洗html 注释
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    # 全角空格转半角空格
    text = re.sub(r"　", " ", text)
    # 多个换行符替换为两个换行符
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()
    return Document(page_content=text, metadata=doc.metadata.copy())


def clean_documents(docs: list[Document]) -> list[Document]:
    return [clean_document(doc) for doc in docs]
