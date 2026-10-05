# `ml_models/generic.py`

## Constants

`IMPLEMENTED_MODELS = ['lda', 'svm']`.

## `class generic_ml_model(ABC)`

- Abstract: `get_params() -> list`, `set_params(params : list) -> None`, `init_params(**kwargs) -> None`.
- Concrete :
    - `fit(X, y)` → `self.model.fit(X, y)`;
    - `predict(X)` → `self.model.predict(X)`;
    - `compute_metrics(y_true, y_predict, regression = False) -> dict`: regression → `{'mse', 'mae'}`, classification → `{'accuracy'}` (TODO: precision/recall/F1). **Missing `self`**, so calling it on an instance shifts the arguments (`y_true` becomes the instance).

There is no `__init__`. Subclasses must set `self.model`.

## `get_ml_model(ml_model_name : str, ml_model_config : dict) -> generic_ml_model`

Validates against `IMPLEMENTED_MODELS`, lazily imports `ml_models.<name>.model`, returns `model(ml_model_config)`.
