# Wiki index — `clinnova_fl`

LLM-oriented wiki of the `clinnova_fl` package (Federated Learning on biological data with Flower, Clinnova project).
Its purpose is to avoid re-analyzing the repository from scratch before each task.
Start from [`0_wiki_quickstart.md`](./0_wiki_quickstart.md) for the overview and architecture.

Wiki snapshot: generated from branch `Test-(2)` (commit `905df18`), updated after the name-mismatch fixes. Update the relevant pages when the code changes.

## Top-level files and folders

| Path | Content |
|------|---------|
| [`0_wiki_quickstart.md`](./0_wiki_quickstart.md) | Purpose, layout, run flow, key concepts, how to run. |
| [`coding_style_instructions_ENG.md`](./coding_style_instructions_ENG.md) | Mandatory coding style (dividers, snake_case classes, `a : int`, `if cond :`, aligned `=`, numpydoc + sphinx refs, f-strings, hyphenated CLI names). **Read-only.** |
| `instructions/` | Task instructions written by the user for the LLM (e.g. how this wiki was created). Not part of the package docs and can be ignored for normal development. |
| [`examples/`](./examples/0_examples_quickstart.md) | Description of the repository `examples/` folder. |
| [`modules/`](#modules) | Detailed per-module, per-file documentation. |

## Modules

Each module has a `0_<module>_quickstart.md` (overview and index) plus one page per Python file.

- **Package root** — [`modules/package_root/0_package_root_quickstart.md`](./modules/package_root/0_package_root_quickstart.md)
    - [`cli.py`](./modules/package_root/cli.md): `clinnova-hist` entry point and `write_debug_config`.
- **`apps`** — [`modules/apps/0_apps_quickstart.md`](./modules/apps/0_apps_quickstart.md) (dispatch model, how to add an app)
    - [`__init__.py`](./modules/apps/__init__.md), [`server.py`](./modules/apps/server.md) (root ServerApp), [`client.py`](./modules/apps/client.md) (root ClientApp, node config resolution), [`support_fl.py`](./modules/apps/support_fl.md) (Message API helpers)
    - **`flower_hist`** — [`0_flower_hist_quickstart.md`](./modules/apps/flower_hist/0_flower_hist_quickstart.md): [`cli.py`](./modules/apps/flower_hist/cli.md), [`client.py`](./modules/apps/flower_hist/client.md), [`server.py`](./modules/apps/flower_hist/server.md), [`support.py`](./modules/apps/flower_hist/support.md)
    - **`flower_ml_tabular`** (WIP) — [`0_flower_ml_tabular_quickstart.md`](./modules/apps/flower_ml_tabular/0_flower_ml_tabular_quickstart.md): [`cli.py`](./modules/apps/flower_ml_tabular/cli.md), [`client.py`](./modules/apps/flower_ml_tabular/client.md), [`server.py`](./modules/apps/flower_ml_tabular/server.md), [`support_ml_app.py`](./modules/apps/flower_ml_tabular/support_ml_app.md)
        - **`ml_models`** — [`0_ml_models_quickstart.md`](./modules/apps/flower_ml_tabular/ml_models/0_ml_models_quickstart.md): [`generic.py`](./modules/apps/flower_ml_tabular/ml_models/generic.md), [`svm.py`](./modules/apps/flower_ml_tabular/ml_models/svm.md), [`lda.py`](./modules/apps/flower_ml_tabular/ml_models/lda.md)
- **`config`** — [`modules/config/0_config_quickstart.md`](./modules/config/0_config_quickstart.md) (configuration layers, connector config pattern)
    - [`__init__.py`](./modules/config/__init__.md), [`config.py`](./modules/config/config.md), [`apps/generic.py`](./modules/config/apps/generic.md), [`connector/generic.py`](./modules/config/connector/generic.md), [`connector/csv.py`](./modules/config/connector/csv.md), [`connector/synthetic.py`](./modules/config/connector/synthetic.md), [`debug_config/*.toml`](./modules/config/debug_config.md)
- **`dataset`** — [`modules/dataset/0_dataset_quickstart.md`](./modules/dataset/0_dataset_quickstart.md)
    - [`__init__.py`](./modules/dataset/__init__.md), [`generic.py`](./modules/dataset/generic.md), [`tabular.py`](./modules/dataset/tabular.md), [`images.py`](./modules/dataset/images.md)
- **`data_connector`** — [`modules/data_connector/0_data_connector_quickstart.md`](./modules/data_connector/0_data_connector_quickstart.md)
    - [`generic.py`](./modules/data_connector/generic.md), [`csv.py`](./modules/data_connector/csv.md), [`synthetic.py`](./modules/data_connector/synthetic.md)
- **`ui`** — [`modules/ui/0_ui_quickstart.md`](./modules/ui/0_ui_quickstart.md)
    - [`OLD_streamlit_interface/`](./modules/ui/OLD_streamlit_interface.md) (legacy, reference only)

## Other repository resources

- `src/README.md`: package philosophy, Flower primer, app/dataset/data_connector design. Owned by the user: **do not modify** (only typos, grammar, formatting).
- `README.md` (root): `run_config` mechanics and debugging tips for `flwr run`.
- `pyproject.toml`: package `clinnova-fl` 1.0.0 (hatchling, `src/clinnova_fl`). Deps: `flwr[simulation]>=1.28`, `flwr-datasets[vision]`, `matplotlib`, `numpy>=2`, `pandas==2.2.3`, `scikit-learn`, `streamlit`, `toml`. No `requires-python` (but Python >= 3.12 is needed) and no `torch` (imported by `dataset`).
- `data/`: PRISM IBD metagenomics data (Franzosa et al., Nat. Microbiol. 2018; `41564_2018_306_MOESM4_ESM.xlsx`), `original_data.csv/.xlsx` (features as rows, samples as columns; includes `Age`, `Diagnosis` ∈ {Control, UC, CD}, medications, EC enzyme abundances), `backup.xlsx`.
- Ignored artefacts: root `config/`, `shared_app/`, `old_code_backup/`.

## Status summary

| Component | Status |
|-----------|--------|
| Root server/client dispatch | Works for `flower_hist`. |
| `flower_hist` | Logic complete. End-to-end runs are blocked by the data layer bugs below. |
| `flower_ml_tabular` | WIP, not runnable. |
| `dataset.tabular` | `get_feature` path OK; labels path broken. |
| `dataset.images` | Stub. |
| `data_connector.synthetic` | Broken (labels type check, getitem). |
| `data_connector.csv` + its config | Broken (dataclass field order, abstract `__len__`). |
| `config.apps` | Skeleton, unused. |
| `ui` | Only legacy code. |
| Tests | None in the repository. |

## Known issues (consolidated)

Ordered roughly by impact. Details are in each linked page.

1. `data_connector/synthetic.py`: inverted int check in `set_labels` and `.to_numpy()` on an ndarray. This breaks `clinnova-hist --debug`. [page](./modules/data_connector/synthetic.md)
2. `config/connector/csv.py`: dataclass field order error, no `feature_to_predict`. [page](./modules/config/connector/csv.md)
3. `data_connector/csv.py`: missing `__len__`, `set_labels` called before data is loaded, wrong numeric dtype check. [page](./modules/data_connector/csv.md)
4. `dataset/tabular.py`: `self.labels` never set, connector labels not propagated. [page](./modules/dataset/tabular.md)
5. `ml_models/svm.py`, `lda.py` subclass a function (`generic.get_ml_model`); `compute_metrics` misses `self`; LDA `labels_`/`scalings_`/`init_params` issues. [page](./modules/apps/flower_ml_tabular/ml_models/0_ml_models_quickstart.md)
6. FedAvg messages carry no `custom_config`, so the root client cannot build the dataset for strategy-based apps. A nested `ml_model_config` is not valid in a `ConfigRecord`. [page](./modules/apps/flower_ml_tabular/server.md)
7. `'fields_to_use_for_the_train in app_config'` string-literal check (ML client/server). [page](./modules/apps/flower_ml_tabular/client.md)
8. ML `evaluate` takes 2 arguments but is called with 3. [page](./modules/apps/flower_ml_tabular/client.md)
9. `flower_hist/server.py`: `node_ids_round` undefined when both predefined min/max are given; log bins with `min < 0 < max` are undefined. [page](./modules/apps/flower_hist/server.md)
10. Non-simulation runs: the server always forwards `simulation`, so the deployment `full_node_config_path` branch in `apps/client.py` is unreachable through `flower_hist`. `run_with_nvflare` is never forwarded. [page](./modules/apps/client.md)
11. `flower_k_means` listed but not implemented. `SUPPORTED_MODALITY` is missing a comma. `support_fl.check_custom_config` uses `isinstance` with generics. `images.py` raises `NotImplemented`.
12. Packaging: `torch` missing from dependencies; Python >= 3.12 required (nested same-quote f-strings) but not declared.
13. Leftover debug `pprint` calls in `apps/client.py` and `config/config.py`.
