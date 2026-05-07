"""
Support function for the ml training

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
@date: September 2025
"""
import numpy as np
import pandas as pd

from sklearn import svm, discriminant_analysis, linear_model
from sklearn import metrics

from collections.abc import Iterable

from flwr.common import NDArrays

def get_ml_model(ml_model_name : str, ml_model_config : dict) :
    if ml_model_name == 'SVM' :
        model = svm.LinearSVC(
            penalty = ml_model_config['penalty'],
            loss = ml_model_config['loss'],
            dual = ml_model_config['dual'],
            tol = ml_model_config['tol'],
            C = ml_model_config['C'],
            multi_class = ml_model_config['multi_class'],
            max_iter = ml_model_config['max_iter']
        )
    elif ml_model_name == 'LDA' :
        model = discriminant_analysis.LinearDiscriminantAnalysis(
            solver = ml_model_config['solver'],
            shrinkage = ml_model_config['shrinkage'],
            tol = ml_model_config['tol'],
            n_components = ml_model_config['n_components'],
            store_covariance = True,
        )
    elif ml_model_name == 'LASSO' :
        model = linear_model.Lasso(alpha = ml_model_config['alpha'])
    else :
        raise ValueError(f"ML algorithm {ml_model_name} not implemented")
    return model

def get_model_params(ml_model_name : str, ml_model) -> NDArrays:
    if ml_model_name == 'SVM' :
        return [ml_model.coef_, ml_model.intercept_]
    elif ml_model_name == 'LDA' :
        params = [ml_model.coef_, ml_model.intercept_, ml_model.covariance_, ml_model.means_, ml_model.priors_, ml_model.classes_, ml_model.labels_]
        if ml_model.solver == 'svd' :
            params.append(ml_model.scalings_)
    elif ml_model_name == 'LASSO' :
        params = [ml_model.coef_, np.asarray([ml_model.intercept_])]
    else:
        raise ValueError(f"ML algorithm {ml_model_name} not implemented")
    return params

def set_model_params(ml_model_name : str, ml_model, params: NDArrays) :
    if ml_model_name == 'SVM' :
        ml_model.coef_ = params[0]
        if ml_model.fit_intercept:
            ml_model.intercept_ = params[1]
    elif ml_model_name == 'LDA' :
        ml_model.coef_ = params[0]
        ml_model.intercept_ = params[1]
        ml_model.covariance_ = params[2]
        ml_model.means_ = params[3]
        ml_model.priors_ = params[4]
        ml_model.classes_ = params[5]
        ml_model.labels_ = params[6]
        if ml_model.solver == 'svd' :
            ml_model.scalings_ = params[7]
    elif ml_model_name == 'LASSO' :
        ml_model.coef_ = params[0]
        if ml_model.fit_intercept:
            ml_model.intercept_ = params[1][0]
    else:
        raise ValueError(f"ML algorithm {ml_model_name} not implemented")
    return ml_model

def set_initial_params(ml_model_name : str, ml_model, n_classes : int, n_features : int) :
    if ml_model_name == 'SVM' or ml_model_name == 'LASSO':
        ml_model.classes_ = np.array([i for i in range(n_classes)])
        coef = np.zeros((n_classes, n_features))
        intercept = np.zeros((n_classes,))
        initial_param = [coef, intercept]
        x_fake = np.random.rand(n_classes, n_features)
        y_fake = np.arange(n_classes)
        ml_model.fit(x_fake, y_fake)
    elif ml_model_name == 'k-means' :
        initial_param = get_kmeans_initial_parameters()
    else:
        raise ValueError(f"ML algorithm {ml_model_name} not implemented")
    ml_model = set_model_params(ml_model_name, ml_model, initial_param)
    return ml_model

def get_kmeans_initial_parameters() :
    pass

def read_txt_list(filepath : str) -> list[str]:
    with open(filepath, "r") as file:
        lines = file.readlines()
    lines = [line.strip() for line in lines if line.strip()]
    return lines

def get_data(path_data : str, fields_to_use_for_the_train : Iterable[str] | None = None) -> tuple[np.ndarray, np.ndarray]:
    dataset_client = pd.read_csv(path_data)
    x_data = dataset_client[fields_to_use_for_the_train].to_numpy()
    labels_str = dataset_client['Diagnosis'].to_numpy()
    labels_str_to_int = {'Control': 0, 'UC': 1, 'CD': 2}
    y_data = [labels_str_to_int[label] for label in labels_str]
    return x_data, y_data, labels_str

def compute_metrics(y_true, y_predict, regression : bool = False) -> dict:
    metrics_dict = dict()
    if regression :
        metrics_dict['mse'] = metrics.mean_squared_error(y_true, y_predict)
        metrics_dict['mae'] = metrics.mean_absolute_error(y_true, y_predict)
    else :
        metrics_dict['accuracy'] = metrics.accuracy_score(y_true, y_predict)
    return metrics_dict
