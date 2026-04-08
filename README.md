# Any File Translator

多格式文件翻译 Skill，支持 PDF、TXT、MD、DOCX、EPUB 等格式，能够智能处理超大文件（1000-2000 页），并提供基于 AI 的翻译质量评估和迭代改进机制。

## 功能特性

- **多格式支持**: 支持 .txt, .pdf, .docx, .md, .epub 等格式
- **超大文件处理**: 智能拆分 1000-2000 页的超大文件
- **多翻译 API**: 支持 OpenAI 兼容接口、IDE 内置模型（Trae）
- **质量评估**: 自动评估翻译质量（流畅度、准确性、格式保持度）
- **迭代改进**: 翻译不达标时自动改进

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 使用示例

```python
from src.skill import translate_file

# 翻译文件
result = translate_file(
    file_path="document.pdf",
    target_language="zh",
    output_format="markdown"
)

print(f"翻译完成: {result.output_path}")
print(f"质量评分: {result.quality_score}")
```

## 项目结构

```
any-file-translator/
├── src/
│   ├── parsers/          # 文件解析器
│   ├── translators/      # 翻译服务
│   ├── evaluators/       # 质量评估器
│   └── utils/            # 工具模块
├── tests/                # 测试
├── config/               # 配置文件
├── docs/                 # 文档
└── data/                 # 示例数据
```

## 开发

### 运行测试

```bash
python -m pytest tests/ -v
```

### 类型检查

```bash
python -m mypy src/ --ignore-missing-imports
```

## 许可证

MIT
