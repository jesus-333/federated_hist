# `ml_models/svm.py`

## `class model(generic.get_ml_model)` (should be `generic.generic_ml_model`)

### `__init__(self, model_config : dict)`

```python
self.model = SGDClassifier(
    loss         = model_config.get('loss', 'hinge'),
    penalty      = model_config.get('penalty', 'l2'),
    alpha        = model_config.get('alpha', 1e-4),
    tol          = model_config.get('tol', 1e-3),
    max_iter     = model_config.get('max_iter', 1),
    random_state = model_config.get('random_state', None),
    warm_start   = True,   # continue from the aggregated weights each round
)
```

The debug template `[ml_model_config]` contains `LinearSVC`-style keys (`C`, `dual`, `multi_class`, `loss = "squared_hinge"`). Only `loss`, `penalty`, `alpha`, `tol`, `max_iter` are read here. `squared_hinge` is a valid `SGDClassifier` loss.

### `get_params()` → `[coef_, intercept_]`

### `set_params(params)` → sets `coef_`, `intercept_`

### `init_params(num_classes, n_features)`

Sets `classes_ = arange(num_classes)` and zero `coef_` with shape `(1 if binary else num_classes, n_features)` plus zero `intercept_`.

Caveat: with `warm_start = True`, `SGDClassifier.fit` reuses `coef_`/`intercept_` only when it has been fitted before. Setting the attributes manually may not be enough for sklearn to treat them as `coef_init`. Passing `coef_init`/`intercept_init` to `fit`, or using `partial_fit(classes = ...)`, is more robust (verify against the installed sklearn version).
