# `ui` module — quickstart

User interfaces for the package.
**There is no current UI implementation.**

```txt
ui/
├── __init__.py                 # empty
├── streamlit/__init__.py       # empty placeholder for the future Streamlit UI
└── OLD_streamlit_interface/    # legacy PoC code, reference only
```

- `streamlit/`: placeholder where the new UI is expected to live.
- `OLD_streamlit_interface/`: ad-hoc Streamlit apps from the earlier histogram/ML proof of concept. Its README says it is kept only as a reference and that a completely new UI module should be implemented. It is not importable as a package module (it uses flat imports such as `import support_plot_hist`) and it depends on paths that no longer exist (`./other_scripts/run_hist_app.sh`, `./config/server_config.toml`).

Details: [`OLD_streamlit_interface.md`](./OLD_streamlit_interface.md).
The legacy files are documented in a single page because they are reference-only code.
