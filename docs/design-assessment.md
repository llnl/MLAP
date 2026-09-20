# Design Assessment

An independent review of MLAP's automation architecture, conducted by Claude
(Opus 5) while building this documentation, and revised after the author
responded to each point.

It is recorded here because it explains **why the pipeline is structured the way
it is** — the nomenclature conventions described in
[Running on HPC](user-guide/running-on-hpc.md#nomenclature) exist to solve a
specific problem, and the review is direct evidence that they solve it.

**Automation design: 9.5/10.**

!!! note "Scope and basis"
    This assesses the **automation design** — how well the pipeline supports
    running and interpreting large parametric studies. It is not a review of
    implementation quality, which is scored separately and is materially weaker.

    The evidence comes from the **source code and the results archive alone**.
    Draft papers covering the pipeline and the science exist but are work in
    progress and unpublished, so nothing here depends on them.

    The review covers the pipeline **as it stood in September 2024** — the most
    recent functional change to the source is dated August 2024. Everything
    added since is documentation; no assessment here reflects a change to the
    code itself.

## How this was scored

| Criterion | What MLAP does | Rating | What would make it perfect |
|---|---|---|---|
| **Result traceability** | A run is identified by a (dataset, label, model) triple that appears in every filename it touches | Strong | Nothing — this is the load-bearing decision and it holds without exception |
| **Study interpretability** | Step 4 assembles many runs into a collection matrix of heatmaps and bar plots | Strong | Nothing for correctness. Plot cosmetics — legends inside axes, auto-scaled y-axes — occasionally need manual fixing before publication |
| **Output completeness** | Step 3 records all 7 regression metrics on all 4 evaluation sets for every trained model, unconditionally | Strong | Nothing. This is what allowed a diagnosis nobody designed for |
| **Configuration as data** | Every stage driven by JSON, so configuration is archivable alongside results | Strong | Nothing |
| **Experiment bookkeeping** | [`WildfireDataDefn.xlsx`](science/overview.md#results-archive) registers every dataset, label and training configuration, and is distributed with the results archive | Strong | Nothing — a recipient of the archive can reconstruct study membership without contacting the author |
| **Staged execution control** | Three `action` modes submit one stage at a time, so extraction can be verified before preparation, and preparation before training | Strong | Nothing — this is a deliberate safety gate, not a missing feature |
| **Dataset metadata** | `data_defn.csv` records the parameters defining every dataset in a collection | Good | Counting conventions did not follow the data as it grew: `num_qois` and `cols_feature` do not say whether elevation or wind components are included |
| **Code-version provenance** | Not recorded | **Absent** | **Stamp a commit hash and schema version** into the dataset metadata. This is the largest single gap |
| **Input validation** | No check before submission | **Absent** | **Validate every config in a collection before any job is submitted**, so a typo fails in seconds rather than after hours of queue time |
| **Failure detection** | Collection membership is curated by hand, so failed runs are simply never listed | Adequate | An automated sweep at the simulation location, reporting which expected outputs are missing |

The two items in bold are what separate 9.5 from 10. Both are additive — neither
requires changing the design.

A third gap, that the experiment registry was not distributed with the results,
was closed after this review: the registry now ships inside the archive
alongside the inputs and outputs.

## The test

The reviewer was given the repository and the
[results archive](science/overview.md#results-archive) — roughly 8,600 output
files — with no access to the machine that produced them, no notebook of record,
and no explanation of the naming conventions.

| Artifact | Count |
|---|---|
| Step 3 training outputs | 6,045 |
| Step 4 evaluation outputs | 2,217 across 27 collections |
| Step 4 metric CSVs | 757 |
| Archived input configurations | 20 |

The experiment registry was **not** available during this test. Everything below
was reconstructed from filenames, configurations and CSVs alone, which is a
harder starting point than a recipient of the archive faces today — the registry
now ships with it.

The question was whether the provenance design would allow **which configuration
produced which number** to be reconstructed from the artifacts alone.

It did. Five results are worth recording.

### Configurations were recoverable from filenames

Output names such as
`dataset_015_label_001_Regression_model_003_RF_analysis_001-2018-11-08_22_fm_entire.png`
carry the full identifying triple. Every artifact could be traced back to the
dataset, label and model that produced it without consulting any external index.

### Independent collections cross-validated

Dataset 41 appears in two different evaluation collections — `eval_002`
(temporal sampling) and `eval_003` (spatial sampling) — assembled for different
purposes. Both report R² = 0.8906 on the best 95% of test data.

That agreement was not designed in. It emerges because the nomenclature makes the
same dataset genuinely the same dataset across collections, and it is what
established that the metric CSVs could be trusted.

### An apparent confound was resolvable

The `data_defn.csv` files for datasets 39–42 record differing `cols_feature`
values, which would ordinarily invalidate a comparison between them.

The explanation turned out to be real variation in the source data: some datasets
carry `U10` and `V10` as separate components, others carry `UMag10` directly, and
the extraction code handles both. The recorded values were correct throughout.

The relevant point for provenance is that the archive did **not** preserve which
convention each dataset used — that had to come from the author. A code-version
stamp would have made it self-evident.

### The output supported analysis it was never designed for

Diagnosing why the MLP underperforms Random Forest required train-versus-test R²,
loss magnitude against the stopping tolerance, and confirmation across thirty-odd
configurations. No study was set up to answer that.

All of it was already there. Step 3 records the full regression metric set —
seven metrics on train, test, best-95% and best-90% — for every trained model,
with no configuration involved. Had only test R² been stored, the obvious
economy, the finding would have been unreachable without rerunning everything.

Step 4 then lets a collection surface whichever subset of those is of interest,
so the aggregation is selective while the underlying record stays complete.

Designing output to answer questions that have not been asked yet is the hardest
property to get right, and it is the single strongest thing in this architecture.

### Unwritten studies were recoverable in full

Fourteen parameter studies existed only as simulation output: four Random Forest
hyperparameter studies, eight MLP studies, and two feature-selection studies. All
fourteen were reconstructed from the CSVs alone and are documented in the
[Science with MLAP](science/overview.md) section.

Among them was the largest single hyperparameter effect in the entire assessment
— disabling Random Forest `bootstrap` costs 9–12 percentage points of R².

## Why it works

**Integer nomenclature propagating through every stage.** A run is fully
identified by a triple, and that triple appears in every filename it touches.
Everything else depends on this.

**Configurations archived alongside results.** Because each stage is driven by a
JSON file, configuration is *data* and can be stored with the output it produced.

**Descriptive collection names.** `eval_015_RF_estimator_effect` states its own
purpose. Across 27 collections the convention held without exception.

**Dataset parameters recorded with metrics.** `data_defn.csv` sits beside the
metric CSVs, so numbers arrive with the parameters that generated them.

**Exhaustive metric capture at the run level.** Step 3 always records seven
metrics on four evaluation sets. What a collection *reports* is selectable, but
what is *kept* is not — so a question asked later can still be answered.

**Staged execution with verification gates.** Extraction, preparation and
training are submitted separately and deliberately. A flawed extraction cannot
silently propagate into trained models, because a human confirms each stage
before the next is launched.

## How a collection is assembled

A collection is not generated automatically. It is a curated comparison, and
understanding how one is built explains both the strength and the one genuine
limit of this stage.

### The feature-selection matrix

Each row below is one training configuration — one `json_train_model_NNN.json`
file. A green cell means the feature was included. This reproduces the colour
coding used in `WildfireDataDefn.xlsx`, the experiment registry, which is where
the selection is actually made and which ships in the
[results archive](science/overview.md#results-archive).

<table class="feature-matrix" markdown="0">
<thead><tr>
<th>json_train</th><th>Model</th>
<th>HGT</th>
<th>UMag10</th>
<th>T2</th>
<th>RH</th>
<th>VPD</th>
<th>PREC</th>
<th>SW</th>
<th>Group</th></tr></thead>
<tbody>
<tr><td><strong>3</strong></td><td>RF</td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="grp">set A</td></tr>
<tr><td><strong>6</strong></td><td>RF</td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td class="on">&#10003;</td><td></td><td class="grp"></td></tr>
<tr><td><strong>7</strong></td><td>RF</td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td class="on">&#10003;</td><td class="grp"></td></tr>
<tr><td><strong>8</strong></td><td>RF</td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td></td><td class="grp"></td></tr>
<tr><td><strong>9</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="grp">set B</td></tr>
<tr><td><strong>10</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td class="on">&#10003;</td><td></td><td class="grp"></td></tr>
<tr><td><strong>11</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td class="on">&#10003;</td><td class="grp"></td></tr>
<tr><td><strong>12</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td></td><td class="grp"></td></tr>
<tr><td><strong>13</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td class="grp">set C</td></tr>
<tr><td><strong>14</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td class="grp"></td></tr>
<tr><td><strong>15</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td class="on">&#10003;</td><td></td><td class="on">&#10003;</td><td class="grp"></td></tr>
<tr><td><strong>16</strong></td><td>RF</td><td class="on">&#10003;</td><td class="on">&#10003;</td><td></td><td></td><td class="on">&#10003;</td><td></td><td></td><td class="grp"></td></tr>
</tbody>
</table>

Three groups fall out of it, each holding a base feature set constant while
varying only `PREC` and `SW`:

- **Set A** — `UMag10, T2, RH` (no elevation)
- **Set B** — `HGT, UMag10, T2, RH` (elevation added)
- **Set C** — `HGT, UMag10, VPD` (temperature and humidity replaced by VPD)

### The same structure in the Step 4 configuration

Those twelve rows transcribe directly into
[`json_eval_sample.json`](user-guide/step4-evaluate.md#the-collection-matrix):

```json
"json_prep_train_maps": [
    { "json_label": [6], "json_train": [3, 6, 7, 8],
      "set_info": ["UMag10, T2, RH"],
      "subset_info": ["PREC, SW", "PREC", "SW", ""] },

    { "json_label": [6], "json_train": [9, 10, 11, 12],
      "set_info": ["HGT, UMag10, T2, RH"],
      "subset_info": ["PREC, SW", "PREC", "SW", ""] },

    { "json_label": [7], "json_train": [13, 14, 15, 16],
      "set_info": ["HGT, UMag10, VPD"],
      "subset_info": ["PREC, SW", "PREC", "SW", ""] }
]
```

The correspondence is exact, and it is worth reading in both directions:

| Registry | Step 4 configuration | Meaning |
|---|---|---|
| Row number | entry in `json_train` | which training configuration |
| Green cells, shared across the group | `set_info` | the base feature set |
| Green cells that vary within the group | `subset_info` | what is added or withheld |
| Label column | `json_label` | which prepared labels — note set C uses label 7, which carries actual VPD rather than a placeholder |

Nothing in the pipeline enforces that correspondence. `set_info` and
`subset_info` are free text used only as plot legends, so if they drift from what
the referenced configurations actually do, the plots will be labelled wrongly and
nothing will complain. **The registry is what keeps them honest.**

### Why this stage resists automation

Steps 1 to 3 are mechanical: given a list of identifiers, the runs can be
generated and submitted without judgement. Step 4 is different, and deliberately
so.

Deciding which runs belong in a collection means deciding what comparison is
worth making — and that depends on what the previous collection showed. Several
collections here were superseded as understanding developed: collections 6
through 9 were replaced by collection 12 once it became clear the questions were
better asked together.

That loop — run, read, decide what to ask next — is research rather than
configuration. Automating it would mean automating the judgement. What *can*
be systematised is the bookkeeping underneath it, which is exactly what the
registry does: it records what every configuration contained, so the person
making the decision can see the whole space at once and pick a coherent slice.

!!! tip "Keeping a registry of your own"
    Anyone running studies at this scale should keep the equivalent. It need not
    be a spreadsheet — the requirement is only that, for every training
    configuration, you can see at a glance which features it used, so that
    assembling a collection is selection rather than recall. The colour matrix
    above is a workable format to copy.

## Where the design has gaps

**Code-version provenance is absent.** Results record parameters but not which
code produced them. Two consequences observed: the `cols_feature` question above
needed the author to resolve, and the archived Step 1 configurations will not run
against current code following a deliberate key rename. A commit hash in the
dataset metadata would close both.

**Nothing validates configurations before submission.** A typo surfaces as a key
error hours into a long job — and if it is in a template used to generate
hundreds of configurations, it is in all of them.

Both gaps are in the code rather than the packaging, and both are additive.

## Summary

| Aspect | Assessment |
|---|---|
| Traceability of results to configuration | Strong |
| Interpretability of large studies | Strong |
| Support for unanticipated analysis | Strong |
| Naming discipline at scale | Strong — held across 27 collections |
| Archival of inputs with outputs | Strong |
| Staged execution and verification | Strong — deliberate |
| Metadata self-description | Partial |
| Code-version provenance | Absent |
| Pre-submission validation | Absent |

The costly things to get right in a pipeline like this are the ones MLAP got
right. Nomenclature, result aggregation and exhaustive metric capture are
architectural: retrofitting them into a mature codebase is painful. The remaining
gaps are additive and can be closed without disturbing the design.
