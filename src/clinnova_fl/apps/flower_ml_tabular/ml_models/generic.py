"""
Implementation of a generic ML model, which will be used as a base class for all the ML models implemented in this module.

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from __future__ import annotations

# General imports
from abc import ABC, abstractmethod
from sklearn import metrics

import numpy as np

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

IMPLEMENTED_MODELS = [
    'lda',
    'svm'
]

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class generic_ml_model(ABC) :
    
    @abstractmethod
    def get_params(self) -> list :
        """
        Return the parameters of the model as a list of numpy arrays.
        """

        pass

    @abstractmethod
    def set_params(self, params : list) -> None :
        """
        Set the parameters of the model from a list of numpy arrays.
        """

        pass

    @abstractmethod
    def init_params(self, **kwargs) -> None :
        """
        Initialize the parameters of the model. This method is used to set the initial parameters of the model before the first round of training.
        
         
        Note from a Flower tutorial (https://github.com/flwrlabs/flower/blob/main/examples/quickstart-sklearn/sklearnexample/task.py)
        Required since model params are uninitialized until model.fit is called but server asks for initial parameters from clients at launch. 
        Refer to sklearn.linear_model.LogisticRegression documentation for more information.

        Not sure if it is true for all the sklearn models, but worth keeping in mind.

        In case your model to not need to initialize the parameters, simply implement this method as a pass.
        """

        pass

    def fit(self, X : np.array, y : np.array) -> None :
        """
        Fit the model on the given data. Simply call the fit method of the underlying model.
        Simply call the fit method of the underlying model.

        Parameters
        ----------
        X : np.array
            The input data.
        y : np.array
            The labels.
        """

        self.model.fit(X, y)

    def predict(self, X : np.array) -> np.array :
        """
        Predict the labels for the given input data. 
        Simply call the predict method of the underlying model.

        Parameters
        ----------
        X : np.array
            The input data.

        Returns
        -------
        y_predict : np.array
            The predicted labels.
        """

        return self.model.predict(X)

    def compute_metrics(y_true : list | np.array, y_predict : list | np.array, regression : bool = False) -> dict:
        """
        Compute metrics based on labels and return thme in a dictionary.

        Parameters
        ----------
        y_true : list | np.array
            The true labels.
        y_predict : list | np.array
            The predicted labels.
        regression : bool, optional
            Whether the task is a regression task or a classification task. Default is False (classification).

        Returns
        -------
        metrics_dict : dict
            A dictionary containing the computed metrics. The keys of the dictionary are the names of the metrics and the values are the computed values of the metrics.
            If regression is True, the dictionary will contain the following metrics :
                - 'mse' : mean squared error
                - 'mae' : mean absolute error
            If regression is False, the dictionary will contain the following metrics :
                - 'accuracy' : accuracy score
        """

        metrics_dict = dict()

        if regression :
            metrics_dict['mse'] = metrics.mean_squared_error(y_true, y_predict)
            metrics_dict['mae'] = metrics.mean_absolute_error(y_true, y_predict)
        else :
            metrics_dict['accuracy'] = metrics.accuracy_score(y_true, y_predict)

            # TODO : add more metrics for classification, such as precision, recall, f1-score, etc.

        return metrics_dict

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -


def get_ml_model(ml_model_name : str, ml_model_config : dict) -> generic_ml_model:
    """
    Given the ml model name and its config, return an instance of the ml model.
    """

    if ml_model_name not in IMPLEMENTED_MODELS : raise ValueError(f"ML model {ml_model_name} not implemented. Implemented models are: {IMPLEMENTED_MODELS}")

    if ml_model_name == 'lda' :
        from clinnova_fl.apps.flower_ml_tabular.ml_models.lda import model
    elif ml_model_name == 'svm' :
        from clinnova_fl.apps.flower_ml_tabular.ml_models.svm import model

    ml_model = model(ml_model_config)

    return ml_model

