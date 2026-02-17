Copy of the Flower apps already developed to be shared.

# Notes on Flower Apps
Flower apps are the way flower managed the federated learning workflow. The high level structure of each app is more or less always the same :
- The Client Logic (ClientApp)(`client_app.py`): Defines how to train on local data.
- The Server Logic (ServerApp)(`server_app.py`): Defines how to aggregate the results.
- The Configuration (`pyproject.toml`): Tells Flower where to find these apps. Usually it specifies the federation settings, which file contains the app and eventually run settings (e.g. algorithm hyperparameters)

I add some extra notes about ClientApp and ServerApp inside [`client_app`](./flower_app_hist_V1/client_app.py) and [`server_app`](./flower_app_hist_V1/server_app.py) of the `flower_app_hist_V1` app.
Also I add some extra notes to [`pyproject.toml`](./flower_app_hist_V1/pyproject.toml) of the same app.

# List of Current Apps
- `flower_app_hist`. Compute histogram in a federated environment. It use the Flower Message API to create custom round (i.e. send and received specif data for each round)
- `flower_app_ml`. Train a linear classifier using the [Federated Average](https://flower.ai/docs/framework/ref-api/flwr.server.strategy.FedAvg.html) algorithm already implemented by flower.

# Versions List
Currently available
- V1. Work with synthetic data and synthetic config (both hardcoded inside the scripts)
    - Note that for both V1 apps I hardcoded the number of client as 2. So even if you run the simulation with more than 2 clients it should only use the first 2 that contact.
    - For the hist app It will create a histogram with 30 bins. The data for both clients are randomly generated sampling from a uniform distribution between 0 and 1

TODO
- V2. Config read from an external file and synthetic data.
- V3. Config read from an external file and data read from an external file


# How to ...

## How to run app with flower simulation?
To run the app using flower you could use the `flwr run` command specifying the federation you want to use and path to the app. The command has the following structure `flwr run [OPTIONS] [APP] [FEDERATION]`.
- `[OPTIONS]` are extra option for the command. You can ignore them for now.
- `[APP]` is the path of the Flower App to run (basically the folder where the `pyproject.toml` file is located).
- `FEDERATION` is the name of the federation to run the app on. (Note that you can run your app only in the federation specified inside the `pyproject.toml` file). If no federation is specified it will try to run the app on the default federation, defined by the field `[tool.flwr.federations]` inside `pyproject.toml`. If the default federation is not defined an no federation is provided the command will raise an error.

Examples :
- The command `flwr ./flower_app_ml_V1` will run the app on the federation called `local-deployment` since we do not provide any federation and the default federation is called `local-deployment`
- The command `flwr ./flower_app_ml_V1 local-simulation` will run the app inside the folder `./flower_app_hist_V1` with the settings specified in the field `[tool.flwr.federations.local-simulation]` of the [`pyproject.toml`](./flower_app_hist_V1/pyproject.toml) file.
- The command `flwr ./flower_app_ml_V1 remote-hist-fed` will raise an error since no federation called `remote-hist-fed` is present inside `pyproject.toml`

Useful links :
- Flower [tutorial](https://flower.ai/docs/framework/how-to-run-simulations.html) on simulation engine 
- Flower CLI commands [Documentation](https://flower.ai/docs/framework/ref-api-cli.html)

## How to run app with nvflare simulation?
I created two python scripts called [`nvflare_job.py`](./nvflare_job.py) and [`nvflare_recipe.py`](./nvflare_recipe.py) that works similarly to the `flwr run` command. 
You could execute the python script with the command 
```shell
python nvflare_job.py --job_name "flwr-job" --flower_app_dir "path/to/flower/app" --work_dir "path/to/work_dir"
``` 
where
- `--job_name`, name of the job in Flare.
- `--flower_app_dir`, path to the flower app (basically the folder where the `pyproject.toml` file is located)
- `--work_dir`, the folder where the nvflare simulation will be executed. If not specified by default will be `./nvflare_sim`

The only difference between the two script is that [`nvflare_job.py`](./nvflare_job.py) use the [`FlowerJob`](https://github.com/NVIDIA/NVFlare/blob/main/nvflare/app_opt/flower/flower_job.py) and [nvflare_recipe.py](./nvflare_recipe.py) use [`FlowerRecipe`](https://github.com/NVIDIA/NVFlare/blob/main/nvflare/app_opt/flower/recipe.py).
The `FlowerRecipe` is a [recipe](https://nvflare.readthedocs.io/en/main/user_guide/data_scientist_guide/job_recipe.html) of the `FlowerJob` (basically a wrapper of the `FlowerJob`).

So for example to run through simulation the app `flower_app_hist_V1` from this folder you have to run the command 
```shell
python nvflare_job.py --job_name "flwr-ml" --flower_app_dir "./flower_app_hist_V1/" --work_dir "./simulation/"
```

If the flag `--work_dir` is not specified, all the files of simulation will be placed automatically in a folder called `nvflare_sim`

## How to export app as nvflare job?
This is similar to the nvflare simulation but you have to add the `--export_job` flag to the script and change the flag `--work_dir` to `--export_dir`

So for example to export the app `flower_app_hist_V1` from this folder you have to run the command 
```shell
python nvflare_job.py --job_name "flwr-ml" --flower_app_dir "./flower_app_hist_V1/" --export_job --export_dir "./job_dir/"
```

If the flag `--export_dir` is not specified, all the files will be placed automatically in a folder called `nvflare_job`
