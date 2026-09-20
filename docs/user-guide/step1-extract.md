# Step 1: Extract Data

**Driver:** `Step1_ExtractData/Extract_DFM_Data.py`
**Config:** `json_extract_data.json`

```bash
python Extract_DFM_Data.py json_extract_data.json
```

## What this step does

The raw reanalysis dataset — 21 years of hourly data on a 3 km grid — is far too
large to train on in its entirety. Step 1 draws a manageable subsample across
both time and space, and assembles it into a pandas DataFrame.

Sampling in **time** captures diurnal, seasonal, and interannual variability
(El Niño and similar). Sampling in **space** captures topographic variation
across mountains, valleys, and coastline.

Each row of the output is one **(reference time, grid point)** pair: the FM
values at that time and place, plus the history of atmospheric quantities
leading up to it.

## Temporal sampling

`percent_files_to_use` sets how many hourly files to sample. Each sampled file
provides one reference time, \(t_{ref}\), at which FM is taken as the dependent
variable. Sampling can be random or uniform, set by `sampling_type`.

## Spatial sampling

Two parameters control the spatial side:

- **`clip_data_train_test`** restricts which grid indices are eligible. The
  default excludes ocean points (FM is computed everywhere in the domain
  regardless of surface cover) and Nevada, since the focus is California. You can
  narrow this further — to the Central Valley or the coastal ranges, for example.
- **`percent_grid_points_to_use`** sets how many points to draw from those valid
  indices, for each sampled time.

Grid points are re-drawn independently for each reference time, which helps keep
the resulting dataset unbiased.

!!! note "Sampling order"
    `sampling_type.sample_first` chooses whether times or grid points are sampled
    first. With `"time"`, times are drawn and then grid points for each; with
    `"space"`, the reverse. This affects the statistics of the resulting dataset —
    see [Data Sampling](../science/data-sampling.md).

**Total rows = number of sampled times × number of sampled grid points.**

## History parameters

These two parameters define the independent variables and have a large effect on
feature count:

| Parameter | Meaning |
|---|---|
| `max_history_to_consider` | How far back to look, \(t_{max\_history}\), in hours |
| `history_interval` | How often to sample within that window, \(t_{history}\), in hours |

With \(t_{max\_history} = 48\) and \(t_{history} = 4\), atmospheric data are read
at \(t_{ref}-4, t_{ref}-8, \ldots, t_{ref}-48\) — 12 historical times.

Feature count follows directly:

$$
n_{features} = n_{history} \times n_{QoIs} + 1
$$

The \(+1\) is elevation, which is fixed in time. So 12 historical times × 5 QoIs
+ elevation = **61 features**. Dropping to \(t_{max\_history} = 32\) gives 8
historical times and **41 features**.

Larger or smaller fuel elements justify different history windows — a 1000-hour
fuel needs a longer \(t_{max\_history}\) than a 10-hour fuel.

## Quantities of interest

`qois_to_read` selects the time-varying atmospheric variables. The default set is
everything available in the dataset:

| Name | Definition |
|---|---|
| `UMag10` | Wind speed magnitude at 10 m (m/s) |
| `T2` | Air temperature at 2 m (°C) |
| `RH` | Relative humidity (%) |
| `PRECIP` | Precipitation (cm) |
| `SWDOWN` | Solar shortwave downward flux |
| `HGT` | Elevation — extracted by default, fixed in time |

`labels_to_read` selects the FM categories to extract as dependent variables:

| Name | Definition |
|---|---|
| `FM_1hr` | 1-hour fuel moisture |
| `FM_10hr` | 10-hour fuel moisture |
| `FM_100hr` | 100-hour fuel moisture |
| `FM_1000hr` | 1000-hour fuel moisture |

## Example dataset definitions

The parameters above combine to define a dataset. These examples are drawn from
the dataset registry published in the
[results archive](../science/overview.md#results-archive), and show how the
settings translate into data volume and feature count.

| Dataset | \(t_{max\_history}\) (h) | \(t_{history}\) (h) | History times | Reference times | Grid points per time | Rows extracted | QoIs | Features |
|---|---|---|---|---|---|---|---|---|
| 41 | 32 | 4 | 8 | 2,000 | 3,000 | 6,000,000 | 5 | 41 |
| 42 | 32 | 4 | 8 | 2,000 | 4,000 | 8,000,000 | 5 | 41 |
| 43 | 32 | 4 | 8 | 3,000 | 1,000 | 3,000,000 | 5 | 41 |
| 44 | 32 | 4 | 8 | 3,000 | 2,000 | 6,000,000 | 5 | 41 |
| 59 | 36 | 4 | 9 | 2,000 | 4,000 | 8,000,000 | 5 | 46 |
| 60 | 40 | 4 | 10 | 2,000 | 4,000 | 8,000,000 | 5 | 51 |
| 61 | 44 | 4 | 11 | 2,000 | 4,000 | 8,000,000 | 5 | 56 |
| 62 | 48 | 4 | 12 | 2,000 | 4,000 | 8,000,000 | 5 | 61 |

"QoIs" counts the time-varying quantities only; elevation is extracted separately
and is fixed in time.

Two relationships hold across every row, and are worth checking when defining a
new dataset:

$$
n_{rows} = n_{reference\ times} \times n_{grid\ points}
$$

$$
n_{features} = n_{history\ times} \times n_{QoIs} + 1
$$

Datasets 41–44 hold the history parameters fixed and vary only the sampling
counts. Datasets 59–62 do the reverse, holding sampling fixed at 2,000 × 4,000
while \(t_{max\_history}\) grows from 36 to 48 hours — which is what drives the
feature count from 46 up to 61.

!!! note "Dataset numbering is a convention, not a registry"
    These identifiers are simply the `data_set_count` values used for those runs.
    Numbers are assigned as studies are created and are not contiguous — the
    [Science with MLAP](../science/overview.md) section draws on datasets 39, 45, 46, 49,
    53, 63–66 and 79–81 as well. Dataset 41 appears both here and there, with the
    same definition of 2,000 reference times by 3,000 grid points.

## Reading other data sources

MLAP can extract from datasets other than the SJSU reanalysis by mapping their
variable names onto MLAP's. `SJSU_HRRR_Map` does this for HRRR data:

```json
"SJSU_HRRR_Map": {
    "U10": "ugrd10m",
    "V10": "vgrd10m",
    "T2": "tmp2m",
    "RH": "rh",
    "PRECIP": "apcp",
    "SWDOWN": "dswrf"
}
```

This is what lets a model trained on the reanalysis be applied to forecasts or
climate projections — as long as each required variable has a counterpart in the
new source. `SJSU_RRM_Maps` does the same for E3SM regionally refined model data.

## Sample configuration

```json
{
    "paths": {
        "data_files_location": "/p/vast1/climres/DFM_reanalysis",
        "extracted_data_base_loc": ".../01_WRF_Nelson_Data_Extracted"
    },
    "data_set_defn": {
        "data_set_count": 0,
        "percent_files_to_use": 0.008148,
        "percent_grid_points_to_use": 0.005956,
        "max_history_to_consider": 8,
        "history_interval": 2
    },
    "sampling_type": {
        "sample_first": "time",
        "time": "uniform",
        "space": "random"
    },
    "nevada_data": {
        "remove_nevada": true,
        "j_nevada": 80, "i_nevada": 250,
        "j_anchor": 310, "i_anchor": 250
    },
    "features_labels": {
        "qois_to_read": ["UMag10", "T2", "RH", "PRECIP", "SWDOWN"],
        "labels_to_read": ["FM_10hr", "FM_100hr"],
        "labels_ind_in_nc_file": [1, 2]
    },
    "clip_data_train_test": { "x_clip": null, "y_clip": null }
}
```

Every key is documented in the [JSON Reference](json-reference.md).

## Output

A pandas DataFrame containing FM labels and the corresponding atmospheric history
for each (time, grid) pair, written under `extracted_data_base_loc` and named by
`data_set_count`. This dataset becomes the input to
[Step 2](step2-prepare.md).

`data_set_count` is the identifier that follows the dataset through the rest of
the pipeline — see [Nomenclature](running-on-hpc.md#nomenclature).
