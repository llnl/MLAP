# MLAP Documentation Plan

Working plan for building user and scientific documentation for the Machine
Learning Automation Pipeline (MLAP). Branch: `documentation` (off `development`).

## 1. Goal

Two bodies of documentation, published as one searchable site:

1. **User guide** — how to run the pipeline: the five steps, the HPC submission
   workflow, and a complete reference for the JSON files that drive everything.
2. **Scientific description** — what the simulations show: the effect of data
   sampling, history parameters, ML hyperparameters, and physical quantities on
   fuel moisture (FM) prediction accuracy.

## 2. Decisions made

| Decision | Choice |
|---|---|
| Toolchain | MkDocs + Material theme |
| Hosting | GitHub Pages on `LLNL/MLAP` → `llnl.github.io/MLAP` |
| Source format | Plain Markdown in `docs/` |
| Build | GitHub Action publishing to `gh-pages` |
| Figures | Committed to `docs/assets/` (2.4 MB total) |
| Phase 4 scope | Write the manuscript's "To Do" sections **where simulation results exist** |
| Plot interpretation | Show the plot and ask before asserting a conclusion |

### Why MkDocs rather than Sphinx/ReadTheDocs

- Source stays plain Markdown, so it still renders on github.com if the build
  ever breaks.
- Search matters here: the Step 1 config alone exposes ~40 JSON keys.
- Sphinx's main advantage is `autodoc`, which is worthless in this repo —
  **docstring coverage is 0% across all 77 functions and classes**.
- GitHub Pages keeps hosting inside the LLNL org with no third-party account.

## 3. Source material

All source material lives in `ForClaude/` at the repo root. It is **gitignored**
(594 MB) and must never be committed.

### Manuscripts

| File | Role | State |
|---|---|---|
| `EMS_Paper_2024_10_23_PKJ_Only.docx` | Software / methods paper | **Complete.** 9 parameter tables, 18 figures, appendices A.1–A.5 with full sample JSON |
| `AI4ES_Paper_WIP_2026_09_18.docx` | Science / results paper | **Work in progress.** 28 figures; roughly half the results sections are empty stubs |

The EMS paper is effectively a ready-made user manual. The AI4ES paper is the
science source but is incomplete.

### Simulation output — `ForClaude/Wildfire_Scratch/`

| Path | Contents |
|---|---|
| `InputJson/Extract/` | 20 sample Step 1 configs (`json_extract_data_039..058.json`) |
| `Output/Step2_PrepData/` | 260 files — label distributions |
| `Output/Step3_Train/` | 6,045 files — per-model scatter plots and eval CSVs |
| `Output/Step4_Eval/` | 2,217 files across 27 `eval_*` directories, including **757 metric CSVs** |
| `Output/Step5_Analyze/` | 22 files — FM maps for California and subregions |
| `Trends/` | 28 FM trend plots, 2015–2099 (provenance unclear — see open questions) |

The `eval_*` directory names map almost 1:1 onto AI4ES section headings, and the
CSVs contain the numbers for studies the manuscript has not yet written up.

### Source code

`MachineLearningAutomationPipleline/` — 11 Python files, 6,341 LOC:

- `Step1_ExtractData/`, `Step2_PrepareData/`, `Step3_TrainModel/`,
  `Step4_EvalModels/`, `Step5_Analyze/`, `SimulationScripts/`
- 10 JSON config files, one per step (five for Step 3, one per model)
- The `.py` files are `jupyter nbconvert` exports of the `.ipynb` notebooks;
  notebooks are canonical, sbatch runs the generated `.py`

## 4. Target structure

```
docs/
  index.md                     Overview, schematics, citation, LLNL release info
  user-guide/
    installation.md
    step1-extract.md
    step2-prepare.md
    step3-train.md
    step4-evaluate.md
    step5-analyze.md
    running-on-hpc.md          sbatch scripts + submit_multiple_runs.py
    json-reference.md          All parameters, one searchable page
  science/
    overview.md                Approach, data source, methods
    data-sampling.md           Temporal and spatial data size
    history.md                 max_history_to_consider, history_interval
    ml-parameters.md           Random Forest and MLP hyperparameters
    physical-quantities.md     Elevation, PRECIP, SWDOWN, RH/T2/VPD
  assets/                      46 figures extracted from the manuscripts
mkdocs.yml
requirements-docs.txt
.github/workflows/docs.yml
```

## 5. Phases

### Phase 0 — Scaffold and prove deployment

Build `mkdocs.yml`, `requirements-docs.txt`, a stub `docs/index.md`, and the
GitHub Action. Get one real page live before writing any prose, so deployment
problems surface immediately rather than at the end.

**Risk to resolve first:** whether GitHub Pages can be enabled on `LLNL/MLAP`.
Merge rights on the repo do not guarantee Pages permission at the org level. If
Pages is blocked, fall back to Markdown rendering on github.com — the source
format is identical, so no work is lost.

**Done when:** `llnl.github.io/MLAP` serves a page built by CI.

### Phase 1 — Extract and name figures

Extract 46 PNGs from `word/media/` in both `.docx` files into `docs/assets/`,
renamed descriptively (`fig-mlap-stages.png`, not `image4.png`). Captions are
already recoverable from the manuscript text; produce a manifest mapping each
figure to its caption and destination page.

**Done when:** every figure is named, placed, and attributed to a source paper.

### Phase 2 — User guide (from the EMS paper)

Highest-value work: the source is complete and this is what an external user
needs. One page per pipeline step following the paper's structure, pairing its
prose with the actual config file in the repo.

Also covers the `.ipynb → nbconvert → .py → sbatch` developer workflow and its
staleness risk.

**Done when:** a new user can run all five steps from the docs alone.

### Phase 3 — JSON parameter reference

The single searchable page that justifies the toolchain. Built by reading the
**code**, then cross-checked against the paper's Tables 1, 4, 5, 6 and 7.

This ordering is deliberate — paper and code have already drifted (section 6).
Every discrepancy gets reported rather than silently resolved.

**Done when:** every JSON key the code reads is documented, and every drift is
either fixed or logged.

### Phase 4 — Science section

Two tiers, clearly distinguished in the text.

**Tier 1 — sections the manuscript completes.** Written from the paper, with the
R² error (section 6) corrected:

| Section | Source |
|---|---|
| Effect of temporal data size | `eval_002_temporal_data_effect` |
| Effect of spatial data size | `eval_003_spatial_data_effect` |
| Effect of maximum history | `eval_011_max_hist_effect` |
| Effect of history interval | `eval_026_temp_resol` |
| Effect of elevation | `eval_004_elevation_effect` |

**Tier 2 — sections marked "To Do" that have results.** Written from the CSVs
and flagged in the text as derived from simulation output not yet in the
manuscript:

| Section | Source |
|---|---|
| RF: data scaling | `eval_014_RF_scaling_effect` |
| RF: estimators | `eval_015_RF_estimator_effect` |
| RF: max_features | `eval_016_RF_max_features_effect` |
| RF: bootstrap | `eval_017_RF_bootstrap_effect` |
| MLP: hidden layers, activation, solver, alpha, learning rate, lr init, max_iter, shuffle | `eval_018` … `eval_025` |
| Dropping PRECIP and SWDOWN | `eval_005_precip_flux_effect` |
| RH / T2 / VPD substitution | `eval_006`, `eval_007`, `eval_008`, `eval_009`, `eval_010`, `eval_012` |

**Tier 3 — cannot be written.** These sections are marked "To Do" in the
manuscript and have **no corresponding results** in `Wildfire_Scratch`. They
stay out of the docs until the simulations are run:

- Effect of terrain ruggedness as a feature
- Effect of selecting data for specific months
- Effect of selecting data from a specific region
- Cross-application of trained models in time
- Cross-application of trained models in space

**Done when:** Tiers 1 and 2 are written with numbers and plots; Tier 3 is
listed as future work.

### Phase 5 — Integration

README points at the site; cross-links between user guide and science sections;
navigation and search verified.

## 6. Known issues to resolve while writing

1. **Manuscript error — confirmed.** AI4ES states "as the number of sampled data
   files increases, the R2 increases." The data shows the opposite: in
   `eval_002_temporal_data_effect`, as sampled reference times go
   2,000 → 3,000 → 3,999 → 4,999, test R² falls 0.8216 → 0.8001 and RMSE rises
   0.0288 → 0.0301, consistently across train, test, and best-95% metrics. The
   docs will state the correct direction. **The manuscript needs the same fix.**

2. **`features_to_read` → `qois_to_read` rename is incomplete.** The JSON key
   was deliberately renamed to `qois_to_read`. The code and the in-repo configs
   are correct and need no change; three trailing references remain:

   - **EMS Appendix A.1 still shows `features_to_read`** — a manuscript fix, not
     a code fix. The paper is internally inconsistent, since its Table 1 already
     uses `qois_to_read`. Docs will document `qois_to_read`.
   - **Internal variable and parameter names still say `features_to_read`** —
     14 occurrences in `Extract_DFM_Data_Helper.py`, plus
     `Analyze.py:462` (`features_to_read = features_labels['qois_to_read']`).
     These are local names, not JSON keys, so nothing is broken; it is a
     cosmetic inconsistency. Left alone unless you want it cleaned up.
   - **All 20 archived configs in `Wildfire_Scratch/InputJson/Extract/` use the
     old key** and none use the new one. They record how the published results
     were produced but **will not run against the current code**. They must not
     be reused as example configs in the docs without updating the key.

3. **Undocumented config key.** The code reads `ref_time_indices`, which the
   repo's sample config does not define.

4. **Notebook / script staleness.** `Extract_DFM_Data.ipynb` is newer than its
   generated `Extract_DFM_Data.py`, which is what sbatch actually runs.

5. **No docstrings.** 0 of 77 functions and classes are documented. Out of scope
   for this plan, but it forecloses API autodoc and is worth a follow-up.

## 7. Open questions

- **GitHub Pages permission** on `LLNL/MLAP` — blocks Phase 0 if denied.
- **`Trends/` provenance.** 28 plots spanning 2015–2099 suggest future climate
  projections, but neither manuscript covers this. Include, or leave out?
- **Plot interpretation.** Where a conclusion depends on reading a figure rather
  than a CSV, the plot gets shown for a decision before anything is asserted.
