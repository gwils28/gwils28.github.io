---
title: "[Demo] Churn prediction"
date: 2026-09-27
draft: false
description: "Demo project: predicting customer churn a month ahead, from EDA to a scoring API. It will be removed."
summary: "Demo project: predicting customer churn a month ahead, from EDA to a scoring API."
tags: ["demo", "python", "scikit-learn", "fastapi", "classification"]
featureImage: "cover.png"
showTableOfContents: true
---

{{< alert icon="triangle-exclamation" cardColor="#f59e0b" iconColor="#1f2937" textColor="#1f2937" >}}
**Demo project.** The data and figures are made up: this page is a layout
template for real projects, and will be removed as soon as the first one is
published.
{{< /alert >}}

{{< lead >}}
Spot subscribers about to cancel, a month before they leave — accurately enough
that the retention offer costs less than the churn itself.
{{< /lead >}}

{{< fiche-projet
    statut="Completed"
    periode="March – May 2026"
    role="Solo, from EDA to deployment"
    stack="Python 3.12, polars, scikit-learn, XGBoost, SHAP, FastAPI, Docker"
    code="https://github.com/gwils28/REPO"
    demo="https://example.org" >}}

{{< stats >}}
{{< stat value="0.89" label="AUC" >}}vs 0.84 for the baseline{{< /stat >}}
{{< stat value="58%" label="of churners caught" >}}by targeting only 20% of customers{{< /stat >}}
{{< stat value="40 ms" label="per prediction" >}}served by the API, p95{{< /stat >}}
{{< /stats >}}

## The problem

A telecom operator loses **12% of its subscribers every year**. A retention
offer costs about €30, a lost customer close to €400 in margin: the offer pays
off — as long as it isn't sent to the whole customer base.

So the real question wasn't "who will leave?" but **"who should we target, and
how far down the list should we go?"** — a ranking and cost problem more than a
raw accuracy one.

## The approach

{{< steps >}}
{{< step number="1" title="Explore" >}}
7,000 customers, 21 features. Two signals stand out from the EDA: contract type
and tenure. Month-to-month customers churn **three times more**.
{{< /step >}}
{{< step number="2" title="Set a baseline" >}}
Logistic regression: a performance floor, and readable coefficients to check
the business intuition before going further.
{{< /step >}}
{{< step number="3" title="Scale up" >}}
Gradient boosting (XGBoost) with **time-based** cross-validation — train on the
past, test on the future, just like in production.
{{< /step >}}
{{< step number="4" title="Pick the threshold" >}}
Threshold tuned on **business cost** rather than F1: a missed churner costs
thirteen times more than an offer sent for nothing.
{{< /step >}}
{{< step number="5" title="Serve" >}}
Model exposed behind a containerised FastAPI service, returning the top three
reasons behind each customer's score (SHAP).
{{< /step >}}
{{< /steps >}}

## The result

The gain curve answers the targeting question directly: by contacting the
top-ranked 20% of customers, we reach 58% of future churners, versus 20% at
random.

{{< chart >}}
type: 'line',
data: {
  labels: ['0%', '10%', '20%', '30%', '40%', '50%', '60%', '70%', '80%', '90%', '100%'],
  datasets: [
    { label: 'Gradient boosting', data: [0, 36, 58, 72, 82, 89, 93, 96, 98, 99, 100],
      borderColor: css(modeSombre ? '--color-primary-400' : '--color-primary-700'), backgroundColor: css(modeSombre ? '--color-primary-400' : '--color-primary-700'), borderWidth: 3, tension: 0.3 },
    { label: 'Logistic regression', data: [0, 28, 47, 61, 72, 81, 87, 92, 96, 99, 100],
      borderColor: css(modeSombre ? '--color-primary-700' : '--color-primary-300'), backgroundColor: css(modeSombre ? '--color-primary-700' : '--color-primary-300'), borderWidth: 2, tension: 0.3 },
    { label: 'Random', data: [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100],
      borderColor: css('--color-neutral-500'), backgroundColor: css('--color-neutral-500'), borderDash: [6, 6], borderWidth: 1.5, pointRadius: 0 }
  ]
},
options: {
  plugins: { title: { display: true, text: 'Share of churners caught vs share of customers targeted' } },
  scales: {
    x: { title: { display: true, text: 'Customers targeted (by descending score)' } },
    y: { title: { display: true, text: 'Churners caught (%)' }, min: 0, max: 100 }
  }
}
{{< /chart >}}

| Model               | AUC  | Recall @ 50% precision | Estimated net gain / year |
| ------------------- | ---- | ---------------------- | ------------------------- |
| Logistic regression | 0.84 | 0.61                   | €142k                     |
| Gradient boosting   | 0.89 | 0.73                   | €187k                     |

{{< alert icon="circle-info" >}}
**Known limitation**: the model degrades on contracts signed after the pricing
overhaul, which are under-represented in the training history. Quarterly
retraining and drift monitoring are planned.
{{< /alert >}}

## What I took away

- **The threshold matters as much as the model.** Switching from F1 to business
  cost gained more than moving from logistic regression to boosting.
- **Time-based validation is non-negotiable.** With random cross-validation, AUC
  climbed to 0.93 — a flattering and wrong number.
- **Explaining each score** (SHAP) got the sales team to adopt the tool far
  faster than any global metric would have.
