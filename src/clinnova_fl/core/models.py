from __future__ import annotations

import numpy as np
from flwr.common import NDArrays
from sklearn import discriminant_analysis, linear_model, metrics, svm


def get_ml_model(ml_model_name: str, ml_model_config: dict):
    if ml_model_name == "SVM":
        return svm.LinearSVC(
            penalty=ml_model_config["penalty"],
            loss=ml_model_config["loss"],
            dual=ml_model_config["dual"],
            tol=ml_model_config["tol"],
            C=ml_model_config["C"],
            multi_class=ml_model_config["multi_class"],
            max_iter=ml_model_config["max_iter"],
        )
    if ml_model_name == "LDA":
        return discriminant_analysis.LinearDiscriminantAnalysis(
            solver=ml_model_config["solver"],
            shrinkage=ml_model_config["shrinkage"],
            tol=ml_model_config["tol"],
            n_components=ml_model_config["n_components"],
            store_covariance=True,
        )
    if ml_model_name == "LASSO":
        return linear_model.Lasso(alpha=ml_model_config["alpha"])
    raise ValueError(f"ML algorithm {ml_model_name} not implemented")


def get_model_params(ml_model_name: str, ml_model) -> NDArrays:
    if ml_model_name == "SVM":
        return [ml_model.coef_, ml_model.intercept_]
    if ml_model_name == "LDA":
        params = [
            ml_model.coef_,
            ml_model.intercept_,
            ml_model.covariance_,
            ml_model.means_,
            ml_model.priors_,
            ml_model.classes_,
            ml_model.labels_,
        ]
        if ml_model.solver == "svd":
            params.append(ml_model.scalings_)
        return params
    if ml_model_name == "LASSO":
        return [ml_model.coef_, np.asarray([ml_model.intercept_])]
    raise ValueError(f"ML algorithm {ml_model_name} not implemented")


def set_model_params(ml_model_name: str, ml_model, params: NDArrays):
    if ml_model_name == "SVM":
        ml_model.coef_ = params[0]
        if ml_model.fit_intercept:
            ml_model.intercept_ = params[1]
    elif ml_model_name == "LDA":
        ml_model.coef_ = params[0]
        ml_model.intercept_ = params[1]
        ml_model.covariance_ = params[2]
        ml_model.means_ = params[3]
        ml_model.priors_ = params[4]
        ml_model.classes_ = params[5]
        ml_model.labels_ = params[6]
        if ml_model.solver == "svd":
            ml_model.scalings_ = params[7]
    elif ml_model_name == "LASSO":
        ml_model.coef_ = params[0]
        if ml_model.fit_intercept:
            ml_model.intercept_ = params[1][0]
    else:
        raise ValueError(f"ML algorithm {ml_model_name} not implemented")
    return ml_model


def set_initial_params(ml_model_name: str, ml_model, n_classes: int, n_features: int):
    if ml_model_name in {"SVM", "LASSO"}:
        ml_model.classes_ = np.array([i for i in range(n_classes)])
        coef = np.zeros((n_classes, n_features))
        intercept = np.zeros((n_classes,))
        initial_param = [coef, intercept]
        x_fake = np.random.rand(n_classes, n_features)
        y_fake = np.arange(n_classes)
        ml_model.fit(x_fake, y_fake)
    elif ml_model_name == "k-means":
        initial_param = get_kmeans_initial_parameters()
    else:
        raise ValueError(f"ML algorithm {ml_model_name} not implemented")
    return set_model_params(ml_model_name, ml_model, initial_param)


def get_kmeans_initial_parameters():
    raise NotImplementedError


def serialize_model_weights(ml_model_name: str, params: NDArrays) -> dict:
    if ml_model_name == "SVM":
        return {f"coef_class_{i}": list(params[0][i]) for i in range(len(params[0]))} | {"intercept": list(params[1])}
    if ml_model_name == "LASSO":
        return {"coef": list(params[0]), "intercept": list(params[1])}
    raise ValueError(f"ML algorithm {ml_model_name} not implemented")


def deserialize_model_weights(ml_model_name: str, weights: dict) -> NDArrays:
    if ml_model_name == "SVM":
        coef = np.array([np.array(weights[f"coef_class_{i}"]) for i in range(len(weights) - 1)])
        return [coef, np.array(weights["intercept"])]
    if ml_model_name == "LASSO":
        return [np.array(weights["coef"]), np.array(weights["intercept"])]
    raise ValueError(f"ML algorithm {ml_model_name} not implemented")


def compute_metrics(y_true, y_predict, regression: bool = False) -> dict:
    if regression:
        return {
            "mse": metrics.mean_squared_error(y_true, y_predict),
            "mae": metrics.mean_absolute_error(y_true, y_predict),
        }
    return {"accuracy": metrics.accuracy_score(y_true, y_predict)}
