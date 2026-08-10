import os
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from config import Config


def load_prompt_template(template_name: str, config: Config) -> str:
    path = os.path.join(config.PROMPTS_DIR, template_name)
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def assemble_context(retrieved: list[tuple]) -> str:
    parts = []
    seen = set()
    for doc, score in retrieved:
        source = doc.metadata.get("source_file", "unknown")
        if source not in seen:
            parts.append(f"【来源：{source}】")
            seen.add(source)
        parts.append(doc.page_content.strip())
        parts.append("")
    return "\n".join(parts).strip()


def generate_answer(
    query: str, retrieved: list[tuple], config: Config
) -> dict:
    template = load_prompt_template("answer_template.txt", config)
    context = assemble_context(retrieved)

    prompt = template.replace("{context}", context).replace("{question}", query)

    llm = ChatOpenAI(
        model=config.DEEPSEEK_MODEL,
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        temperature=0,
    )

    response = llm.invoke([
        SystemMessage(content="你是一个严格基于参考资料回答问题的企业知识库问答助手。"),
        HumanMessage(content=prompt),
    ])

    sources = list({
        doc.metadata.get("source_file", "unknown")
        for doc, _ in retrieved
    })

    return {
        "answer": response.content,
        "sources": sources,
        "refused": False,
        "chunk_count": len(retrieved),
    }
