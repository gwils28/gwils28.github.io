---
title: "About"
description: "Data Scientist and ML Engineer based in Rennes, France. Biostatistician by training, specialised in time series forecasting and putting models into production."
layout: "simple"
showDate: false
showAuthor: false
showReadingTime: true
showTableOfContents: true
showPagination: false
---

I'm **Wilson Goma**, a Data Scientist and ML Engineer based in Rennes, France.

A biostatistician by training, I started out on medical research cohorts before
moving into industry. Today at **Orange**, I build forecasting models that
anticipate field technician workload across the French telecom network — and I
keep them running in production.

I work on the part of this job that coding assistants haven't absorbed: deciding
*which* question is worth answering, establishing *which* decision it changes,
and shipping a system somebody is accountable for.

## What I actually do

The "Data Scientist" title covers three professions with incompatible
foundations. Nobody practises all three at the same level, and claiming
otherwise is the surest way to be mediocre at all of them. Here is an honest
account of where I stand.

### My two depths

**Forecasting and time series.** This is the through-line of my career.
Temperature forecasting inside refrigerated containers to protect a cold chain;
remaining-capacity estimation for IoT batteries to schedule maintenance; today,
anticipating technician workload across a national network. Each time,
forecasting is not the endpoint — it feeds a stock, capacity or scheduling
decision whose costs are asymmetric.

**Production engineering and MLOps.** I deploy and maintain what I design. I
contributed to an internal Python library that standardised model packaging and
deployment across a banking group, led a migration of use cases to Google Cloud,
and set up CI/CD, monitoring and version tracking on systems that are actually
running. Certified *Google Cloud Professional Machine Learning Engineer*.

### My foundation

**Inferential statistics**, through both training and my first three years. A
master's in biostatistics and a stint at INSERM — cohort analysis, modelling the
clinical impact of biomarkers, an epidemic propagation model — leave behind
reflexes that applied machine learning doesn't teach: suspicion when a result
looks too good, insistence on the interval, and a clear line between what was
measured and what one would like to conclude.

### My current bet

**Generative AI systems.** I explore agent and LLM orchestration in R&D, to
automate back-office processes. This is where I'm learning, not where I'm an
expert — and I'd rather write that down than let it be assumed.

### My stack

Python, SQL, Bash · scikit-learn, PyTorch, PySpark · Airflow, Docker, Terraform,
GitLab · Google Cloud (BigQuery, Vertex AI) · Dash · LangChain / LangGraph

## Career

**Data Scientist & ML Engineer — Orange, Rennes**<br>
*since December 2023*

Forecasting technician workload across the French telecom network. R&D on AI
agent architectures for back-office automation. Data pipelines, MLOps on GCP, a
Dash application giving business users a way to interact with the models.
Technical referent, mentoring apprentices and interns.

**Data Scientist & MLOps — BPCE-SI, Aix-en-Provence**<br>
*2021 – 2023*

Customer segmentation, churn prediction, recommendation engine, prediction of
customer "life events". Contributor to **Packta**, an internal library for model
packaging and deployment. Industrialisation, CI/CD, monitoring. Migration of
data science use cases to Google Cloud.

**Data Scientist & IoT Analytics — Traxens, Marseille**<br>
*2019 – 2020*

Temperature forecasting for cold chain monitoring. Battery capacity estimation
for maintenance planning. Sensor-based event detection. Satellite imagery
processing for maritime transport. Data governance and quality.

**Data Scientist — IT-CE, Marseille**<br>
*2017 – 2019*

Unsupervised anomaly detection for cheque fraud. Churn models supporting
retention strategy. Data lake structuring, decision-support dashboards.

**Biostatistics Engineer — INSERM, Paris**<br>
*2014 – 2017*

Inferential analysis and genomic profile clustering on research cohorts.
Modelling the clinical impact of biomarkers in leukaemia. A dengue propagation
model.

**MSc in Biostatistics** — Aix-Marseille University, 2016

## My doctrine

I wrote a manifesto on what this profession becomes now that producing
analytical code has become nearly free. Seven principles carry its substance.

### 1. The decision comes before the data

No work starts until we have named the decision it changes, the person who makes
it, how often it is made, and what would be done with no model at all. Failed
data projects all share one trait: nobody ever asked "who will do what
differently once this system exists?"

### 2. The business metric is the only loss function that matters

AUC, RMSE, F1 are worth nothing until an explicit chain ties them to euros or to
risk avoided. A metric without that translation is a comfort indicator: it
reassures the team and informs nobody.

The world is never symmetric. Underforecasting demand costs a stockout;
overforecasting costs inventory. Optimising a symmetric RMSE in that setting
isn't an approximation, it's a methodological error.

### 3. Correlation is not a decision

The moment a decision means **acting on** a variable, an observational
predictive model becomes invalid as decision support. Most high-value business
requests are action requests disguised as prediction requests: "predict churn"
actually means "who should I contact, and does contact reduce churn?"

### 4. An undeployed model does not exist

A model scoring 0.94 AUC asleep in a notebook is worth less than a business rule
at 0.71 used every day. Modelling accounts for a minority share of the real
effort on a system taken to completion; caring only about that share means
caring about a tenth of the job.

So my first deliverable is the dumbest possible end-to-end chain, **in
production**. A moving average, a constant. It exposes the real obstacles —
always somewhere other than expected — and it establishes the true baseline
every later gain will be measured against.

### 5. Uncertainty is a deliverable

A point prediction with no quantified uncertainty is incomplete information, and
often dangerous. The right stock decision isn't made on the median forecast but
on a quantile set by the ratio of stockout cost to holding cost — the newsvendor
model has said so since 1888.

I separate three kinds of uncertainty: irreducible noise, ignorance about the
model, and the possibility that the model is simply wrong. Confusing the first
two leads to promising impossible improvements; ignoring the third leads to the
most spectacular failures.

### 6. Simplicity is an engineering choice, never an admission of defeat

The model I keep is the simplest one that clears the useful performance
threshold. Every additional tier of complexity must beat the previous one by a
margin defined **in advance**.

Complexity is paid every month — comprehension time for each newcomer, failure
surface, audit difficulty, fragility under distribution shift. The gain is
measured once, and usually optimistically.

### 7. I rent my job, I own my skills

A job is a temporary context; a skill is a personal asset that depreciates
without maintenance. They don't depreciate at the same rate: a library's syntax
lasts two years, a statistical method lasts thirty. I invest accordingly — this
blog is the instrument.

## What I decline

A reasoned refusal is a deliverable in its own right: it saves the organisation
a project.

- **I don't start a project whose target decision hasn't been named.** If the
  sponsor can't name it, my first deliverable is a framing workshop, not a model.
- **I don't ship a performance metric without its business translation.** If the
  translation can't be established, I write that into the deliverable rather than
  implying value I haven't demonstrated.
- **I don't recommend action based on a purely predictive observational model.**
  Either I get an identification design, or I ship the analysis with a
  non-causality warning at the top of the document — not in a footnote.
- **I don't ship a bare point forecast when the downstream decision is
  asymmetric.** I ship the quantile that matches the decision, and I document
  which one.
- **I don't deploy a model more complex than necessary** for the sake of
  technical prestige or a request to "do some AI". If the request is about the
  technology rather than the outcome, I reframe it.

## How I work with assistants

I use them heavily — refusing to would be a productivity failure, not proof of
rigour. But under a strict protocol.

I never delegate **problem definition**: the assistant receives a specification,
it doesn't produce one. I never delegate **validation**: generated code is
reviewed and tested, every result checked through an independent path. I
delegate production, never understanding — shipping code you couldn't explain
line by line is signing a cheque without reading the amount.

## Away from the screen

I play jazz double bass, occasionally at jam sessions with friends. It's the one
area where I don't try to measure my progress.

---

You can reach me on [LinkedIn](https://www.linkedin.com/in/wilson-goma/) or
follow my code on [GitHub](https://github.com/gwils28).
