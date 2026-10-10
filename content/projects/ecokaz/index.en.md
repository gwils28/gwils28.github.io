---
title: "Ecokaz: a household's energy and carbon, measured rather than estimated"
date: 2026-10-10
draft: true
nature: "produit"
description: "A web app to track a household's electricity, gas, water and fuel use, in units, euros and kgCO₂e, with an AI coach that explains but never computes. Under development: the foundation is in place."
summary: "Household energy and carbon copilot: actual electricity, gas, water and fuel use, in units, euros and kgCO₂e, with an AI coach that explains. The foundation has shipped; the domain and the Linky import come next."
tags: ["python", "fastapi", "postgresql", "react", "typescript", "docker", "llm", "claude code"]
featureImage: "carte.png"
showTableOfContents: true
---

{{< lead >}}
Knowing what the household actually uses, in kWh, euros and CO₂, week after week, and being
warned when something drifts. With figures that can always be checked.
{{< /lead >}}

{{< fiche-projet
    statut="Under development · lot 0 of 9 shipped"
    periode="Since October 2026"
    role="Solo: scoping, architecture, development"
    stack="Python 3.13, FastAPI, SQLAlchemy 2, Alembic, PostgreSQL 17, React 19, TypeScript, Vite, Tailwind, Docker Compose, Caddy, GitHub Actions"
    code="https://github.com/gwils28/Ecokaz" >}}

{{< stats >}}
{{< stat value="9" label="planned lots" >}}each closed by a proof, not an impression{{< /stat >}}
{{< stat value="17,500" label="readings a year" >}}the Linky load curve at 30-minute resolution{{< /stat >}}
{{< stat value="0" label="figures computed by the LLM" >}}the coach calls tested functions, then comments{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

{{< alert icon="circle-info" >}}
**Work in progress.** This page describes the repository as of 10 October 2026: the plan is
approved and the foundation is in place. It will be updated with every lot shipped.
{{< /alert >}}

## The problem

The broad strokes of a household's carbon footprint are well known: heating, the car, food. But
online calculators work from self-reported answers ("roughly how many kilometres a year?") and
give a single figure, once. Nothing then tells you whether a change of habit actually lowered
consumption, or why this month's bill went up.

Yet the data exists: the Linky meter measures electricity every half hour, and gas and water
meters take ten seconds to read. I wanted a tool that starts from these **actual measurements**:

- **in three units at once**: the quantity used, its cost, and its footprint in kgCO₂e;
- **compared** with the self-reported baseline, to see the gap between what we believe and what
  we measure;
- **monitored**: an alert when consumption drifts away from its usual level, with the method
  explained;
- **commented on** by a coach that answers questions in natural language, without ever making up
  a figure.

The success criterion for the first version is deliberately concrete: opening it every week for
two months, and having made at least one decision because of it.

## Four non-negotiable principles

### The LLM never computes

A language model that announces "you used 412 kWh this month" can be wrong, and nobody will
notice. In Ecokaz, **every figure comes from a tested Python function**: conversions, costs,
emissions, anomalies, goals. The coach (deterministic rules, then Mistral) calls these functions
as tools and only explains their result. An evaluation set will be written **before** the
prompts, to check that no figure is hallucinated.

### Sourced, versioned emission factors

No emission factor, price or conversion coefficient is hard-coded. They live in a single table,
each value with its source (ADEME's Base Empreinte) and its validity period. Every kgCO₂e shown
can be traced back to its source, and an updated factor does not rewrite the past.

### One data source, one adapter

The Conso API (which relays Enedis data), the CSV export from the customer area, manual gas,
water and mileage readings: every source implements the same interface and yields **normalised
readings**. Adding a source touches neither storage nor the dashboard.

### A simple baseline before a model

Anomalies will first be detected with a simple, explainable statistical method: a robust
day-of-week baseline. A machine-learning model will only replace it if it does better, on a
protocol written in advance. It is the same discipline as in my time-series work: beat the naive
model first.

## The roadmap

Development is split into nine lots. None is declared done without a proof written in advance.

| Lot | Content | Expected proof |
|---|---|---|
| 0 ✅ | Foundation: repository, tooling, Docker Compose, CI, Claude Code setup | `docker compose up` and green CI |
| 1 | Domain: conversions, euros, CO₂e, readings → consumption | green property tests (non-negativity, additivity, decreasing index rejected) |
| 2 | Electricity: Enedis CSV import, Conso API connector, daily sync | my real load curve imported, quality checks passed (gaps, duplicates, units) |
| 3 | Authentication, UI, electricity dashboard | screenshots on desktop and mobile, light and dark theme |
| 4 | Deployment on a server in Europe | HTTPS URL, backup restore tested |
| 5 | Gas, water, car, tariffs, multi-category dashboard | totals consistent with my bills, gap explained |
| 6 | Self-reported footprint, compared with the measured one | result checked against Nos Gestes Climat on my profile |
| 7 | Goals and spike detection | tests on synthetic series: injected spike detected, flat series without false alarm |
| 8 | Coach: rules, then Mistral tool calling | versioned evaluation set, no hallucinated figure |

Deployment comes early on purpose (lot 4): a tool that is not used every day cannot meet its
success criterion.

## How it is built

### A modular monolith

A FastAPI backend split into modules: `domain` for pure computations, `sources` for the
adapters, `coach` for the rules and the Mistral client, `api` for the routes, `jobs` for the
daily sync. Business rules live in a package with no I/O at all, tested with property-based
tests (Hypothesis). On the other side, a React UI reuses this blog's visual identity, served
behind Caddy.

A few deliberately plain choices:

- **PostgreSQL without a time-series extension.** At 30-minute resolution, electricity is about
  17,500 points a year: a regular database is more than enough.
- **No task queue.** The daily sync runs on an in-process scheduler, without Celery or Redis.
- **Exact decimals.** Quantities and amounts are `Decimal` / `NUMERIC`, never floats; readings
  are half-open intervals in UTC, and a meter index that decreases is rejected, not silently
  fixed.
- **No invented split.** Two gas readings three weeks apart give consumption over three weeks,
  without spreading it day by day.

### A foundation inherited from Kwak Finance

The foundation comes from [Kwak Finance](/en/projects/kwak-finance/), my other product: same
conventions, same hooks, same Claude Code setup. Starting from a proven base saved time, but the
review uncovered inherited defects: migrations saw no model, the API container never applied
them, and the UI received the database credentials. All are fixed, and recorded in the plan's
deviation log.

### Built with an agent, under control

Like Kwak Finance, the project applies the method described in
[my post on Claude Code](/en/posts/claude-code-data-science/): whatever must always hold becomes a
hook, not an instruction.

- **I am the sole author of every commit.** The agent prepares the change and proposes a
  Conventional Commits message; a Git hook and CI reject any other format and any co-author.
- **Household data is out of reach.** A hook makes the `data/` folder read-only and the secrets
  unreadable; test fixtures are synthetic.
- **"Done" means "verified".** The agent cannot finish while lint, type checks and tests fail.
- **A cold review.** A read-only subagent reviews every diff and reports correctness issues only.

## What's next

Lot 1 lays down the core of the domain, tests first. Lot 2 will plug in my real Linky load
curve, and that is where the project gets interesting: real time series, with their gaps, their
duplicates and their clock changes. This page will be updated with every lot shipped.

## Try it

```bash
git clone https://github.com/gwils28/Ecokaz
cd Ecokaz
cp .env.example .env   # then change the values
make setup             # dependencies and Git hook
make check             # everything CI runs
make up                # the full stack on https://localhost:8453
```
