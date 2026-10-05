# `clinnova_fl/apps/support_fl.py`

Server-side helpers built on the Flower Message API (`Grid.send_and_receive`).
They are used by apps that implement a custom strategy (e.g. `flower_hist`).

## Functions

### `get_node_ids(grid, min_nodes, max_number_of_attempts = 10) -> list[int]`

Polls `grid.get_node_ids()` every 2 s until at least `min_nodes` are connected.
Raises `ValueError` if `min_nodes <= 0` and `Exception` if not enough nodes after `max_number_of_attempts`.
With `min_nodes = 1` it returns whatever nodes are connected at the first successful poll.

### `send_and_receive_data(message_type, grid, node_ids, server_round, custom_config = None)`

- Builds one `RecordDict` with `recorddict['custom_config'] = ConfigRecord(custom_config)` (if not `None`).
- Creates one `Message(content = recorddict, message_type = message_type, dst_node_id = node_id, group_id = str(server_round))` per node. All messages share the same `RecordDict` object.
- `replies = grid.send_and_receive(messages)`.
- Returns `None` if any reply `has_error()`, else the list of replies.

`message_type` is a `flwr.common.MessageType` (`QUERY`, `TRAIN`, `EVALUATE`), which selects the `@app.query/train/evaluate` function on the client.

### `get_data_from_clients(message_type, grid, node_ids, custom_config = None, max_number_of_attempts = 10, sleep_time = 2) -> list[Message]`

Retry loop around `send_and_receive_data` (always `server_round = 0`).
Raises after `max_number_of_attempts` failures.
Clients read the dict via `msg.content.config_records["custom_config"]`.

### `check_custom_config(custom_config : dict)`

Intended to validate that values are `ConfigRecord`-compatible: `int | float | str | bytes | bool | list[int] | list[float] | list[str] | list[bytes] | list[bool]`.
**Broken**: `isinstance` does not accept parameterized generics (`list[int]`), so this raises `TypeError`. It is not called anywhere.

## Notes

- `group_id` is always `"0"` through `get_data_from_clients`. The histogram app distinguishes rounds via `custom_config['server_round']` instead.
- Docstring of `send_and_receive_data` mentions a `my_config` parameter that no longer exists.
- Nested dicts are not allowed in `ConfigRecord`. Do not forward an `app_config` that contains TOML tables (e.g. `[ml_model_config]`) via `custom_config`.
