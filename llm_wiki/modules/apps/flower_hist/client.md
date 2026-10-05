# `apps/flower_hist/client.py`

## `query(msg : Message, context : Context, dataset_istance : tabular.dataset) -> Message`

Called by the root `apps/client.py:query`.

- `my_config = msg.content.config_records["custom_config"]`.
- `server_round = my_config["server_round"]`, `bins_variable = my_config["bins_variable"]`.
- `data = dataset_istance.get_feature(bins_variable)` (1D numpy array).
- Round `0` → `{"min": float, "max": float}`.
- Round `1` → `{"histogram": list[int], "average": float, "std": float}`, using `bins = my_config["bins"]`.
- Other rounds → `ValueError`.
- Reply: `Message(RecordDict({"query_results": MetricRecord(query_results)}), reply_to = msg)`.

The function docstring contains a long commented example of the `Message` and `Context` objects (metadata, `node_config` with `partition-id`/`num-partitions` in simulation, `run_config`, `state`).
It is a useful reference for the Flower object layout.

## Notes

- The key `"query_results"` is an app convention shared with `server.py`.
- Only the dataset method `get_feature` is required. Labels are not used.
