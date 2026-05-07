from __future__ import annotations

import streamlit as st

from clinnova_fl.ui.streamlit import components


def main() -> None:
    st.set_page_config(page_title="Clinnova Federated Hist PoC", layout="wide")
    st.header("Clinnova User Portal", divider=True)
    hist_canvas = st.columns([1], border=False)[0]
    hist_computation_option_column, hist_plot_column = st.columns([0.5, 0.5], border=False, gap="medium")
    with hist_computation_option_column:
        components.build_hist_computation_options(hist_canvas)
    with hist_plot_column:
        components.build_hist_plot_options(hist_canvas)
    st.write("---")


if __name__ == "__main__":
    main()
