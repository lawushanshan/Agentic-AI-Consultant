def should_refuse(retrieved: list) -> bool:
    return len(retrieved) == 0


def format_refusal() -> dict:
    return {
        "answer": "根据当前知识库中的资料，无法回答您的问题。建议您联系相关部门获取准确信息。",
        "sources": [],
        "refused": True,
    }
