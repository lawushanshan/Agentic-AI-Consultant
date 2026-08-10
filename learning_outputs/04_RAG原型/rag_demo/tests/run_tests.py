import json
import os
import time
from datetime import datetime

from config import Config
from pipeline.indexer import load_vector_store
from pipeline.retriever import retrieve
from pipeline.refusal import should_refuse
from pipeline.answerer import generate_answer


def evaluate_result(question_data: dict, result: dict) -> dict:
    passed = True
    reasons = []

    q_type = question_data["type"]

    if q_type == "no_answer":
        if not result.get("refused"):
            passed = False
            reasons.append("应拒答但给出了答案")
        else:
            answer_text = result.get("answer", "")
            for kw in question_data.get("expected_keywords", []):
                if kw not in answer_text:
                    reasons.append(f"拒答回复中缺少关键词: {kw}")
    else:
        if result.get("refused"):
            passed = False
            reasons.append("不应拒答但拒答了")

        sources = result.get("sources", [])
        expected_source = question_data.get("expected_source")
        if expected_source and expected_source not in sources:
            passed = False
            reasons.append(
                f"期望来源 {expected_source}，实际: {', '.join(sources) or '无'}"
            )

        answer_text = result.get("answer", "")
        for kw in question_data.get("expected_keywords", []):
            if kw not in answer_text:
                reasons.append(f"回答中缺少关键词: {kw}")
                passed = False

    return {
        "passed": passed,
        "reasons": reasons,
    }


def run_single_test(question_data: dict, config: Config) -> dict:
    vector_store = load_vector_store(config)
    question = question_data["question"]

    start = time.time()
    retrieved = retrieve(question, vector_store, config)

    if should_refuse(retrieved):
        result = {"answer": "根据当前知识库中的资料，无法回答您的问题。建议您联系相关部门获取准确信息。", "sources": [], "refused": True}
    else:
        result = generate_answer(question, retrieved, config)
    elapsed = time.time() - start

    evaluation = evaluate_result(question_data, result)

    return {
        "id": question_data["id"],
        "question": question,
        "type": question_data["type"],
        "expected_source": question_data.get("expected_source"),
        "answer": result["answer"],
        "sources": result.get("sources", []),
        "refused": result.get("refused", False),
        "elapsed": round(elapsed, 2),
        "passed": evaluation["passed"],
        "reasons": evaluation["reasons"],
    }


def run_test_suite(config: Config, output_file: str | None = None):
    test_path = os.path.join(os.path.dirname(__file__), "test_questions.json")
    with open(test_path, "r", encoding="utf-8") as f:
        test_data = json.load(f)

    questions = test_data["questions"]
    results = []
    pass_count = 0
    fail_count = 0

    print(f"开始运行测试: {len(questions)} 个问题\n")
    print(f"{'编号':<5} {'状态':<6} {'来源':<25} {'耗时':<8} {'备注'}")
    print("-" * 70)

    for q in questions:
        print(f"测试 {q['id']}: {q['question'][:30]}...", end=" ", flush=True)
        try:
            result = run_single_test(q, config)
        except Exception as e:
            result = {
                "id": q["id"],
                "question": q["question"],
                "type": q["type"],
                "expected_source": q.get("expected_source"),
                "answer": f"[错误] {str(e)}",
                "sources": [],
                "refused": False,
                "elapsed": 0,
                "passed": False,
                "reasons": [str(e)],
            }

        results.append(result)

        status = "PASS" if result["passed"] else "FAIL"
        if result["passed"]:
            pass_count += 1
        else:
            fail_count += 1

        source_str = (
            "拒答" if result["refused"]
            else ", ".join(result["sources"]) or "无"
        )
        source_str = source_str[:24]
        note = "; ".join(result["reasons"])[:20] if result["reasons"] else ""

        print(f"\r{result['id']:<5} {status:<6} {source_str:<25} {result['elapsed']:<7}s {note}")

        time.sleep(1)

    print("-" * 70)
    print(f"\n总结: {pass_count}/{len(questions)} PASS, {fail_count} FAIL")

    report = {
        "run_time": datetime.now().isoformat(),
        "total": len(questions),
        "passed": pass_count,
        "failed": fail_count,
        "results": results,
    }

    if output_file:
        out_path = output_file
    else:
        os.makedirs(config.RESULTS_DIR, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join(config.RESULTS_DIR, f"test_run_{date_str}.json")

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n测试报告已保存到: {out_path}")
