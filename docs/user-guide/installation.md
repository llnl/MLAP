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

## Getting the code

```bash
git clone https://github.com/LLNL/MLAP.git
cd MLAP
```

The pipeline lives in `MachineLearningAutomationPipleline/`:

```text
MachineLearningAutomationPipleline/
├── Step1_ExtractData/
├── Step2_PrepareData/
├── Step3_TrainModel/
├── Step4_EvalModels/
├── Step5_Analyze/
└── SimulationScripts/
```

`Others/` holds archived and miscellaneous code that is not part of the pipeline.

## The scripts are the source of truth

Each pipeline step is a `.py` file, and that file is what runs and what you
edit. The batch scripts submit it directly.

```text
MachineLearningAutomationPipleline/Step1_ExtractData/Extract_DFM_Data.py
```

!!! note "Notebooks in the repository"
    Some steps still carry a `.ipynb` alongside the script, left from how the
    code was first written. They are **not** part of the pipeline and are not
    kept in step with the scripts, so treat them as history rather than as
    something to edit and convert.

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

!!! tip "Running a step without arguments, for testing"
    Each script reads its JSON paths from `sys.argv`, which is how the batch
    scripts invoke it. Directly above those lines sits a commented block of
    absolute paths:

    ```python
    # Input file paths for testing and experimentation.
    # Uncomment and edit these to run the script outside the batch system.

    #json_file_extract_data = '/p/lustre2/.../json_extract_data_022.json'

    # Input file paths taken from the command line.
    # This is how the batch scripts invoke this file, and the normal path.

    json_file_extract_data = sys.argv[1]
    ```

    Uncomment and edit them to run a step interactively with fixed inputs.
    Leave the committed copy on `sys.argv`, or batch jobs will silently read
    whichever file the absolute paths point at instead of their arguments.

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
