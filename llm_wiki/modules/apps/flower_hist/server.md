# `apps/flower_hist/server.py`

Server logic of the federated histogram (custom strategy, 2 QUERY rounds).

## `main(grid : Grid, context : Context, experiment_config : dict) -> None`

1. `app_config = experiment_config['app_config']`. Read the settings with defaults (see the table in [`0_flower_hist_quickstart.md`](./0_flower_hist_quickstart.md)) and validate them (positive ints, `bins_variable` required, `bins_distribution` in `{'uniform', 'logarithmic'}`).
2. `my_config = app_config.copy()` with `server_round = -1`. This dict is the `custom_config` forwarded to clients, so it carries `dataset_id`, `simulation` and `paths_nodes_config` needed by the root client.
3. **Round 0** (if `predefined_min` or `predefined_max` is missing) :
    - `node_ids_round = get_node_ids(grid, min_nodes)`;
    - `get_data_from_clients(MessageType.QUERY, ...)` with `server_round = 0`;
    - `compute_min_max_federation` and then override with the predefined value if any.
4. **Round 1** :
    - bins: `np.linspace(min, max, n_bins + 1)` (uniform) or `np.geomspace` (logarithmic, `min == 0` replaced by `1e-10`);
    - `my_config['bins'] = list(bins)`, `server_round = 1`, query clients;
    - `compute_hist` and then `save_results`.

## Helper functions

- `compute_min_max_federation(results_round_zero) -> (min, max)`: reads `rep.content["query_results"]["min"/"max"]`.
- `compute_hist(n_bins, results_round_one) -> (final_hist, mean, std)`: sums the histograms. The mean is weighted by the per-client sample count (sum of the local histogram). The std is a **weighted average of the local stds** (not the pooled std, there is a TODO).
- `save_results(info_to_save, final_hist, mean, std, path_to_save)`: writes `.pkl`, `.toml`, `bins_*.npy`, `hist_*.npy` under `path_to_save/<bins_variable_name>/`.

## Known issues

- If both `predefined_min` and `predefined_max` are set, round 0 is skipped and `node_ids_round` is never defined, so round 1 raises `NameError`.
- `bins_distribution = 'logarithmic'` with `min < 0 < max` leaves `bins` undefined (`pass` branch). With `min < 0` and `max <= 0` `geomspace` works only for same-sign values.
- `min`/`max` shadow the builtins inside `main` (works, but fragile).
- `np.average(..., weights = n_samples_list)` fails if all weights are zero (empty data).
- `list(bins)` holds `np.float64` values. They are accepted by `ConfigRecord` as floats in current Flower, but `toml.dump` of numpy objects may need care.
- `final_hist` is a numpy array inside `info_to_save` when dumped to TOML.
