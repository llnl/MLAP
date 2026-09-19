# Contributing

## Repository layout

```text
MachineLearningAutomationPipleline/   The pipeline — Step1..Step5, SimulationScripts
Others/                               Archived and miscellaneous code, not part of the pipeline
docs/                                 This documentation
mkdocs.yml                            Documentation configuration
```

## Working with the notebooks

Each pipeline step exists as a notebook and a generated script. **The notebook is
canonical.** After editing one, regenerate its script:

```bash
jupyter nbconvert --to python Extract_DFM_Data.ipynb
```

Commit both. The batch scripts run the `.py`, so a notebook edit that is not
converted has no effect on a submitted job — it silently runs the old code.

!!! warning "Known staleness"
    Some `.py` files in the repository are currently older than their notebooks.
    If you touch a step, check that its script is regenerated before relying on
    batch results.

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
[MLP study](../science/ml-parameters.md#effect-of-the-remaining-parameters)
disappeared under that check.

## Reporting issues

Issues and pull requests: <https://github.com/LLNL/MLAP>

Contact: Pankaj K. Jha — pankaj.psu@gmail.com (primary), jha3@llnl.gov
