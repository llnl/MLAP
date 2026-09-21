# Contributing

## Repository layout

```text
MachineLearningAutomationPipleline/   The pipeline — Step1..Step5, SimulationScripts
Others/                               Archived and miscellaneous code, not part of the pipeline
docs/                                 This documentation
mkdocs.yml                            Documentation configuration
```

## Where the logic lives

Each step is a thin driver plus a helper module. **The driver reads the JSON,
calls helpers in order, and writes output; the helpers hold the actual work.**
If you are looking for an algorithm, it is almost certainly in a helper.

| Helper | Lines | Functions | Responsibilities |
|---|---|---|---|
| `Step1_ExtractData/Extract_DFM_Data_Helper.py` | 1,434 | 30 | Sampling times and grid points, reading NetCDF, assembling history, building the DataFrame |
| `Step3_TrainModel/TrainModel_Helper.py` | 672 | 21 | Scaler and model construction, fitting, metrics, scatter and confusion plots |
| `Step2_PrepareData/Prepare_TrainTest_Data_Helper.py` | 345 | 15 | Pruning, derived features, binary and multi-class label construction |
| `Step5_Analyze/Analyze_Helper.py` | 180 | 8 | Timestamp parsing, region handling, reading HRRR and RRM sources |

`Extract_DFM_Data_Helper.py` is the largest file in the repository and carries
the sampling logic — `downsample_data_files`, `remove_data_around_fire`,
`get_fire_time_indices` — that determines what any dataset actually contains.

`Step4_EvalModels` has no helper; `EvaluateTrainedModels.py` is self-contained.

!!! note
    None of these modules have docstrings, so the function names are the only
    guide. Adding one while you are in a function is welcome — see
    [Docstrings](#docstrings).

## Working with the scripts

Each pipeline step is a `.py` file. Edit it directly and commit it — it is what
the batch scripts submit and what every result in the archive was produced by.

Each step reads its JSON input paths from `sys.argv`, which is how
`submit_multiple_runs.py` invokes it. A commented block of absolute paths sits
directly above, for running a step by hand during testing and experimentation —
uncomment and edit those, and restore `sys.argv` before committing.

!!! note "Notebooks in the repository"
    Some steps still carry a `.ipynb` beside the script, left from how the code
    was first written. They are not part of the pipeline and are not kept in
    step with the scripts. Do not edit a notebook expecting the change to reach
    a run.

## Adding a model

Models are constructed in `Step3_TrainModel/TrainModel_Helper.py`, which
dispatches on `model_name` and the label type. Adding one means:

1. Import the estimator.
2. Add a branch for the new `model_name` in both the regression and
   classification paths.
3. Document the name in the
   [JSON Reference](../user-guide/json-reference.md#models).

Hyperparameters need no code change — whatever appears in the `params` object is
passed through to the constructor.

## Adding a derived feature

Derived features are computed during [Step 2](../user-guide/step2-prepare.md).
VPD is the existing example. A new one needs a branch in the preparation helper
and an entry in `qois_derived`.

## Adding a raw data source

[Step 1](../user-guide/step1-extract.md#reading-other-data-sources) maps external
variable names onto MLAP's through objects like `SJSU_HRRR_Map`. Supporting a new
source means adding an analogous map, so long as the source provides a
counterpart for each required quantity.

## Docstrings

The pipeline currently has no docstrings — none of its 77 functions and classes
are documented. This is why the documentation is hand-written rather than
generated from the source.

If you are modifying a function, adding a docstring is welcome. Enough coverage
would make an API reference worth generating.

## Building the documentation

```bash
pip install -r requirements-docs.txt
mkdocs serve          # preview at http://127.0.0.1:8000
mkdocs build --strict # what CI runs; fails on broken links
```

Pages live under `docs/`, and the navigation is defined in `mkdocs.yml` — a new
page needs an entry there or `--strict` will flag it.

The site is published by `.github/workflows/docs.yml`, which builds and deploys
to GitHub Pages on every push to `master` or `development`. Both branches publish
to the same site, so whichever pushes last is what gets served.

## Documenting results

When adding scientific results, cite the metric CSVs from
[Step 4](../user-guide/step4-evaluate.md) rather than reading values off plots,
and report the dataset identifiers so a reader can locate the source. Where a
result has not been reproduced across more than one dataset, say so — several
apparent effects in the
[MLP study](../science/mlp.md#summary-of-the-eight-studies)
disappeared under that check.

## Reporting issues

Issues and pull requests: <https://github.com/LLNL/MLAP>

Contact: Pankaj K. Jha — pankaj.psu@gmail.com (primary), jha3@llnl.gov
