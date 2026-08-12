import argparse
import json
import os
import sys
import time
from datetime import datetime

from config import Config
from pipeline.loader import load_kb_documents
from pipeline.cleaner import clean_documents
from pipeline.chunker import chunk_documents
from pipeline.metadata import annotate_chunk_metadata
from pipeline.indexer import build_vector_store, load_vector_store
from pipeline.retriever import retrieve
from pipeline.refusal import should_refuse, format_refusal
from pipeline.answerer import generate_answer


def build_index(config: Config):
    docs = load_kb_documents(config.KB_DOCS_DIR)
    docs = clean_documents(docs)
    chunks = chunk_documents(docs, config.CHUNK_SIZE, config.CHUNK_OVERLAP)
    chunks = annotate_chunk_metadata(chunks)
    build_vector_store(chunks, config)
    print("\n索引构建完成。可以开始提问了。")


def ask_question(question: str, config: Config) -> dict:
    # 从向量库中加载数据
    vector_store = load_vector_store(config)
    # 根据问题进行检索
    retrieved = retrieve(question, vector_store, config)

    # 判断是否拒答
    if should_refuse(retrieved):
        return format_refusal()
    # 生成回答
    return generate_answer(question, retrieved, config)


def print_result(question: str, result: dict):
    print(f"\n问题：{question}")
    print(f"回答：{result['answer']}")
    if result["sources"]:
        print(f"来源：{'、'.join(result['sources'])}")
    if result.get("refused"):
        print("[系统] 已拒答 — 知识库中无相关信息")
    print("-" * 60)


def run_interactive(config: Config):
    print("企业知识库问答 RAG Demo (输入 'quit' 退出)\n")
    while True:
        try:
            question = input("请输入问题：").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        if not question:
            continue
        if question.lower() in ("quit", "exit", "q"):
            print("再见！")
            break
        start = time.time()
        result = ask_question(question, config)
        elapsed = time.time() - start
        print_result(question, result)
        print(f"[耗时] {elapsed:.1f}s\n")


def run_tests(config: Config, output_file: str | None = None):
    from tests.run_tests import run_test_suite

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    run_test_suite(config, output_file)


def main():
    parser = argparse.ArgumentParser(
        description="企业知识库问答 RAG Demo"
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("build-index", help="构建向量索引")

    ask_parser = subparsers.add_parser("ask", help="提问")
    ask_parser.add_argument("question", type=str, help="问题内容")

    subparsers.add_parser("interactive", help="交互式问答")

    test_parser = subparsers.add_parser("test", help="运行测试")
    test_parser.add_argument(
        "--output", type=str, default=None, help="输出文件路径"
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    config = Config()

    if args.command == "build-index":
        build_index(config)
    elif args.command == "ask":
        start = time.time()
        result = ask_question(args.question, config)
        elapsed = time.time() - start
        print_result(args.question, result)
        print(f"[耗时] {elapsed:.1f}s")
    elif args.command == "interactive":
        run_interactive(config)
    elif args.command == "test":
        run_tests(config, args.output)


if __name__ == "__main__":
    main()
