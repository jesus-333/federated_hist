# `ui/OLD_streamlit_interface/` (legacy, reference only)

Streamlit apps from the PoC. Run (historically) with `streamlit run interface_hist.py` / `interface_ml.py` from inside the folder.
The apps edit a server TOML, call a shell script that ran the Flower app, then load and plot the results.

## Files

| File | Content |
|------|---------|
| `interface_hist.py` | Streamlit page "Clinnova User Portal" for the histogram: sidebar options plus a plot canvas. Uses `support_interface_hist`. |
| `interface_ml.py` | Same for the ML app (SVM). Uses `support_interface_ml`. |
| `support_interface_hist.py` | `read_txt_list`, `save_txt_list`, widget builders (`build_hist_computation_options`, `build_hist_plot_options[_matplotlib]`), `update_server_config` (writes `./config/server_config.toml`), `compute_hist` (runs `sh ./other_scripts/run_hist_app.sh`). |
| `support_interface_ml.py` | Widget builders for the ML settings (`build_ml_computation_basic_options`, `build_SVM_computation_settings`, `build_ml_plot_options`, `build_options_dimensionality_reduction`) and `train_ml_model` (runs `sh ./other_scripts/run_ml_app.sh`). |
| `support_plot_hist.py` | Histogram plotting: matplotlib (`create_hist_matplotlib`, `plot_data_inside_ax`, `beautify_hist_matplotlib`) and native Streamlit (`draw_hist_streamlit`). Also colour helpers and result loading from `.pkl` (`load_data_for_plotting`, `load_data_from_pkl_file`). |
| `support_plot_ml.py` | Decision-boundary plots: dimensionality reduction (+ inverse), meshgrid, model reconstruction from pickled params (`create_model_and_load_params`), colour helpers. |
| `support_ml_app.py` | Copy of `apps/flower_ml_tabular/support_ml_app.py` (see [`../apps/flower_ml_tabular/support_ml_app.md`](../apps/flower_ml_tabular/support_ml_app.md)). |
| `field_hist.txt`, `field_hist_D2.txt`, `all_fields.txt` | Lists of selectable features (PRISM data: `Age` and EC enzyme names such as `1.1.1.1: Alcohol dehydrogenase`). |
| `field_categorical.txt`, `field_to_avoid.txt` | Small feature lists (categorical / excluded). |
| `README.md` | States that this is old code kept as a reference. |

## Useful when

- Building the new `ui/streamlit` module (widget layout and plotting code can be reused).
- Plotting saved `flower_hist` results (`support_plot_hist.create_hist_matplotlib` works on the result dict format: `bins`, `histogram`, ...).
