# ML Parameters

How much do the hyperparameters of the ML models actually matter?

!!! info "Results not yet in the manuscript"
    Every study on this page was run and its output is complete, but these
    sections are still placeholders in the fuel moisture assessment manuscript.
    The numbers below come from the metric CSVs rather than from the paper.

All studies here use the same three datasets, which differ only in spatial sample
size, with \(t_{max\_history} = 32\) h and \(t_{history} = 4\) h:

| Dataset | Reference times | Grid points | Rows |
|---|---|---|---|
| 79 | 1,000 | 1,000 | 1,000,000 |
| 80 | 1,000 | 1,500 | 1,500,000 |
| 81 | 1,000 | 2,002 | 2,002,000 |

Reporting three datasets rather than one matters: a hyperparameter effect that
does not reproduce across all three is not a real effect.

## Model choice dominates everything

Before any hyperparameter, the largest single factor is which model is used. On
identical data:

| Model | R² (test p95), dataset 81 |
|---|---|
| Random Forest, defaults | **0.8960** |
| MLP, defaults | 0.7918 |

That gap — more than 10 percentage points — is larger than any hyperparameter
effect measured below, with two exceptions that are both catastrophic
misconfigurations rather than tuning choices.

**Random Forest with scikit-learn defaults is a strong baseline for this problem.**

## Random Forest

### Effect of data scaling

| Scaler | Dataset 79 | Dataset 80 | Dataset 81 |
|---|---|---|---|
| `Standard` | 0.8724 | 0.8863 | 0.8960 |
| `MinMax` | 0.8722 | 0.8852 | 0.8951 |
| `MaxAbs` | 0.8724 | 0.8857 | 0.8953 |
| `Robust` | 0.8724 | 0.8861 | 0.8954 |

Scaling makes **no meaningful difference** — the spread is under 0.001 on every
dataset, far below the difference between datasets.

This is expected. Random Forest splits on feature *ordering*, not magnitude, so
any monotonic rescaling leaves the tree structure essentially unchanged. Scaling
matters for distance- and gradient-based models such as SVM and MLP; for tree
ensembles it is close to a no-op.

### Effect of the number of estimators

| `n_estimators` | Dataset 79 | Dataset 80 | Dataset 81 |
|---|---|---|---|
| 50 | 0.8702 | 0.8845 | 0.8947 |
| 75 | 0.8725 | 0.8851 | 0.8949 |
| 100 *(default)* | 0.8724 | 0.8863 | 0.8960 |
| 125 | 0.8722 | 0.8861 | 0.8957 |
| 150 | 0.8729 | 0.8859 | 0.8960 |

Accuracy rises slightly from 50 to 100 trees, then **plateaus completely**. Going
from 100 to 150 changes R² by at most 0.0001 while costing 50% more training time.

The scikit-learn default of 100 is a good choice here. There is no benefit to
tuning this upward.

### Effect of `max_features`

| `max_features` | Dataset 79 | Dataset 80 | Dataset 81 |
|---|---|---|---|
| `1.0` *(all features)* | 0.8724 | 0.8863 | 0.8960 |
| `"sqrt"` | 0.8671 | 0.8802 | 0.8884 |
| `"log2"` | 0.8663 | 0.8777 | 0.8867 |

Using **all** features at each split is consistently best, by about 0.008–0.009
over `sqrt` and slightly more over `log2`. The ordering holds on all three
datasets, and the margin grows with dataset size.

This is worth noting because `sqrt` is the scikit-learn default for
*classification* — applying that habit to this regression problem would cost
close to a percentage point.

### Effect of `bootstrap`

| `bootstrap` | Dataset 79 | Dataset 80 | Dataset 81 |
|---|---|---|---|
| `True` *(default)* | 0.8724 | 0.8863 | 0.8960 |
| `False` | 0.7546 | 0.7836 | 0.8037 |

This is the **single largest hyperparameter effect in the entire assessment**.
Disabling bootstrap costs 9–12 percentage points of R².

With `bootstrap=False` every tree is fitted on the identical full dataset. The
trees become highly correlated, and averaging correlated predictors recovers
almost none of the variance reduction that makes a forest work. Bootstrap
sampling is what makes the ensemble an ensemble.

**Leave `bootstrap` at `True`.**

### Random Forest summary

| Parameter | Recommendation | Cost of getting it wrong |
|---|---|---|
| `bootstrap` | `True` | Severe — up to 12 points of R² |
| `max_features` | `1.0` | Moderate — about 1 point |
| `n_estimators` | 100 | Negligible above 100 |
| `scaler_type` | Any | None |

Only one of these four is worth thinking about.

## Multi-layer Perceptron

The MLP was configured from the baseline in the software paper:
`hidden_layer_sizes` `[15, 15]`, `relu`, `adam`, `alpha` 1e-4, constant learning
rate, `learning_rate_init` 0.001, `max_iter` 500, `shuffle` true, `tol` 1e-3.
Each study varies one parameter from that baseline.

### Effect of `solver`

| `solver` | Dataset 79 | Dataset 80 | Dataset 81 |
|---|---|---|---|
| `adam` | 0.7758 | 0.7853 | 0.7918 |
| `sgd` | 0.6588 | 0.6888 | 0.6924 |
| `lbfgs` | 0.6444 | 0.4946 | 0.3364 |

`adam` is decisively best, and the failure of `lbfgs` is the striking result: it
gets **worse as the dataset grows**, collapsing from 0.64 to 0.34.

That direction is the opposite of every other trend in this assessment, and it is
the expected signature of a full-batch optimizer that has not converged. `lbfgs`
processes the entire dataset per iteration, so with `max_iter` fixed at 500 it
falls progressively further from convergence as rows are added. It is unsuited to
datasets of this size.

!!! note
    The manuscript flags this section as needing re-investigation. The pattern
    above is consistent with a convergence failure rather than a property of the
    solver itself — a rerun with a much larger `max_iter`, or with convergence
    warnings captured, would settle it.

**Use `adam`.**

### Effect of hidden layer sizes

| `hidden_layer_sizes` | Dataset 79 | Dataset 80 | Dataset 81 |
|---|---|---|---|
| `[10, 10]` | 0.7838 | 0.7816 | 0.7849 |
| `[15, 15]` *(baseline)* | 0.7758 | 0.7853 | 0.7918 |
| `[20, 20]` | 0.7906 | 0.7941 | 0.7942 |
| `[25, 25]` | 0.7947 | 0.7890 | 0.7957 |
| `[10, 10, 10]` | 0.7734 | 0.7814 | 0.7861 |
| `[15, 15, 15]` | 0.7902 | 0.7876 | 0.7905 |
| `[20, 20, 20]` | 0.7907 | 0.7987 | 0.7976 |
| `[25, 25, 25]` | 0.7952 | 0.8022 | **0.8027** |

Larger networks do better, with `[25, 25, 25]` best on all three datasets. But
the whole range spans only about 0.018 in R², and even the best MLP configuration
(0.8027) remains far below an untuned Random Forest (0.8960).

The trend has not flattened at three layers of 25, so wider or deeper networks
might improve further — though closing a 10-point gap by architecture search
alone looks unlikely.

### Effect of the remaining parameters

The other five studies produced differences at or below the level of
dataset-to-dataset scatter, with orderings that do not hold across all three
datasets. Values shown are for dataset 81:

| Parameter | Values tested | Range in R² | Consistent? |
|---|---|---|---|
| `activation` | `relu`, `logistic`, `tanh` | 0.7769 – 0.7918 | No — ordering flips between datasets |
| `alpha` | 5e-5, 1e-4, 2e-4 | 0.7846 – 0.7918 | No |
| `learning_rate` | `constant`, `invscaling`, `adaptive` | 0.7873 – 0.7918 | No |
| `learning_rate_init` | 1e-4, 2e-4, 5e-4, 1e-3 | 0.7801 – 0.7929 | Partly — the two larger values do better |
| `max_iter` | 50, 100, 200, 500 | 0.7865 – 0.7918 | No |
| `shuffle` | `true`, `false` | 0.7880 – 0.7918 | No |

Two of these deserve comment.

**`max_iter` is essentially flat.** Fifty iterations performs as well as 500
(0.7900 against 0.7918 on dataset 81). With `tol` at 1e-3, training is stopping
on the tolerance long before the iteration cap — so the cap is not the binding
constraint, and raising it will not help. This is also why the `lbfgs` result
above is worth rechecking: for that solver the cap may well be binding.

**`activation` shows no reliable winner.** `tanh` leads on dataset 79, `relu` on
80 and 81, `logistic` never. The spread is comparable to the noise between
datasets, so the honest reading is that this choice does not matter much at this
network size.

### MLP summary

| Parameter | Recommendation |
|---|---|
| `solver` | `adam` — the only choice that works |
| `hidden_layer_sizes` | Larger helps; `[25, 25, 25]` was best tested |
| Everything else | Defaults are fine; no reliable effect measured |

## Practical guidance

1. **Start with Random Forest defaults.** They beat every MLP configuration
   tested, with no tuning.
2. **Check `bootstrap` and `max_features`.** They are the only Random Forest
   settings that move the result.
3. **Do not spend effort on scaling for tree models.** It changes nothing.
4. **If using MLP, use `adam`**, and expect to remain well behind Random Forest.
5. **Validate hyperparameter findings across several datasets.** Several
   apparent MLP effects vanish when checked on a second dataset.
