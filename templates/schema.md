# Medical Wiki Schema

This file defines the rules, conventions, and templates the LLM follows when maintaining your medical wiki. Edit it freely — the LLM will adopt your changes on the next ingest.

## Directory Structure

```
raw/                    # Immutable sources (LLM reads, never writes)
  papers/               #   PMID-first-author-year.md
  guidelines/           #   organization_topic_year.md
  notes/                #   descriptive-name.md
  protocols/            #   study-protocol-name.md
  stats/                #   analysis-plan-name.md

wiki/                   # LLM-maintained knowledge pages
  index.md              # Master table of contents
  log.md                # Append-only operation log
  diseases/
  drugs/
  biomarkers/
  methods/
  guidelines/
  concepts/
  trials/
```

## Naming Convention

- **Files**: kebab-case, lowercase. `egfr-mutation-nsclc.md` not `EGFR_Mutation_NSCLC.md`
- **Papers**: `PMID12345678_FirstAuthor_Year.md` (short title keyword optional)
- **Disease pages**: use MeSH preferred term when available
- **Drug pages**: use INN (international nonproprietary name), not brand names
- **Biomarker pages**: use HGNC gene symbol for genes, standard name for proteins

## YAML Frontmatter

Every wiki page must have:
```yaml
---
type: disease | drug | biomarker | method | guideline | concept | trial
updated: YYYY-MM-DD
aliases: [synonym1, synonym2]
---
```

Optional fields by type:

| Field | Used by | Values |
|-------|---------|--------|
| `specialty` | disease, guideline | oncology, cardiology, neurology, ... |
| `drug_class` | drug | TKI, monoclonal_antibody, small_molecule, ... |
| `biomarker_category` | biomarker | diagnostic, prognostic, predictive, pharmacodynamic |
| `evidence_level` | concept, trial | high, moderate, low, very-low (GRADE) |
| `pmid` | trial, concept | PubMed ID |
| `doi` | any | DOI |
| `nct_id` | trial | ClinicalTrials.gov ID |
| `guideline_organization` | guideline | NCCN, ESC, AHA, WHO, NICE, ... |
| `guideline_year` | guideline | YYYY |
| `status` | any | current, superseded, controversial, historical |

## Cross-Referencing

- Use `[[page-name]]` for internal wiki links (Obsidian compatible)
- Always link diseases, drugs, and biomarkers on first mention in any page
- Build index pages that group related entities (e.g., `wiki/diseases/_oncologic.md` for all cancer types)

## Evidence Tagging

Inline evidence tags help readers gauge claim reliability:

| Tag | Meaning |
|-----|---------|
| `[EL:high]` | Multiple consistent RCTs or meta-analyses |
| `[EL:moderate]` | Single RCT or strong observational data |
| `[EL:low]` | Case series, retrospective, expert opinion |
| `[EL:guideline:NCCN]` | From a named guideline |
| `[EL:preclinical]` | In vitro or animal data only |

## Ingestion Rules

When ingesting a new source:

1. **Read** the raw source completely
2. **Identify** all mentioned diseases, drugs, biomarkers, methods, and concepts
3. **Extract** PICO elements for any study described
4. **Create** new wiki pages for novel entities (following templates)
5. **Update** existing pages with new findings or references
6. **Link** new pages from existing ones where relevant
7. **Update** `wiki/index.md` with new entries
8. **Append** to `wiki/log.md`: `| YYYY-MM-DD | ingest | <source filename> | <summary of changes> |`

## Query Rules

When answering a query:

1. **Read** `wiki/index.md` first to find relevant pages
2. **Read** those pages
3. **Synthesize** an answer with `[[wikilink]]` citations
4. **Note** any gaps in the wiki that would improve the answer
5. **Offer** to archive the answer if it adds new synthesized knowledge

## Special Considerations

- Drugs may have different brand names in different countries — store by INN, list brands in aliases
- Clinical guidelines are versioned — when ingesting a new version, mark old as `status: superseded` and link to new
- Gene names change (HGNC updates) — store the most recent approved symbol and list deprecated ones in aliases
- Study results may be superseded (e.g., early-phase promising results nullified by later Phase III) — update with cross-reference, don't delete history
