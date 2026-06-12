# Flower Histogram

Implementation of the Histogram App.

This app computes the histogram for a specific feature for a specific dataset, split among clients.
It works only on dataset that can be represented/stored as table (i.e. sample on the row and features on the column).

If the app runs successfully the results will be saved in folder `/path_superlink_execution/{path_to_save}/{bins_variable}/`, where `path_superlink_execution` is the folder where the `superlink` was created, and `path_to_save` and `bins_variable` are settings specific in the app config file (see below)
In total, 4 files will be produced :
- `bins_{bins_distribution}.npy` : Bins used to computed the histogram.
- `hist_{bins_distribution}.npy` : Histogram data (not normalized, only the raw cont is saved)
- `results_{bins_distribution}.pkl` : Dictionary serialized through the `pickle` package that contains the previous results plus all the settigns that you have used to run the app.
- `results_{bins_distribution}.toml` : Like `results_{bins_distribution}.pkl`  but as a toml file.

## App specific config

When creating the `toml` config file for this app the possible options are as follows
- `n_bins` : Number of bins you want to use to compute the histogram
- `bins_variable` : Name of the feature on which you want the histogram to be calculated.
- `bins_distribution` : Distribution of the bins. Can be only `uniform` or `logarithmic`.
- `path_to_save` : Path (in the server) where the results are saved.
- `create_plot` : Optional boolean. If present and set to True create also a plot and save it as png file (still to implement)

Example of `toml` config
```toml
n_bins = 10
bins_variable = "feature_0"
bins_distribution = "uniform"
path_to_save = "./results/"
create_plot = false
```
