"""
Support function used for the streamlit interface (ml algorithm)

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import streamlit as st
import subprocess

import support_plot_ml
import support_interface_hist

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def build_ml_computation_basic_options() :
    st.subheader("Federation Settings", divider = True)

    column_proportions = [0.5, 0.5]
    bins_options_column, node_option_column  = st.columns(column_proportions)

    st.selectbox(
        label = 'Select the ML model',
        options = ['SVM'], index = 0,
        key = 'ml_model_name',
    )

    st.write("Node to use for the computation")
    st.checkbox('Client 1', key = 'checkbox_node_1', value = True)
    st.checkbox('Client 2', key = 'checkbox_node_2', value = True)

    st.button(
        label    = "Train Model",
        key      = "train_ml_model",
        on_click = train_ml_model,
    )

def build_ml_computation_settings() :
    st.subheader("Algorithm hyperparameters", divider = True)
    ml_model_name = st.session_state.ml_model_name

    if ml_model_name == 'SVM' :
        build_SVM_computation_settings()

def build_SVM_computation_settings() :
    """
    Add hyperparameters for sklearn SVM model
    """

    st.selectbox(
        label = 'Penalty',
        options = ['l2', 'l1'], index = 0,
        key = 'svm_penalty',
    )

    st.selectbox(
        label = 'Loss function',
        options = ['squared_hinge', 'hinge'], index = 0,
        key = 'svm_loss',
    )

    st.checkbox(
        label = 'Dual formulation',
        key = 'svm_dual',
        value = True,
    )

    st.number_input(
        label = 'Tolerance for stopping criteria',
        min_value = 1e-6, max_value = 1e-1, step = 1e-6,
        value = 1e-4,
        format="%.6f",
        key = 'svm_tol',
    )

    st.number_input(
        label = 'Regularization parameter C',
        min_value = 0.01, max_value = 10.0, step = 0.01,
        value = 1.0,
        format="%.2f",
        key = 'svm_C',
    )

    st.selectbox(
        label = 'Multi-class strategy',
        options = ['ovr', 'crammer_singer'], index = 0,
        key = 'svm_multi_class',
    )

    st.number_input(
        label = 'Maximum number of iterations',
        min_value = 100, max_value = 10000, step = 100,
        value = 1000,
        key = 'svm_max_iter',
    )

def build_ml_plot_options(streamlit_container_for_the_plot) :
    st.subheader("Plot Settings", divider = True)

    st.write("Class color")
    color_column_list = st.columns([0.33, 0.33, 0.33])
    
    for i in range(3) :
        with color_column_list[i] :
            st.selectbox(
                label = f"Color class {i}",
                options = support_plot_ml.get_color_hex(), index = i,
                format_func = support_plot_ml.get_color_name_from_hex,
                key = f'color_class_{i}',
                on_change = support_plot_ml.plot_decision_boundary,
                args = [streamlit_container_for_the_plot]
            )

    st.radio(
        label = "Training mode",
        options = ["FL training", "Only client 1", "Only client 2"],
        captions = [
            "Show the decision boundary obtained with the FL training",
            "Show the decision boundary if only data from client 1 were used for the training",
            "Show the decision boundary if only data from client 2 were used for the training",
        ],
        key = 'type_of_params',
        on_change = support_plot_ml.plot_decision_boundary,
        args = [streamlit_container_for_the_plot]
    )

    st.slider(
        label = "Grid Resolution",
        min_value = 0.01, max_value = 1., step = 0.01,
        value = 0.05,
        key = 'grid_resolution',
    )

    st.slider(
        label = "Grid Padding (%)",
        min_value = 0., max_value = 1., step = 0.01,
        value = 0.05,
        key = 'grid_padding',
    )

    st.selectbox(
        label = 'Dimensionality Reduction Method',
        options = ['None', 'PCA', 't-SNE'], index = 0,
        key = 'dimensionality_reduction',
        on_change = support_plot_ml.plot_decision_boundary,
        args = [streamlit_container_for_the_plot]
    )

    build_options_dimensionality_reduction(st.session_state.dimensionality_reduction, streamlit_container_for_the_plot)

def build_options_dimensionality_reduction(dimensionality_reduction_methods : str, streamlit_container_for_the_plot) :
    if dimensionality_reduction_methods == 'None' :
        clf_variables = support_interface_hist.read_txt_list("./streamlit_interface/field_hist.txt")

        # Create column for the two variable to plot
        column_variable_1, column_variable_2 = st.columns([0.5, 0.5])

        with column_variable_1 :
            st.selectbox(
                label = 'Variable 1',
                options = clf_variables, index = 0,
                key = 'clf_variable_1',
                on_change = support_plot_ml.plot_decision_boundary,
                args = [streamlit_container_for_the_plot]
            )

        with column_variable_2 :
            st.selectbox(
                label = 'Variable 2',
                options = clf_variables, index = 1,
                key = 'clf_variable_2',
                on_change = support_plot_ml.plot_decision_boundary,
                args = [streamlit_container_for_the_plot]
            )
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def train_ml_model(streamlit_container_for_the_plot) :

    subprocess.call(['sh', './other_scripts/run_ml_app.sh'])

