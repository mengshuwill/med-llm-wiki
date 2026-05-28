# Med LLM Wiki

A Claude Code skill for building a Karpathy-style personal knowledge base, designed for medical researchers.

## What is this?

This is a **skill** for Claude Code that turns your scattered research materials — papers, guidelines, trial protocols, clinical notes, stats plans — into a structured, interlinked, git-backed Markdown wiki maintained by an LLM.

Based on [Andrej Karpathy's LLM Wiki concept](https://github.com/Astro-Han/karpathy-llm-wiki): the LLM acts as your wiki compiler, not a one-shot Q&A bot.

## Why medical research?

Medical knowledge is uniquely suited to this approach:
- **High entity density**: diseases, drugs, biomarkers, genes, trials — all richly interconnected
- **Evidence hierarchy**: not all claims are equal, and evidence levels decay over time
- **Living guidelines**: standards of care update frequently, and old knowledge needs flagging
- **Cross-disciplinary**: oncology touches immunology; cardiology touches endocrinology. A wiki captures these links naturally.

## Quick Start

### Install

```bash
npx add-skill william/mmed-llm-wiki
```

Or add to your project's `CLAUDE.md`:

```yaml
skills:
  - william/med-llm-wiki
```

### Initialize a medical wiki

```
/med-llm-wiki init
```

This creates the directory structure, schema, and templates.

### Ingest your first paper

1. Save a paper to `raw/papers/PMID12345678_Smith_2025.md`
2. Run: `/med-llm-wiki ingest raw/papers/PMID12345678_Smith_2025.md`
3. The LLM extracts PICO, creates disease/drug/biomarker pages, updates the index
4. Review changes (Obsidian recommended) and `git commit`

### Query your knowledge

```
/med-llm-wiki query What is the current first-line treatment for EGFR-mutated NSCLC?
```

The answer is synthesized from your wiki pages with citations.

### Check wiki health

```
/med-llm-wiki lint
```

Detects contradictions, stale pages, broken links, outdated guidelines.

## Architecture

```
your-med-wiki/
├── raw/                    # Immutable sources
│   ├── papers/
│   ├── guidelines/
│   ├── notes/
│   ├── protocols/
│   └── stats/
├── wiki/                   # LLM-maintained knowledge
│   ├── index.md
│   ├── log.md
│   ├── diseases/
│   ├── drugs/
│   ├── biomarkers/
│   ├── methods/
│   ├── guidelines/
│   ├── concepts/
│   └── trials/
└── schema.md               # LLM rules and conventions
```

## Entity Types

| Type | Example | Template |
|------|---------|----------|
| Disease | `nsclc.md` | Disease definition, epidemiology, diagnosis, treatment, prognosis |
| Drug | `osimertinib.md` | Mechanism, indications, pivotal trials, safety, interactions |
| Biomarker | `egfr-l858r.md` | Biological rationale, detection, clinical utility, evidence level |
| Trial | `adaura.md` | PICO, design, results table, limitations, guideline impact |
| Guideline | `nccn-nsclc-2025.md` | Recommendations, evidence base, version history |
| Method | `cox-regression.md` | When to use, assumptions, interpretation, common pitfalls |
| Concept | `pdl1-testing.md` | Cross-cutting topics that span multiple entity types |

## Evidence Grading

Every claim is tagged with an evidence level:

| Tag | Meaning |
|-----|---------|
| `[EL:high]` | Multiple consistent RCTs or meta-analyses |
| `[EL:moderate]` | Single RCT or strong observational data |
| `[EL:low]` | Case series, expert opinion |
| `[EL:guideline:NCCN]` | From a named clinical guideline |

## Companion Tools

- **[Obsidian](https://obsidian.md)**: Visual graph view of your knowledge graph
- **git**: Every LLM change is a commit — fully auditable
- **[Zotero](https://www.zotero.org)**: Export papers with PMID-based filenames to `raw/papers/`
- **paper-analyze skill**: Deep paper analysis before wiki ingestion

## Comparison with Generic LLM Wiki

| Feature | Generic LLM Wiki | Med LLM Wiki |
|---------|-----------------|--------------|
| Entity types | Generic (concept, entity) | Disease, Drug, Biomarker, Trial, Guideline, Method |
| Templates | Minimal | Full PICO-structured templates per type |
| Evidence grading | None | GRADE-based with guideline attribution |
| Lint rules | Broken links, orphans | + evidence decay, guideline versioning, drug safety alerts |
| Metadata | Basic | PMID, DOI, NCT, evidence_level, MeSH terms |
| Privacy | Not addressed | PHI-aware, research-only scope |

## Contributing

This skill is designed for the medical research community. If you have templates for additional entity types (imaging findings, surgical techniques, genetic variants, etc.), PRs are welcome.

## License

MIT
