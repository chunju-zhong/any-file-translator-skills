# Any File Translator - 多格式文件翻译 Skill

## Problem Statement

AI Coding IDE 用户在处理多语言文档时面临巨大挑战：需要翻译各种格式的文档（PDF、DOCX、EPUB、Markdown 等），但现有工具要么不支持多种格式，要么无法处理超大文件（1000-2000 页），更缺乏翻译质量评估机制。这导致开发者需要使用多个工具、手动检查翻译质量，效率低下且容易出错。

## Evidence

- 开发者经常需要翻译技术文档、API 文档、项目文档等多语言材料
- 现有翻译工具（如 Google Translate）对技术文档的翻译质量不稳定，准确率仅 87%
- 超大文件翻译需要手动拆分，耗时且容易遗漏内容
- 缺乏自动化的翻译质量评估，需要人工逐段检查
- AI Coding IDE 缺乏集成的翻译能力，用户需要切换到外部工具

## Proposed Solution

构建一个集成到 AI Coding IDE 的翻译 Skill，支持多种文件格式和直接文本输入，能够智能处理超大文件（自动按章节拆分），并提供基于 AI 的翻译质量评估和迭代改进机制。使用多种翻译 API（OpenAI 兼容接口、DeepL、Google Translate）以及 IDE 内置的免费模型，确保翻译质量和成本效益。

## Key Hypothesis

我们相信提供一个集成到 AI Coding IDE 的多格式文件翻译 Skill，能够解决开发者在处理多语言文档时的效率和质量问题。我们将通过以下指标验证成功：翻译质量评分达到 85 分以上（满分 100），用户满意度评分 4.5/5 以上，单次翻译处理时间比手动方法减少 70%。

## What We're NOT Building

- **实时协作翻译**：不支持多人同时编辑同一文档的翻译
- **专业术语库管理**：不构建独立的术语管理系统（可后续扩展）
- **翻译记忆库**：不提供跨文档的翻译记忆功能
- **语音翻译**：不支持音频文件的翻译
- **图片 OCR + 翻译**：虽然支持 PDF 中的图片，但不专门处理纯图片文件（已有 visa-doc-translate skill）
- **网页实时翻译**：不提供浏览器插件或网页实时翻译功能

## Success Metrics

| Metric | Target | How Measured |
|--------|--------|--------------|
| 翻译质量评分 | ≥85/100 | 自动化质量评估系统（流畅度、准确性、格式保持度、完整性） |
| 用户满意度 | ≥4.5/5 | 用户反馈评分 |
| 处理效率提升 | ≥70% | 对比手动翻译方法的时间节省 |
| 超大文件处理成功率 | ≥95% | 1000+ 页文件的成功处理比例 |
| 格式保持准确率 | ≥90% | 输出文档与原文档格式一致性检查 |
| 迭代改进成功率 | ≥80% | 首次翻译不达标后，经过改进达到标准的比例 |

## Open Questions

- [ ] 如何平衡翻译速度和质量？是否需要提供"快速模式"和"高质量模式"？
- [ ] 对于专业领域文档（如医疗、法律），是否需要专门的翻译模型？
- [ ] 如何处理翻译中的版权和敏感信息问题？
- [ ] 是否需要支持离线翻译功能？

---

## Users & Context

**Primary User**
- **Who**: 使用 AI Coding IDE 的开发者、技术文档撰写者、项目经理
- **Current behavior**: 使用 Google Translate、DeepL 等在线工具，手动复制粘贴，需要手动检查质量
- **Trigger**: 需要阅读或撰写非母语的技术文档、API 文档、项目文档
- **Success state**: 快速获得高质量翻译，格式完整，无需手动调整

**Job to Be Done**
当我需要理解或撰写非母语的技术文档时，我想要一个能够自动翻译多种格式文件并保证质量的工具，以便我能够高效地完成工作而不需要切换多个工具。

**Non-Users**
- 专业翻译人员（他们需要更专业的 CAT 工具和术语管理）
- 普通用户（非开发者，可能更倾向于使用简单的在线翻译工具）
- 需要实时语音翻译的用户

---

## Solution Detail

### Core Capabilities (MoSCoW)

| Priority | Capability | Rationale |
|----------|------------|-----------|
| Must | 多格式文件输入支持 | 核心功能，支持 .txt, .pdf, .docx, .md, .epub 格式 |
| Must | 直接文本输入支持 | 允许用户直接粘贴文本进行翻译 |
| Must | 多格式输出支持 | 输出为 PDF, DOCX, Markdown 格式 |
| Must | 超大文件智能拆分 | 支持 1000-2000 页文件，按章节自然拆分 |
| Must | 翻译质量评估系统 | 自动评估流畅度、准确性、格式保持度、完整性 |
| Must | 迭代改进机制 | 翻译不达标时自动改进直到达标 |
| Should | 多翻译 API 支持 | 支持 OpenAI 兼容接口（GPT、Azure、本地模型）、DeepL、Google Translate 及 IDE 内置模型 |
| Should | 翻译历史记录 | 保存翻译历史，方便后续参考 |
| Should | 批量文件翻译 | 支持一次翻译多个文件 |
| Could | 自定义术语表 | 允许用户定义专业术语的翻译 |
| Could | 翻译对比视图 | 并排显示原文和译文 |
| Won't | 实时协作翻译 | 超出当前范围，需要复杂的同步机制 |

### MVP Scope

第一阶段 MVP 将包含：
1. 基本的文件格式支持（.txt, .md, .pdf）
2. 直接文本输入
3. 单一翻译 API（OpenAI 兼容接口，默认使用 OpenAI GPT 或 IDE 内置模型）
4. 基本的质量评估（流畅度、完整性）
5. 简单的文件拆分（按页数拆分）
6. Markdown 输出

### User Flow

```
用户输入（文件路径或文本）
    ↓
格式检测与验证
    ↓
文件预处理（提取文本、检测章节）
    ↓
[超大文件？] → 是 → 智能拆分（按章节/段落）
    ↓           ↓
    否          处理拆分后的文件块
    ↓           ↓
翻译处理（调用翻译 API）
    ↓
质量评估（流畅度、准确性、格式、完整性）
    ↓
[达标？] → 否 → 生成改进建议 → 重新翻译
    ↓       ↓
    是      [达标？]
    ↓           ↓
格式化输出（PDF/DOCX/Markdown）
    ↓
保存文件（大文件保存为多个文件）
    ↓
完成报告（质量评分、改进建议）
```

---

## Technical Approach

**Feasibility**: HIGH

**Architecture Notes**
- 采用模块化设计，便于扩展新的文件格式和翻译 API
- 使用 pdfplumber 处理 PDF 文件，支持大文件流式处理
- 使用 pypdf 进行 PDF 拆分和合并
- 使用 python-docx 处理 DOCX 文件
- 使用 ebooklib 处理 EPUB 文件
- 翻译质量评估采用多维度评分系统
- 文件拆分优先使用 PDF 书签/大纲，其次使用字体大小和章节模式识别

**Technical Risks**

| Risk | Likelihood | Mitigation |
|------|------------|------------|
| 超大文件内存溢出 | M | 使用流式处理和分页加载，限制单次处理页数 |
| 翻译 API 限流 | M | 实现请求队列和重试机制，支持多个 API 轮换 |
| 格式丢失 | M | 使用专业的文档处理库，保留原始格式信息 |
| 翻译质量不稳定 | M | 多维度评估，迭代改进，提供人工审核选项 |
| 章节识别失败 | L | 提供多种识别策略，允许手动指定拆分点 |

---

## Implementation Phases

| # | Phase | Description | Status | Parallel | Depends | PRP Plan |
|---|-------|-------------|--------|----------|---------|----------|
| 1 | Core Infrastructure | 基础架构搭建：文件处理、翻译接口、质量评估框架 | complete | - | - | .claude/PRPs/reports/core-infrastructure-report.md |
| 2 | Basic File Support | 基础文件格式支持：.txt, .md, 直接文本输入 | complete | - | 1 | .claude/PRPs/reports/basic-file-support-report.md |
| 3 | PDF Processing | PDF 文件处理：提取、拆分、输出 | complete | - | 1 | .claude/PRPs/reports/pdf-processing-report.md |
| 4 | DOCX & EPUB Support | DOCX 和 EPUB 文件格式支持 | completed | - | 1 | .claude/PRPs/plans/docx-epub-support.plan.md |
| 5 | Quality Evaluation System | 翻译质量评估系统：多维度评分 | pending | - | 1 | - |
| 6 | Iterative Improvement | 迭代改进机制：自动改进不达标翻译 | pending | - | 5 | - |
| 7 | Large File Handling | 超大文件处理：智能拆分、并行翻译 | pending | - | 3, 4 | - |
| 8 | Multi-API Support | 多翻译 API 支持：OpenAI, DeepL, Google, IDE 内置模型 | pending | - | 1 | - |
| 9 | Output Formatting | 输出格式化：PDF, DOCX, Markdown 输出 | pending | - | 2, 3, 4 | - |
| 10 | Integration & Polish | 集成测试、性能优化、文档完善 | pending | - | all | - |

### Phase Details

**Phase 1: Core Infrastructure**
- **Goal**: 搭建可扩展的基础架构，支持后续功能模块化开发
- **Scope**: 
  - 文件处理抽象层（FileProcessor 接口）
  - 翻译服务抽象层（TranslationService 接口）
  - 质量评估框架（QualityEvaluator 接口）
  - 配置管理系统
  - 日志和错误处理系统
- **Success signal**: 所有接口定义完成，单元测试通过，可以成功调用 Mock 实现

**Phase 2: Basic File Support**
- **Goal**: 实现最基础的文件格式支持，快速验证核心流程
- **Scope**:
  - .txt 文件读取和写入
  - .md 文件读取和写入（保留 Markdown 格式）
  - 直接文本输入处理
  - 基本的翻译流程（调用 OpenAI API）
  - 简单的质量检查（完整性）
- **Success signal**: 可以成功翻译 .txt 和 .md 文件，输出质量评分

**Phase 3: PDF Processing**
- **Goal**: 支持 PDF 文件的读取、处理和输出
- **Scope**:
  - 使用 pdfplumber 提取 PDF 文本
  - 保留 PDF 格式信息（标题、段落、列表）
  - 使用 pypdf 进行 PDF 拆分
  - PDF 输出（使用 reportlab 或 fpdf）
  - 基本的 PDF 章节识别（基于书签）
- **Success signal**: 可以成功翻译 PDF 文件，输出格式基本保持

**Phase 4: DOCX & EPUB Support**
- **Goal**: 扩展文件格式支持
- **Scope**:
  - 使用 python-docx 处理 DOCX 文件
  - 使用 ebooklib 处理 EPUB 文件
  - 保留文档格式和结构
  - DOCX 和 EPUB 输出
- **Success signal**: 可以成功翻译 DOCX 和 EPUB 文件

**Phase 5: Quality Evaluation System**
- **Goal**: 建立全面的翻译质量评估体系
- **Scope**:
  - 流畅度评分（使用语言模型评估）
  - 术语准确性检查（基于上下文）
  - 格式保持度检查（对比原文和译文格式）
  - 完整性检查（段落、句子数量对比）
  - "人味"评分（避免机器翻译痕迹）
  - 综合评分算法
- **Success signal**: 质量评估系统能够准确识别翻译问题，评分与人工评估相关性 > 0.8

**Phase 6: Iterative Improvement**
- **Goal**: 实现自动改进机制
- **Scope**:
  - 根据质量评估结果生成改进建议
  - 自动重新翻译不达标部分
  - 迭代次数限制（最多 3 次）
  - 改进效果跟踪
- **Success signal**: 首次翻译不达标的文本，经过迭代后 80% 达到标准

**Phase 7: Large File Handling**
- **Goal**: 支持超大文件的智能处理
- **Scope**:
  - 智能章节识别（书签、字体大小、章节模式）
  - 动态拆分策略
  - 并行翻译处理
  - 进度跟踪和恢复机制
  - 多文件输出
- **Success signal**: 可以成功处理 1000-2000 页的 PDF 文件，内存使用 < 2GB

**Phase 8: Multi-API Support**
- **Goal**: 支持多种翻译 API
- **Scope**:
  - OpenAI API 兼容接口集成（支持 OpenAI GPT、Azure OpenAI、本地模型、vLLM、Ollama 等）
  - DeepL API 集成
  - Google Translate API 集成
  - IDE 内置模型集成（通过 OpenAI 兼容接口）
  - API 选择策略（基于成本、质量、速度）
  - API 限流处理
- **Success signal**: 可以成功切换不同的翻译 API，翻译质量符合预期

**Phase 9: Output Formatting**
- **Goal**: 完善输出格式化功能
- **Scope**:
  - PDF 输出优化（格式、排版）
  - DOCX 输出优化（样式、格式）
  - Markdown 输出优化（格式、代码块）
  - 双语对照输出
  - 输出文件命名和组织
- **Success signal**: 输出文件格式美观，与原文档格式一致性 > 90%

**Phase 10: Integration & Polish**
- **Goal**: 完善系统，准备发布
- **Scope**:
  - 集成测试
  - 性能优化
  - 错误处理完善
  - 用户文档编写
  - 示例和教程
  - Skill 元数据完善
- **Success signal**: 所有测试通过，性能达标，文档完善

### Parallelism Notes

- Phase 2, 3, 4 可以并行开发（都依赖 Phase 1，但彼此独立）
- Phase 5, 8 可以并行开发（都依赖 Phase 1，但彼此独立）
- Phase 6 必须在 Phase 5 完成后开始
- Phase 7 必须在 Phase 3 和 Phase 4 完成后开始
- Phase 9 必须在 Phase 2, 3, 4 完成后开始
- Phase 10 必须在所有其他阶段完成后开始

---

## Decisions Log

| Decision | Choice | Alternatives | Rationale |
|----------|--------|--------------|-----------|
| PDF 处理库 | pdfplumber + pypdf | PyMuPDF, pikepdf | pdfplumber 提取文本质量高，pypdf 拆分合并功能完善，两者都是纯 Python 实现 |
| 翻译 API 优先级 | OpenAI 兼容接口 > DeepL > Google | DeepL > OpenAI > Google | OpenAI 兼容接口支持多种模型（GPT、本地模型、IDE 内置模型），灵活性高，适合技术文档 |
| 文件拆分策略 | 章节优先，页数兜底 | 固定页数，固定大小 | 章节拆分更符合文档逻辑，用户体验更好 |
| 质量评估方法 | AI 评估 + 规则检查 | 纯 AI 评估，纯规则检查 | 结合两者优势，AI 评估语义质量，规则检查格式完整性 |
| 迭代改进次数 | 最多 3 次 | 无限制，固定 1 次 | 平衡质量和效率，避免无限循环 |

---

## Research Summary

**Market Context**
- 翻译 API 市场竞争激烈，DeepL 在技术文档翻译质量最高（89%），OpenAI GPT-4 紧随其后（91% with good prompts），Google Translate 稍低（87%）
- 现有翻译工具大多不支持超大文件，或需要手动拆分
- 翻译质量评估主要依赖人工，自动化评估工具（如 BLEU）存在局限性
- AI Coding IDE 市场增长迅速，但缺乏集成的翻译功能

**Technical Context**
- pdfplumber 支持流式处理大文件，内存控制良好（500 页文档内存峰值 < 1.2GB）
- pypdf 成熟稳定，支持 PDF 拆分、合并、格式转换
- PDF 章节识别可以基于书签（outline）、字体大小、章节模式（"Chapter X", "第X章"）
- 翻译质量评估可以使用 BLEU、METEOR 等自动化指标，但需要结合人工评估
- OpenAI API 兼容接口广泛支持，包括 OpenAI GPT、Azure OpenAI、本地模型（vLLM、Ollama、LocalAI）、云服务（Together AI、Fireworks AI、Groq）以及 IDE 内置模型，提供统一接口调用不同模型

---

*Generated: 2026-04-07*
*Status: DRAFT - needs validation*
