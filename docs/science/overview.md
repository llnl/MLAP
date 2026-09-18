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

## What is assessed

| Study | Question |
|---|---|
| [Data Sampling](data-sampling.md) | How many reference times and grid points are needed? |
| [Historical Data](history.md) | How far back must atmospheric history reach, and how finely sampled? |
| [ML Parameters](ml-parameters.md) | Which Random Forest and MLP hyperparameters matter? |
| [Physical Quantities](physical-quantities.md) | Which atmospheric variables actually carry the signal? |

## Headline findings

- **Random Forest substantially outperforms MLP** on identical datasets — R²
  around 0.89 against 0.79. See [ML Parameters](ml-parameters.md).
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

## Not yet studied

These appear in the manuscript outline but have no simulation results yet:

- Terrain ruggedness as a feature
- Restricting data to specific months of the year
- Restricting data to a specific sub-region
- Cross-application of a trained model across time
- Cross-application of a trained model across space

The pipeline supports all five —
[`clip_data_train_test`](../user-guide/json-reference.md#clip_data_train_test)
handles the spatial subsetting, and
[Step 5](../user-guide/step5-analyze.md) handles cross-application — but the runs
have not been made.
