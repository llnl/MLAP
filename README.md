# Machine Learning Automation Pipeline (MLAP)
- This is developed for wildfire analysis to begin with
- Architected in a way that it can be adapted to other ML problems.

# Documentation

| Site | Status | URL |
|---|---|---|
| Documentation site | **[Not yet live]** | https://software.llnl.gov/MLAP/ |
| Development mirror | **[Live and up-to-date]** | https://pkjha-aero.github.io/Wildfire_ML/ |

`software.llnl.gov/MLAP` is the canonical home — LLNL serves its GitHub Pages
under that domain, so `llnl.github.io/MLAP` redirects there. It goes live once
GitHub Pages is enabled on this repository. Until then, read the documentation
at the development mirror, which is built from the same sources:

- [User Guide](https://pkjha-aero.github.io/Wildfire_ML/user-guide/installation/) — installation and a page per pipeline step
- [JSON Reference](https://pkjha-aero.github.io/Wildfire_ML/user-guide/json-reference/) — every input parameter, searchable
- [Scientific Assessment](https://pkjha-aero.github.io/Wildfire_ML/science/overview/) — what the simulations show
- [Design Assessment](https://pkjha-aero.github.io/Wildfire_ML/design-assessment/) — independent review of the automation architecture

# Results archive

The simulation output behind the documentation — 27 evaluation collections, 757
metric CSVs, the Step 1 input configurations, and `WildfireDataDefn.xlsx`, the
experiment registry recording which features every run used:

**https://drive.google.com/drive/folders/1Mi1s9He0AsPTgG9OjPES-twJyBbZREdV**

See [Results archive](https://pkjha-aero.github.io/Wildfire_ML/science/overview/#results-archive)
for its layout and how to trace any documented number back to the run that
produced it.

The pipeline has five stages, each driven by a JSON input file:

| Step | Purpose |
|---|---|
| 1 | Extract a subsampled training set from 21 years of raw data |
| 2 | Prepare features and labels for regression or classification |
| 3 | Train ML models and compute metrics |
| 4 | Compare many models across many datasets |
| 5 | Predict fuel moisture at a chosen time and region |

Source lives in `MachineLearningAutomationPipleline/`; `Others/` holds archived
and miscellaneous code that is not part of the pipeline.

To build the documentation locally:

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

# Sponsorship
This work was performed under the auspices of the U.S. Department of Energy by Lawrence Livermore National Laboratory under Contract `DE-AC52-07NA27344` and was supported by the LLNL-LDRD Program under Project No. `22-SI-008.`

This work was prepared as an account of work sponsored by an agency of the
United States Government. Neither the United States Government nor Lawrence
Livermore National Security, LLC, nor any of their employees makes any warranty,
expressed or implied, or assumes any legal liability or responsibility for the
accuracy, completeness, or usefulness of any information, apparatus, product, or
process disclosed, or represents that its use would not infringe privately owned
rights. Reference herein to any specific commercial product, process, or service
by trade name, trademark, manufacturer, or otherwise does not necessarily
constitute or imply its endorsement, recommendation, or favoring by the United
States Government or Lawrence Livermore National Security, LLC. The views and
opinions of authors expressed herein do not necessarily state or reflect those
of the United States Government or Lawrence Livermore National Security, LLC,
and shall not be used for advertising or product endorsement purposes.

# License
This software package is an Unclassified/Open-Source Distribution under the terms of the MIT license and has been approved by Lawrence Livermore National Laboratory for unrestricted release.

# Project, repository, and authorship

MLAP is developed by **Pankaj K. Jha** at **Lawrence Livermore National
Laboratory (LLNL)**.

| | |
|---|---|
| **Author** | Pankaj K. Jha |
| **Institution** | Lawrence Livermore National Laboratory (LLNL) |
| **Main repository** | https://github.com/LLNL/MLAP |
| **Documentation site** | **[Not yet live]** https://software.llnl.gov/MLAP/ |
| **Development mirror** | **[Live and up-to-date]** https://pkjha-aero.github.io/Wildfire_ML/ |
| **Release ID** | LLNL-CODE-2001016 |
| **Release title** | Machine Learning Automation Pipeline (MLAP), v 1.0 |
| **License** | MIT |
| **Contact** | pankaj.psu@gmail.com (primary), jha3@llnl.gov |
