from __future__ import annotations

import pickle
import subprocess
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st
import toml

from clinnova_fl.core.config import config_path, other_script_path, project_path, streamlit_path


def get_color_hex() -> list[str]:
    return ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def get_color_name_from_hex(hex: str):
    return {
        "#1f77b4": "blue",
        "#ff7f0e": "orange",
        "#2ca02c": "green",
        "#d62728": "red",
        "#9467bd": "purple",
        "#8c564b": "brown",
        "#e377c2": "pink",
        "#7f7f7f": "gray",
        "#bcbd22": "olive",
        "#17becf": "cyan",
    }[hex]


def build_ml_computation_basic_options() -> None:
    st.subheader("Federation Settings", divider=True)
    st.selectbox(label="Select the ML model", options=["SVM"], index=0, key="ml_model_name")
    st.write("Node to use for the computation")
    st.checkbox("Client 1", key="checkbox_node_1", value=True)
    st.checkbox("Client 2", key="checkbox_node_2", value=True)
    st.button(label="Train Model", key="train_ml_model", on_click=train_ml_model)


def build_ml_computation_settings() -> None:
    st.subheader("Algorithm hyperparameters", divider=True)
    if st.session_state.ml_model_name == "SVM":
        st.selectbox(label="Penalty", options=["l2", "l1"], index=0, key="svm_penalty")
        st.selectbox(label="Loss function", options=["squared_hinge", "hinge"], index=0, key="svm_loss")
        st.checkbox(label="Dual formulation", key="svm_dual", value=True)
        st.number_input(label="Tolerance for stopping criteria", min_value=1e-6, max_value=1e-1, step=1e-6, value=1e-4, format="%.6f", key="svm_tol")
        st.number_input(label="Regularization parameter C", min_value=0.01, max_value=10.0, step=0.01, value=1.0, format="%.2f", key="svm_C")
        st.selectbox(label="Multi-class strategy", options=["ovr", "crammer_singer"], index=0, key="svm_multi_class")
        st.number_input(label="Maximum number of iterations", min_value=100, max_value=10000, step=100, value=1000, key="svm_max_iter")


def build_hist_computation_options(streamlit_container):
    hist_variable = read_txt_list(config_path("fields_categorical.txt")) if config_path("fields_categorical.txt").exists() else read_txt_list(streamlit_path("field_hist.txt"))
    bins_variable = st.selectbox(label="Select the variable for histogram computation", options=hist_variable, index=0, key="bins_variable")
    n_bins = st.slider(label="N. of bins", min_value=5, max_value=15, step=1, value=10, key="n_bins")
    node_option_column, bins_options_column = st.columns([0.5, 0.5])
    with bins_options_column:
        st.radio(label="Bins Distribution", options=["Uniform", "Logarithmic"], captions=["Bins are evenly distributed between min and max", "bins are logarithmically distributed between min and max"], key="bins_distribution")
    with node_option_column:
        st.write("Node to use for the computation")
        checkbox_node_1 = st.checkbox("Client 1", key="checkbox_node_1", value=True)
        checkbox_node_2 = st.checkbox("Client 2", key="checkbox_node_2", value=True)
    compute_hist_button = st.button(label="Compute Histogram", key="compute_hist_button", on_click=compute_hist, args=[streamlit_container])
    return dict(bins_variable=bins_variable, n_bins=n_bins, checkbox_node_1=checkbox_node_1, checkbox_node_2=checkbox_node_2, histogram_computed=compute_hist_button)


def build_hist_plot_options(streamlit_container_for_the_plot):
    plot_backend = st.selectbox(label="Select the plot backend", options=["matplotlib", "streamlit"], index=0, key="plot_backend", on_change=draw_hist, args=[streamlit_container_for_the_plot])
    st.radio(label="Plot type", options=["Type 1", "Type 2", "Type 3"], captions=["1 plot, all class mixed", "3, plot, classes separated", "1 plot, classes separated"], key="plot_type", on_change=draw_hist, args=[streamlit_container_for_the_plot])
    st.write("Other options")
    st.checkbox(label="Normalize hist", key="normalize_hist", value=False, on_change=draw_hist, args=[streamlit_container_for_the_plot])
    st.selectbox(label="Select color", options=get_color_hex(), index=0, format_func=get_color_name_from_hex, key="color", on_change=draw_hist, args=[streamlit_container_for_the_plot])
    if plot_backend == "matplotlib":
        st.slider(label="Alpha", key="alpha", min_value=0.5, max_value=1.0, value=1.0, step=0.05, on_change=draw_hist_matplotlib, args=[streamlit_container_for_the_plot])
        c1, c2 = st.columns([0.5, 0.5])
        with c1:
            st.checkbox("Display Grid", key="add_grid", value=True, on_change=draw_hist_matplotlib, args=[streamlit_container_for_the_plot])
            st.checkbox("Display edge", key="add_edge", value=True, on_change=draw_hist_matplotlib, args=[streamlit_container_for_the_plot])
        with c2:
            st.checkbox("Display Mean", key="add_mean", value=False, on_change=draw_hist_matplotlib, args=[streamlit_container_for_the_plot])
            st.checkbox("Display Std", key="add_std", value=False, on_change=draw_hist_matplotlib, args=[streamlit_container_for_the_plot])
            st.checkbox("Log scale y axis", key="y_axis_log", value=False, on_change=draw_hist, args=[streamlit_container_for_the_plot])
        st.button(label="Save Histogram", key="save_hist_button")


def draw_hist(streamlit_container):
    if st.session_state.plot_backend == "matplotlib":
        draw_hist_matplotlib(streamlit_container)
    else:
        draw_hist_streamlit(streamlit_container)


def draw_hist_matplotlib(streamlit_container):
    results = load_data_for_plotting()
    matplotlib_config = get_matplotlib_config()
    fig, _ = create_hist_matplotlib(results, matplotlib_config)
    with streamlit_container:
        st.pyplot(fig)


def draw_hist_streamlit(streamlit_container):
    results = load_data_for_plotting()
    plot_type = st.session_state.plot_type if "plot_type" in st.session_state else "Type 1"
    if plot_type == "Type 1":
        results_df = pd.DataFrame({"labels": results["labels"], "histogram": results["histogram"]})
        with streamlit_container:
            st.bar_chart(data=results_df, x="labels", y="histogram", x_label=results["bins_variable"], y_label="Proportion of samples" if max(results["histogram"]) <= 1 else "Number of samples", color=st.session_state.color)
    elif plot_type == "Type 3":
        results_UC = results["results_UC"]
        results_CD = results["results_CD"]
        results_control = results["results_control"]
        results_df = pd.DataFrame(data=np.array([results_UC["histogram"], results_CD["histogram"], results_control["histogram"]]).T, columns=["UC", "CD", "control"])
        results_df.insert(0, "labels", results_UC["labels"])
        with streamlit_container:
            st.bar_chart(data=results_df, x="labels", y=["UC", "CD", "control"], x_label=results_UC["bins_variable"], y_label="Proportion of samples" if max(results_UC["histogram"]) <= 1 else "Number of samples")


def get_matplotlib_config() -> dict:
    return dict(
        bins_distribution=st.session_state.get("bins_distribution", "uniform").lower(),
        plot_type=st.session_state.get("plot_type", "Type 1"),
        normalize_hist=st.session_state.get("normalize_hist", False),
        color=st.session_state.get("color", "#1f77b4"),
        alpha=st.session_state.get("alpha", 1.0),
        add_grid=st.session_state.get("add_grid", True),
        add_edge=st.session_state.get("add_edge", True),
        add_mean=st.session_state.get("add_mean", False),
        add_std=st.session_state.get("add_std", False),
        y_axis_log=st.session_state.get("y_axis_log", False),
    )


def create_hist_matplotlib(results: dict, matplotlib_config: dict):
    fig, ax = plt.subplots(figsize=(18, 5))
    if matplotlib_config["plot_type"] == "Type 1":
        histogram = np.asarray(results["histogram"])
        if matplotlib_config["normalize_hist"]:
            histogram = histogram / np.sum(histogram)
        bins = np.asarray(results["bins"])
        ax = plot_data_inside_ax(ax, bins, histogram, matplotlib_config)
        fig, ax = beautify_hist_matplotlib(fig, ax, results, histogram, bins, matplotlib_config)
    elif matplotlib_config["plot_type"] == "Type 3":
        fig, ax = plt.subplots(1, 1, figsize=(18, 5))
        total_bottom = np.zeros(len(results["results_UC"]["histogram"]))
        for class_to_plot in ["UC", "CD", "control"]:
            results_for_the_class = results[f"results_{class_to_plot}"]
            histogram = np.asarray(results_for_the_class["histogram"])
            if matplotlib_config["normalize_hist"]:
                histogram = histogram / np.sum(results["results_all"]["histogram"])
            bins = np.asarray(results_for_the_class["bins"])
            ax = plot_data_inside_ax(ax, bins, histogram, matplotlib_config, label=class_to_plot, bottom=total_bottom)
            total_bottom += histogram
        fig, ax = beautify_hist_matplotlib(fig, ax, results["results_all"], total_bottom, bins, matplotlib_config)
        ax.legend(title="Classes")
    return fig, ax


def plot_data_inside_ax(ax, bins: np.ndarray, histogram: np.ndarray, matplotlib_config: dict, label: str | None = None, bottom=None):
    width = np.diff(bins)
    ax.bar(bins[:-1], histogram, width=width, align="edge", edgecolor="black" if matplotlib_config["add_edge"] else None, color=matplotlib_config["color"] if "color" in matplotlib_config else None, alpha=matplotlib_config["alpha"], label=label, bottom=bottom)
    return ax


def beautify_hist_matplotlib(fig, ax, results: dict, histogram, bins, matplotlib_config: dict):
    if matplotlib_config["normalize_hist"]:
        yticks_labels = [float(item.get_text()) for item in ax.get_yticklabels()]
        ax.set_yticklabels([f"{item * 100:.1f}%" for item in yticks_labels])
    if matplotlib_config["add_mean"]:
        ax.axvline(results["mean"], color="red", linestyle="dashed", linewidth=1)
    if matplotlib_config["add_std"]:
        ax.axvline(results["mean"] - results["std"], color="orange", linestyle="dashed", linewidth=1)
        ax.axvline(results["mean"] + results["std"], color="orange", linestyle="dashed", linewidth=1)
    if matplotlib_config["bins_distribution"] == "logarithmic":
        ax.set_xscale("log")
    ax.set_xticks(bins)
    ax.set_xticklabels(np.round(bins, 1))
    ax.set_xlabel(results["bins_variable"])
    if matplotlib_config["y_axis_log"]:
        ax.set_yscale("log")
    ax.set_ylabel("Proportion of samples" if matplotlib_config["normalize_hist"] else "Number of samples")
    if matplotlib_config["add_grid"]:
        ax.set_axisbelow(True)
        ax.grid(True)
    ax.set_ylim([0, max(histogram) * 1.1])
    fig.tight_layout()
    return fig, ax


def load_data_for_plotting() -> dict:
    bins_variable = st.session_state.bins_variable
    if ":" in bins_variable:
        bins_variable = bins_variable.split(":")[1].strip()
    plot_type = st.session_state.plot_type
    if plot_type == "Type 1":
        path_to_results = project_path("results", bins_variable, "results_all.pkl")
        return load_data_from_pkl_file(path_to_results)
    results = {}
    for class_to_load in ["UC", "CD", "control", "all"]:
        path_to_results = project_path("results", bins_variable, f"results_{class_to_load}.pkl")
        results[f"results_{class_to_load}"] = load_data_from_pkl_file(path_to_results)
    return results


def load_data_from_pkl_file(path_to_results: str | Path) -> dict:
    with open(path_to_results, "rb") as f:
        results = pickle.load(f)
    x_labels = [f"{round(results['bins'][i], 1)}-{round(results['bins'][i + 1], 1)}" for i in range(len(results["bins"]) - 1)]
    results["labels"] = x_labels
    return results


def update_server_config() -> None:
    server_config = dict(
        n_nodes=int(st.session_state.checkbox_node_1) + int(st.session_state.checkbox_node_2),
        max_number_of_attempts=10,
        n_bins=st.session_state.n_bins,
        bins_variable=st.session_state.bins_variable,
        bins_distribution=st.session_state.bins_distribution.lower(),
        path_to_save="./results/",
    )
    with open(config_path("server_config.toml"), "w") as toml_file:
        toml.dump(server_config, toml_file)


def compute_hist(streamlit_container):
    update_server_config()
    subprocess.call(["sh", str(other_script_path("run_hist_app.sh"))])
    if st.session_state.plot_backend == "matplotlib":
        draw_hist_matplotlib(streamlit_container)
    else:
        draw_hist_streamlit(streamlit_container)


def train_ml_model(streamlit_container_for_the_plot=None):
    subprocess.call(["sh", str(other_script_path("run_ml_app.sh"))])
