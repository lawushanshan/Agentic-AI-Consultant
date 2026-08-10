import os
import re
from langchain_core.documents import Document

DOC_TYPE_MAP = {
    "员工请假制度": "制度",
    "报销流程说明": "流程",
    "客户常见问题": "FAQ",
    "产品使用手册": "手册",
    "售后服务规则": "规则",
}


def extract_section_title(text: str) -> str:
    lines = text.split("\n")
    for line in lines:
        m = re.match(r"^#{1,3}\s+(.+)", line)
        if m:
            return m.group(1).strip()
    return ""


def annotate_chunk_metadata(chunks: list[Document]) -> list[Document]:
    annotated = []
    for chunk in chunks:
        source_path = chunk.metadata.get("source", "")
        filename = os.path.basename(source_path) if source_path else "unknown"

        doc_name = os.path.splitext(filename)[0]
        doc_type = DOC_TYPE_MAP.get(doc_name, "其他")

        section_title = extract_section_title(chunk.page_content)

        chunk.metadata.update({
            "source_file": filename,
            "doc_type": doc_type,
            "section_title": section_title,
        })
        annotated.append(chunk)

    print(f"[metadata] 元数据标注完成: {len(annotated)} 个片段")
    return annotated
