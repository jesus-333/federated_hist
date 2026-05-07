"""

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
"""
import streamlit as st

import support_interface_ml

st.set_page_config(page_title = "Clinnova Federated Hist PoC", layout="wide")
debug = True
column_gap = 'medium'
st.header("Clinnova User Portal", divider = True)
column_proportions = [0.5, 0.5]
ml_training_basic_options_column, ml_training_advanced_options_column = st.columns(column_proportions, border = debug, gap = column_gap)
with ml_training_basic_options_column :
    support_interface_ml.build_ml_computation_basic_options()
with ml_training_advanced_options_column :
    support_interface_ml.build_ml_computation_settings()
st.write("---")
ml_training_results_container = st.container(key = 'ml_training_results_container')
with ml_training_results_container :
    st.subheader("ML Training Results", divider = True)
    st.write("The average accuracy of the trained model is: xx.xx%")
    st.write("Confusion Matrix")
    st.dataframe({'': ['True Positive', 'False Negative', 'False Positive', 'True Negative'], 'Predicted Positive': [50, 5, 3, 42], 'Predicted Negative': [2, 48, 4, 46]}, use_container_width = True)
    st.write("Model was saved to: /saved_model/model_SVM.pkl")
