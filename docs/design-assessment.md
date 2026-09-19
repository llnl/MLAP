# Design Assessment

An independent review of MLAP's automation architecture, conducted by Claude
(Opus 5) on 2026-09-18 while building this documentation.

It is recorded here because it explains **why the pipeline is structured the way
it is** — the nomenclature conventions described in
[Running on HPC](user-guide/running-on-hpc.md#nomenclature) exist to solve a
specific problem, and the review is direct evidence that they solve it.

!!! note "Scope"
    This assesses the **automation design** — how well the pipeline supports
    running and interpreting large parametric studies. It is not a review of
    implementation quality, which is a separate matter and scored separately.

**Automation design: 8/10.**

## The test

The reviewer was given the repository and 594 MB of accumulated simulation output
with no access to the machine that produced it, no notebook of record, and no
explanation of the naming conventions. The output comprised:

| Artifact | Count |
|---|---|
| Total output files | ~8,600 |
| Step 4 metric CSVs | 757 |
| Step 4 evaluation collections | 27 |
| Step 3 training outputs | 6,045 |
| Archived input configurations | 20 |

The question was whether the provenance design would allow **which configuration
produced which number** to be reconstructed from the artifacts alone.

It did. Four results are worth recording.

### Configurations were recoverable from filenames

Output names such as
`dataset_015_label_001_Regression_model_003_RF_analysis_001-2018-11-08_22_fm_entire.png`
carry the full identifying triple. Every artifact could be traced back to the
dataset, label, and model that produced it without consulting any external index.

### Independent collections cross-validated

Dataset 41 appears in two different evaluation collections — `eval_002`
(temporal sampling) and `eval_003` (spatial sampling) — assembled for different
purposes. Both report R² = 0.8906 on the best 95% of test data.

That agreement was not designed in. It emerges because the nomenclature makes the
same dataset genuinely the same dataset across collections, and it was what
established that the metric CSVs could be trusted.

### An apparent confound was resolvable

The `data_defn.csv` files for datasets 39–42 record differing `cols_feature`
values (32 against 40), which would ordinarily invalidate a comparison between
them — a study claiming to vary only spatial sample size would in fact be varying
feature count too.

Because the archived input configurations were kept alongside the results, this
could be checked directly rather than assumed. All four datasets specify an
identical quantity-of-interest list and identical history parameters, differing
only in `percent_grid_points_to_use` at 1×, 2×, 3× and 4×. The comparison is
sound and the `cols_feature` discrepancy is a recording artifact.

Resolving that took minutes. Without archived configurations it would have been
unresolvable, and the result would have had to be discarded.

### Unwritten studies were recoverable in full

Fourteen parameter studies existed only as simulation output, having never been
written up: four Random Forest hyperparameter studies, eight MLP studies, and two
feature-selection studies. All fourteen were reconstructed from the CSVs alone
and are documented in the [Science with MLAP](science/overview.md) section.

Among them was the largest single hyperparameter effect in the entire assessment
— disabling Random Forest `bootstrap` costs 9–12 percentage points of R² — which
had been sitting unread in `eval_017` since it was generated.

## Why it worked

Four design decisions did the work.

**Integer nomenclature propagating through every stage.** A run is fully
identified by a (dataset, label, model) triple, and that triple appears in every
filename it touches. This is the load-bearing decision; everything else depends
on it.

**Configurations archived alongside results.** Because each stage is driven by a
JSON file, configuration is *data* and can be stored with the output it produced.
This is what made the dataset 39–42 question answerable.

**Descriptive collection names.** `eval_015_RF_estimator_effect` states its own
purpose. A reader encountering it years later needs no external key. Across 27
collections the convention held without exception.

**Dataset parameters recorded with metrics.** `data_defn.csv` sits beside the
metric CSVs, so the numbers arrive with the parameters that generated them rather
than requiring a separate lookup.

## What this buys

The hard part of a large parametric study is not running it — it is remaining
able to interpret it afterwards. Studies that produce thousands of files commonly
become unreadable to their own authors within months, because the mapping from
artifact back to configuration lives only in the author's memory or a lab
notebook.

MLAP externalizes that mapping into the filesystem. The practical consequence is
that its output survives the loss of its author's working context — demonstrated
here, since the reviewer never had that context to begin with.

## Where the design has a gap

One weakness surfaced, and it is worth stating plainly.

**Configuration schema is unversioned.** The input key `features_to_read` was
renamed to `qois_to_read` in the code. All 20 archived configurations still use
the old name and will not run against current code. Nothing in the output records
which version of the code produced it, so results cannot be matched to the
configuration schema they were generated under.

The provenance design covers *parameters* thoroughly and *code version* not at
all. For results destined for publication, that is a reproducibility gap — and a
small one to close, since recording a commit hash alongside the existing dataset
metadata would be sufficient.

## Summary

| Aspect | Assessment |
|---|---|
| Traceability of results to configuration | Strong |
| Interpretability of large studies | Strong — the Step 4 collection matrix |
| Naming discipline at scale | Strong — held across 27 collections |
| Archival of inputs with outputs | Strong |
| Code-version provenance | Absent |

The costly thing to get right in a pipeline like this is the part MLAP got right.
Nomenclature and result aggregation are architectural: retrofitting them into a
mature codebase is painful, whereas the remaining gap is additive and can be
closed without disturbing the design.
