from __future__ import annotations

import streamlit as st

from clinnova_fl.ui.streamlit import components


def main() -> None:
    st.set_page_config(page_title="Clinnova Federated Hist PoC", layout="wide")
    st.header("Clinnova User Portal", divider=True)
    left, right = st.columns([0.5, 0.5], border=True, gap="medium")
    with left:
        components.build_ml_computation_basic_options()
    with right:
        components.build_ml_computation_settings()
    st.write("---")
    result_container = st.container(key="ml_training_results_container")
    with result_container:
        st.subheader("ML Training Results", divider=True)
        st.write("The average accuracy of the trained model is: xx.xx%")
        st.write("Confusion Matrix")
        st.dataframe({"": ["True Positive", "False Negative", "False Positive", "True Negative"], "Predicted Positive": [50, 5, 3, 42], "Predicted Negative": [2, 48, 4, 46]}, use_container_width=True)
        st.write("Model was saved to: /saved_model/model_SVM.pkl")


if __name__ == "__main__":
    main()
