# MLAP Documentation Plan

Working plan for the MLAP documentation. Rewritten 2026-09-20 to record what is
built and to set out what remains.

## 1. Status

The documentation site is **built and live**. Seventeen pages covering a user
guide, a scientific assessment, the Claude Opus score card and a contributing
guide.

| | |
|---|---|
| Toolchain | MkDocs + Material theme, plain Markdown in `docs/` |
| Build | `.github/workflows/docs.yml`, `mkdocs build --strict` with link validation |
| Canonical URL | `https://software.llnl.gov/MLAP/` — **not yet live** |
| Live now | `https://pkjha-aero.github.io/Wildfire_ML/` |
| Merged so far | PRs #14, #15, #18, #19, #20, #21, #22, #23, #24 |

`llnl.github.io/MLAP` redirects to `software.llnl.gov/MLAP` — LLNL serves its
GitHub Pages under a custom domain. Enabling Pages on `LLNL/MLAP` needs
organisation-level access, which the author does not have; the fork publishes in
the meantime.

## 2. Completed

- **Scaffold and deployment** — MkDocs, Material, MathJax, GitHub Action, Pages
- **User guide** — installation, one page per pipeline step, HPC submission
- **JSON reference** — every parameter across all five steps and the driver
- **Scientific assessment** — data sampling, historical data, Random Forest
  parameters, physical quantities, and the MLP study on its own page
- **Design assessment** — independent review of the automation architecture
- **Figures** — 37 assets: 23 from the manuscripts, 14 from the simulation output
- **Presentation** — three-level nested sidebar, integrated page TOC, ReadTheDocs
  code-block styling

## 3. Source material

Local reference material lives in `ForClaude/` at the repo root. It is
**gitignored** and must never be committed.

| Path | Contents |
|---|---|
| `EMS_Paper_2024_10_23_PKJ_Only.docx` | Software paper — complete. 9 tables, 18 figures, appendices A.1–A.5 |
| `AI4ES_Paper_WIP_2026_09_18.docx` | Science paper — work in progress, 28 figures |
| `Wildfire_Results/` | Simulation output, formerly `Wildfire_Scratch` |

Published results archive:
<https://drive.google.com/drive/folders/1Mi1s9He0AsPTgG9OjPES-twJyBbZREdV>

## 4. Provenance approach

Results in the documentation must be traceable to the runs that produced them.

**The identifier is the primary mechanism, not the link.** Every study cites its
evaluation collection — `eval_015_RF_estimator_effect` — and every dataset cites
its `data_set_count`. These are location-independent: they identify a run whether
the archive sits on Google Drive, a DOI, or an LLNL filesystem.

**The archive location is stated once.** A single pointer on the Science overview
page says where the results live. If the location changes, one line changes
rather than twenty.

### Recommendation: move to a DOI when convenient

Google Drive is fine as an interim but is weak for published science:

- Folder links break when permissions, ownership or folder structure change
- No version history, so "the results as of the paper" cannot be pinned
- Not citable — a reviewer cannot cite a Drive URL
- Not archival — it disappears if the account does

**Zenodo** would be the better home: a permanent DOI, versioned, citable in the
AI4ES paper, and free for records up to 50 GB. The 582 MB archive fits
comfortably. Uploading the `Output/Step4_Eval` tree alone — 757 metric CSVs plus
plots — would cover everything the documentation cites.

Until then, the Drive link serves, and the identifiers mean nothing breaks when
it is replaced.

## 5. Outstanding work

From the coverage audit of 2026-09-20. The two manuscripts are fully accounted
for; these gaps are in the source code and simulation output.

| # | Gap | Status |
|---|---|---|
| 1 | Only 5 of 27 evaluation collections are named in the docs | **To do** |
| 2 | `Trends/` — 28 plots, 2015–2099, entirely undocumented | **Deferred** |
| 3 | Four of five per-model config files unmentioned | **To do** |
| 4 | SVM and MLP hyperparameters not documented | **To do** |
| 5 | Three `_Helper.py` modules never mentioned | **To do** |
| 6 | `Step2_PrepData` and `Step5_Analyze` outputs unused | **Excluded** |

### 1. Collection provenance

Roughly twenty studies have their results documented but no link back to the
collection that produced them. This undercuts the traceability the design
assessment praises. Each science section should name its source collection, and
the Science overview should carry the archive pointer.

### 3. Per-model configuration files

The repository ships `json_train_model_{GB,Linear,MLP,RF,SVM}.json`. Only the
Random Forest one appears in the documentation.

### 4. Model hyperparameters

The JSON reference describes `params` as passed through to the scikit-learn
constructor without documenting what belongs there. The MLP set appears only in
the science pages; the SVM set appears nowhere.

### 5. Helper modules

`Extract_DFM_Data_Helper.py` (1,434 lines — the largest file in the repository),
`Prepare_TrainTest_Data_Helper.py` and `Analyze_Helper.py` are never mentioned.
A reader navigating the source will not know the logic lives there.

### 2. Trends — deferred

Twenty-eight plots spanning 2015–2020, 2029–2034, 2044–2049 and 2094–2099. Those
decades indicate future climate projections, likely E3SM regionally refined model
output. Neither manuscript covers this work. **Needs the author's input on what
it is and whether it belongs in the documentation.**

### 6. Unused simulation output — excluded

`Output/Step2_PrepData` (260 label distributions) and `Output/Step5_Analyze`
(21 fuel maps) are not used; the documentation uses the manuscript's versions of
these figures instead. Excluded by decision, not oversight.

## 6. Defects carried forward

1. **Manuscript error — confirmed by the author.** The AI4ES paper states that R²
   rises with temporal sample size. Every metric shows the opposite: test R² falls
   0.8216 → 0.8001 and RMSE rises 0.0288 → 0.0301 as sampled reference times go
   2,000 → 4,999. The documentation states the correct direction. **The
   manuscript still needs the same fix.**

2. **MLP training appears to stop prematurely.** `tol` is 1e-3 while the converged
   training MSE is 0.0014, so the stopping threshold is roughly 70% of the entire
   final loss. Train and test R² are within 0.0025 of each other, which is
   underfitting rather than overfitting. All eight MLP studies ran under this
   criterion and are marked provisional. A rerun with `tol` at 1e-6 is the single
   highest-value follow-up.

3. **`features_to_read` → `qois_to_read` rename is incomplete.** The code and
   in-repo configs are correct. Remaining: EMS Appendix A.1 still shows the old
   key; 14 local variable names in `Extract_DFM_Data_Helper.py` and
   `Analyze.py:462` still use it; and all archived Step 1 configs use the old key
   and **will not run** against current code.

4. **EMS Table 6 omits a scaler.** It states four options and lists three; the
   code supports `Standard` as well, which is what the Random Forest
   configuration uses.

5. ~~**Command-line input is commented out.**~~ Fixed: all seven step scripts
   now read their JSON paths from `sys.argv`, with the absolute development
   paths kept commented above for testing and experimentation.

6. **No docstrings.** 0 of 77 functions and classes. Forecloses API autodoc.

Items 3–6 and the wider engineering gaps are covered in `IMPROVEMENT_SCOPE.md`
(gitignored).

## 7. Open questions

- **GitHub Pages on `LLNL/MLAP`** — needs an organisation owner. Until then the
  canonical URL stays dark.
- **`Trends/` provenance** — what is this work, and does it belong here?
- **Zenodo DOI** — worth doing before the AI4ES paper cites these results.
