# Optimizations in the Source

MLAP handles more raw data than fits comfortably in memory, and several
deliberate choices in the source exist to keep that tractable. They are
collected here because they are easy to miss when reading a single step, and
because two of them change the *numbers*, not just the runtime.

Line numbers refer to the `development` branch.

## What is optimized, and where

| Optimization | Purpose | Where |
|---|---|---|
| **`float16` arrays for all features, labels and elevation** | Quarter the memory of `float64` | [`Extract_DFM_Data_Helper.py`](https://github.com/LLNL/MLAP/blob/development/MachineLearningAutomationPipleline/Step1_ExtractData/Extract_DFM_Data_Helper.py) — 1088, 1227, 1231, 1235 |
| **`int32` index columns** (time, grid, `j`, `i`) | Halve the memory of `int64` | same file — 1219–1225 |
| **`reduce_data_size`** — `float64`→`float16`, `int64`→`int32` | Catch anything still at full width | [`Prepare_TrainTest_Data_Helper.py`](https://github.com/LLNL/MLAP/blob/development/MachineLearningAutomationPipleline/Step2_PrepareData/Prepare_TrainTest_Data_Helper.py) — 63 |
| **`int16` for computed class labels** | Class indices need one byte of range | same file — 266, 286 |
| **Temporal downsampling** — `percent_files_to_use` | Read a fraction of available time steps | [`Extract_DFM_Data.py`](https://github.com/LLNL/MLAP/blob/development/MachineLearningAutomationPipleline/Step1_ExtractData/Extract_DFM_Data.py) — 69, 171 |
| **Spatial downsampling** — `percent_grid_points_to_use` | Sample a fraction of grid points | same file — 70, 291 |
| **Row pruning** — `prune_data` | Drop rows outside a useful range before training | [`Prepare_TrainTest_Data.py`](https://github.com/LLNL/MLAP/blob/development/MachineLearningAutomationPipleline/Step2_PrepareData/Prepare_TrainTest_Data.py) — 167 |
| **Pickle checkpointing between stages** | Each step persists its output so the next never recomputes it | same file — 156, 290 |

The two downsampling controls are the ones with a documented effect on
accuracy — see [Data Sampling](../science/data-sampling.md). The rest are
invisible in the configuration.

## Precision: what `float16` costs

The data is `float16` from the moment it is extracted, not from Step 2 —
Step 1 allocates every feature, label and elevation array at that precision, so
`reduce_data_size` is already a no-op for those columns by the time it runs.

`float16` keeps about **3.3 significant decimal digits**. The absolute spacing
between representable values scales with magnitude, so the cost depends on the
size of the numbers a quantity is stored at:

| Quantity | Stored range | Spacing at the top of the range |
|---|---|---|
| `FM` (fraction) | 0–0.35 | 0.0002 |
| `RH` (%) | 0–100 | 0.06 |
| `UMag10` (m/s) | 0–30 | 0.016 |
| `T2` | 250–320 | **0.25** |
| `SWDOWN` (W/m²) | 0–1200 | 1.0 |
| `HGT` (m) | 0–4000 | 2.0 |

For labels and for features used directly, this sits below the noise in the
source data. Where it compounds is in a quantity *derived* from several of them.

!!! warning "VPD is computed in `float16` throughout"
    Because its inputs are `float16`, every stage of the
    [VPD calculation](../user-guide/step2-prepare.md#derived-features) stays in
    `float16` — the offset, the eighth-order saturation-pressure polynomial and
    the final subtraction. Precision is lost twice: the offset cancels most of
    the significant digits of `T2`, and \(VPD = e_s - e\) cancels again, the
    more so the higher the humidity.

    Measured against the same calculation in `float64`, over 200,000 realistic
    temperature and humidity pairs:

    | | Relative error in VPD |
    |---|---|
    | mean | **1.4%** |
    | 99th percentile | 3.9% |
    | worst case | 9.7% |
    | mean above 95% RH | 1.8% |

    This is a floor on how finely VPD can be resolved, and it is larger than the
    precision of any quantity it is built from. Casting the inputs up to
    `float32` for the derivation alone would remove it; the stored columns could
    stay `float16`.

Class labels are computed from the quantized values too, so a row whose true
`FM` sits within about \(1.5 \times 10^{-5}\) of a class boundary can fall on
either side of it. Against a `FM_binary_threshold` of 0.05 that band is too
narrow to matter.

!!! note "Quantizing the label is a different thing"
    Binary and multi-class labels quantize continuous FM *on purpose* — a
    threshold or a list of levels turns a real number into a class. That is the
    point of those label types, and is described under
    [Preparing labels](../user-guide/step2-prepare.md#preparing-labels). The
    precision reduction above is separate and applies whatever label type is in
    use, regression included.

## One optimization not taken

Models are constructed with default arguments
([`TrainModel_Helper.py`](https://github.com/LLNL/MLAP/blob/development/MachineLearningAutomationPipleline/Step3_TrainModel/TrainModel_Helper.py) — 96, 108):

```python
model = RandomForestRegressor()
```

`n_jobs` is left unset, so scikit-learn builds the forest on a **single core**.
Random Forest training parallelizes across trees almost perfectly, and the
[estimator-count study](../science/ml-parameters.md) runs up to several hundred
trees, so `n_jobs=-1` is the cheapest speed-up available anywhere in the
pipeline. It changes no result — only how long it takes to get one.
