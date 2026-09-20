# JSON Reference

Every parameter across all five steps, in one page. Use your browser's find, or
the search box above.

Parameters are documented as the **code reads them**. Where the published papers
differ, the code is authoritative and the difference is noted.

---

## Step 1 — Extract Data

`json_extract_data.json`

### `paths`

| Key | Type | Description |
|---|---|---|
| `data_files_location` | string | Directory holding the raw hourly reanalysis files |
| `extracted_data_base_loc` | string | Where the extracted dataset is written |

### `data_set_defn`

| Key | Type | Description |
|---|---|---|
| `data_set_count` | int | Identifier for this dataset. Zero-padded to three digits in filenames and carried through every later step |
| `percent_files_to_use` | float | Percentage of the 21 years of hourly files to sample |
| `percent_grid_points_to_use` | float | Percentage of valid grid points to sample per reference time |
| `max_history_to_consider` | int | \(t_{max\_history}\) — how far back to read atmospheric data, in hours |
| `history_interval` | int | \(t_{history}\) — interval at which history is sampled, in hours |

Number of historical times is \(t_{max\_history} / t_{history}\), and feature
count is \(n_{history} \times n_{QoIs} + 1\) (the \(+1\) being elevation).

### `sampling_type`

| Key | Type | Options | Description |
|---|---|---|---|
| `sample_first` | string | `"time"`, `"space"` | Whether times or grid points are sampled first |
| `time` | string | `"random"`, `"uniform"` | Temporal sampling strategy |
| `space` | string | `"random"`, `"uniform"` | Spatial sampling strategy |

### `nevada_data`

Removes the Nevada portion of the domain, since the study focuses on California.

| Key | Type | Description |
|---|---|---|
| `remove_nevada` | bool | Whether to exclude Nevada grid points |
| `j_nevada`, `i_nevada` | int | Grid indices defining the Nevada cut |
| `j_anchor`, `i_anchor` | int | Anchor indices for that cut |

### `features_labels`

| Key | Type | Description |
|---|---|---|
| `qois_to_read` | list | Time-varying quantities to extract, e.g. `["UMag10", "T2", "RH", "PRECIP", "SWDOWN"]` |
| `labels_to_read` | list | FM categories to extract, e.g. `["FM_10hr", "FM_100hr"]` |
| `labels_ind_in_nc_file` | list | Index of each label within the NetCDF file |
| `SJSU_HRRR_Map` | object | Maps MLAP quantity names to HRRR variable names |
| `SJSU_RRM_Maps` | object | Maps MLAP quantity names to E3SM RRM variable names |

!!! warning "Renamed from `features_to_read`"
    This key is `qois_to_read`. It was previously `features_to_read`, renamed
    because the list holds quantities of interest — features are those
    quantities multiplied by the number of history times.

    All archived example configurations under
    `Wildfire_Scratch/InputJson/Extract/` still use the old key and **will not
    run against current code** without updating it.

Available quantities:

| Name | Definition |
|---|---|
| `UMag10` | Wind speed magnitude at 10 m (m/s) |
| `U10`, `V10` | Wind components at 10 m |
| `T2` | Air temperature at 2 m (°C) |
| `RH` | Relative humidity (%) |
| `PRECIP` | Precipitation (cm) |
| `SWDOWN` | Solar shortwave downward flux |
| `HGT` | Elevation — extracted by default, fixed in time |

### `fire_flags`

| Key | Type | Description |
|---|---|---|
| `remove_fire_data_from_train_test` | bool | Exclude data from named fire events from training |
| `extract_fire_data` | bool | Extract data for named fire events |

### `data_in_a_file`

| Key | Type | Description |
|---|---|---|
| `prescribe_file_flag` | bool | `true` reads a specific file; `false` picks one at random from the sample |
| `data_file_to_read` | string | Filename, e.g. `"wrf_2018-11-07_16.nc"`. The timestamp is parsed out of this name |

### `fire_time_stamps`

Named fire events, each with a reference, start, and end time in
`YYYY-MM-DD_HH` format:

```json
"Woosley": {"Ref": "2018-11-08_22", "Start": "2018-11-01_00", "End": "2018-11-15_00"}
```

### `clip_data_train_test`

| Key | Type | Description |
|---|---|---|
| `x_clip` | list or null | Bounds restricting eligible x grid indices; `null` means no clipping |
| `y_clip` | list or null | Bounds restricting eligible y grid indices |

This is how you confine a study to a sub-region such as the Central Valley.

### `qoi_to_plot` and `plot_options`

Diagnostic plotting only — these do not affect the extracted data.

| Key | Type | Description |
|---|---|---|
| `contours` | list | Quantities to draw as contour plots |
| `pdfs` | list | Quantities to draw as probability density plots |
| `contours_with_cb` | list | Quantities to draw with a color bar |
| `cont_levels_count` | int | Number of contour levels |
| `qoi_cont_range` | list | Value range for contours, e.g. `[0, 0.3]` |

`plot_options` holds booleans switching each diagnostic on or off:
`plot_sampled_datetime`, `plot_contours_of_indices`, `plot_contours_of_qoi`,
`plot_pdfs_of_qoi`, `plot_fm_contours_with_cb`, `plot_sampled_grid_indices_2d`,
`plot_sampled_grid_indices_3d`.

---

## Step 2 — Prepare Data

`json_prep_data_label.json`

### `paths`

| Key | Type | Description |
|---|---|---|
| `prepared_data_base_loc` | string | Where the prepared dataset is written |

### `label_defn`

| Key | Type | Description |
|---|---|---|
| `label_count` | int | Identifier for this label configuration, zero-padded to three digits downstream |

### `FM_labels`

| Key | Type | Description |
|---|---|---|
| `label_type` | string | `"Regression"`, `"Binary"`, or `"MultiClass"` |
| `FM_binary_threshold` | float | Binary only. FM above it → label `0` (moist); at or below → label `1` (dry, fire-prone) |
| `FM_MC_levels` | list | MultiClass only. Class boundaries, need not be uniform |

### `features`

| Key | Type | Description |
|---|---|---|
| `qois_to_use` | list | Quantities to use as features — a subset of `qois_to_read`, optionally with `HGT` |
| `qois_derived` | list | Derived quantities to compute. Currently `["VPD"]` |

!!! note "Name shortening"
    Prepared data uses `PREC` and `SW` where extracted data uses `PRECIP` and
    `SWDOWN`.

### `prune_data`

Variable-to-range pairs limiting which rows are kept:

```json
"prune_data": { "FM_10hr": [0.00001, 0.3] }
```

Several variables may be pruned at once. This removes rows from training, and is
unrelated to the `test_p95` / `test_p90` metrics.

### `qoi_to_plot`

| Key | Type | Description |
|---|---|---|
| `FM_hr` | int | Which FM category to plot, e.g. `10` |

---

## Step 3 — Train Models

`json_train_model_<MODEL>.json`

### `paths`

| Key | Type | Description |
|---|---|---|
| `trained_model_base_loc` | string | Where trained models and metrics are written |

### `train_options`

| Key | Type | Description |
|---|---|---|
| `train_from_scratch` | bool | `true` trains fresh; `false` loads an existing model and evaluates it |
| `save_train_data` | bool | Retain the training split |
| `save_test_data` | bool | Retain the test split |

### `models`

| Key | Type | Description |
|---|---|---|
| `model_count` | int | Identifier for this model configuration |
| `scaler_type` | string | `"Standard"`, `"MinMax"`, `"MaxAbs"`, or `"Robust"` |
| `test_data_frac` | float | Fraction held out for testing, e.g. `0.2` |
| `model_name` | string | `"Linear"`, `"SVM"`, `"RF"`, `"MLP"`, or `"GB"` |
| `params` | object | Hyperparameters passed to the scikit-learn constructor. `{}` uses defaults |

!!! warning "Paper lists only three scalers"
    EMS Table 6 states four scaling options are available but lists only
    `MinMax`, `MaxAbs` and `Robust`. The fourth is `Standard`
    (`StandardScaler`), which is what the repository's Random Forest
    configuration uses. An unrecognized value raises a `ValueError`.

Model mapping:

| `model_name` | Regression | Classification |
|---|---|---|
| `"Linear"` | `LinearRegression` | — |
| `"SVM"` | `SVR` | `SVC` |
| `"RF"` | `RandomForestRegressor` | `RandomForestClassifier` |
| `"MLP"` | `MLPRegressor` | `MLPClassifier` |
| `"GB"` | `GradientBoostingRegressor` | `GradientBoostingClassifier` |

#### `models.params`

Whatever appears here is handed straight to the scikit-learn constructor, so any
argument that estimator accepts is valid and MLAP needs no change to support it.
An empty `{}` uses scikit-learn defaults, which is what the Linear, Random Forest
and Gradient Boosting configurations do.

Two of the shipped configurations populate it. The values below are what the
repository ships, not recommendations — see
[ML Parameters](../science/ml-parameters.md) and
[Multi-layer Perceptron](../science/mlp.md) for what the studies found.

**`json_train_model_MLP.json`** — `MLPRegressor` / `MLPClassifier`:

| Key | Shipped value | Meaning |
|---|---|---|
| `hidden_layer_sizes` | `[15, 15]` | Neurons per hidden layer |
| `activation` | `"relu"` | `"identity"`, `"logistic"`, `"tanh"`, `"relu"` |
| `solver` | `"adam"` | `"lbfgs"`, `"sgd"`, `"adam"` |
| `alpha` | `0.0001` | L2 penalty strength |
| `batch_size` | `"auto"` | Minibatch size for `sgd` / `adam` |
| `learning_rate` | `"constant"` | `"constant"`, `"invscaling"`, `"adaptive"` — `sgd` only |
| `learning_rate_init` | `0.001` | Initial step size |
| `power_t` | `0.5` | Exponent for `"invscaling"` |
| `max_iter` | `500` | Maximum iterations (epochs for `sgd` / `adam`) |
| `shuffle` | `true` | Reshuffle samples each iteration |
| `random_state` | `null` | Seed for reproducibility |
| `tol` | `0.001` | Convergence tolerance — see the warning below |
| `verbose` | `true` | Print progress |
| `warm_start` | `false` | Reuse the previous solution |
| `momentum` | `0.9` | Momentum for `sgd` |
| `nesterovs_momentum` | `true` | Nesterov momentum for `sgd` |
| `early_stopping` | `false` | Stop on validation score instead of loss |
| `validation_fraction` | `0.1` | Hold-out fraction when `early_stopping` is on |
| `beta_1`, `beta_2` | `0.9`, `0.999` | `adam` decay rates |
| `epsilon` | `1e-8` | `adam` numerical stability |
| `n_iter_no_change` | `10` | Iterations without improvement before stopping |
| `max_fun` | `15000` | Maximum loss-function calls for `lbfgs` |

!!! warning "`tol` is too loose at this label scale"
    Training stops when the loss fails to improve by more than `tol` for
    `n_iter_no_change` consecutive iterations. The shipped value of `1e-3` is
    close to the converged training MSE of about `0.0014`, so the criterion fires
    almost immediately and the network underfits. It is also ten times looser
    than scikit-learn's own default of `1e-4`. See
    [Why the MLP underperforms Random Forest](../science/mlp.md#why-the-mlp-underperforms-random-forest).

**`json_train_model_SVM.json`** — `SVR` / `SVC`:

| Key | Shipped value | Meaning |
|---|---|---|
| `kernel` | `"rbf"` | `"linear"`, `"poly"`, `"rbf"`, `"sigmoid"`, `"precomputed"` |
| `degree` | `3` | Polynomial degree — `"poly"` only |
| `gamma` | `"scale"` | Kernel coefficient; `"scale"`, `"auto"`, or a float |
| `coef0` | `0.0` | Independent term — `"poly"` and `"sigmoid"` |
| `tol` | `0.001` | Stopping tolerance |
| `C` | `1.0` | Regularization strength; lower means stronger |
| `shrinking` | `true` | Use the shrinking heuristic |
| `cache_size` | `200` | Kernel cache in MB |
| `verbose` | `true` | Print progress |
| `max_iter` | `-1` | Iteration limit; `-1` means no limit |

!!! note "SVM cost"
    Kernel SVMs scale poorly beyond roughly 10,000 samples, and the datasets here
    run to millions of rows. No SVM results appear in the
    [scientific assessment](../science/overview.md) for that reason. Raising
    `cache_size` helps somewhat; a `"linear"` kernel is far cheaper than `"rbf"`.

### `features_labels`

| Key | Type | Description |
|---|---|---|
| `qois_for_training` | list | Subset of prepared features to train on. Varying this drives feature-importance studies |
| `label_log` | bool | Whether to take the logarithm of the label |

### `evaluation`

Plot appearance only.

| Key | Type | Description |
|---|---|---|
| `max_data_size_scatter` | int | Maximum points drawn in a scatter plot |
| `fig_size_x`, `fig_size_y` | int | Figure dimensions |
| `font_size` | int | Plot font size |
| `x_lim` | list | Axis limits, e.g. `[0, 0.35]` |
| `normalize_cm` | bool | Normalize the confusion matrix |

---

## Step 4 — Evaluate Models

`json_eval_sample.json`

### `paths`

| Key | Type | Description |
|---|---|---|
| `eval_model_base_loc` | string | Where collection outputs are written |
| `sim_dir` | string | Root simulation directory |
| `json_extract_base` | string | Path template for Step 1 configs, relative to `sim_dir` |
| `json_prep_base` | string | Path template for Step 2 configs |
| `json_train_base` | string | Path template for Step 3 configs |

Identifiers are appended as `_%03d.json`, so `39` under
`InputJson/Extract/json_extract_data` resolves to
`json_extract_data_039.json`.

### `collection_options`

| Key | Type | Description |
|---|---|---|
| `json_extract_counts` | list | Dataset identifiers forming one axis of the collection matrix |
| `json_prep_train_maps` | list | Groups of (label, model) identifiers forming the other axis |
| `FM_label_type` | string | `"Regression"` or a classification type |
| `metric_names` | list | Metrics to compute |
| `metric_on_sets` | list | Datasets to compute them on |

Each entry of `json_prep_train_maps`:

| Key | Type | Description |
|---|---|---|
| `json_label` | list | Step 2 label identifiers |
| `json_train` | list | Step 3 model identifiers |
| `set_info` | list | Descriptive label for the base feature set, used in plot legends |
| `subset_info` | list | Descriptive labels for each variant, parallel to `json_train` |

`set_info` and `subset_info` are descriptive only — nothing verifies they match
what the referenced configurations do.

Available metrics:

| Metric | Definition |
|---|---|
| `r2_score` | R-squared |
| `ev_score` | Explained variance score |
| `mse` | Mean squared error |
| `rmse` | Root mean squared error |
| `max_err` | Maximum error |
| `mae` | Mean absolute error |
| `medae` | Median absolute error |

Available sets:

| Set | Definition |
|---|---|
| `train` | Training data after scaling |
| `test` | Test data after scaling |
| `test_p95` | Best 95% of test data, ranked by prediction error |
| `test_p90` | Best 90% of test data, ranked by prediction error |

### `evaluation`

| Key | Type | Description |
|---|---|---|
| `count` | int | Collection identifier |
| `identifier_text` | string | Descriptive name. Combines into the output directory name, e.g. `eval_001_many_cases` |

---

## Step 5 — Analyze and Predict

`json_analyze.json`

### `paths`

| Key | Type | Description |
|---|---|---|
| `analysis_data_base_loc` | string | Where predictions and plots are written |
| `raw_data.SJSU` | string | Reanalysis data location |
| `raw_data.HRRR` | string | HRRR forecast data location |
| `raw_data.RRM` | string | E3SM regionally refined model data location |

### Top-level keys

| Key | Type | Description |
|---|---|---|
| `analysis_count` | int | Identifier for this analysis |
| `analysis_data_desired` | list | Which sources to run against, e.g. `["SJSU", "HRRR", "RRM"]` |

### Per-source request lists

Each named source takes a list of requests:

| Key | Type | Description |
|---|---|---|
| `RefTime` | string | Prediction time, `YYYY-MM-DD_HH` |
| `regions_x_indices` | list of lists | x grid-index bounds per region |
| `regions_y_indices` | list of lists | y grid-index bounds per region |

The x and y lists pair elementwise — first x-range with first y-range is region 1.
Regions may differ between reference times.

### `analysis`

Plot appearance, same keys as Step 3's `evaluation` block.

---

## Simulation driver

`json_simulate.json` — see [Running on HPC](running-on-hpc.md).

### `paths`

| Key | Type | Description |
|---|---|---|
| `sim_dir` | string | Root simulation directory |
| `sbatch_scripts.base` | string | Directory holding the batch scripts |
| `sbatch_scripts.{extract,prep,train}` | string | Batch script filenames |
| `python_scripts.base` | string | Pipeline root directory |
| `python_scripts.{extract,prep,train}` | string | Driver script paths, relative to that base |
| `json_base.{extract,prep,train}` | string | Config path templates, relative to `sim_dir` |

### Top-level keys

| Key | Type | Description |
|---|---|---|
| `action` | string | `"Extract"`, `"Prep"`, or `"Train"` — controls how many nested loops run |
| `exempt_flag` | string | Passed straight to `sbatch`, for queue flags |

### `execution_options`

| Key | Type | Description |
|---|---|---|
| `print_interactive_command` | bool | Print the plain `python …` command |
| `print_sbatch_command` | bool | Print the `sbatch …` command |
| `run_interactively` | bool | **Execute** locally, in sequence |
| `submit_job` | bool | **Submit** to Slurm |

### `collection_options`

| Key | Type | Description |
|---|---|---|
| `json_extract_counts` | list | Step 1 identifiers to iterate |
| `json_prep_counts` | list | Step 2 identifiers to iterate |
| `json_train_counts` | list | Step 3 identifiers to iterate |

Total jobs is the product of the lists `action` reaches, so verify the count with
a dry run before submitting.
