"""
Wrapper for the lda (Linear Discriminant Analysis) model provided by sklearn

Authors
-------
Alberto Zancanaro <alberto.zancanaro@uni.lu>
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

from sklearn import discriminant_analysis

from clinnova_fl.apps.flower_ml_tabular.ml_models import generic

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class model(generic.get_ml_model) :

    def __init__(self, model_config) :
        """
        """

        self.model = discriminant_analysis.LinearDiscriminantAnalysis(
            solver           = model_config['solver'],
            shrinkage        = model_config['shrinkage'],
            tol              = model_config['tol'],
            n_components     = model_config['n_components'],
            store_covariance = True,
        )
    
    def get_params(self) -> list :
        """
        Return the parameters of the model as a list of numpy arrays.
        
        Returns
        -------
        params : list
            The parameters of the model as a list of numpy arrays. For the LDA model, this is a list containing the coefficients and the intercept.
        """

        params = [
            self.model.coef_,
            self.model.intercept_,
            self.model.covariance_,
            self.model.means_,
            self.model.priors_,
            self.model.classes_,
            self.model.labels_,
        ]

        return params

    def set_params(self, params : list) -> None :
        """
        Set the parameters of the model from a list of numpy arrays.
        
        Parameters
        ----------
        params : list
            The parameters of the model as a list of numpy arrays. For the LDA model, this is a list containing the coefficients and the intercept.
        """

        self.model.coef_       = params[0]
        self.model.intercept_  = params[1]
        self.model.covariance_ = params[2]
        self.model.means_      = params[3]
        self.model.priors_     = params[4]
        self.model.classes_    = params[5]
        self.model.labels_     = params[6]

        if self.model.solver == 'svd' : self.model.scalings_ = params[7]

    def init_params(self, num_classes : int, n_features : int) :
        """
        """

        n_rows = 1 if num_classes == 2 else num_classes








