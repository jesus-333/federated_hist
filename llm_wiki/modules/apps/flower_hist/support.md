# `apps/flower_hist/support.py`

Plot helpers for the histogram app (matplotlib). Not used by the app yet (`create_plot` is not implemented).

- `plot_single_hist(bins, hist_data) -> plt.Figure`: calls `ax.hist(hist_data, bins = bins)`. Note that this expects *raw samples*, not pre-computed counts. For saved counts use `ax.stairs(hist, bins)` or `ax.bar`.
- `plot_merge_hist(bins, list_of_hist_data, list_of_labels) -> plt.Figure`: docstring only, no body (returns `None`).

For a more complete legacy plotting implementation see `ui/OLD_streamlit_interface/support_plot_hist.py` ([`../../ui/OLD_streamlit_interface.md`](../../ui/OLD_streamlit_interface.md)).
