---
title: "Kwak Finance: a household's budget and net worth, self-hosted"
date: 2026-10-08
draft: false
nature: "produit"
description: "A self-hosted web app to track a household's budget and net worth, without the data ever leaving home. Under development: the budget module has shipped, and so have budget plans and their review."
summary: "Self-hosted web app for household budgeting and net worth. Bank import, categorisation, budget matrix, budget plans by period with a review, projection and money flows; net worth, forecasting and local AI come next."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "claude code"]
featureImage: "carte-en.png"
showTableOfContents: true
---

{{< lead >}}
Know where the household's money goes, month after month, and what its assets are worth, without
handing bank statements to an online service. Everything runs on a machine at home.
{{< /lead >}}

{{< fiche-projet
    statut="In development · phase 1 shipped, phase 2 under way"
    periode="Since October 2026"
    role="Solo: specifications, architecture, development, operations"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, PostgreSQL 17, React 19, TypeScript, Tailwind, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/kwak-finance" >}}

{{< stats >}}
{{< stat value="53" label="merged pull requests" >}}each one blocked until CI is green{{< /stat >}}
{{< stat value="531" label="automated tests" >}}including 35 property tests on financial invariants{{< /stat >}}
{{< stat value="8" label="architecture decisions" >}}written down, with the rejected alternatives{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Work in progress.** This page describes the repository as of 11 October 2026. The figures above
are counted in the code, and will be updated with each phase shipped.
{{< /alert >}}

{{< alert icon="image" >}}
**Every screenshot shows fictional data.** They come from a demo instance, filled with an
invented household (Camille and Sam, four accounts, a year of generated transactions). No amount,
label or balance comes from real accounts. The interface is shown in French.
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

{{< timelineItem md="true" icon="code" header="Phase 2 · Full budget" badge="Under way" subheader="What makes it an everyday tool" >}}
**Shipped:** budget plans by quarter, semester or year, with their review (end-of-plan
projection, drifting categories, money flows, plan comparison); the household's joint account and
per-scope views; an in-app guide; a second bank format. **Left:** recurring expenses, splitting
shared expenses ("who owes what to whom"), reports by period.
{{< /timelineItem >}}

{{< timelineItem icon="scale-balanced" header="Phase 3 · Net worth" badge="Upcoming" subheader="Assets and liabilities" >}}
Brokerage accounts, life insurance, crypto-assets, real estate, loans with amortisation schedules,
depreciated use assets, daily market prices and net-worth history.
{{< /timelineItem >}}

{{< timelineItem icon="lightbulb" header="Phase 4 · Analytics and data science" badge="Upcoming" subheader="Where my day job comes in" >}}
Cash-flow forecasting, evaluated by rolling-origin backtesting against a naive model, and
Monte Carlo net-worth simulation (allocation scenarios, retirement projection).
{{< /timelineItem >}}

{{< timelineItem icon="wand-magic-sparkles" header="Phase 5 · Local generative AI" badge="Upcoming" subheader="Without anything leaving the machine" >}}
An assistant that answers natural-language questions about your own data, using a local language
model (Ollama), restricted to a read-only analytics view.
{{< /timelineItem >}}

{{< /timeline >}}

## What works today

### One household, several accounts, three points of view

The owner creates the household and invites the other members with a single-use link; there is
no public sign-up. Login with a password (argon2id) and a mandatory TOTP code, with recovery codes
and rate limiting.

Each account has a visibility: **private** (its holder only), **shared** (visible to the whole
household, but still its holder's) or **joint** (the common account that pays rent and groceries,
nobody's own). Every aggregated view can then be read in three scopes: the whole **household**,
the **joint accounts**, or **just mine**.

In a narrower scope, a transfer crossing the scope's edge is not neutral: each member's share
paid into the joint account shows up as money "paid in from other accounts", and the joint
account's savings stay right. At household level, the same transfers cancel out.

### Importing a statement without breaking anything

You drop the bank's CSV export (two banks supported, with three layouts): the app shows a
**preview** before writing anything. Each transaction gets a fingerprint, so **re-importing the
same file changes nothing**, and a file that overlaps the previous one only adds what is missing.
After the import, the computed balance is checked against the bank's, and any import can be
rolled back.

![Import preview: eleven new transactions, three already imported](import-apercu.webp "Previewing a statement that overlaps the previous one: the three late-September transactions are recognised and skipped. Fictional data.")

### Categorise once, never again

A two-level category tree, named in the household's language, and ordered **rules** ("label
contains …", amount, account) applied on every import and every manual entry. You categorise one
transaction, a batch, or create a rule from a transaction with the "Rule" button. Whatever the
rules did not recognise stays flagged "to categorise".

![The transaction list, with two transactions to categorise](operations.webp "Transactions across the whole household: the category is picked on the row, and the two transactions no rule recognised are flagged. Fictional data.")

![Categorisation rules](regles.webp "Rules, applied in order: the first one that matches sets the category. They can be re-applied to past transactions. Fictional data.")

Transfers between your own accounts are detected, suggested, then linked: they leave spending and
income, and each row names the other account.

![Internal transfers linked between the household's accounts](virements.webp "Linked transfers: savings into the passbook account, contributions to the joint account. Neither spending nor income. Fictional data.")

### The month at a glance

Spending, income, net cash flow and savings rate, compared with the previous month and with the
12-month average, along with the number of transactions to categorise. Below: spending by
category, the month's cumulative spending against the budget pace, and spending and income over
the last twelve months. A "Getting started" checklist guides the first steps, and an in-app guide
describes every page.

![The October overview](vue-ensemble.webp "The overview at household level: the month's indicators, spending by category, cumulative spending against the budget and twelve months of history. Fictional data.")

### Budget plans by period

A monthly target per category does not survive real life: a new job, a raise, a new fixed cost.
So targets live in **plans** covering a quarter, a semester or a year. Within a plan's envelope, a
cheaper month offsets a dearer one, which replaces the surplus rollover planned at first.

A new plan starts from the previous one's targets. It can be edited until the end of its first
month; after that, you **close it early**, with a reason, and a replacement plan covers the rest
of the period. The closed plan keeps its targets and is reviewed over the months it covered. Each
target can also say who pays: the joint account or personal ones.

The budget matrix remains the central view: one row per category, one column per month, the
plan's target first. Each cell shows the spending and the gap to the target of the plan covering
that month, coloured by whether it is under target, within the ±5% band, or above.

![The budget matrix and the current quarter's plan](matrice.webp "The Budget page: the quarter's plan, its targets and who pays them, then the matrix. Green: under target; grey: within ±5%; burnt orange: above. Fictional data.")

### The plan review

This is the newest part, and the one closest to my day job. During a plan, the review says where
things stand: share of time elapsed, spent, expected to date, and above all a **projection** at
the end of the plan. Categories projected above their envelope are listed as **drifting**, largest
first. Once the plan is over, the same screen gives the final result, the actual savings and the
planned savings.

![Summary of the running plan and a drifting category](bilan-synthese.webp "Summary of the current quarter on 12 October: restaurants are projected €88 over their envelope. Fictional data.")

The projection is not a simple rule of three. Completed months count as spent; the current month
and the following ones count for at least their target, or for the completed months' average if
it is higher. So rent paid on the 1st is not taken for a drift, while spending above the target
shows at once. The phase 4 forecasting can replace this projection.

Two charts follow: the projected gap by category, in the matrix's colours, and cumulative spending
day by day against the envelope line, in total or for one category.

![Projected gap by category and cumulative spending](bilan-graphiques.webp "Left, the projected end-of-plan gap by category; right, cumulative spending against the envelope line. Fictional data.")

The flow diagram (Sankey) shows where the plan's money comes from and where it goes: income and
transfers paid in on the left, an "available" node in the middle, then spending by category,
savings and the unallocated rest on the right. Both sides always add up to the same total.

![The plan's money flows](bilan-flux.webp "The plan's flows: salaries on the left, spending, savings and the unallocated rest on the right. Categories can be broken down into subcategories. Fictional data.")

Finally, a comparison puts two plans side by side, as monthly averages so that plans of different
lengths stay comparable.

![Comparing the summer plan with the current one](bilan-comparaison.webp "The summer quarter against the current quarter: targets, average monthly spending and change. Fictional data.")

### Verified backups

A full backup every night, checked before it is kept, with rotation (7 days, 4 weeks, 12 months)
and a written restore procedure.

## How it is built

### A simple architecture, designed for what comes next

Everything starts from a single `docker compose up`: a Caddy proxy with TLS on the local network,
a FastAPI API, a PostgreSQL database and a backup service. The React interface is served from the
same origin as the API, which allows cookie sessions with no CORS configuration.

On the Python side, the code is split into packages with a strict rule: `kwak_core` holds **all
the business rules** (amounts, balances, deduplication fingerprints, categorisation rules, plans,
projection, flows, indicators) and depends on nothing. It is tested without a database. The API
and the future analytics layer depend on it, never the other way round: a given figure has only
one definition.

The contract between the API and the interface is the OpenAPI schema: the TypeScript client is
**generated** from it, never written by hand. CI fails if someone forgets to regenerate it.

### Money does not tolerate "roughly"

Amounts are exact decimals (`Decimal` in Python, `NUMERIC` in the database), never floats. And the
rules that must always hold are written in the specifications, then checked by **property tests**
(Hypothesis): instead of a few hand-picked examples, the test generates hundreds of cases and
looks for the one that breaks the rule.

| Invariant | What the test checks |
|---|---|
| Balance | An account's balance equals its opening balance plus its transactions, in any order |
| Idempotent import | Importing the same file twice changes nothing |
| Transfers | A linked transfer nets to zero across the two accounts and is never reused |
| Matrix | The total row equals the sum of the categories plus "to categorise" |
| Plans | Two plans never overlap, and an envelope equals the monthly target times the number of months |
| Flows | Both sides of the flow diagram add up to the same total |
| Bank format | Everything the bank writes is read back exactly |
| Visibility | Another member only sees shared and joint accounts |

API tests run against a **real PostgreSQL** started in a container, never against a mocked
database.

### Decisions written down

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

Deviations from the original plan are logged in the `README` too, to the day.

### Built with an agent, under control

The project applies the method described in
[my article on Claude Code]({{< relref "/posts/claude-code-data-science" >}}), with one starting
rule: **what must always be true becomes a hook**, not an instruction.

- **I am the only commit author.** The agent prepares the change and proposes the message; a Git
  hook and CI reject any message that is not in Conventional Commits format or that adds a
  co-author.
- **Real data is out of reach.** A hook blocks any write into `data/` and any read of secrets; the
  test files are synthetic, and only reproduce the bank's layout.
- **"Done" means "verified".** When the agent has changed code, a hook re-runs lint, types and
  tests, and keeps it from wrapping up while they fail.
- **A cold review.** A read-only subagent reviews each diff before the pull request: correctness,
  invariants, tests, one topic per change.
- **One PR per topic.** Every change goes through a short branch and a pull request, merged only
  once every check is green (lint, strict typing, tests, Docker image builds).
- **Specification first.** Budget plans started with a documentation-only PR that set the rules
  (periods, early close, projection) before any code.

## What got stuck

- **The real bank format.** The specifications planned user-configurable import profiles. Banks
  actually export quite different layouts, sometimes two for the same bank depending on the
  account type. I chose to code one format per layout, each tested on a synthetic file copying its
  exact structure. A generic profile will come for other banks.
- **A projection that was too naive.** The first plan projection was linear: spent divided by the
  share of time elapsed. On the 3rd of the month, rent already paid showed up as a huge drift. It
  now starts from each remaining month's expected spending.
- **The joint account.** As long as everything was "private" or "shared", a transfer into the
  joint account made no sense in a personal view. It took a third visibility, then judging each
  scope on its own transfers and its own targets.
- **Moving tooling.** The TypeScript client generator needs the JavaScript compiler API, which
  TypeScript 7 no longer exposes: it runs separately, with TypeScript 6.
- **What does not survive the disk.** A backup on the same disk does not protect against a disk
  failure. Off-machine copies remain manual, and that is an open question.

## What's next

Phase 2 ends with recurring expenses, splitting shared expenses and reports by period. Phase 3
will add net worth. But phase 4 is the one I care about most: cash-flow forecasting treated as a
real time-series problem, with a protocol written in advance, a backtest with no leakage from the
future, and a naive model to beat before anything else. It already has a first customer: the plan
review's projection. This page will be updated with each phase shipped.

## Try it

```bash
git clone https://github.com/gwils28/kwak-finance
cd kwak-finance
make setup        # dependencies and Git hooks
make check        # everything CI runs
make up           # the full stack on https://localhost:8443
```

The steps to create the owner account and the encryption key are in the `README`, and the app
itself offers, at the bottom of every page, a guide to start, stop and update it.
