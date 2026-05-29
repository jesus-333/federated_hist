"""
Support function for flower_hist app.
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import matplotlib.pyplot as plt
import numpy as np

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def plot_single_hist(bins : np.ndarray, hist_data : np.ndarray) -> plt.Figure:
    """
    Create a histogram from the given data.
    """

    fig, ax = plt.subplots()
    ax.hist(hist_data, bins = bins)
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    ax.set_title("Histogram")

    return fig


def plot_merge_hist(bins : np.ndarray, list_of_hist_data : list[np.ndarray], list_of_labels : list[str]) -> plt.Figure:
    """
    Given a list of histogram, that share the same bins, merge them in a single histogram and return the figure.
    """

