---
title: "Kwak Finance: a household's budget and net worth, self-hosted"
date: 2026-10-08
draft: false
nature: "produit"
description: "A self-hosted web app to track a household's budget and net worth, without the data ever leaving home. Under development: the budget module has shipped."
summary: "Self-hosted web app for household budgeting and net worth. The budget module has shipped (bank import, categorisation, budget matrix, indicators); net worth, forecasting and local AI come next."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "claude code"]
featureImage: "cover.png"
showTableOfContents: true
---

{{< lead >}}
Know where the household's money goes, month after month, and what its assets are worth, without
handing bank statements to an online service. Everything runs on a machine at home.
{{< /lead >}}

{{< fiche-projet
    statut="In development · phase 1 of 5 shipped"
    periode="Since October 2026"
    role="Solo: specifications, architecture, development, operations"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL 17, React 19, TypeScript, Tailwind, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/kwak-finance" >}}

{{< stats >}}
{{< stat value="37" label="merged pull requests" >}}each one blocked until CI is green{{< /stat >}}
{{< stat value="380" label="automated tests" >}}including 25 property tests on financial invariants{{< /stat >}}
{{< stat value="8" label="architecture decisions" >}}written down, with the rejected alternatives{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Work in progress.** This page describes the repository as of 8 October 2026. The figures above
are counted in the code, and will be updated with each phase shipped.
{{< /alert >}}

## The problem

Consumer budgeting apps almost all ask for the same thing: access to your bank accounts, and
hosting your financial history on their servers. Spreadsheets ask for nothing, but get abandoned
after three months: re-typing, copying and categorising by hand costs too much.

I wanted a tool in between:

- **private by design**: the data stays on a household machine, with no telemetry and no
  third-party service;
- **fed effortlessly**: you import the bank's CSV export, and expenses sort themselves into their
  categories;
- **exact to the cent**: every total must be recomputable from the transactions;
- **ready for data science**: cash-flow forecasting, net-worth simulation and a natural-language
  assistant must be addable without rebuilding the foundations.

It is also my first product: a project meant to last, not a throwaway experiment. So it is where
I apply [my way of working with Claude Code]({{< relref "/posts/claude-code-data-science" >}}).

## Where the project stands

{{< timeline >}}

{{< timelineItem icon="check" header="Phase 0 · Foundations" badge="Shipped" subheader="Technical groundwork" >}}
Specifications, architecture and decisions written before the first line of code. Repository,
tooling, continuous integration, Docker Compose stack, Claude Code configuration and a visual
identity borrowed from this blog.
{{< /timelineItem >}}

{{< timelineItem icon="check" header="Phase 1 · Budget" badge="Shipped" subheader="The core of the product" >}}
Two-factor authentication, household and invitations, accounts, bank import, manual entry,
rule-based categorisation, internal transfers, budget matrix, spending indicators and automatic
backups. Interface in French and English.
{{< /timelineItem >}}

{{< timelineItem icon="code" header="Phase 2 · Full budget" badge="Next" subheader="What makes it an everyday tool" >}}
Rolling a month's surplus over to the next, detecting recurring expenses, splitting shared
expenses ("who owes what to whom"), reports by period.
{{< /timelineItem >}}

{{< timelineItem icon="scale-balanced" header="Phase 3 · Net worth" badge="Upcoming" subheader="Assets and liabilities" >}}
Brokerage accounts, life insurance, crypto-assets, real estate, loans with amortisation schedules,
depreciating personal assets, daily market prices and net-worth history.
{{< /timelineItem >}}

{{< timelineItem icon="lightbulb" header="Phase 4 · Analytics and data science" badge="Upcoming" subheader="Where my day job comes in" >}}
Cash-flow forecasting, evaluated by rolling-origin backtest against a naive model, and Monte Carlo
net-worth simulation (allocation scenarios, retirement projection).
{{< /timelineItem >}}

{{< timelineItem icon="wand-magic-sparkles" header="Phase 5 · Local generative AI" badge="Upcoming" subheader="Without anything leaving the machine" >}}
An assistant that answers questions about your own data in natural language, using a local
language model (Ollama), restricted to a read-only analytical view.
{{< /timelineItem >}}

{{< /timeline >}}

## What works today

{{< steps >}}
{{< step number="1" title="A household, accounts, permissions" >}}
The owner creates the household and invites the other members through a single-use link; there
is no public sign-up. Each account is **private** or **shared**, and everyone only sees what
concerns them. Login with a password (argon2id) and a mandatory TOTP code, with recovery codes
and rate-limited attempts.
{{< /step >}}
{{< step number="2" title="Import a statement without breaking anything" >}}
You drop in the bank's CSV export: the app shows a **preview** before writing anything (rows read,
duplicates detected, errors with their line number). Each transaction gets a fingerprint, so
**re-importing the same file changes nothing**, and a file that overlaps the previous one only adds
what is missing. Any import can be undone.
{{< /step >}}
{{< step number="3" title="Categorise once, never again" >}}
A two-level category tree, and ordered **rules** ("the label contains …", amount, account) applied
on every import. You categorise one transaction, a batch, or create a rule from a transaction.
Transfers between your own accounts are suggested, linked, and excluded from spending and income.
{{< /step >}}
{{< step number="4" title="The budget matrix" >}}
The central view: one row per category, one column per month, the monthly target up front. Each
cell gives the spending and the gap to the target, in euros and as a percentage, coloured by
whether you are under the target, within the ±5% tolerance or above it. An "uncategorised" row
always stays visible, so that no total is ever silently wrong.
{{< /step >}}
{{< /steps >}}

![The Kwak Finance budget matrix over eleven months](cover.png "The budget matrix, in dark mode, on a demo household: fictional data, French interface. Green: under target; grey: within ±5%; burnt orange: above.")

{{< steps >}}
{{< step number="5" title="The month's indicators" >}}
Spending, income, balance and savings rate, compared with the previous month and the twelve-month
average; the top five categories; charts by category, over twelve months, and cumulative against
the budget line.
{{< /step >}}
{{< step number="6" title="Verified backups" >}}
A full backup every night, checked before being kept, with rotation (7 days, 4 weeks, 12 months)
and a written restore procedure.
{{< /step >}}
{{< /steps >}}

## How it is built

### A simple architecture, designed for what comes next

Everything starts from a single `docker compose up`: a Caddy proxy with TLS on the local network,
a FastAPI API, a PostgreSQL database and a backup service. The React interface is served from the
same origin as the API, which allows cookie sessions with no CORS configuration.

On the Python side, the code is split into packages with a strict rule: `kwak_core` holds **all
the business rules** (amounts, balances, deduplication fingerprints, categorisation rules, budget,
indicators) and depends on nothing. It is tested without a database. The API and the future
analytics layer depend on it, never the other way round: any given figure has exactly one
definition.

The contract between the API and the interface is the OpenAPI schema: the TypeScript client is
**generated** from it, never written by hand. CI fails if someone forgets to regenerate it.

### Money doesn't tolerate "roughly"

Amounts are exact decimals (`Decimal` in Python, `NUMERIC` in the database), never floats. And
the rules that must always hold are written in the specifications, then checked by **property
tests** (Hypothesis): instead of a few hand-picked examples, the test generates hundreds of cases
and looks for the one that breaks the rule.

| Invariant | What the test checks |
|---|---|
| Balance | An account's balance equals its opening balance plus its transactions, in any order |
| Idempotent import | Importing the same file twice changes nothing |
| Transfers | A linked transfer cancels out between the two accounts and is never reused |
| Matrix | The total row equals the sum of the categories plus "uncategorised" |
| Bank format | Everything the bank writes is read back exactly |
| Visibility | Another member only sees shared accounts |

API tests run against a **real PostgreSQL** started in a container, never against a mocked
database.

### Written decisions

Every structural choice gets a decision record (ADR), dated, with its rejected alternatives. A
decision that changes gets a new record; the old one is never rewritten.

| Decision | Rather than |
|---|---|
| Self-hosting with Docker Compose | Cloud hosting: needless cost and exposed financial data |
| FastAPI, SQLAlchemy 2, Alembic | Django: heavier, and the admin interface is of no use |
| PostgreSQL, then DuckDB for analytics | SQLite alone: concurrent writes, no vector extension |
| Euro only | Full multi-currency accounting, too costly for a single real need |
| Server sessions and mandatory TOTP | JWT tokens, hard to revoke |
| Local language model (Ollama) | A cloud API: the data must never leave the machine |

Deviations from the initial plan are logged in the `README` too, down to the day.

### Built with an agent, under control

The project applies the method described in
[my post on Claude Code]({{< relref "/posts/claude-code-data-science" >}}), with one founding rule:
**whatever must always be true becomes a hook**, not an instruction.

- **I am the sole author of the commits.** The agent prepares the change and proposes the
  message; a Git hook and CI reject any message that isn't in Conventional Commits format or that
  adds a co-author.
- **Real data is out of reach.** A hook blocks any write to `data/` and any read of secrets; test
  files are synthetic, and only reproduce the bank's layout.
- **"Done" means "verified".** When the agent has changed code, a hook re-runs lint, type checks
  and tests, and stops it from wrapping up while they fail.
- **A cold review.** A read-only sub-agent reviews every diff before the pull request:
  correctness, invariants, tests, one topic per change.
- **One PR per topic.** Every change goes through a short-lived branch and a pull request, merged
  only once all checks are green (lint, strict typing, tests, Docker image builds).

## What got stuck

- **The real bank format.** The specifications planned import profiles configurable by the user.
  The bank actually exports two different layouts depending on the account type. I chose to code
  one format per layout, each tested on a synthetic file that copies its exact structure. A
  generic profile will come for other banks.
- **An account's opening date.** Rows dated before the opening date were dropped without
  explanation. The import preview now flags them, and offers to move the date.
- **Moving tooling.** The TypeScript client generator needs the JavaScript compiler API, which
  TypeScript 7 no longer exposes: it runs separately, with TypeScript 6.
- **What doesn't survive the disk.** A backup on the same disk doesn't protect against a disk
  failure. The off-machine copy is still manual, and that is an open question.

## What's next

Phase 2 will make it an everyday tool (recurring expenses, surplus roll-over, expense splitting).
Phase 3 will add net worth. But phase 4 is the one I care about most: cash-flow forecasting
treated as a real time-series problem, with a protocol written in advance, a backtest with no
look-ahead leakage and a naive model to beat before anything else. This page will be updated
with each phase shipped.

## Try it

```bash
git clone https://github.com/gwils28/kwak-finance
cd kwak-finance
make setup        # dependencies and Git hooks
make check        # everything CI runs
make up           # the full stack on https://localhost:8443
```

The steps to create the owner account and the encryption key are in the `README`.
