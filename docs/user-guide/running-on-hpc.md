# Running on HPC

Running one case by hand is fine. Parametric studies mean hundreds of cases, and
that is what `SimulationScripts/` automates.

## Nomenclature

Automation depends on a naming convention. Each step's configuration carries an
integer identifier:

| Step | Identifier key | Example file |
|---|---|---|
| 1 — Extract | `data_set_count` | `json_extract_data_039.json` |
| 2 — Prepare | `label_count` | `json_prep_data_label_006.json` |
| 3 — Train | `model_count` | `json_train_model_013.json` |

Identifiers are **zero-padded to three digits** (`%03d`). A trained model is then
identified by the triple — dataset 39, label 6, model 13 — and that triple
propagates into every output filename and into
[Step 4](step4-evaluate.md)'s collection matrix.

Naming discipline here is what makes a study of hundreds of runs interpretable
afterwards.

## Directory layout

Both `submit_multiple_runs.py` and [Step 4](step4-evaluate.md) reconstruct file
paths from a simulation directory plus these identifiers, so the layout matters:

```text
<sim_dir>/
└── InputJson/
    ├── Extract/  json_extract_data_039.json, _040.json, …
    ├── Prep/     json_prep_data_label_006.json, …
    └── Train/    json_train_model_013.json, …
```

## The submission driver

`submit_multiple_runs.py` generates and optionally submits commands for whole
collections of cases. It is configured by `json_simulate.json`:

```json
{
    "paths": {
        "sim_dir": ".../Wildfire_LDRD_SI",
        "sbatch_scripts": {
            "base": ".../SimulationScripts",
            "extract": "sbatch_script_extract.sh",
            "prep": "sbatch_script_prep.sh",
            "train": "sbatch_script_train.sh"
        },
        "python_scripts": {
            "base": ".../MachineLearningAutomationPipleline",
            "extract": "Step1_ExtractData/Extract_DFM_Data.py",
            "prep": "Step2_PrepareData/Prepare_TrainTest_Data.py",
            "train": "Step3_TrainModel/TrainModel.py"
        },
        "json_base": {
            "extract": "InputJson/Extract/json_extract_data",
            "prep": "InputJson/Prep/json_prep_data_label",
            "train": "InputJson/Train/json_train_model"
        }
    },
    "action": "Train",
    "execution_options": {
        "print_interactive_command": false,
        "print_sbatch_command": true,
        "run_interactively": false,
        "submit_job": false
    },
    "exempt_flag": "",
    "collection_options": {
        "json_extract_counts": [39, 40, 41],
        "json_prep_counts": [6, 7],
        "json_train_counts": [13, 14]
    }
}
```

### `action` selects which stage to submit

`action` launches jobs for **that stage only**. It does not run the preceding
stages.

| `action` | Jobs submitted | Identifier lists used | Count from the example above |
|---|---|---|---|
| `"Extract"` | Step 1 only | extract | 3 |
| `"Prep"` | Step 2 only | extract × prep | 3 × 2 = 6 |
| `"Train"` | Step 3 only | extract × prep × train | 3 × 2 × 2 = 12 |

The lists are nested because a job is identified by the full triple, not because
earlier stages are re-run. With `action` set to `"Train"`, every job is a
**training** job; the extract and prep identifiers say *which already-extracted
dataset and already-prepared labels it trains on*. Dataset 39, label 6, model 13
names a training run against data that must already exist.

A modest-looking set of lists expands quickly — check the count before
submitting.

!!! tip "The staging is deliberate — verify between stages"
    Running the three stages separately, rather than chaining them, is a design
    choice worth preserving.

    Submit all extractions, then **inspect the extracted data before going
    further**. Only once they look right, submit the preparation jobs against
    those datasets. Only once the prepared data look right, submit training.

    Automatic chaining would mean a flawed extraction silently produces prepared
    data and trained models built on it — spending the compute and, worse,
    producing plausible-looking results from bad inputs. The manual gate between
    stages is what prevents that.

### `execution_options` controls what actually happens

| Flag | Effect |
|---|---|
| `print_interactive_command` | Print the plain `python …` command |
| `print_sbatch_command` | Print the `sbatch …` command |
| `run_interactively` | **Execute** locally, in sequence |
| `submit_job` | **Submit** to Slurm |

!!! tip "Dry run first"
    The defaults print the sbatch commands without submitting. Leave
    `submit_job` as `false`, inspect the generated commands, and only then set it
    to `true`. This is the cheapest way to catch a wrong path or an accidentally
    enormous collection.

`exempt_flag` is passed straight through to `sbatch`, for queue flags such as an
exemption or reservation.

## The batch scripts

The three `sbatch_script_*.sh` files are thin wrappers. Each takes the Python
script followed by the JSON files its step requires:

```bash
sbatch sbatch_script_train.sh TrainModel.py extract.json prep.json train.json
```

The script body reduces to:

```bash
python $python_script $json_extract_data $json_prepare_data $json_train_model
```

The Slurm header carries LLNL-specific settings that you will need to change:

```bash
#SBATCH -J wildfire_train
#SBATCH -N 1
#SBATCH --partition=quartz
#SBATCH -t 24:00:00
#SBATCH -A cr4ns
#SBATCH -p pbatch
```

!!! warning "Adjust before running elsewhere"
    The account (`-A cr4ns`) and partition are specific to LLNL clusters. Note
    also that partition is set twice — `--partition=quartz` and `-p pbatch` — and
    the later flag wins. Set one, not both.

## Environment activation

The scripts expect to run inside an already-active conda or virtualenv
environment. Activation lines are present but commented out:

```bash
# RUN THIS SCRIPT FROM A conda ENVIRONMENT
#conda activate py3_ml
#source $HOME/VirtualEnv/py3_ml_wind/bin/activate
```

Either activate your environment before submitting, or uncomment and edit the
line matching your setup.

## Suggested workflow for a study

1. Decide what you are varying and write one JSON per variant, numbered
   consistently.
2. Place them under `<sim_dir>/InputJson/{Extract,Prep,Train}/`.
3. Set `action` to the first stage you need and list the identifiers.
4. Dry-run with `submit_job: false` and read the commands.
5. Submit, then repeat for the next stage.
6. Collect the results with [Step 4](step4-evaluate.md), giving the collection a
   descriptive `identifier_text`.
