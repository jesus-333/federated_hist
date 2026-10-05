# `clinnova_fl/config/debug_config/` (TOML templates)

Templates consumed by `clinnova_fl.cli.write_debug_config` (via `DEBUG_CONFIG_PATH`).

## `hist.toml` (app template, `flower_hist`)

```toml
app = "flower_hist"
dataset_id = 'synth_1'
debug = true
max_number_of_attempts = 10
n_bins = 10
bins_variable = "feature_1"      # synthetic features are named feature_1..feature_n
bins_distribution = "uniform"
path_to_save = "./results/"
create_plot = false
seed = 42
required_dataset_type = "tabular" # debug only: dataset type to generate
```

## `ml_tabular.toml` (app template, ML tabular)

`app = "flower_ml_tabular"`, `dataset_id = 'synth_1'`, `ml_model_name = "svm"`, `fields_to_use_for_the_train = []`, `num_rounds = 4`, `num_classes = -1`, `n_features = -1`, `use_partial_fit_if_available = false`, `path_to_save = "./results"`, and a table `[ml_model_config]` (`alpha`, `penalty`, `loss`, `dual`, `tol`, `C`, `multi_class`, `max_iter`).
It does **not** contain `required_dataset_type`, which `write_debug_config` requires.
Registered in `DEBUG_CONFIG_PATH` as `flower_ml_tabular`.
It contains a long comment on `warm_start`/`partial_fit`.

## `synthetic_data_connector.toml` (connector template)

```toml
modality = 'synthetic'
seed = 42
distribution = 'normal'
size = -1        # replaced per client
num_classes = -1
loc = 0
scale = 1
[data_size_based_on_dataset_type]   # debug only
tabular = [500, 20]
```

## `hist_plot.toml`

`figsize = [15, 10]`, `fontsize = 12`. Not referenced by current code.
