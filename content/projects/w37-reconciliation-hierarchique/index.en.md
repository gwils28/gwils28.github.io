---
title: "Hierarchical reconciliation: MinT from scratch and éCO2mix"
date: 2026-10-02
draft: false
nature: "labo"
description: "One week to master hierarchical reconciliation: MinT rewritten in NumPy, its limits measured, and a mini-project on French grid data where bottom-up wins."
summary: "MinT rewritten from scratch, its assumptions tested one by one, and an éCO2mix mini-project (12 regions → France) where bottom-up beats the reference method."
tags: ["forecasting", "hierarchical reconciliation", "MinT", "python", "time series", "éCO2mix"]
featureImage: "cover.png"
showTableOfContents: true
---

{{< lead >}}
Understand hierarchical reconciliation well enough to know when it helps, when it hurts, and
why. Not just call it: rewrite it, then put it to the test on real data.
{{< /lead >}}

{{< fiche-projet
    stack="Python 3.12, NumPy, statsforecast, HierarchicalForecast, BayesReconPy, uv, pytest"
    code="https://github.com/gwils28/W37_hierarchical_reconciliation" >}}

{{< stats >}}
{{< stat value="1.07e-5" label="gap to the library" >}}home-made MinT(shrink) vs HierarchicalForecast{{< /stat >}}
{{< stat value="+2.3%" label="regional MASE" >}}MinT shrink vs bottom-up, over 119 éCO2mix origins{{< /stat >}}
{{< stat value="88" label="tests" >}}77 unit, 11 end-to-end{{< /stat >}}
{{< /stats >}}

{{< note-ia >}}

This repository is the lab behind the post
[Hierarchical forecast reconciliation: promises and limits]({{< relref "/posts/reconciliation-hierarchique" >}}).
The post tells what I learned; this page shows how the work is organised and how to reproduce
it. The repository and its figures are in French.

## The goal

Forecasts produced series by series don't add up: the regions don't sum to the national total,
and someone has to arbitrate. Reconciliation (MinT first) promises to remove that arbitration. I
wanted to find out three things:

- write the projection `P = S(S'W⁻¹S)⁻¹S'W⁻¹` by hand, and match the library to the digit;
- find where MinT breaks: bias, quantiles, the numerical wall;
- check on real data whether reconciliation improves accuracy, or only coherence.

## The approach

The work follows six blocks, one folder each. The code lives in a single package
(`src/w37_reconciliation`), the teaching notebooks call it, and each block has its `README`
(results) and its `TUTORIEL` (how to rerun it).

{{< steps >}}
{{< step number="1" title="Research" >}}
Four 2026 papers checked, a three-point summary and a note on what is overrated:
reconciliation sold as an accuracy gain.
{{< /step >}}
{{< step number="2" title="MinT from scratch" >}}
Schäfer–Strimmer shrinkage, oblique projection, three assertions. Gap to HierarchicalForecast:
1.07e-5. It does not come from λ, as the plan assumed, but from the covariance estimator
(centring and dividing by T−1).
{{< /step >}}
{{< step number="3" title="System design" >}}
A materialised batch job with a versioned YAML contract, a hash of the hierarchy and a quality
gate that blocks publication.
{{< /step >}}
{{< step number="4" title="Fundamentals" >}}
MinT spreads the bias of a single forecast to every leaf. Applied to quantiles, it gives a
vector that is coherent and wrong: 0.764 coverage instead of 0.900. Only joint sampling is
calibrated.
{{< /step >}}
{{< step number="5" title="éCO2mix mini-project" >}}
12 regions → France, RTE data 2013-2024, rolling-origin backtest. Details below.
{{< /step >}}
{{< step number="6" title="BayesReconPy" >}}
On intermittent sales (M5), Gaussian MinT produces negative sales; Bayesian conditioning
produces none, and is the most accurate.
{{< /step >}}
{{< /steps >}}

## The éCO2mix mini-project

**The business goal**: deliver electricity demand forecasts where the 12 regions add up exactly
to the France total.

**The protocol**, fixed before the results in `configs/eco2mix.yaml`:
- hourly data;
- SeasonalNaive(168) and MSTL as base models;
- a 52-week training window, strictly before each origin;
- a 24 h horizon;
- five reconciliations, compared by MASE level by level.

The result comes in two steps. On the 4 origins of the main protocol, MinT shrink seemed to win
(−2.2% regional MASE). Over **119 origins** covering all of 2024, it does worse than bottom-up,
on all 13 series.

![MASE by level and by method, 119 origins in 2024](figure_cle_robustesse.svg "MASE by level and by method (mean ± standard deviation) over 119 origins in 2024 (labels in French). Bottom-up is best at both levels.")

**The cause is shown by a controlled experiment.** MinT estimates its W matrix on in-sample
residuals. MSTL's are smoothing leftovers, correlated at 0.11 across regions, while the real
errors are correlated at 0.56. Estimated on the errors of past origins instead, W brings MinT
back level with bottom-up (−0.1%, not significant).

## What got in the way

- **Data before models.** Nouvelle-Aquitaine stops at the end of 2024. The source also has a
  daylight-saving defect every year: duplicates in March, a missing hour in October. A missing
  row raises no error, it silently skews the total.
- **4 origins rank nothing.** The ranking flips over 119 origins: paired tests with Holm
  correction are needed before concluding.
- **The naive λ doesn't scale.** The `T × m × m` tensor weighs 31 GB at m = 5,000. Going
  through the `T × T` Gram matrix brings that down to 0.6 GB, with the same result.
- **Check a package before recommending it.** BayesReconPy 0.5.0 no longer installs as is
  (PuLP 4), and its licence is contradictory.

## What I take away

- Coherent doesn't mean calibrated, nor more accurate: MinT guarantees coherence, the rest is a
  bonus.
- On a flat, highly correlated hierarchy, bottom-up is the most accurate choice and the easiest
  to defend.
- A hidden assumption (in-sample W) can overturn a result: test it, don't assume it.

## Reproduce

```bash
git clone https://github.com/gwils28/W37_hierarchical_reconciliation
cd W37_hierarchical_reconciliation
uv sync && uv run pytest
make eco2mix               # downloads the RTE data, backtest, report
```

Data: **Open Data Réseaux Énergies (ODRÉ) — RTE**, Licence Ouverte v2.0.
