# `clinnova_fl/config/config.py`

Module docstring: "Decide if keeping this file or not." (tentative).

## Path constants

Resolved from the file location (`parents[3]` = repository root, valid only for an editable/source install) :
`PROJECT_ROOT`, `SRC_ROOT`, `PACKAGE_ROOT`, `CONFIG_DIR` (`<root>/config`), `DATA_DIR` (`<root>/data`), `STREAMLIT_DIR` (`<root>/streamlit_interface`, does not exist), `OTHER_SCRIPTS_DIR` (`<root>/other_scripts`, does not exist), `RESULTS_DIR`.

Helpers: `project_path(*parts)`, `config_path(name)`, `data_path(name)`, `streamlit_path(name)`, `other_script_path(name)`.
They are not used by the current package code.

## Debug template loaders

- `get_debug_config_app(app_name) -> dict`: `toml.load(DEBUG_CONFIG_PATH[app_name])`.
- `get_debug_config_data_connector(data_type) -> dict`: same, for connectors (kept separate on purpose for future connector-specific processing).

Both contain a leftover `pprint.pprint(DEBUG_CONFIG_PATH)`.
