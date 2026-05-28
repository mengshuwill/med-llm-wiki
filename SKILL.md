---
name: med-llm-wiki
description: Build a Karpathy-style personal knowledge base for medical research. Ingest papers, guidelines, trial protocols, and clinical notes into a living, git-backed Markdown wiki maintained by LLM. For medical researchers, clinicians, and PhD students.
---

# Med LLM Wiki

A Karpathy-style personal knowledge base for medical research. The LLM acts as your wiki maintainer: it reads raw sources (papers, guidelines, notes), compiles structured knowledge into interlinked Markdown pages, and keeps everything consistent over time.

## Philosophy

RAG asks the same question to raw documents every time. LLM Wiki compiles once and reuses forever — knowledge earns compound interest.

```
RAG:   raw docs → retrieve → answer (throwaway)
Wiki:  raw docs → LLM compiles → wiki pages → query with context → archive answers back
```

You bring the domain expertise (what to read, what matters). The LLM handles the labor (summarize, structure, cross-link, update).

## Architecture

```
your-med-wiki/
├── raw/                    # Immutable source material (read-only)
│   ├── papers/             #   PMID123456_smith2025.md, ...
│   ├── guidelines/         #   nccn_nsclc_2025.md, ...
│   ├── notes/              #   journal-club-2025-03.md, ...
│   ├── protocols/          #   irb-2025-001.md, ...
│   └── stats/              #   analysis-plan-rct.md, ...
├── wiki/                   # LLM-compiled knowledge pages
│   ├── index.md            # Global TOC — entry point for every query
│   ├── log.md              # Append-only operation log (date, action, files touched)
│   ├── diseases/           #   nsclc.md, type-2-diabetes.md, ...
│   ├── drugs/              #   osimertinib.md, metformin.md, ...
│   ├── biomarkers/         #   egfr-l858r.md, hba1c.md, ...
│   ├── methods/            #   rct-design.md, cox-regression.md, ...
│   ├── guidelines/         #   nccn-2025.md, esc-2024.md, ...
│   └── concepts/           #   pdl1-testing.md, intention-to-treat.md, ...
├── schema.md               # Rules for the LLM: structure, naming, templates
└── CLAUDE.md               # (optional) project-level instructions
```

## Core Commands

The skill provides 6 commands:

| Command | Purpose |
|---------|---------|
| `init` | Create new wiki directory structure |
| `zotero-list` | List Zotero collections and items |
| `zotero-import` | Export papers from Zotero to `raw/papers/` |
| `ingest` | Compile raw sources into wiki pages |
| `query` | Answer questions grounded in wiki knowledge |
| `lint` | Health check: broken links, contradictions, stale content |

## Three Core Operations

### 1. Ingest (`/med-llm-wiki ingest`)

Add new source material to the wiki.

**Workflow:**
1. User places source in `raw/` (or provides path to a paper/note)
2. LLM reads the source
3. LLM extracts: key findings, study design, population, interventions, outcomes, effect sizes, limitations
4. LLM updates or creates wiki pages (typically 5–15 files touched per source)
5. LLM updates `wiki/index.md` and appends to `wiki/log.md`
6. Optional: LLM suggests related sources already in the wiki

**Medical-specific extraction:**
- Study design (RCT, cohort, case-control, case series, meta-analysis, systematic review)
- PICO: Population, Intervention, Comparison, Outcome
- Evidence level (GRADE or Oxford CEBM)
- Effect sizes with CIs
- Drug/disease/gene/biomarker mentions
- Funding source and conflicts of interest
- PMID / DOI / ClinicalTrials.gov ID

### 2. Query (`/med-llm-wiki query <question>`)

Ask a question, get an answer grounded in your wiki.

**Workflow:**
1. LLM reads `wiki/index.md` to locate relevant pages
2. LLM reads those pages
3. LLM synthesizes answer with inline citations to wiki pages
4. User can optionally archive the answer back to wiki

### 3. Lint (`/med-llm-wiki lint`)

Health check on the knowledge base.

**Checks:**
- Broken [[wiki links]]
- Orphan pages (not linked from any index or other page)
- Contradictory claims across pages
- Outdated guidelines (newer version exists)
- Missing PICO elements in study summaries
- Pages without evidence level tags
- Stale pages (no updates > 6 months in fast-moving fields)

## Medical Schema

### Entity Page Templates

Every disease, drug, biomarker, and method gets a consistent page.

**Disease page** (`wiki/diseases/<name>.md`):
```markdown
---
aliases: [synonyms]
type: disease
specialty: [oncology, cardiology, ...]
updated: YYYY-MM-DD
---

# Disease Name

## Definition
## Epidemiology
## Pathophysiology
## Diagnosis
### Clinical Criteria
### Imaging
### Biomarkers
## Treatment
### First-line
### Second-line
### Emerging
## Prognosis
## Guidelines
## Key Trials
## References
```

**Drug page** (`wiki/drugs/<name>.md`):
```markdown
---
aliases: [brand names, INN]
type: drug
class: [mechanism class]
updated: YYYY-MM-DD
---

# Drug Name

## Mechanism of Action
## Indications
## Pivotal Trials
## Efficacy
## Safety & Adverse Events
## Drug Interactions
## Guidelines Referencing
## References
```

**Biomarker page** (`wiki/biomarkers/<name>.md`):
```markdown
---
aliases: []
type: biomarker
category: [diagnostic, prognostic, predictive, pharmacodynamic]
updated: YYYY-MM-DD
---

# Biomarker Name

## Biological Rationale
## Detection Methods
## Clinical Utility
### Indication
### Evidence Level
## Associated Conditions
## Associated Drugs
## Key Studies
## References
```

### YAML Frontmatter Convention

Every wiki page must have:
- `type`: one of `disease`, `drug`, `biomarker`, `method`, `guideline`, `concept`, `trial`
- `updated`: ISO date of last LLM modification
- `aliases`: list of synonyms or alternative names

Optional but recommended:
- `evidence_level`: `high` | `moderate` | `low` | `very-low` (GRADE)
- `pmid`: PubMed ID
- `doi`: DOI
- `status`: `current` | `superseded` | `controversial`

### Cross-Referencing

Use Obsidian-style `[[wikilinks]]`:
- `[[nsclc]]` links to `wiki/diseases/nsclc.md`
- `[[osimertinib]]` links to `wiki/drugs/osimertinib.md`
- `[[egfr-l858r]]` links to `wiki/biomarkers/egfr-l858r.md`

### Evidence Grading

Tag claims with evidence level when citing:
- `[EL:high]` — multiple RCTs or meta-analyses
- `[EL:moderate]` — single RCT or well-designed observational studies
- `[EL:low]` — case series, expert opinion
- `[EL:guideline]` — from a major clinical guideline (name the guideline)

## Zotero Integration

Direct pipeline from Zotero to wiki — the primary workflow for medical researchers.

### Prerequisites

Zotero desktop with the Better BibTeX or default SQLite storage. No API key required. The script reads `~/Zotero/zotero.sqlite` directly (read-only, never modifies your library).

### List collections and items

```
# List all Zotero collections with item counts
/med-llm-wiki zotero-list

# List items in a specific collection
/med-llm-wiki zotero-list --collection "EGFR-TKI resistance"
```

### Import from Zotero to raw/papers/

```
# Export first 10 papers from a collection to raw/papers/
/med-llm-wiki zotero-import --collection "EGFR-TKI resistance" --limit 10

# Export all papers to a specific output directory
/med-llm-wiki zotero-import --collection "My Project" --output ./raw/papers/
```

**What happens:**
1. Python reads Zotero SQLite, extracts items from the named collection
2. Each item is formatted as a markdown file in `raw/papers/`:
   - YAML frontmatter with zotero_key, title, authors, journal, year, doi, pmid, tags
   - Abstract text
   - Zotero notes (preserved from your annotations)
   - Attachment paths (PDF links preserved)
3. Filename convention: `PMID{id}_{FirstAuthor}_{Year}.md` (or DOI-based if no PMID)

### Batch ingest after import

After `zotero-import`, the LLM will offer to begin ingesting the exported files. You can:

```
# Ingest them all at once
/med-llm-wiki ingest --all

# Or one at a time for review
/med-llm-wiki ingest raw/papers/PMID12345678_Smith_2025.md
```

### Typical workflow with a new project

```
# 1. Initialize wiki
/med-llm-wiki init

# 2. See what's in your Zotero collection
/med-llm-wiki zotero-list --collection "My Research Topic"

# 3. Import the top 5 seed papers
/med-llm-wiki zotero-import --collection "My Research Topic" --limit 5

# 4. Ingest them (LLM builds the wiki skeleton)
/med-llm-wiki ingest --all

# 5. Add more papers, ingest, rinse, repeat
/med-llm-wiki zotero-import --collection "My Research Topic" --limit 10
/med-llm-wiki ingest --all

# 6. Run health checks periodically
/med-llm-wiki lint
```

## Getting Started

### Initialize a new medical wiki

```
/med-llm-wiki init
```

This creates the directory structure, `schema.md`, and initial `index.md` and `log.md`.

### Ingest your first source

1. Download a paper PDF or save a guideline to `raw/`
2. Run `/med-llm-wiki ingest raw/papers/PMID123456_smith2025.md`
3. The LLM reads, extracts, and creates/updates wiki pages
4. Review the changes in your editor (Obsidian recommended)
5. Commit to git

### Recommended companion tools

- **Zotero** (primary): `zotero-import` directly from your Zotero library — no manual file management needed.
- **Obsidian**: Visual graph view. See connections between drugs, diseases, biomarkers as they grow.
- **git**: Every LLM change is a commit. Rollback anytime.
- **paper-analyze skill**: Use before ingest for deep paper analysis; ingest the analysis output into the wiki.

## Medical-Specific Lint Rules

Beyond the standard checks, medical lint includes:

1. **Evidence decay**: Flag sources > 5 years old in fast-moving fields (oncology, immunology)
2. **Guideline versioning**: Detect when a newer guideline version exists but old one is still referenced
3. **Conflict detection**: Flag contradictory efficacy claims between sources
4. **Missing PICO**: Study summaries missing Population, Intervention, Comparison, Outcome
5. **Orphan drugs/biomarkers**: Entities mentioned but without a dedicated page
6. **Recalled/withdrawn drugs**: Check if referenced drugs have safety alerts

## Privacy Note

This skill processes research literature and clinical knowledge. It should NOT ingest:
- Patient-identifiable information (PHI)
- Unpublished clinical trial data without authorization
- Confidential peer review materials

The wiki is designed for published research and personal study notes, not patient records.

## Tips

- Start small: ingest 5–10 key papers in your field, then query. See the value before scaling.
- Commit often: `git commit -m "wiki: ingest Smith et al. 2025 on NSCLC third-line"` after each ingest.
- Trust but verify: the LLM makes mistakes. Spot-check new pages, especially drug doses and statistical claims.
- The schema is living: adjust `schema.md` as your research focus shifts. The LLM will follow updated rules on the next ingest.
- Re-ingest is normal: if a paper matters, run ingest again after you've added related papers — the LLM sees more context and produces richer pages.
