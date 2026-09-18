# Installation

## Requirements

MLAP is pure Python and relies on the scientific Python stack:

| Package | Used for |
|---|---|
| `numpy` | Array handling throughout |
| `pandas` | Extracted and prepared data are pandas DataFrames |
| `scikit-learn` | All ML models, scalers, and metrics |
| `matplotlib` | Plots at every step |
| `netCDF4` | Reading raw reanalysis files |
| `jupyter` | Notebooks are the canonical source (see below) |

## Getting the code

```bash
git clone https://github.com/LLNL/MLAP.git
cd MLAP
```

The pipeline lives in `MachineLearningAutomationPipleline/`:

```
MachineLearningAutomationPipleline/
├── Step1_ExtractData/
├── Step2_PrepareData/
├── Step3_TrainModel/
├── Step4_EvalModels/
├── Step5_Analyze/
└── SimulationScripts/
```

`Others/` holds archived and miscellaneous code that is not part of the pipeline.

## Notebooks are the source of truth

Each step exists as both a notebook and a script. **The notebook is canonical**;
the `.py` file is generated from it:

```bash
jupyter nbconvert --to python Extract_DFM_Data.ipynb
```

The batch scripts run the generated `.py` file, not the notebook. So the workflow
is:

1. Edit the `.ipynb`
2. Regenerate the `.py` with `nbconvert`
3. Submit the `.py` via sbatch

!!! warning "Regenerate before submitting"
    If you edit a notebook and forget to re-run `nbconvert`, your batch job
    silently runs the **old** code. Some `.py` files in the repository are
    currently older than their notebooks.

## Running a step

Every step takes its JSON input file(s) as command-line arguments. Each step
needs the configuration of all preceding steps, so the argument list grows:

```bash
# Step 1 — extract
python Extract_DFM_Data.py json_extract_data.json

# Step 2 — prepare
python Prepare_TrainTest_Data.py json_extract_data.json json_prep_data_label.json

# Step 3 — train
python TrainModel.py json_extract_data.json json_prep_data_label.json json_train_model_RF.json
```

For running many cases on a cluster, see [Running on HPC](running-on-hpc.md).

## Data paths

The JSON files carry absolute paths to input data and output locations, for
example:

```json
"paths": {
    "data_files_location": "/p/vast1/climres/DFM_reanalysis",
    "extracted_data_base_loc": "/p/lustre2/jha3/Wildfire/Wildfire_LDRD_SI/01_WRF_Nelson_Data_Extracted"
}
```

These point at LLNL filesystems. **Change them to your own locations before
running anything.** See the [JSON Reference](json-reference.md) for every path
parameter.
