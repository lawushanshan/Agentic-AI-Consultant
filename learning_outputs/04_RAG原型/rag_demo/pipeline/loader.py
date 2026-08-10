from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_core.documents import Document


def load_kb_documents(docs_dir: str) -> list[Document]:
    loader = DirectoryLoader(
        docs_dir,
        glob="**/*.md",
        loader_cls=TextLoader,
        loader_kwargs={"autodetect_encoding": True},
    )
    docs = loader.load()
    print(f"[loader] 加载了 {len(docs)} 篇文档")
    for doc in docs:
        print(f"  - {doc.metadata['source']}: {len(doc.page_content)} 字符")
    return docs
