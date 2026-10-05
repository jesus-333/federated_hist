# `apps/flower_ml_tabular/server.py`

## `main(grid : Grid, context : Context, experiment_config : dict) -> None`

1. `app_config = experiment_config['app_config']`.
2. Compute `n_features` (same buggy membership check as the client). `path_to_save` defaults to `'./results/'`.
3. `ml_model = generic.get_ml_model(app_config['ml_model_name'], app_config['ml_model_config'])`, then `ml_model.init_params(app_config['num_classes'], n_features)`.
4. `arrays = ArrayRecord(ml_model.get_params())`.
5. `result = strategy.FedAvg().start(grid = grid, initial_arrays = arrays, num_rounds = app_config['num_rounds'], train_config = ConfigRecord(config_dict = app_config))`.
6. `params_final = result.arrays.to_numpy_ndarrays()`, pickled to `{path_to_save}/final_params_{ml_model_name}.pkl`.

## Notes

- FedAvg is used with default arguments (fraction of clients, min nodes and evaluation are left at the Flower defaults). FedAvg also sends `EVALUATE` messages, which reach the broken `evaluate` (see [`client.md`](./client.md)).
- FedAvg does not put a `custom_config` into the messages, so the root client cannot build the dataset (see [`../client.md`](../client.md#interaction-with-flower-strategies)). A fix is either to include `dataset_id`/`simulation`/`paths_nodes_config` into the `train_config` and make `get_experiment_and_node_config` also read `msg.content["config"]`, or to set `custom_config` via a custom strategy.
- `ConfigRecord` does not accept the nested `ml_model_config` dict. It must be flattened or serialized (e.g. to a JSON string).
- There is a TODO: algorithm-specific checks (e.g. LDA needs only 1 round).
