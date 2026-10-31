---
title: "Jazzar: jazz press archives, searchable and cited to the page"
date: 2026-10-31
draft: true
nature: "produit"
description: "A SaaS under construction that makes decades of jazz press archives searchable: answers cited to the page, research briefs written by agents, data journalism through Text-to-SQL. In progress: the foundation of the first three pillars is coded, the first measurements are next."
summary: "A SaaS for jazz press archives, under construction: hybrid search with answers cited to the PDF page, briefs written by a team of agents, data journalism through guarded Text-to-SQL. The foundation is coded and runs on twelve issues of DownBeat; measuring quality, cost and latency is the next step."
tags: ["python", "fastapi", "postgresql", "pgvector", "rag", "llm", "agents", "rust", "next.js", "claude code"]
featureImage: "carte-en.png"
showTableOfContents: true
---

{{< lead >}}
Ask a question in French of decades of English-language jazz press, and get an answer where
every sentence points to the magazine page it comes from. Or nothing, if the archive says nothing.
{{< /lead >}}

{{< fiche-projet
    statut="In development · foundation of the first three pillars coded, measurements next"
    periode="Since October 2026"
    role="Solo: scoping, architecture, development"
    stack="Python 3.12, FastAPI, async SQLAlchemy, PostgreSQL 17, pgvector, Redis, bge-m3, Claude Opus 5.5 and Haiku 5.5, Rust (PyO3), sqlglot, Next.js 16, React 19, Tailwind 4, Plotly, Docker Compose"
    code="https://github.com/gwils28/jazzar" >}}

{{< stats >}}
{{< stat value="1,124" label="DownBeat pages indexed" >}}twelve 2025 issues, split into 3,381 passages{{< /stat >}}
{{< stat value="17" label="evaluation cases" >}}including 6 traps where the only right answer is to refuse{{< /stat >}}
{{< stat value="0" label="lines of generated code executed" >}}model-written SQL is validated, charts are a specification{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Work in progress.** This page describes the repository as of 31 October 2026, a week after the
first commit. The code of the first three pillars is written and search runs on the real corpus,
but synthesis by Claude has not yet been evaluated for real: **no quality, cost or latency figure
has been measured yet.** The page will be updated with each roadmap step.
{{< /alert >}}

{{< alert icon="image" >}}
**The cover is a mock-up**, not a screenshot: it uses the app's design system (palette, typefaces,
logo) on a question whose answer can be checked.
{{< /alert >}}

## The problem

Jazz is a music its press has documented closely. DownBeat has been published since 1934: album
reviews rated out of five stars, interviews, *Blindfold Tests*, *Critics Poll* and *Readers Poll*
results. Yet for anyone looking for something specific (what a critic thought of an album when it
came out, how a musician's reception changed over twenty years, who won a poll in a given year),
that mass is hard to use: thousands of PDFs, a full-text search that stumbles on OCR, and no way to
ask a numerical question about the ratings.

A general-purpose chatbot doesn't solve it. It answers confidently, including when it makes things
up, and doesn't say where its claims come from. On a subject where names, dates and session
line-ups matter, that rules it out.

I wanted a tool that starts from the archive itself:

- **cited to the page**: every claim points to the passage and the PDF page it comes from;
- **able to stay silent**: a question with a false premise, or with no answer in the archive, must
  get a refusal, not an invention;
- **multilingual**: questions in French over an English corpus;
- **frugal**: the large model only where it helps, the rest served by a small model, a cache or a
  plain query;
- **up without AI**: if the model's API goes down, the app keeps searching and showing passages.

It is a personal tool first (jazz is the other half of this site, see
[the jazz notebook](/en/jazz/)), hosted on my machine. But it is structured to become a B2B SaaS
without a rewrite: record labels, documentary makers, festival programmers, culture journalists,
historians. The name says as much: *jazz* and *quasar*.

## Four pillars

The 25 October specification made an unusual choice for an MVP: three pillars "fairly advanced"
from the start rather than a single polished one. A fourth was specified on 29 October.

| Pillar | What it does | Status on 31 October |
|---|---|---|
| **Ask** | A question → routing → hybrid search → streamed answer, every claim cited `[n]` and clickable to the PDF page | Coded; validated in no-AI mode on the real corpus; synthesis by Claude not yet tested for real |
| **Briefs** | "Prepare a brief on the Chicago scene, 1965-1975" → team of agents → written deliverable, every sentence sourced | Coded, never run with an API key |
| **Insights** | A numerical question → generated and validated SQL → data → chart and written reading | Coded; the review and poll tables are still empty |
| **Discover** | Albums, artists and tracks recommended from the user's tastes, each card explained by a quote from the archive | Specified, not yet coded |

Two cross-cutting spaces complete it: the **Library** (documents, passages, link to the cited page)
and the **Observatory** (latency, cost per use, cache rate, 👍/👎 feedback, evaluation results).

## Where the project stands

{{< timeline >}}

{{< timelineItem icon="check" header="Initial foundation" badge="25 October" subheader="The first three pillars at once" >}}
A monorepo with a Python backend, a Next.js frontend and a Rust extension. Markdown, Wikipedia and
PDF ingestion, hybrid search, router, semantic cache, Briefs pipeline, Text-to-SQL engine, golden
set and Observatory. A fictional sample corpus stands in for the archives during development.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="The real corpus" badge="28 October" subheader="Twelve 2025 issues of DownBeat" >}}
OCR preparation, issue naming recognised, page headers filtered, passages that are too short
dropped: 1,124 pages and 3,381 passages indexed. Search validated in no-AI mode.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Visual identity and specification" badge="28-29 October" subheader="A reference that follows the code" >}}
The eighth-note-quasar logo, palette and typefaces signed off. The specification becomes the
reference for scope, with its decision log. The Discover pillar is specified there.
{{< /timelineItem >}}

{{< timelineItem icon="lightbulb" header="Plug in Claude and measure" badge="Next step" subheader="A baseline in numbers" >}}
Replay the questions that fail on keywords, run the full evaluation: faithfulness, traps, cost and
latency, for the first time on real answers.
{{< /timelineItem >}}

{{< timelineItem icon="list" header="Structured data, catalogue, Discover" badge="Coming" subheader="What unlocks BI and recommendation" >}}
Extract review ratings and poll results, split issues into articles, link reviews and albums to
MusicBrainz, then build the recommendation engine.
{{< /timelineItem >}}

{{< /timeline >}}

## How it works

{{< mermaid >}}
flowchart TD
    subgraph Ingestion
        direction LR
        P["DownBeat PDFs<br/>Wikipedia · Markdown"] --> T["OCR cleanup, chunking, simhash<br/>(Rust, Python fallback)"]
        T --> E["bge-m3 embeddings<br/>local, GPU"]
        E --> DB[("PostgreSQL<br/>pgvector + full text")]
    end
    subgraph Ask
        direction TD
        Q[Question] --> R["Router<br/>Haiku, structured output"]
        R --> C{Semantic<br/>cache}
        C -->|"cosine ≥ 0.95"| A
        C -->|miss| H["Hybrid search<br/>vectors ∪ keywords, RRF"]
        DB --> H
        H --> A["Cited answer [n]<br/>Opus or Haiku by route"]
    end
{{< /mermaid >}}

### Ingestion: the page as the unit of citation

A DownBeat PDF becomes a document, and **the page is the unit of citation**: that is what makes it
possible to open the PDF exactly where the cited passage sits. The publisher's issues carry
embedded text on about 83% of pages; the rest go through `ocrmypdf` in `--skip-text` mode, which
keeps the native text and only OCRs image pages. I tried `--force-ocr`: the file grows 2.3 times
and the resulting text is worse than the publisher's. Full-page ads stay without text, a deliberate
choice for now.

Two filters matter more than they seem. Folios like "12 DOWNBEAT JULY 2025", repeated at the top
of every page, are stripped at extraction: without that, a question about July 2025 pulls up every
page of that issue. And passages shorter than 60 characters are not indexed: they are mostly
captions and layout fragments.

Cleanup, chunking and near-duplicate detection (simhash) run in a Rust extension called from Python
(PyO3). A Python fallback with the same interface exists, and a parity test checks that both
produce the same output. Any change to the algorithm is made in both, or the test fails.

Embeddings come from `BAAI/bge-m3`, locally on the GPU: 1,024 dimensions, multilingual (a question
in French finds a passage in English), and no API cost.

### Ask: route before searching

Not every question deserves the same treatment. A small model (Claude Haiku 5.5, low effort,
structured output validated by Pydantic) first sorts the question into five routes:

| Route | Example | Handling |
|---|---|---|
| `lookup` | "Who plays piano on *Freddie Freeloader*?" | Few passages, small model |
| `semantic` | "What did critics say about *Bitches Brew* when it came out?" | Hybrid search, large model |
| `synthesis` | "Summarise how criticism of Monk changed over twenty years" | Wider search, large model, high effort |
| `bi` | "Average rating of free jazz versus hard bop in the 60s" | Text-to-SQL (Insights pillar) |
| `clarify` | An ambiguous entity with no context | Asks for clarification |

The same call extracts the **exact filters** in the question (year bounds, document types,
authors) and a list of keywords **in English** for full-text search. If the model is unavailable, a
heuristic takes over: regular expressions on years and decades, a few trigger words for BI.

Search is **hybrid**: a vector search (pgvector, HNSW, cosine) and a full-text search (PostgreSQL
`tsvector`) run with the same SQL filters, then their rankings are merged by *Reciprocal Rank
Fusion* (k = 60). RRF only combines ranks, which avoids calibrating two incomparable score scales.
A final pass caps results at three passages per document, so a long article doesn't monopolise the
answer.

The answering model can only cite the passages it is given, and the interface links each `[n]` to
its source. In front of the answer, a Redis **semantic cache** serves questions already asked: if a
past question has an embedding above 0.95 cosine, with the same filters and the same language, the
answer and its citations come back without a model call.

Finally, **degraded mode**: without an API key, or if the API goes down, the app still starts and
returns passages ranked by full-text search. That mode is what validated ingestion of the real
corpus. It also showed its limit: a question like "who won the 2025 Critics Poll?" fails on keywords
alone, which makes it the first test for synthesis.

### Briefs: a team of agents, every sentence sourced

The target use case is a professional who doesn't have time to ask fifty questions: a producer, a
documentary maker, a programmer who wants a written, sourced deliverable. The pipeline chains four
roles:

{{< steps >}}
{{< step number="1" title="Planner" >}}
A structured output: a title, sections, and for each section two to four precise research
questions.
{{< /step >}}
{{< step number="2" title="Researcher" >}}
An agentic loop (the Anthropic SDK's *tool runner*, fourteen iterations at most) with three tools:
hybrid search, reading a whole document from one passage, and an SQL query on the metadata, which
goes through the same validation as the Insights pillar. Every passage seen gets a short identifier
`[S-xxxxxxxx]`, derived from the passage's real identifier in the database.
{{< /step >}}
{{< step number="3" title="Writer" >}}
It writes the brief in Markdown from the researcher's notes, every claim followed by its `[S-…]`
reference, copied verbatim.
{{< /step >}}
{{< step number="4" title="Critic" >}}
It checks every reference: if it is missing from the list of passages seen, or doesn't support the
sentence, it is corrected or the claim is removed.
{{< /step >}}
{{< /steps >}}

Since every reference points to a real passage, the final deliverable keeps clickable links to the
source page. Each step is logged with the brief. The original plan named LangGraph or CrewAI; the
SDK's *tool runner* is enough for a loop this size, and keeps the whole orchestration readable in a
single file.

### Insights: generated SQL treated as untrusted input

The question "show me how the average rating of free jazz compares with hard bop through the 60s"
isn't answered with passages, but with a computation over the metadata (ratings, years, genres,
labels). The large model produces a structured plan: the SQL query and the shape of the chart. That
SQL is then treated like any input from outside:

- parsed by `sqlglot`: **a single statement**, and it must be a `SELECT` (CTEs and `UNION` allowed);
- any `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `ALTER` or `SET` node, even nested, is
  rejected;
- the tables read must be on an **allow-list** of five analytical tables;
- a `LIMIT 500` is added, or enforced if it was larger;
- execution goes through a **read-only** PostgreSQL role, with an eight-second
  `statement_timeout`.

The first two safeguards catch the model's mistakes; the last two hold even if validation let
something through. The chart isn't code either: it is a Plotly specification in JSON rendered by
the browser, which applies the palette. The original plan called for a *Code Interpreter* that
would have written and run Python; I set it aside, because running generated code opens a risk
surface without adding anything for standard charts. A small model then writes the reading of the
result.

### Evaluate and observe

The golden set holds 17 cases: 10 simple factual questions, one question that requires connecting
several sources, and **6 traps**. A trap asks a question with a false premise ("On which album did
John Coltrane and Jimi Hendrix record together?", "Which Grammy did Charlie Parker win in 1953?"):
the only correct answer is to refuse, and some phrasings are forbidden in the answer.

The evaluation doesn't just produce a score: it has **blocking gates**.

| Gate | Required value |
|---|---|
| Traps passed (`refusal_trap_pass_rate`) | 100% |
| Citation coverage on factual questions | 100% |
| Faithfulness to sources, scored by a Haiku judge | ≥ 95% |
| Right document retrieved (`retrieval_passk`) | ≥ 85% |

A single failed trap fails the evaluation, whatever the rest. On the observability side, every
model call is logged in the database with its tokens, cache use and actual cost; every question with
its route, latency and the user's 👍/👎 feedback. The Observatory shows it all.

## What changed from the original plan

The project started from a design note written before any code (`plan.md` in the repository). The
specification records every departure from it.

| Topic | Original plan | Choice made | Reason |
|---|---|---|---|
| Vector store | Qdrant or GCP Vector Search | pgvector in PostgreSQL | One service, exact SQL filters in the same query; enough up to several million passages |
| Models | Llama 3 8B as small, Gemini 1.5 Pro or GPT-4o as large | Claude Haiku 5.5 and Opus 5.5 | One provider, structured outputs, prompt caching |
| Orchestration | LangGraph or CrewAI | Anthropic SDK *tool runner* | A loop this size doesn't need a framework |
| Charts | Code Interpreter | Plotly JSON specification | No generated code executed |
| Evaluation | RAGAS | Home-made golden set, Haiku judge, blocking gates | Jazz-specific traps, and a failure that blocks |
| Observability | LangSmith or Datadog | `llm_calls` and `queries` tables | Enough locally; an external tool can still be plugged in |

## The data, and what I don't do with it

The twelve 2025 issues come from my personal subscription, for private use: they are neither
published nor redistributable, and the repository doesn't contain them. A sample corpus is used for
development: its discographic facts are accurate, but the ratings and critical phrasing are made up
and flagged as such (`source: sample`), to be removed once the real archives are enough.

For the historical archives, I catalogued the 1,280 DownBeat PDFs (1937-1999) hosted by
worldradiohistory.com. The site has removed its public index, blocks clients that aren't browsers
and disallows AI crawlers in its `robots.txt`. So I didn't write a downloader: acquisition will be
done by hand or with the site owner's agreement.

## The numerical targets, and where they stand

The plan sets precise targets. None is measured yet, and one of them is probably not achievable as
stated.

| Target | Goal | Status on 31 October |
|---|---|---|
| No claim without a source | Mandatory citations, critic for briefs | Implemented, to be checked by the evaluation |
| Anti-hallucination traps | 100% | Implemented, no first measurement |
| Working without AI | Search and passages without an API key | Validated on the real corpus |
| Latency | p95 < 1.5 s | Not measured |
| Cost | < $0.01 per complex query | Estimated at $0.04 to $0.15 by route: not met on Opus |

The cost estimate is based on prompt sizes: under a tenth of a cent for a `lookup`, four to six
cents for a `semantic` question, ten to fifteen for a synthesis, fifty cents to a dollar and a half
for a brief. The levers are known (low effort on the `semantic` route, a mid-sized model as the
large one, set by an environment variable), but I'd rather decide on them from a real evaluation
than from an estimate.

## What comes next

The specification's roadmap is ordered by dependencies:

1. **Plug in Claude and measure**: a first numerical baseline for faithfulness, traps, cost and
   latency.
2. **Fill in reviews and polls**: in the PDFs, ratings are star glyphs in a symbol font (`HHHH` for
   four stars), extractable without a model along with the artist, album, label and author. That
   will give the Insights pillar real data.
3. **Split issues into articles** and extract the entities mentioned (artists, albums, tracks), for
   complete citations with title and author.
4. **Link the archive to MusicBrainz**: each review attached to its album and its musicians, which
   serves both BI and recommendation.
5. **Discover**: a layered recommendation engine, from content (a profile built from embeddings,
   diversity through MMR) to the graph (personalised PageRank over artists, albums and sidemen),
   then behaviour once there are users. The archive isn't what gets recommended but the evidence:
   a card without a supporting quote isn't shown.

The path to SaaS (authentication, organisations, quotas, billing, deployment) comes after. The
columns and the cost tracking are designed to take it without a rewrite, but the criterion for
committing to it is simple: the tool has to convince me first.

## What I take from it so far

- **The no-AI mode was useful before the AI.** I had planned it as a production safeguard; above
  all, it validated ingestion of the real corpus and surfaced the questions that genuinely need the
  model.
- **Cleaning the PDFs weighs as much as search.** Repeated folios and layout fragments degraded
  results more than any tuning of the fusion.
- **Writing down departures from the plan as they happen.** Six technical choices changed from the
  original note; the decision log keeps track of why, which also helped me write this page. The
  project follows [my way of working with Claude Code](/en/posts/claude-code-methode-revisee/).
