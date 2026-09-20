# Scientific Assessment

This section documents what MLAP simulations show about predicting 10-hour dead
fuel moisture from atmospheric history — how accuracy responds to data sampling,
history parameters, ML hyperparameters, and the choice of physical quantities.

## How to read these results

Every number here comes from the metric CSVs written by
[Step 4](../user-guide/step4-evaluate.md). Unless stated otherwise:

- The metric is **R² on the best 95% of test data** (`r2_score`, `test_p95`),
  which suppresses the handful of outliers that would otherwise dominate the
  aggregate.
- The model is **Random Forest with scikit-learn defaults**.
- The label is 10-hour fuel moisture, treated as a **regression** problem.
- Datasets use \(t_{max\_history} = 32\) h and \(t_{history} = 4\) h unless the
  study varies them.

Where a trend is consistent across `train`, `test`, `test_p95` and `rmse`, it is
reported as a trend. Where metrics disagree or the effect is smaller than the
scatter between datasets, that is said explicitly.

!!! info "Two tiers of result"
    Some sections correspond to written sections of the fuel moisture assessment
    manuscript. Others report studies that were **run but not yet written up** —
    the simulation output exists in full, and those sections are marked with a
    note. Both are drawn from the same CSVs.

## Assessment performed

Five groups of studies were run, spanning 27 evaluation collections and drawing
on datasets from 1 to 15 million rows. Random Forest is the baseline model
throughout; the Multi-layer Perceptron study exists to show the same machinery
running on a second model family.

| Study | Question | Scope |
|---|---|---|
| [Data Sampling](data-sampling.md) | How many reference times and grid points are needed? | 7 datasets, 2–15 million rows |
| [Historical Data](history.md) | How far back must atmospheric history reach, and how finely sampled? | 9 datasets; 32–48 h maximum history, 1–8 h interval |
| [Random Forest Parameters](ml-parameters.md) | Which hyperparameters of the baseline model matter? | 4 hyperparameter studies, each across 3 datasets |
| [Physical Quantities](physical-quantities.md) | Which atmospheric variables actually carry the signal? | 3 feature studies across 4 datasets |
| [Multi-layer Perceptron](mlp.md) | Can MLAP run the same parametric machinery on a second model family? | 8 hyperparameter studies, each across 3 datasets |

Every hyperparameter and feature study was repeated on more than one dataset, so
an effect that does not reproduce across all of them is reported as
unestablished rather than as a finding.

## Headline findings

- **Random Forest substantially outperforms the MLP as configured** on identical
  datasets — R² around 0.89 against 0.79. The MLP appears to be stopping training
  prematurely, so this is not yet a fair comparison between the two methods. See
  [Multi-layer Perceptron](mlp.md#why-the-mlp-underperforms-random-forest).
- **Most hyperparameters barely matter.** Two exceptions dominate everything
  else: Random Forest `bootstrap` and MLP `solver`.
- **Spatial and temporal sampling behave differently.** More grid points improves
  accuracy; more reference times does not. See
  [Data Sampling](data-sampling.md).
- **Shortwave downward flux matters far more than precipitation**, and vapor
  pressure deficit does not substitute for temperature and humidity without loss.
  See [Physical Quantities](physical-quantities.md).
- **Returns on history are real but small** — roughly 1% in R² for 50% more
  history, which rarely justifies the cost. See [Historical Data](history.md).

## Potential future studies

Each of the following is a natural extension of the results above, and the
pipeline already supports all five — they need runs, not new code.

| Study | Question it would answer |
|---|---|
| Terrain ruggedness as a feature | Elevation alone gives a small but very consistent gain. Does slope and variability carry signal beyond height? |
| Restricting data to specific months | Do season-specific models beat one year-round model, given how strongly fuel moisture varies through the year? |
| Restricting data to a sub-region | Does a model tuned to one landscape — Central Valley, Sierra, coastal ranges — outperform a statewide one? |
| Cross-application across time | How well does a model trained on one period predict another? This is the central question for applying MLAP to climate projections. |
| Cross-application across space | Does a California-trained model transfer to other regions, and how far does it degrade? |

The mechanisms are already in place:
[`clip_data_train_test`](../user-guide/json-reference.md#clip_data_train_test)
restricts the spatial domain,
[`qois_for_training`](../user-guide/step3-train.md#choosing-features-for-training)
selects the feature set, and
[Step 5](../user-guide/step5-analyze.md) applies a trained model to any time and
region for which the required atmospheric data exist — including forecasts and
climate scenarios.

The two cross-application studies are the most consequential, since the case for
MLAP as a cheap surrogate rests on trained models generalizing beyond the
conditions they were fitted to. That claim is currently argued from design rather
than measured.
