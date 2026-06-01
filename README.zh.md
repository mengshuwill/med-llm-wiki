# Med LLM Wiki

面向医学科研工作者的 Claude Code 技能 — 基于 Karpathy 的 LLM Wiki 理念，将分散的论文、指南、笔记、审稿意见和统计方案，编译成一个可持续生长、可追溯、可复用的个人知识库。

[English](README.md)

## 这是什么？

这是一个 **Claude Code 技能**。LLM 不再是即用即弃的问答机器人，而是你的知识库维护者：持续把原始文献"编译"成结构化的、互相链接的 Markdown 页面，知识产生复利效应。

思路源自 [Andrej Karpathy 的 LLM Wiki](https://github.com/Astro-Han/karpathy-llm-wiki)：代码世界里的 RAG 像解释器（每次重新求值），LLM Wiki 像编译器（一次编译，反复使用）。

## 为什么面向医学科研？

医学知识天然适合这套方法：

- **实体密度高**：疾病、药物、生物标志物、基因、临床试验，彼此高度关联
- **证据等级分明**：RCT 的结论和病例报告的结论不应被同等对待
- **指南持续更新**：标准在变，旧知识需要标记归档，而不是删除
- **学科交叉普遍**：肿瘤涉及免疫、心脏涉及内分泌。Wiki 的图谱能捕捉这些自然联系

## 快速开始

### 安装

```bash
npx add-skill mengshuwill/med-llm-wiki
```

或在项目的 `CLAUDE.md` 中添加：

```yaml
skills:
  - mengshuwill/med-llm-wiki
```

### 初始化

```
/med-llm-wiki init
```

创建完整的目录结构、schema 规则文件和初始模板。

### 首次摄入

1. 将论文放入 `raw/papers/`（或直接从 Zotero 导入，见下文）
2. 运行：`/med-llm-wiki ingest raw/papers/PMID12345678_Smith_2025.md`
3. LLM 自动提取 PICO 要素、创建疾病/药物/生物标志物页面、更新索引
4. 在 Obsidian 中检阅图谱变化，然后 `git commit`

### 查询知识

```
/med-llm-wiki query 目前 EGFR 突变 NSCLC 的一线标准治疗是什么？
```

回答基于你的 wiki 页面，带 `[[wikilink]]` 引用，可追溯来源。

### 健康检查

```
/med-llm-wiki lint
```

自动检测：失效链接、孤立页面、矛盾声明、过时指南、缺失证据等级。

## Zotero 一键导入

这是本技能的核心差异化功能 — 不用手动下载论文、复制摘要、整理文件。

```
# 列出所有 Zotero 分类目录
/med-llm-wiki zotero-list

# 查看某个分类下的论文
/med-llm-wiki zotero-list --collection "EGFR-TKI 耐药"

# 导入前 10 篇到 raw/papers/
/med-llm-wiki zotero-import --collection "EGFR-TKI 耐药" --limit 10

# 然后批量摄入
/med-llm-wiki ingest --all
```

脚本直接读取本地 `~/Zotero/zotero.sqlite`（只读，不修改文献库），提取标题、摘要、作者、期刊、DOI、PMID、标签和你的 Zotero 笔记，生成带 YAML frontmatter 的 Markdown 文件。零 API 配置。

## 架构

```
your-med-wiki/
├── raw/                    # 不可变源文件
│   ├── papers/             #   论文（自动或手动导入）
│   ├── guidelines/         #   临床指南
│   ├── notes/              #   会诊笔记、读书笔记
│   ├── protocols/          #   研究方案
│   └── stats/              #   统计分析计划
├── wiki/                   # LLM 维护的知识页面
│   ├── index.md            #   主索引（每次查询的入口）
│   ├── log.md              #   操作日志（追加写入）
│   ├── diseases/           #   疾病页（定义、分期、治疗、预后）
│   ├── drugs/              #   药物页（机制、适应症、关键试验、不良反应）
│   ├── biomarkers/         #   标志物页（原理、检测方法、临床效用、证据等级）
│   ├── methods/            #   方法学页（试验设计、统计方法、偏倚评估）
│   ├── guidelines/         #   指南页（推荐意见、证据基础、版本历史）
│   ├── concepts/           #   概念页（跨实体主题，如 PD-L1 检测、ITT 分析）
│   ├── datasets/           #   数据集页（模态、标注方式、基准结果、偏倚）
│   ├── models/             #   AI 模型页（架构、任务、性能、部署状态）
│   └── trials/             #   试验页（PICO、设计、结果表、局限性）
└── schema.md               # LLM 行为规则（命名、模板、链接约定）
```

## 实体类型

| 类型 | 示例 | 内容 |
|------|------|------|
| 疾病 | `nsclc.md` | 定义、流行病学、诊断、分期、治疗路径、预后 |
| 药物 | `osimertinib.md` | 作用机制、适应症、关键试验、疗效、安全性、耐药 |
| 生物标志物 | `egfr-l858r.md` | 生物学原理、检测方法、临床效用、证据等级 |
| 临床试验 | `adaura.md` | PICO、研究设计、结果表、局限性、指南影响 |
| 临床指南 | `nccn-nsclc-2025.md` | 推荐意见、证据基础、版本更替 |
| 方法学 | `cox-regression.md` | 适用场景、假设条件、结果解读、常见误区 |
| 概念 | `pdl1-testing.md` | 跨实体主题，多页交叉引用 |
| 数据集 | `mimic-cxr.md` | 模态、解剖部位、标注方式、基准结果、偏倚、访问方式 |
| AI模型 | `nnunet.md` | 架构、任务、训练数据、性能、代码可用性、部署状态 |

## 证据分级

每条声明标注证据等级：

| 标签 | 含义 |
|------|------|
| `[EL:high]` | 多个一致 RCT 或 Meta 分析 |
| `[EL:moderate]` | 单个 RCT 或高质量观察性研究 |
| `[EL:low]` | 病例系列、专家意见 |
| `[EL:guideline:NCCN]` | 来自指定指南的推荐 |

## 与通用 LLM Wiki 的区别

| 特性 | 通用 LLM Wiki | Med LLM Wiki |
|------|--------------|--------------|
| 实体类型 | 通用（概念、实体） | 疾病、药物、标志物、试验、指南、方法学、数据集、AI模型 |
| 页面模板 | 极简 | 含 PICO 结构化模板 |
| 证据分级 | 无 | GRADE 体系 + 指南出处标注 |
| 一致性检查 | 失效链接、孤立页 | + 证据时效衰减、指南版本冲突、药物安全警示 |
| 元数据 | 基础 | PMID、DOI、NCT、evidence_level、MeSH |
| 隐私考量 | 未涉及 | PHI 敏感，仅处理已发表研究 |
| 文献管理集成 | 无 | Zotero 本地 SQLite 一键导入 |

## 推荐配套工具

- **[Zotero](https://www.zotero.org)**（主力）：`zotero-import` 直接从文献库导入，无需手动管理文件
- **[Obsidian](https://obsidian.md)**：图谱视图，直观看到疾病、药物、标志物之间的关联演进
- **git**：每次 LLM 修改一个 commit，完全可审计、可回滚
- **paper-analyze 技能**：深度分析单篇论文后再摄入 wiki

## 典型工作流

以一个课题项目为例：

```
# 1. 初始化
/med-llm-wiki init

# 2. 从 Zotero 看文献概况
/med-llm-wiki zotero-list --collection "我的课题"

# 3. 先导入 5 篇种子论文，建立骨架
/med-llm-wiki zotero-import --collection "我的课题" --limit 5
/med-llm-wiki ingest --all

# 4. 逐步追加，每批 5-10 篇
/med-llm-wiki zotero-import --collection "我的课题" --limit 10
/med-llm-wiki ingest --all

# 5. 写综述/标书前做一次全面健康检查
/med-llm-wiki lint

# 6. 基于 wiki 输出内容
/med-llm-wiki query "我的课题领域目前有哪些未解决的临床问题？"
```

## 适用范围和隐私

本技能处理公开的科研文献和临床知识。不应摄入：

- 含患者身份信息（PHI）的临床记录
- 未经授权的未发表临床试验数据
- 保密性同行评审材料

Wiki 设计面向已发表研究和学习笔记，而非病历。

## 贡献

欢迎医学领域的 PR。如果你有额外实体类型的模板（如影像征象、外科技术、遗传变异等），欢迎提交。

## 协议

MIT
