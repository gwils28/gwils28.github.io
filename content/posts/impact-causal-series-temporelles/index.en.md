---
title: "Causal impact on time series: the counterfactual and its placebos"
date: 2026-10-26
draft: false
description: "A day of hands-on research into estimating the effect of an intervention on a time series: a structural counterfactual built by hand, validated by placebo tests on a panel with a known truth and on the Volkswagen dieselgate, then compared with Google's CausalImpact."
summary: "A counterfactual is a forecast. What I observed building one by hand, measuring its coverage on 100 panels with a known truth, planting four violations of the design, and applying it to Volkswagen's share price after dieselgate."
categories: ["Tech watch"]
featureImage: "cover.png"
tags: ["causal inference", "time series", "counterfactual", "BSTS", "CausalImpact", "placebo tests", "state space", "python", "forecasting"]
showTableOfContents: true
---

{{< katex >}}

{{< lead >}}
What was the effect of a promotion, a price change, an announcement, on a series that could not be
randomised? The usual answer is a counterfactual: a forecast of what the series would have done
without the intervention. Building one by hand, what I mostly learned is what that forecast cannot
say on its own, and what placebo tests can check about it.
{{< /lead >}}

*Reading time: about 40 minutes. Every formula is followed by its intuition, so you can skim the
maths without losing the thread.*

{{< note-ia >}}

This article distils a **day of hands-on research** into causal inference for time series, the
one announced at the end of [the article on retraining
frequency]({{< ref "/posts/frequence-reentrainement" >}}). I started from a work plan in four
blocks: two recent papers to read at the source, a counterfactual to build and validate by
placebo, an architecture decision for a continuous incrementality measurement, and the founding
paper by Brodersen and colleagues to reread equation by equation. The plan proposed a simple success
criterion: a real effect whose interval excludes zero, a placebo effect whose interval contains
zero. I met it, then looked for what it actually guarantees, on a panel where the truth is known.
Everything is reproducible in the
[time_series_causal_statistics](https://github.com/gwils28/time_series_causal_statistics)
repository.

{{< alert icon="lightbulb" >}}
**In short.** The main results, with their scope:

1. **The plan's criterion is met on a known truth and on Volkswagen**: −20.9% [−33.9%, −1.7%] on
   VW's share price after the EPA notice, and twelve fake intervention dates all clean.
2. **The placebo-in-time only validates the pre-intervention model.** On 100 panels where a
   control is contaminated by the intervention, it is green exactly as often as on clean panels
   (17% false alarms in both cases). Contamination needs the placebo-in-space; a relationship that
   breaks at the intervention date is seen by nothing.
3. **A placebo that "finds" an effect is partly a property of the placebo itself**: with a 243-day
   pre period, the maximum-likelihood interval under-covers and the placebo fires on 11 to 17% of
   clean panels, for a nominal 5%.
4. **Static estimators (OLS on the controls, convex synthetic control, difference-in-differences)
   are as accurate as the local level on the point estimate, and six to seven times too
   confident**: 80% false positives at zero effect.
5. **The Python port of Google's CausalImpact gives the same point estimates with intervals half as
   wide.** That is its default prior on the level standard deviation (0.01), not the data: on 30
   panels with a known truth, its 95% interval covers 77% of the time, the hand-built one 90%.
{{< /alert >}}

## 1. The problem: one unit, two worlds

The causal effect of an intervention on a unit at time \(t\) is the difference between what is
observed, \(y_t\), and what would have been observed without the intervention, \(y^0_t\). The
second quantity no longer exists once the intervention has happened. A counterfactual analysis is
therefore a **forecast** of \(y^0_t\) over the post-intervention period, and the effect is the gap
between the observed series and that forecast.

![The treated unit: observed and counterfactual](nb01_two_worlds.svg "On the synthetic panel the counterfactual y0 is known (green): its difference from the observed series (blue) is the true effect, here a 10% lift planted over 90 days. In practice only the blue curve exists.")

The whole point is to make that forecast credible, and honest about its uncertainty. But a good
forecast is not a causal model. The work plan put it as a reflex to acquire: know when a forecast
has causal content, and prove it with placebo tests.

The counterfactual is built from **control series**: comparable units, untouched by the
intervention, whose relationship with the treated unit, learned before the date, is extrapolated
after it. Three assumptions carry the result, and none of them is visible in the quality of the
pre-intervention fit:

| Assumption | What it means for one treated series | What tests it |
|---|---|---|
| the intervention date is "as good as random" given the past | no anticipation, no simultaneous event specific to the treated unit | **placebo-in-time**: a fake date inside the pre period must give an effect whose interval contains zero |
| the controls are not affected, directly or by spillover | no interference: the promotion on A does not cannibalise B, used as a control | **placebo-in-space**: each control treated as if it were the unit of interest, at the real date |
| the pre-period relationship persists | the coefficients linking controls and target still hold after the date | stability diagnostics on the pre period, and coverage on a panel with a known truth |

The plan's protocol has three steps: fit a structural model on the pre period only, forecast the
counterfactual and estimate the pointwise and cumulative effect with a 95% interval, then rerun
exactly the same analysis with a fake intervention date placed inside the pre period. I did it
twice: on a semi-synthetic panel where the truth is known, so that the method can be graded rather
than merely run, and on the Volkswagen dieselgate panel.

## 2. What the recent papers say

I read two papers from 2026 and reread the 2015 one that founds the method. For each, I went to
the body of the text to check what the plan said about it.

**Time-Aware Synthetic Control** (Rho, Illick, Narasipura, Abadie, Hsu and Misra,
[arXiv 2601.03099](https://arxiv.org/abs/2601.03099), January 2026). Classical synthetic control
treats the pre-period time indices as interchangeable: permuting the columns leaves the weights
unchanged. TASC keeps the low-rank structure of synthetic control but encodes time through a linear
Gaussian state-space model with a constant trend, learned by EM (Kalman filter and
Rauch-Tung-Striebel smoother). The counterfactual comes from the target's loading on the smoothed
states, not from a convex combination of donors. What I kept from the simulations: TASC wins when
observation noise is high, loses to robust synthetic control when it is low, and brings little
without a trend. Permuting the pre-period order raises its error by 48.5%, which is the proof that
it uses temporal structure.

Two gaps between the plan and the source. The plan presented the paper as "signed by Abadie
himself": Alberto Abadie is the fourth of six authors. And the plan noted that TASC "produces
narrower confidence intervals" than the Bayesian CausalImpact: that is indeed what the authors
write for Proposition 99 and cricket, but it is a claim about **width**, and no coverage is
reported anywhere in the paper. A narrower interval is not shown to be better. This comes back in
part 9, where I measure what a narrow interval costs.

**When are time series predictions causal?** (Carlson and Shephard,
[arXiv 2603.20394](https://arxiv.org/abs/2603.20394), March 2026). The conceptual paper. Its
"potential system" indexes potential outcomes by assignment paths, with two structural
restrictions: non-anticipation (the outcome at \(t\) depends only on assignments up to \(t\)) and
triangularity (the features at \(t\) depend only on assignments up to \(t-1\)). The central
result, theorem 2, fits in one sentence: **under a matching assignment condition, a difference of
predictions is a causal effect.** Without that condition, it is a difference of predictions. The
table in part 1 is my translation of that condition into three concrete requirements for a single
treated series. The paper also connects impulse response functions, local projections and SVARs to
this framework, and recalls that Granger causality is "not really about causality, but about
prediction". The "Harvard" affiliation given in the plan is not on the abstract page; I did not
verify it.

**Brodersen, Gallusser, Koehler, Remy and Scott (2015)**,
[*Inferring causal impact using Bayesian structural time-series models*](https://arxiv.org/abs/1506.00356),
Annals of Applied Statistics. The model: a state space whose observation is a linear read-out of a
latent state, assembled block by block (local level, trend, seasonality, static or dynamic
regression on the controls), with priors on the variances and a spike-and-slab prior on the
regression coefficients, inferred by Gibbs sampling. What matters for causal impact is the
posterior predictive distribution, conditioned on the treated series before the date and on the
controls before and after, defined **jointly** over the post period so that serial structure
propagates into the cumulative effect.

Three things from this paper served me in what follows. Their simulation study grades the method
by two curves, power and coverage, and shows that a 1% lift is missed in 90% of cases. Their third
empirical analysis applies the model to the **untreated regions** and demands a null result: that
is the placebo-in-space, in their own words, "if the effect of the campaign was truly specific to
treated regions, there should be no effect in the controls". And their central warning, repeated
word for word by the plan: all these inferences depend on the assumption that the covariates were
not themselves affected by the intervention. The paper names two more, which the plan did not
quote: the pre-period relationship persists, and the model structure stays intact. Figure 4 of the
paper shows what happens otherwise: tripling the random-walk standard deviation of a coefficient 90
days into the campaign makes the error explode.

## 3. The model: a local level and a regression on the controls

The plan suggested `tfcausalimpact` or `pycausalimpact`, otherwise `statsmodels` by hand. I chose
the hand, to know what is inside, and kept Google's port as a cross-check (part 9). The model is
Brodersen's without its Bayesian layer:

$$
y_t = \mu_t + \beta' x_t + \varepsilon_t, \qquad \mu_{t+1} = \mu_t + \eta_t,
\qquad \varepsilon_t \sim \mathcal N(0, \sigma^2_\varepsilon),\ \eta_t \sim \mathcal N(0, \sigma^2_\eta).
$$

**The intuition.** The regression \(\beta' x_t\) explains the part the treated unit shares with
its controls. The level \(\mu_t\), a random walk, absorbs the rest: what the target does on its own
and the controls do not see. Both variances are estimated by maximum likelihood on the pre period
only; the counterfactual is the Kalman-filter forecast over the post period, given the controls
observed after the date. Since that distribution is Gaussian, I simulate **joint** paths of the
counterfactual, which the cumulative effect's interval needs; a test in the repository checks that
the simulated quantiles land on the analytic interval.

To see what each component brings, I fitted three models on the same panel: a static regression
alone, the local level plus regression, and a local linear trend plus regression.

| | static | local level | local trend |
|---|---|---|---|
| one-step RMSE (pre period) | 3.10 | 2.94 | 2.98 |
| one-step R² | 0.57 | 0.61 | 0.61 |
| Ljung-Box on the residuals (p) | **0.000** | 0.94 | 0.90 |
| estimated cumulative effect (truth 831) | 681 [617, 748] | 569 [207, 926] | 530 [120, 947] |

The residuals of the static regression are autocorrelated: a slow component remains that the
regression does not see, and that is what the local level absorbs. But the difference between the
models is not in the fit, which looks similar. It is in the **forecast**: the static model assumes
the unexplained part is independent noise every day, the local level assumes it can wander. Those
two beliefs give very different uncertainties 90 days out.

![Three models, three counterfactuals, three uncertainties](nb01_three_models.svg "Same panel, same pre period. The static regression (left) gives a narrow interval that misses the truth; the local level (centre) a wide interval that contains it; the local trend (right) a wider one still.")

The forecast variance of a static regression is constant. A local level adds a random-walk
variance that grows linearly with the horizon \(h\), so the interval on one day grows like
\(\sqrt h\). A local linear trend adds a random slope and the variance grows like \(h^3\). For the
**cumulative** effect these powers go up by two.

![How fast each model admits it does not know](nb01_interval_width.svg "Width of the 95% interval on one day as a function of the horizon: flat for the static regression, square root of h for the local level, faster still for the local trend.")

On this panel the static interval is narrow and misses the truth; the local level's interval is
wide and contains it. Which is right is not a matter of taste: it is a matter of coverage, which
part 5 measures over 100 panels.

**A second source of uncertainty.** The forecast distribution at the maximum-likelihood estimate
accounts for future shocks and for the uncertainty of the current state. It does not account for
the variances and coefficients being estimates themselves. CausalImpact integrates the parameters
out by MCMC; the cheap frequentist counterpart is to draw the parameters from the asymptotic normal
of the MLE and mix the forecast over those draws. On this panel, with 365 pre-period days, that
barely changes the cumulative interval: [207, 926] becomes [203, 914]. Part 5 shows where those
draws matter.

## 4. The protocol on a known truth

The panel: one treated unit and five controls, 365 days before the intervention and 90 after. All
units load on two latent factors (random walks) and a weekly pattern, with their own weights; each
unit also has a small random-walk level of its own that nobody else sees, and observation noise. The
controls are therefore noisy proxies of what drives the target, not copies. The planted effect is a
10% lift over the post period, 831 cumulative units. The counterfactual \(y^0\) is kept, so every
estimator can be graded.

| | relative effect, 95% interval | cumulative effect | tail probability |
|---|---|---|---|
| real intervention (truth 10%, 831) | **+6.6% [+2.3%, +11.3%]** | 569 [207, 926] | 0.000 |
| placebo at day 243, data truncated at the real date | +0.3% [−5.3%, +6.7%] | 38 [−655, 742] | 0.461 |

![The real intervention and its placebo-in-time](nb02_real_vs_placebo.svg "Top: the analysis at the real date, the cumulative interval excludes zero and contains the truth. Bottom: the same analysis with a fake date two thirds into the pre period, on data that stops at the real date; the cumulative effect stays around zero.")

Criterion (a) is met: the real interval excludes zero and contains the truth. Criterion (b) too:
the placebo interval contains zero comfortably, and its point estimate is a small fraction of the
real one. One implementation detail matters here: the placebo is computed on data **truncated at
the real date**, so that no treated data enters the analysis.

One panel proves nothing about the method; it proves the protocol runs. Two extensions make the
placebo more informative:

- **The placebo-in-time as a sweep.** One fake date is one draw. Eight fake dates spread over the
  pre period give the distribution of "effects" the design produces when nothing happens, and that
  is the right yardstick for the real effect. On this panel, all eight intervals contain zero, and
  the fake effects have a standard deviation of 1.8 points.
- **The placebo-in-space as a ranking.** Each control is treated in turn as the unit of interest,
  at the real date, with the other controls as donors; the real treated unit is never used as
  anybody's control. The real unit ranks first of six by absolute effect.

![Placebo-in-time sweep and placebo-in-space ranking](nb02_placebo_sweep_space.svg "Left: eight fake dates with 90-day post windows; the intervals contain zero, the real effect (orange) sits outside the cloud. Right: each unit treated as if it were the target; the real unit is the only one whose interval excludes zero.")

## 5. Is the 95% interval a 95% interval?

Brodersen and colleagues grade their method by two curves: the share of intervals that exclude
zero as a function of the true effect (power, and at zero effect the false-positive rate), and the
share of intervals that contain the truth (coverage, which must stay near 95% whatever the effect).
I drew the same curves over 100 panels per effect size, for the maximum-likelihood interval, for
the interval mixed over parameter draws, and for the placebo-in-time computed on the same panels.

One property of the setup simplifies the reading: with a fixed pre period, the estimation error
does not depend on the planted effect. The counterfactual is fitted on the pre period and forecast
from the post-period controls, neither of which the effect touches. Coverage, width and bias are
therefore the same at every effect size; only detection moves.

| estimator | coverage | false positives at 0% | detection at 1% | 2% | 5% | 10% | mean width |
|---|---|---|---|---|---|---|---|
| local level, MLE interval | 0.92 | 0.08 | 0.10 | 0.15 | 0.51 | 0.94 | 874 |
| local level, 40 parameter draws | 0.93 | 0.07 | 0.07 | 0.13 | 0.47 | 0.92 | 912 |
| placebo-in-time on the same panels (243-day pre period, truth 0) | 0.89 | **0.11** | | | | | 1,321 |

![Power and coverage over 100 panels](nb02_power_coverage.svg "Left: the share of intervals excluding zero by true effect. Right: the share containing the truth; a little under 95% for the MLE interval, one point more with parameter draws, 89% for the placebo.")

Three observations.

**Detection is modest.** A 1% lift is invisible, a 5% lift is seen one time in two, a 10% lift
almost always, with 90 post days and this noise level. That is the same order of magnitude as
Brodersen's simulation, where 1% is missed in 90% of cases.

**The placebo fires more often than 5%.** The placebo windows have a shorter pre period (243 days
instead of 365), and their interval is on average wider but less well calibrated: 11% false
positives. The plan said "if your placebo finds an effect, your design is invalid". On these
panels, one placebo in nine finds an effect on a perfectly valid design. Reading a placebo as one
date against a 5% threshold therefore rejects a correct design one time in nine. Reading the
**sweep** against its own clean-panel rate is fairer, and errs on the cautious side.

**The length of the pre period matters, because a variance needs more points than a mean.** Over
50 panels per cell, at a 5% effect:

| pre period (days) | 60 | 120 | 240 | 365 | 730 |
|---|---|---|---|---|---|
| local level, MLE | 0.72 | 0.84 | 0.92 | 0.88 | 0.92 |
| local level, parameter draws | 0.88 | 0.90 | 0.92 | 0.92 | 0.92 |
| OLS on the controls | 0.18 | 0.20 | 0.22 | 0.10 | 0.16 |

![Coverage, width and error by pre-period length](nb02_pre_length.svg "The MLE interval under-covers on short pre periods; the parameter draws correct it. OLS stays around 0.2 at every length.")

The parameter draws earn their keep on short pre periods and become unnecessary around a year of
daily data. The reason is known: on a short sample, the maximum-likelihood estimate of a level
variance can collapse to zero, and a zero-variance level is a static model with a flat,
overconfident interval. Drawing parameters around a zero maximum does not fix that; a prior does,
and that is one honest reason CausalImpact puts one on the level standard deviation. Part 9 shows
the other side of that prior.

## 6. Nine estimators on the same panels

Each estimator fits on the pre period and returns the cumulative effect with the interval a
practitioner would compute for it (iid errors for the simple ones). Same 100 panels, two effect
sizes, 0 and 5%.

| estimator | coverage | false positives at 0% | detection at 5% | width | RMSE |
|---|---|---|---|---|---|
| pre-period mean | 0.10 | 0.90 | 0.88 | 262 | 954 |
| trend only (local trend, no controls) | 0.96 | 0.04 | 0.15 | 2,224 | 559 |
| difference-in-differences (mean of controls) | 0.12 | 0.88 | 0.90 | 148 | 400 |
| OLS on the controls, iid interval | 0.19 | 0.81 | 0.93 | 124 | 274 |
| convex synthetic control, iid interval | 0.17 | 0.83 | 0.91 | 142 | 335 |
| static regression in state-space form | 0.21 | 0.79 | 0.93 | 135 | 274 |
| **local level + regression (MLE)** | **0.94** | **0.06** | 0.57 | 886 | **227** |
| local level + regression, parameter draws | 0.95 | 0.05 | 0.53 | 938 | 227 |
| local trend + regression | 0.92 | 0.08 | 0.44 | 1,065 | 280 |

![Coverage and false positives of the nine estimators](nb02_baselines.svg "In red, estimators whose coverage is below 90% (left) or whose false-positive rate is above 10% (right). Only the models with a stochastic level, and the trend alone, pass both.")

What I observed:

- **OLS on the controls and the static state-space regression are the same estimator** (identical
  bias and RMSE). Their point estimate is nearly as accurate as the local level's (RMSE 274 against
  227). Their interval is six to seven times too narrow: coverage around 20%, and **80% false
  positives at zero effect**. Four promotions out of five that did nothing would be declared
  effective. That is the measured version of the "overoptimistic inferences" Brodersen cites, after
  Bertrand, Duflo and Mullainathan, against static difference-in-differences.
- **The convex synthetic control is nearly unbiased but inherits the same iid interval**, and the
  same 80% false positives. The classical method knows this: that is why it reports permutation
  ranks rather than intervals.
- **Difference-in-differences is worse on both counts** (RMSE 400, coverage 12%): the mean of the
  controls is a poor synthetic control when loadings differ across units.
- **Trend extrapolation without controls covers**, because its interval is two and a half times
  the local level's, and it detects a 5% lift one time in seven.
- **The local level is the only estimator with near-nominal coverage and false positives near
  5%.** The local trend pays for its extra component with a wider interval and lower power.

That table is, of the whole day, the strongest argument for the placebo: on these panels the
placebo-in-time of an OLS design would fire four times out of five too, and that is how the
practitioner would find out.

## 7. When the design breaks: who catches what

The plan said the real deliverable is not the effect but the ability to say why a measurement is
invalid. I planted four violations one at a time in the panel, with a 5% lift, and ran four checks
on each, 100 panels per scenario:

- **cannibalised control**: the treated effect is subtracted, one for one, from controls c0 and c1
  (a promotion on A that eats the sales of B and C, used as controls);
- **halo on the controls**: the same amount is added to c0 and c1;
- **own trend**: the treated unit drifts by +0.1 per day on its own, from day one (about 36% a year
  on a level of 100), while the controls do not;
- **relation break**: the treated unit's loadings on the common factors change by +30% at the
  intervention date.

The checks: the placebo-in-time, the placebo-in-space (each control as if treated, at the real
date), a Chow test on differences between the two halves of the pre period, and the estimate's bias
against the truth, which one would like to know in practice and never can. The "clean" row gives
each check's false-alarm rate, and the other rows are read against it.

| scenario | coverage | relative bias | placebo-in-time fires | placebo-in-space flags c0 / c1 | flags a clean control | Chow rejects |
|---|---|---|---|---|---|---|
| clean | 0.89 | −0.5% | 0.17 | 0.10 / 0.08 | 0.24 | 0.15 |
| cannibalised control | 0.86 | **+26%** | 0.17 | **0.39 / 0.36** | 0.34 | 0.15 |
| halo on the controls | 0.82 | **−27%** | 0.17 | **0.38 / 0.45** | 0.31 | 0.15 |
| own trend | 0.69 | **+71%** | **0.39** | 0.10 / 0.08 | 0.24 | 0.15 |
| relation break | **0.56** | −11% | 0.17 | 0.10 / 0.08 | 0.24 | 0.15 |

![Who catches what: the share of panels where each check fires, and the bias it is supposed to protect](nb03_who_catches_what.svg "Left: each check's firing rate by scenario. Right: the relative bias of the cumulative effect and the coverage. The relation break is biased and under-covered without any check rising above its false-alarm rate.")

Row by row:

- **Cannibalised control and halo.** The bias is large (+26% and −27% of the true effect) and
  coverage slips. Yet **the placebo-in-time is exactly as often green as on clean panels**: nothing
  is wrong with the pre period, the contamination starts at the intervention. The
  placebo-in-space flags each contaminated control about four times more often than a clean one
  (39% and 36% against 10% and 8%): the check has power, but far from certainty for a
  contamination of this size. It also flags clean controls more often (34% against 24%): a
  contaminated donor contaminates the placebos that use it.
- **Own trend.** The placebo-in-time fires in 39% of panels, more than twice its clean rate. That
  is the design doing its job: a unit that drifts on its own relative to its controls produces
  "effects" at any date. The bias is +71%, because the local level forecasts flat and the drift
  continues.
- **Relation break.** Biased, under-covered, and **no check fires above its clean rate**. A
  relationship that stops holding at the intervention date is indistinguishable, in the data, from
  an effect of the intervention. This is the assumption Brodersen names as the one everything rests
  on, and it is untestable by construction. The only defences are outside the data: a reason to
  believe the relationship persists, and the business reconciliation of part 10.

### Isolating a contaminated control

When the placebo-in-space flags several controls, one of them may be the culprit and the others its
victims. The repository's procedure removes the worst one (the smallest tail probability), reruns
the check on the rest, and repeats until nothing is flagged.

![Contamination check on a cannibalised panel](nb03_isolation.svg "Each control's own effect at the real date, with its interval. The controls removed by the isolation are marked; c0 and c1 are the two controls contaminated by construction.")

On this panel the first round flags only c1; c0, also contaminated, has an interval that just
touches zero ([−10.3%, +0.2%]). The isolation removes c1, then c0, then a clean control, c2, and
keeps c3 and c4. With all controls, the effect is estimated at 601 [283, 937] for a truth of 503:
the interval covers, but the estimate is 20% too high. With the two kept controls: 118 [−416,
676]. The interval still covers, but the estimate has become very imprecise. Removing controls
trades bias for variance, and with five donors the trade is a poor one. That is what made me
write, in part 10, that one should start from a pool of 10 to 20 eligible donors, chosen
**before** the campaign among products that cannot interact with the promoted one: the check is a
guard, not a selection procedure.

## 8. A real case: Volkswagen, 18 September 2015

The plan suggested a series from the Favorita dataset. With no Kaggle credentials on the machine, I
took the public panel that the CausalImpact port uses as a test fixture: weekly closing prices of
Volkswagen, BMW and Allianz, 325 weeks from January 2011 to March 2017. The intervention is dated:
the US EPA's notice of violation against Volkswagen, published on Friday 18 September 2015. Here no
truth is available, and every claim has to be defended by a placebo or a sensitivity analysis.

![Weekly closes, 2011 to 2017](nb04_series.svg "VW, BMW and Allianz, with the date of the EPA notice. VW's price loses 28% in one week.")

### The first thing to notice

The row dated Sunday 20 September 2015 already contains the crash: VW goes from 155.4 to 111.3,
−28%, then to 97.4 the following week. Rows are labelled by the Sunday that opens the week, and
that week holds the Monday 21 and Tuesday 22 sessions. The pre period therefore ends on 13
September (246 weeks) and the post period starts on 20 September (79 weeks, to March 2017), as in
the package's own example.

But **BMW falls in the same week**: −8%, from 75.5 to 69.5, while Allianz gains 1%. BMW's shares
dropped after press reports, on 24 September, about the emissions of one of its models, and the
whole sector was repriced before recovering in October. If BMW reacted to the same event, it is not
an untreated control. The question is dealt with below.

### Is the pre-period relationship stable?

The counterfactual extrapolates the relationship between VW and its controls. If it was already
drifting before the date, extrapolating it is a guess. A rolling 52-week regression shows
coefficients that wander and an R² far from constant: in levels, three share prices co-move through
the market factor, but the loadings are not a law. A Chow test between the two halves of the pre
period, computed on weekly **differences** so that a drifting level does not masquerade as a change
of loadings, does not reject stability (F = 0.95, p = 0.42). My reading: stable enough to try, not
stable enough to trust the result without a placebo.

### The effect, with BMW and Allianz as controls

| | value |
|---|---|
| average effect per week | −33.5 [−65.1, −2.1] |
| cumulative effect over 79 weeks | −2,650 [−5,140, −169] |
| **relative effect** | **−20.9% [−33.9%, −1.7%]** |
| tail probability | 0.018 |
| one-step fit on the pre period | R² 0.99, coverage 0.92, Ljung-Box p = 1.0 |
| coefficients | BMW 0.63, Allianz 0.30 |

![VW, local level and regression on BMW and Allianz](nb04_impact_bmw_allianz.svg "The three usual panels: observed and counterfactual, pointwise effect, cumulative effect. The interval widens fast: 79 weeks is a long horizon for a random-walk level.")

The interval excludes zero, but not by much, and it widens fast: 79 weeks is a long horizon for a
random-walk level whose weekly variance, estimated from the data, is not negligible. The point
estimate says VW traded about a fifth below its counterfactual over the following eighteen months.

The one-step R² of 0.99 says nothing about the controls: a share price is close to a random walk,
and one-step forecasts of a random walk are always excellent. Another number is more telling: the
ratio of the residual spread after and before the date is 3.4. The post period behaves very
differently from the pre period.

### The placebo-in-time, one year earlier

I pretend the intervention happened on 14 September 2014 and rerun the identical analysis on data
that stops on 13 September 2015, so that no post-notice data is seen. Nothing happened to VW in
particular on that date; the estimated effect must be indistinguishable from zero: **+5.4%
[−8.2%, +23.1%]**, tail probability 0.24.

Then the sweep: twelve fake dates between February 2012 and March 2015, each with a 26-week post
window.

![Placebo-in-time sweep on Volkswagen](nb04_placebo_sweep.svg "Twelve fake dates, 26-week post windows, 95% intervals. All contain zero; the real effect over 79 weeks (orange) sits outside the cloud.")

All twelve intervals contain zero, and the placebo estimates scatter on both sides, between −7.6%
and +9.0%. The real effect sits well outside that scatter. This is the (b) half of the criterion,
and it is what makes the (a) half reportable.

This placebo validates the pre-intervention model. It says nothing about BMW, because in the
placebo windows BMW was hit by nothing.

### Were the controls themselves treated?

Brodersen's third analysis: run the model on each control as if it were the treated unit, with the
other control as its donor, at the real date.

| | own effect over 79 weeks | over the 14 weeks after the notice |
|---|---|---|
| BMW (counterfactual from Allianz) | −11.3% [−27.3%, +13.8%] | −1.5% [−10.5%, +9.6%] |
| Allianz (counterfactual from BMW) | +14.7% [−3.7%, +41.6%] | **+9.4% [+1.0%, +19.3%]** |

![Each control treated as if it were the target](nb04_control_check.svg "BMW forecast from Allianz, and Allianz forecast from BMW, over the 14 weeks after the notice. Allianz 'rises' 9.4% relative to BMW: it is BMW that fell.")

With only two controls, this check is a mirror: "BMW fell relative to Allianz" and "Allianz rose
relative to BMW" are the same fact seen from both sides, and the intervals are wide because a single
donor is a poor counterfactual. The weekly rows around the notice are the most direct evidence:
BMW lost 8% in the week of 20 September and recovered 12% two weeks later, Allianz did not move.
The sector was repriced for a few weeks, and BMW is a doubtful control, at least for the short-run
effect. Rather than pick a verdict, I reported the effect under each control set.

### Sensitivity: how much of the answer is a modelling choice?

| specification | relative effect | 95% interval | excludes zero |
|---|---|---|---|
| BMW + Allianz, local level (reference) | −20.9% | [−33.9, −1.7] | yes |
| Allianz only | −27.2% | [−41.8, −2.8] | yes |
| BMW only | −16.8% | [−31.5, +5.9] | no |
| no control, local linear trend | −22.9% | [−45.0, +27.2] | no |
| BMW + Allianz, static regression | −30.1% | [−31.0, −29.1] | yes |
| BMW + Allianz, local linear trend | −19.7% | [−35.1, +4.4] | no |
| BMW + Allianz, log prices | −4.3% | [−8.4, +0.2] | no |
| BMW + Allianz, pre period from 2013 | −21.5% | [−34.9, −1.2] | yes |
| BMW + Allianz, pre period from 2014 | −21.4% | [−34.6, −1.5] | yes |

![Sensitivity of the effect to the specification](nb04_sensitivity.svg "Nine specifications. In grey, those whose interval contains zero. The sign never changes; the interval is what moves.")

Every specification in prices with a control puts the estimate between about −15% and −30%, and
the sign never flips. What moves is the interval. The static regression is confidently narrow, and
part 6 showed that confidence is not earned on autocorrelated data. BMW alone is not significant.
The local linear trend adds a stochastic slope to a share price, and its 79-week forecast is too
uncertain to conclude. Allianz alone, the reference and the shorter pre periods are significant and
agree. The log specification is in the table for its sign only: a relative effect on the log scale
is not a relative effect on the price.

The defensible report is a **range from −17% to −27%**, with the control-set question flagged.

### Does the model use time order at all?

A cheap check, after TASC: shuffle the pre-period rows and refit. A static regression gives the
same answer. A model with a stochastic level does not, because a shuffled random walk is no longer
a random walk, and the level variance collapses.

![Shuffling the pre period: the local level's answer changes, the static regression's cannot](nb04_time_order.svg "Over 20 permutations of the pre period, the local level's cumulative effect converges to the static answer, with an interval ten times narrower than the original.")

Over the permutations, the local level's cumulative effect converges to −4,305 (standard
deviation 64), with a mean interval width of 518 against 4,971 in the original order. The shuffled
fits converge to the static answer and its narrow interval. In other words, the local level's wider
interval is the price of taking the serial dependence of the pre period seriously, and the static
regression's narrow interval is what one gets by pretending the weeks are exchangeable.

## 9. Comparison with Google's CausalImpact

The hand-built model is a frequentist cousin of CausalImpact: same state space, maximum
likelihood instead of priors and MCMC. If the two disagree, the difference is informative. I ran
`tfcausalimpact`, the TensorFlow Probability port (variational inference by default), on the
Volkswagen panel and on synthetic panels.

| case | method | cumulative effect, 95% interval | width |
|---|---|---|---|
| VW, BMW + Allianz | hand-built, MLE | −2,650 [−5,140, −169] | 4,971 |
| | tfcausalimpact, default prior on the level sd (0.01) | −3,355 [−4,427, −2,233] | **2,193** |
| | tfcausalimpact, prior at 0.1 | −2,878 [−5,212, −428] | 4,784 |

![Volkswagen: same state space, half the interval](nb05_vw_intervals.svg "Cumulative effect and 95% interval under four variants, for both control sets. The point estimates sit inside each other's intervals; the widths do not.")

Same data, same state space, point estimates each inside the other's interval, and an interval
half as wide. CausalImpact's default prior on the level standard deviation is 0.01, in units of the
standardised series, inherited from the R package. On a weekly share price, the maximum-likelihood
level standard deviation is about 0.085 in the same units, eight times larger. The prior wins the
argument over 246 weeks of data, because variational inference with a tight prior around a small
value keeps the level nearly deterministic, and a nearly deterministic level forecasts 79 weeks
ahead with a nearly constant variance. Loosening the prior to 0.1 opens the interval up to the
hand-built one. **The narrow interval was the prior, not the data.**

This is not a flaw of either implementation. A prior is the statement that share prices do not
wander, which one may or may not want to make; maximum likelihood is the statement that the pre
period is the only information about how much they wander. What I take from it is that the
interval width on a real case is a modelling choice, and must be reported as such.

On a known truth one can go further and ask who covers:

| 30 panels, 5% lift | coverage | detection | mean width | RMSE | seconds per fit |
|---|---|---|---|---|---|
| hand-built, MLE | **0.90** | 0.53 | 887 | 219 | 0.1 |
| tfcausalimpact, default prior | 0.77 | 0.80 | 494 | 262 | 15.7 |

![Intervals centred on the truth, 30 panels](nb05_coverage_side_by_side.svg "Each segment is a 95% interval recentred on the truth: a segment that misses zero missed the truth. The tfcausalimpact intervals are shorter and miss more often.")

The default prior buys an interval 45% narrower and a higher detection rate (80% against 53%) at
the price of coverage: its 95% interval contains the truth in 77% of panels, the hand-built one in
90%. The point estimates are of similar accuracy. The prior is a reasonable default for the daily
marketing series the method was built for, with a small level variance relative to the regression
on many controls, and a poor default for a series with a large own random walk, which is what this
panel and a share price are. A placebo-in-time sweep would reveal it: its false-positive rate would
sit well above 5%.

Neither "narrow" nor "Bayesian" is a synonym for "calibrated". Coverage on a known truth, or a
placebo sweep on real data, are the only evidence I found. And that brings me back to TASC: its
intervals "narrower than CIM" are a claim about width, and this day showed me what width without
coverage can hide. One practical point, finally: 0.1 seconds per fit against 12 to 16, which
matters for placebo sweeps and Monte Carlo studies.

## 10. Measuring promotion incrementality continuously

The plan's third block was an architecture decision, with no code: a promotion engine runs
campaigns on products in stores, and for each campaign one wants the causal effect on sales, by
counterfactual rather than by holdout, because the business will not hold out stores or customers
for every promotion. Three points decide whether the number is worth anything. The figures quoted
are those of parts 5 to 7.

**Selection and integrity of the controls.** With part of the promoted product's lift
cannibalised from a product used as a control, the effect is overestimated by a quarter and the
placebo-in-time stays green in 83% of cases. Interference is invisible to the check everybody runs.
My answer is twofold. Before the campaign, candidate controls come from a **registry of eligible
donors** built from the product graph: same store cluster and seasonality class as the target, but
a different category and no substitution edge (from basket co-occurrence and past cross-elasticity
estimates). A product in the same category, the same brand family, or a known substitute or
complement is excluded whatever the quality of its pre-period fit, because the best-fitting control
is often the closest substitute. Any donor itself promoted, out of stock, delisted or repriced in
the window is excluded. And the pool holds 10 to 20 donors, to afford losing some. After the
campaign, the placebo-in-space at the real date, with leave-one-out isolation (part 7), flags the
donors that moved with the campaign. A negative own effect on a same-aisle product is a
cannibalisation finding in its own right, and it is part of the promotion's net effect; a positive
one is a halo. Both go into the campaign report, and the effect is reported on the kept pool.

**Monitoring the causal assumption over time.** The counterfactual is unobservable, so nothing is
monitored directly. Four substitutes, each tied to a failure mode the panel reproduces:

| Signal | What it guards | Rule |
|---|---|---|
| pre-period fit of the deployed model (one-step R², Ljung-Box, coverage of the one-step interval), per campaign | the model is the right size for the series | one-step coverage outside [0.90, 0.98] or Ljung-Box p < 0.01 blocks the report |
| rolling placebo-in-time on **never-treated** products, same model, same lengths, every week | the calibration of the design where the truth is zero | share of placebo intervals excluding zero over the last 50 runs above 10% (the panel measured 11% on short pre periods) raises an alert; the clean-panel rate is the baseline |
| placebo-in-space on every campaign | interference | any isolation round beyond the first on a target triggers a review |
| stability of the donor-target relationship: Chow on differences, drift of the coefficients between successive campaigns of the same target | the relationship that is extrapolated | p < 0.01 or a sign change of a coefficient blocks the donor |

What this monitoring cannot see, and the dashboard says so: a relationship that breaks at the
campaign date. The scenario of part 7 is biased and under-covered without any check firing above
its clean rate. That failure mode is caught only by the third point.

**The business guard-rail.** The estimated effect is a forecast residual. It is tied to money
through a quantity that *is* observed later: the **realised incremental margin**, reconciled per
campaign and per month. Each report carries the estimated incremental units with their interval,
converted into margin with the promotion's unit margin, and the *implied* margin that the ledger
should show for the product-store set over the post window. Each month, the sum of estimated
counterfactual and incremental margins is compared with the realised margin of the promoted sets.
The reconciliation gap is a time series: its level is noisy by nature, its **drift** is the alarm.
A gap that grows in one direction for three months means the counterfactuals are systematically
off, and that is what a silently drifting model looks like from outside, including a relation break
that nothing else sees. Two more anchors: an occasional real holdout, on a small share of campaigns
chosen by the engine, with a randomised store holdout, whose experimental effect is compared with
the counterfactual effect on the same campaign, the way Brodersen and colleagues validated their
observational estimate against the randomised one; and the sum of effects across campaigns of the
same category, which cannot exceed the category's observed growth for long without a
cannibalisation the controls missed. As long as the reconciliation gap has not been closed for a
product family, the effect that goes into a decision is the lower bound of the interval, not the
point estimate.

## 11. What I take away

These observations hold for the setups studied here: a semi-synthetic panel with two latent
factors, five controls and 90 post days, and a panel of three share prices. I present them as such.

1. **The counterfactual is a forecast, and its uncertainty is the model's belief about what the
   unexplained part does over time.** A static regression believes it is independent every day; a
   local level lets it wander. On these panels only the second belief gives a 95% interval that
   covers at 95%.
2. **Static estimators are accurate and overconfident**: nearly the same RMSE as the local level,
   and 80% false positives at zero effect. That is, of the day, the strongest argument for not
   skipping the placebo.
3. **The placebo-in-time validates the pre-intervention model, and nothing that starts at the
   intervention date.** It catches a unit drifting on its own (twice its clean rate); it is blind
   to a contaminated control and to a relation break.
4. **The placebo-in-space is the check for interference**, with modest power (about 40% per
   contaminated control against 10% false alarm, for a one-for-one contamination on a 5% effect),
   and it needs leave-one-out isolation because a contaminated donor flags its neighbours.
5. **A relationship that breaks at the intervention date is seen by no data-only check.** Naming
   that limit is what separates a forecast from a causal claim: making it plausible by construction
   (control selection) and auditable afterwards (business reconciliation) is the only treatment I
   found.
6. **A placebo that fires does not necessarily invalidate the design.** With a shortened pre
   period, the interval under-covers and the placebo fires on 11 to 17% of clean panels. I now read
   a sweep against its clean rate, not one date against 5%.
7. **On Volkswagen, the effect of the EPA notice is −17% to −27% over 79 weeks, depending on the
   control set**, placebo clean at twelve fake dates, with BMW flagged as a doubtful control in the
   weeks that follow.
8. **The interval width on a real case is a modelling choice.** CausalImpact's default prior gives
   an interval half as wide as maximum likelihood, and covers 77% instead of 90% on a known truth.
   Loosening the prior reconciles the two.

**Open questions.** I did not implement TASC, nor measure its coverage. The synthetic panel has a
step-shaped effect; the generator can produce a ramp and a pulse, which I did not study. The
placebo-in-space was measured for a single contamination size. And the monitoring of part 10 is a
line of reasoning, not a production system: its thresholds come from the panel, not from promotion
data.

{{< alert icon="circle-question" >}}
**A question to check your understanding.** *A promotion on product A is measured by
counterfactual with, as controls, three products from the same aisle chosen for the quality of
their pre-period fit. The effect is +12% [+4%, +20%], and the placebo-in-time at three fake dates
is clean. What is that number worth?* The placebo-in-time only tests the pre period, where the three
controls were contaminated by nothing (part 7). If the promotion on A took sales from products in
the same aisle, the counterfactual is pulled down and the effect overestimated, without any
placebo-in-time seeing it. What is needed is the placebo-in-space at the real date on each of the
three controls, and, if the aisle is the same, a good reason for having chosen those controls other
than their fit, since the best-fitting control is often the closest substitute.
{{< /alert >}}

## Reproduce and go further

The code, the five notebooks and the 22 tests are in the
[gwils28/time_series_causal_statistics](https://github.com/gwils28/time_series_causal_statistics)
repository (Python 3.13, versions locked with `uv`). Every table in this article comes out of a
`cts synth`, `cts vw`, `cts study all` or `cts tfci` command, with fixed seeds; the Monte Carlo
studies take about fifteen minutes and the cross-check about ten. The Volkswagen panel is
downloaded once from the test fixture of the CausalImpact port.

**Sources**

- Brodersen, Gallusser, Koehler, Remy and Scott, [*Inferring causal impact using Bayesian structural time-series models*](https://arxiv.org/abs/1506.00356), The Annals of Applied Statistics, 9(1), 2015, and the [CausalImpact](https://google.github.io/CausalImpact/) implementation.
- Rho, Illick, Narasipura, Abadie, Hsu and Misra, [*Time-Aware Synthetic Control*](https://arxiv.org/abs/2601.03099), arXiv, January 2026.
- Carlson and Shephard, [*When are time series predictions causal? The potential system and dynamic causal effects*](https://arxiv.org/abs/2603.20394), arXiv, March 2026.
- [tfcausalimpact](https://github.com/WillianFuks/tfcausalimpact), Python port of CausalImpact on TensorFlow Probability, and its test fixture for the Volkswagen panel.
