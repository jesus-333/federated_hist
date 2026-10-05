# `apps/flower_ml_tabular/ml_models` — quickstart

Thin wrappers around scikit-learn models that expose a uniform interface for federated training.
No model is implemented from scratch.

| File | Purpose | Page |
|------|---------|------|
| `__init__.py` | Docstring only. | — |
| `generic.py` | ABC `generic_ml_model`, `IMPLEMENTED_MODELS`, factory `get_ml_model`. | [`generic.md`](./generic.md) |
| `svm.py` | Linear SVM via `SGDClassifier` (hinge loss, `warm_start = True`). | [`svm.md`](./svm.md) |
| `lda.py` | `LinearDiscriminantAnalysis` wrapper (incomplete). | [`lda.md`](./lda.md) |

## Interface

```python
class generic_ml_model(ABC) :
    model                                   # the underlying sklearn estimator (set in __init__)
    get_params() -> list[np.ndarray]        # abstract
    set_params(params : list) -> None       # abstract
    init_params(num_classes, n_features)    # abstract, zero/placeholder params before round 1
    fit(X, y)                               # delegates to self.model.fit
    predict(X)                              # delegates to self.model.predict
    compute_metrics(y_true, y_pred, regression = False) -> dict   # accuracy, or mse/mae
```

Each concrete module must define a class named **`model`** taking `model_config : dict` in `__init__`.

## Adding a model

1. Create `ml_models/<name>.py` with `class model(generic.generic_ml_model)`.
2. Implement `__init__(self, model_config)` (set `self.model`), `get_params`, `set_params`, `init_params`.
3. Add `<name>` to `IMPLEMENTED_MODELS` and a branch in `get_ml_model`.
4. Parameters must be a list of numpy arrays (Flower `ArrayRecord`). Scalars must be wrapped in 1D arrays.
5. For models that benefit from multiple rounds, enable `warm_start` so that `fit` continues from the aggregated weights.

## Known issues

- `svm.py`/`lda.py` subclass `generic.get_ml_model` (a function) → `TypeError` on import. They must subclass `generic.generic_ml_model`.
- `compute_metrics` has no `self`.
- The abstract `init_params(self, **kwargs)` signature differs from the concrete ones `(num_classes, n_features)`.
