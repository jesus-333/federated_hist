# TMP — `clinnova-hist --debug` fix

Temporary note. Delete it once you've read it.

## Symptom

`clinnova-hist --debug` started the simulation, but every client failed on the first QUERY message.
The server retried 10 times and then aborted with :
```txt
Exception: Error in receiving data from clients during round 10. Maximum number of attempts (10) reached
```
The real error was only visible in the client logs (Ray actors) :
```txt
ModuleNotFoundError: No module named 'torch'
```

## What was broken, and why

The client-side path in debug mode is :
`apps/client.py:query` → `dataset.generic.get_dataset` → synthetic connector config → `data_connector.synthetic.data_connector` → `dataset.tabular.dataset` → `flower_hist.client.query`.

There were three blocking problems on this path, plus one config mismatch.

1. **`dataset/tabular.py` imported `torch` at module level.**
   `torch` is not a dependency in `pyproject.toml`. So importing the tabular dataset failed in any environment without PyTorch, even though the default `return_type` is `'numpy'`.
   This is the error that actually showed up in the logs. It masked the bugs below, which would have been hit right after.

2. **`data_connector/synthetic.py:set_labels` had an inverted type check.**
   ```python
   if type(self.config.num_classes) is int : raise ValueError("The number of classes must be an integer.")
   ```
   It raised exactly when the value *was* an integer, so any int value (including the template default `-1`) crashed the connector creation.

3. **`set_labels` raised for values `< 2`.**
   The config docstring says that labels are generated only when `num_classes >= 2`, and otherwise they are not generated. The debug template uses `-1` to mean "no labels". The code raised `ValueError` instead of setting `labels = None`.

4. **Name mismatch (fixed in the previous commit).** The connector read `config.num_classes` while the config field was `n_classes` (`AttributeError`). Now everything uses `num_classes`.

There was also a non-blocking bug in the same connector: `__getitem__` called `.to_numpy()` on a numpy array (it would fail on any `dataset[idx]` access). The histogram app does not hit it (it only uses `get_feature`), but I fixed it too.

## How it was fixed

- `dataset/tabular.py`: removed the module-level `import torch`. Added a small helper `_import_torch()` that imports torch lazily and raises a clear `ImportError` if it is missing. It is called only in the `return_type == 'torch'` branches. torch stays optional.
- `data_connector/synthetic.py:set_labels`, rewritten :
    - `num_classes is None` → `labels = None`;
    - non-integer (or bool) → `ValueError`, with the received value and type;
    - `num_classes >= 2` → random labels in `[0, num_classes)`;
    - `num_classes < 2` (e.g. `-1`) → `labels = None` (as documented).
- `data_connector/synthetic.py:__getitem__`: `return self.data[idx]` (no `.to_numpy()`).
- `config/connector/synthetic.py:from_dict`: the default for `num_classes` is now `-1` (it was `2`), consistent with the dataclass default. A config without the key now means "no labels" instead of silently generating 2-class labels.

## Verification

Run in a Python 3.12 venv with `pip install -e .` (flwr 1.39, no torch installed) :
```txt
Received 7/7 results                      (round 0)
Computed global min: -3.8366555484593694
Computed global max: 8.526932425873621
Received 7/7 results                      (round 1)
Final histogram : [  4  45 240 509 624 598 615 534 274  57]   # sum = 3500 = 7 clients x 500 samples
```
Outputs written: `results/feature_1/{results_feature_1.pkl, results_feature_1.toml, bins_feature_1.npy, hist_feature_1.npy}`.

The connector was also checked directly: `num_classes = 3` gives labels, `-1`/`None`/`1` give `None`, `"3"` raises `ValueError`, and `d[0:2]` returns shape `(2, 4)`.

## Things I noticed but did NOT change

- **`results_*.toml` contains numpy reprs as strings**, e.g. `histogram = [ "np.int64(4)", ... ]`, `mean = "np.float64(3.02...)"`. The `toml` library does not know numpy types. The `.pkl` and `.npy` files are fine. Fix: convert to Python types (`.tolist()`, `float(...)`) in `flower_hist/server.py:save_results` before `toml.dump`.
- **`clinnova-hist` exits with code 0 even when the simulation fails** (the failing run above also returned 0). `flwr run --stream` apparently does not propagate the simulation exit code, so scripts/CI cannot detect failures from the exit code.
- **All debug clients share the same random noise**: same `seed`, only `loc` differs (`loc = i`). Fine for a smoke test, but the client distributions are shifted copies of each other.
- **Very verbose client logs**: `apps/client.py:get_simulated_node_config` still has a debug `pprint.pprint(context)`.
- **Python >= 3.12 is required** (nested same-quote f-strings in `apps/server.py` and `apps/client.py`), but `pyproject.toml` does not declare `requires-python`.
- **`dataset/tabular.py` still never sets `self.labels`.** `dataset[idx]` raises `AttributeError`. It does not affect the histogram app, but it blocks the ML app.
