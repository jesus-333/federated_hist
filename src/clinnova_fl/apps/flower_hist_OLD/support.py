"""
Support function for flower_hist app.
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

import matplotlib.pyplot as plt
import numpy as np

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def create_histogram(bins : np.ndarray, data : np.ndarray) -> plt.Figure:
    """
    Create a histogram from the given data.
    """

    fig, ax = plt.subplots()
    ax.hist(data, bins = bins)
    ax.set_xlabel("Value")
    ax.set_ylabel("Frequency")
    ax.set_title("Histogram")

    return fig
