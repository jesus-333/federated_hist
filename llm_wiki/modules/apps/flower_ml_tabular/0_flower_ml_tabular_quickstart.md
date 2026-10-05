# `apps/flower_ml_tabular` — quickstart

Federated training of classic (scikit-learn) ML models on tabular data, using the built-in Flower **FedAvg** strategy (`flwr.serverapp.strategy.FedAvg`).
It is the reference example of an app that relies on a Flower strategy and on `@app.train()`.

**Status: work in progress, not runnable end-to-end** (see *Known issues*).

## Files

| File | Purpose | Page |
|------|---------|------|
| `__init__.py` | Docstring only. | — |
| `cli.py` | `main_ml_tabular(args, flwr_args)`: builds and runs the `flwr run` command (not wired to a console script). | [`cli.md`](./cli.md) |
| `client.py` | `train(msg, context, dataset_istance)`, placeholder `evaluate`. | [`client.md`](./client.md) |
| `server.py` | `main(grid, context, experiment_config)`: FedAvg loop and saving of the final params. | [`server.md`](./server.md) |
| `support_ml_app.py` | Legacy procedural helpers (pre-`ml_models`). Not imported by the app. | [`support_ml_app.md`](./support_ml_app.md) |
| `ml_models/` | Model wrappers with a common interface (`svm`, `lda`). | [`ml_models/0_ml_models_quickstart.md`](./ml_models/0_ml_models_quickstart.md) |

## Flow

```txt
server: ml_model = get_ml_model(name, ml_model_config); ml_model.init_params(num_classes, n_features)
        FedAvg().start(grid, initial_arrays = ArrayRecord(params), num_rounds, train_config = ConfigRecord(app_config))
client (each round): app_config = msg.content["config"]; build model; init_params; set_params(received arrays)
        x, y = dataset_istance[:]; fit; return ArrayRecord(get_params()) + MetricRecord(metrics + num-examples)
server: result.arrays -> {path_to_save}/final_params_{ml_model_name}.pkl
```

## App config

Debug template: `config/debug_config/ml_tabular.toml` (registered as `DEBUG_CONFIG_PATH['flower_ml_tabular']`).

| Key | Notes |
|-----|-------|
| `app` | `"flower_ml_tabular"`. |
| `dataset_id` | Dataset in `node_config`. |
| `ml_model_name` | `"svm"` or `"lda"` (lower case, see `ml_models/generic.py:IMPLEMENTED_MODELS`). |
| `num_rounds` | FedAvg rounds. |
| `num_classes`, `n_features` | Needed to create the initial parameters. `n_features` is ignored if `fields_to_use_for_the_train` is used. |
| `fields_to_use_for_the_train` | List of feature names (not applied to data yet). |
| `use_partial_fit_if_available` | Reserved, unused. |
| `path_to_save` | Server output folder. |
| `[ml_model_config]` | Model hyper-parameters (TOML table). |

The template contains a useful note on `warm_start` vs `fit`/`partial_fit`.
Models without warm start (LDA, LinearSVC) gain nothing from more than one federated round.

## Known issues (blocking)

1. **`ml_models/svm.py` and `lda.py` inherit from `generic.get_ml_model`** (a function) instead of `generic.generic_ml_model`, so importing them raises `TypeError`.
2. **Dataset on the client**: the root client builds the dataset from `custom_config`, which FedAvg does not send. The run config arrives under `msg.content["config"]`, so `get_dataset` fails with `KeyError: 'dataset_id'`.
3. **Nested config**: `ConfigRecord(config_dict = app_config)` with the `[ml_model_config]` table (a nested dict) is not a supported `ConfigRecord` value.
4. `'fields_to_use_for_the_train in app_config'` is a string literal (always truthy) in both `client.py` and `server.py`. The intended check is `'fields_to_use_for_the_train' in app_config`. With the template's empty list, `n_features = 0`.
5. `tabular.dataset` never sets `self.labels`, so `dataset_istance.labels` raises `AttributeError` (see [`../../dataset/tabular.md`](../../dataset/tabular.md)).
6. `generic_ml_model.compute_metrics` lacks `self`.
