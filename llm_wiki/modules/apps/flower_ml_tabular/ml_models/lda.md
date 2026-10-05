# `ml_models/lda.py`

## `class model(generic.get_ml_model)` (should be `generic.generic_ml_model`)

### `__init__(self, model_config : dict)`

`LinearDiscriminantAnalysis(solver, shrinkage, tol, n_components, store_covariance = True)`.
All keys are required (`model_config[...]`, no defaults). The debug template has none of `solver`, `shrinkage`, `n_components`.

### `get_params()`

`[coef_, intercept_, covariance_, means_, priors_, classes_, labels_]`.

### `set_params(params)`

Sets the same attributes and also `scalings_ = params[7]` when `solver == 'svd'`.

### `init_params(num_classes, n_features)`

**Unfinished**: it computes `n_rows` and does nothing else.

## Known issues

- `labels_` is not a `LinearDiscriminantAnalysis` attribute, so `get_params` raises `AttributeError`.
- `get_params` does not return `scalings_`, but `set_params` reads `params[7]` for `svd`.
- Averaging LDA parameters with FedAvg is not statistically equivalent to centralized LDA. A proper federated LDA should aggregate sufficient statistics (class counts, means, scatter matrices), e.g. through a custom QUERY strategy like `flower_hist`.
