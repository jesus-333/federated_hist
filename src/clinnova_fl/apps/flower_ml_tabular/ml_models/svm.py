"""
Wrapper for a linear Support Vector Machine trained with SGD (sklearn).

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# Module imports
import numpy as np

# Specific imports
from sklearn.linear_model import SGDClassifier

# Internal imports
from clinnova_fl.apps.flower_ml_tabular.ml_models import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class model(generic.get_ml_model) :

    def __init__(self, model_config) :
        """
        Build a linear SVM (hinge loss) optimized with SGD.
        """

        self.model = SGDClassifier(
            loss         = model_config.get('loss', 'hinge'),
            penalty      = model_config.get('penalty', 'l2'),
            alpha        = model_config.get('alpha', 1e-4),
            tol          = model_config.get('tol', 1e-3),
            max_iter     = model_config.get('max_iter', 1),
            random_state = model_config.get('random_state', None),
            warm_start   = True,   # ESSENTIAL: lets fit() continue from the weights loaded by set_params each round instead of restarting from scratch.
        )

    def get_params(self) -> list :
        """
        Return the parameters of the model as a list of numpy arrays.

        Returns
        -------
        params : list
            The parameters of the model as a list of numpy arrays. For the SVM model, this is a list containing the coefficients and the intercept.
        """

        params = [
            self.model.coef_,
            self.model.intercept_,
        ]

        return params

    def set_params(self, params : list) -> None :
        """
        Set the parameters of the model from a list of numpy arrays.

        Parameters
        ----------
        params : list
            The parameters of the model as a list of numpy arrays. For the SVM model, this is a list containing the coefficients and the intercept.
        """

        self.model.coef_ = params[0]
        self.model.intercept_ = params[1]

    def init_params(self, num_classes : int, n_features : int) :
        """
        Initialise the model parameters before the first round.

        Note: you must call this before the first :func:`set_params()` call, otherwise the setter has no valid model to write into.
        """

        # Class labels. This is what makes the model usable for predict()
        # before fit() has ever run.
        self.model.classes_ = np.array([i for i in range(num_classes)])

        # Zero-filled placeholders with the correct. 
        # Note that sklearn linear classifiers use a single row for the binary case and one row per class for the multiclass (one-vs-all) case.
        n_rows = 1 if num_classes == 2 else num_classes
        coef = np.zeros((n_rows, n_features))
        intercept = np.zeros((n_rows,))
        initial_param = [coef, intercept]

        # Load the placeholders through the normal setter.
        self.set_params(initial_param)
