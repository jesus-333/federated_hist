# `apps/flower_ml_tabular/client.py`

## `train(msg : Message, context : Context, dataset_istance : tabular.dataset) -> Message`

1. `app_config = msg.content["config"]` (the `train_config` sent by FedAvg).
2. `n_features`: `len(fields_to_use_for_the_train)` or `app_config['n_features']` (the membership check is buggy, see below).
3. `ml_model = generic.get_ml_model(app_config['ml_model_name'], app_config['ml_model_config'])`.
4. `params = msg.content["arrays"].to_numpy_ndarrays()`, then `ml_model.init_params(num_classes, n_features)` and `ml_model.set_params(params)`.
5. Require `dataset_istance.labels is not None`. Then `x_train, y_train = dataset_istance[:]`.
6. `ml_model.fit` (warnings suppressed). The trained params go into an `ArrayRecord`.
7. Metrics: `compute_metrics(y, predict(x), regression = (ml_model_name == 'LASSO'))` plus `num-examples` (required by FedAvg for weighting), packed into a `MetricRecord`.
8. Saves a pickle to `{node_config['path_to_save_model'] or './'}trained_params_{name}_node_{dataset_id}.pkl`.
9. Returns `Message(content = RecordDict({"arrays": ..., "metrics": ...}), reply_to = msg)`.

## `evaluate(message, context) -> Message`

Placeholder that returns fixed metrics (`mse = 1.0`, `mae = 1.0`, `num-examples = 42`).
**Signature mismatch**: the root client calls `evaluate(msg, context, dataset_istance)` (3 args) but this function accepts 2, so it raises `TypeError`.

## Known issues

- `'fields_to_use_for_the_train in app_config'` is always truthy (string literal).
- The pickle saves `params` (the **received** params), not `params_trained`.
- The path is built by string concatenation (needs a trailing `/`). There is a TODO to use `pathlib`.
- `fields_to_use_for_the_train` is not used to select the columns of `x_train`.
- The `'LASSO'` check is upper case, while model names are lower case and LASSO is not implemented in `ml_models`.
- A commented legacy `query` is kept as a reminder (per-node weights for the PoC).
