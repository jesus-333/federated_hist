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
