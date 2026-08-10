# 企业知识库问答 RAG Demo

基于 LangChain + DeepSeek + ChromaDB 的最小可运行 RAG 原型，用于学习 RAG 流程原理。

## RAG 流程

```
文档加载 → 清洗 → 切分 → 元数据标注 → Embedding → 向量索引
                                                  ↓
用户提问 → 检索相关片段 → 阈值过滤 → [拒答/生成回答] → 返回答案+引用
```

## 环境要求

- Python 3.10+
- DeepSeek API Key（[https://platform.deepseek.com](https://platform.deepseek.com)）

## 安装

```bash
cd rag_demo
pip install -r requirements.txt
```

首次安装 `sentence-transformers` 时会下载 Embedding 模型（约 400MB），后续使用缓存。

## 配置

```bash
cp .env.example .env
```

编辑 `.env`，填入你的 DeepSeek API Key：

```ini
DEEPSEEK_API_KEY=sk-你的真实Key
```

## 使用

### 1. 构建索引

```bash
python main.py build-index
```

读取 `kb_docs/` 下的 5 篇 Markdown 文档，切分后生成向量索引到 `chroma_db/`。

### 2. 提问

```bash
python main.py ask "员工入职满3年年假有几天？"
```

### 3. 交互式问答

```bash
python main.py interactive
```

### 4. 运行测试

```bash
python main.py test
python main.py test --output results/my_test.json
```

自动运行 20 个测试问题，输出 PASS/FAIL 结果到 `results/` 目录。

## 项目结构

```
rag_demo/
├── main.py              # CLI 入口
├── config.py            # 配置管理
├── pipeline/            # RAG pipeline 各步骤
│   ├── loader.py        #   文档加载
│   ├── cleaner.py       #   文档清洗
│   ├── chunker.py       #   文档切分
│   ├── metadata.py      #   元数据标注
│   ├── indexer.py       #   Embedding + 向量存储
│   ├── retriever.py     #   相关性检索
│   ├── answerer.py      #   LLM 回答生成
│   └── refusal.py       #   无答案拒答
├── prompts/             # Prompt 模板
├── kb_docs/             # 知识库文档（5 篇）
├── tests/               # 测试数据和运行器
├── chroma_db/           # 向量索引存储（自动生成）
└── results/             # 测试结果输出（自动生成）
```

## 技术栈

| 组件 | 技术 |
|------|------|
| RAG 框架 | LangChain 0.3+ |
| LLM | DeepSeek (OpenAI 兼容) |
| Embedding | HuggingFace sentence-transformers (本地) |
| 向量数据库 | ChromaDB (本地持久化) |
