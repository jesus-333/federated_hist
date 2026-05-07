"""
Support function used for the streamlit interface (ml algorithm)

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
"""
import streamlit as st
import subprocess

import support_plot_ml
import support_interface_hist

def build_ml_computation_basic_options() :
    st.subheader("Federation Settings", divider = True)
    st.selectbox(label = 'Select the ML model', options = ['SVM'], index = 0, key = 'ml_model_name')
    st.write("Node to use for the computation")
    st.checkbox('Client 1', key = 'checkbox_node_1', value = True)
    st.checkbox('Client 2', key = 'checkbox_node_2', value = True)
    st.button(label = "Train Model", key = "train_ml_model", on_click = train_ml_model)

def build_ml_computation_settings() :
    st.subheader("Algorithm hyperparameters", divider = True)
    ml_model_name = st.session_state.ml_model_name
    if ml_model_name == 'SVM' :
        build_SVM_computation_settings()

def build_SVM_computation_settings() :
    st.selectbox(label = 'Penalty', options = ['l2', 'l1'], index = 0, key = 'svm_penalty')
    st.selectbox(label = 'Loss function', options = ['squared_hinge', 'hinge'], index = 0, key = 'svm_loss')
    st.checkbox(label = 'Dual formulation', key = 'svm_dual', value = True)
    st.number_input(label = 'Tolerance for stopping criteria', min_value = 1e-6, max_value = 1e-1, step = 1e-6, value = 1e-4, format="%.6f", key = 'svm_tol')
    st.number_input(label = 'Regularization parameter C', min_value = 0.01, max_value = 10.0, step = 0.01, value = 1.0, format="%.2f", key = 'svm_C')
    st.selectbox(label = 'Multi-class strategy', options = ['ovr', 'crammer_singer'], index = 0, key = 'svm_multi_class')
    st.number_input(label = 'Maximum number of iterations', min_value = 100, max_value = 10000, step = 100, value = 1000, key = 'svm_max_iter')

def train_ml_model(streamlit_container_for_the_plot) :
    subprocess.call(['sh', './other_scripts/run_ml_app.sh'])
