# `apps/flower_ml_tabular/support_ml_app.py`

Legacy procedural helpers from the PoC, superseded by `ml_models/`.
It is **not imported** by the current app code (only commented references remain in `server.py`).
A near-identical copy lives in `ui/OLD_streamlit_interface/support_ml_app.py`.

## Functions

- `get_ml_model(ml_model_name, ml_model_config)`: `'SVM'` → `sklearn.svm.LinearSVC`, `'LDA'` → `LinearDiscriminantAnalysis(store_covariance = True)`, `'LASSO'` → `linear_model.Lasso`.
- `get_model_params(ml_model_name, ml_model) -> NDArrays`: SVM `[coef_, intercept_]`; LDA `[coef_, intercept_, covariance_, means_, priors_, classes_, labels_ (+ scalings_ if svd)]`; LASSO `[coef_, [intercept_]]`.
- `set_model_params(ml_model_name, ml_model, params)`: inverse of the above.
- `set_initial_params(ml_model_name, ml_model, num_classes, n_features)`: fits on random data, following the Flower sklearn quickstart. It is buggy: `np.random.rand((a, b))` takes a tuple, and `get_kmeans_initial_parameters` is a stub.
- `read_txt_list(filepath) -> list[str]`: non-empty stripped lines.
- `get_data(path_data, fields_to_use_for_the_train)`: reads the CSV and maps `Diagnosis` labels `{'Control': 0, 'UC': 1, 'CD': 2}` (PRISM IBD dataset). Returns 3 values despite the 2-tuple annotation.

Use it only as a reference (e.g. for the LASSO wrapper or the label mapping) when extending `ml_models/`.
