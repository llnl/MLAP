# MLAP — orientation

Machine Learning Automation Pipeline: relates a target variable to the history
of driving variables preceding it on a spatiotemporal grid, then trains and
compares models across a matrix of configurations. Built for wildfire fuel
moisture; the middle of the pipeline is domain-neutral.

## Layout

| Path | What it is |
|---|---|
| `MachineLearningAutomationPipleline/` | The pipeline, five steps plus `SimulationScripts/`. Note the spelling — it is misspelled in the repo and that is load-bearing for paths |
| `docs/` + `mkdocs.yml` | The documentation site (MkDocs Material) |
| `overrides/` | Two Material template overrides — see below |
| `Others/` | Archived and miscellaneous code, not part of the pipeline |
| `ForClaude/` | Results archive and draft papers. **Gitignored**, local reference only |
| `IMPROVEMENT_SCOPE.md` | Internal implementation critique. **Gitignored** — do not quote it into published pages |

Each step is a `.py` file and that file is the source of truth. Some steps still
carry a `.ipynb` beside them; those are history, not canonical, and are not kept
in step with the scripts.

Step scripts read their JSON input paths from `sys.argv`. A commented block of
absolute paths sits directly above for interactive testing — if you uncomment
those to test, restore `sys.argv` before committing, or batch jobs silently read
a fixed file instead of their arguments.

## Git topology

Two remotes, and they are not interchangeable:

- `llnl` → `github.com/LLNL/MLAP` — the real repository. **Pull requests go here**,
  base `development`. Its configured URL is the old capitalised path, so pushes
  print a "repository moved" notice; harmless.
- `pkjha` → `github.com/pkjha-aero/Wildfire_ML` — the fork. **Feature branches are
  pushed here**, and it mirrors `development`.

`development` is the integration branch; `master` is the default branch but is
not where work lands. Never commit directly to `development` — branch, PR, merge,
then fast-forward.

`gh-pages` on both remotes is the deployed site, written by
`.github/workflows/docs.yml` on every push to `development` or `master`. It is
not a feature branch. **Never delete it.**

The live site is `pkjha-aero.github.io/Wildfire_ML`. The `site_url` in
`mkdocs.yml` points at `software.llnl.gov/MLAP`, which 404s — GitHub Pages is not
enabled on `LLNL/MLAP`.

## Template overrides

`overrides/main.html` extends `base.html` and adds the Previous/Next strip — a
block extension, safe across upgrades.

`overrides/partials/header.html` is a **copy** of an upstream partial with only
the title block changed, to show a breadcrumb trail. On a mkdocs-material
upgrade, diff it against `material/templates/partials/header.html`.

## Working here

Documentation work has its own procedure — see the `mlap-docs` skill.

Claims in the docs are expected to be checkable. Figures such as collection
counts, dataset indices and metric values come from reading `ForClaude/` or the
source, not from recall.
