This repository contains code about Federated Learning experiments

N.B. All this work is still in the experimental stage. The repository is still a mess and it will be reorganized for sure in the future.

# How to launch an app?

## `flwr run` command 

## Custom commands

We also implemented some wrappers around the `flwr run` command. At the moment you have :
- `clinnova-hist`

Each command could receive in input the same arguments/flags of `flwr run`

## The `run_config`

Every time you launch an app you MUST pass the `--run_config.` flag. As the name suggest this are config for the current experiment.

But how do they work? Very simply, when `flwr run` is executed, flower checks inside the `pyproject.toml` file to see if there is an `tool.flwr.app.config` section.
If present, all entries within the section are loaded into the `run_config` (that is basically a dictionary you can access during runtime. See client and server implementations for some examples).

When the flag `--run_config` is used all the entries specified after the flag overwrite those in `pyproject.toml`
By design, however, it is not possible to use this flag to pass config options that are not already present in the file.
So any options you want to add in run config MUST also be present in `pyproject` in the `tool.flwr.app.config` section.

To keep things simple, at present, `run_config` should  have 3 necessary inputs (+2 extras) :
- `app` is the name of the app you want to run.
- `path_app_config` is the path to a `toml` file with all the config for the app you want to run.
- `dataset_id` is the id of the dataset you want to use for the experiment
- `simulation` is a boolean value and is one of the extra inputs. It is an extra flag used to indicate when I run the experiment in simulation mode.
- `run_with_nvflare` is a boolean value and is one of the extra inputs. It is a flag used to indicate if the app is executed through the NVFlare framework.
This allows me to keep the `pyproject.toml` file cleaner (only package related configurations, or flower settings) and any configuration related to scientific things is in dedicated files.

When an app is launched, the server read the `run_config` and load the config file. After that, the config, together with the dataset to use and the app name are stored in a dictionary called `experiment_config`
<!-- After that they are saved in a single dictionary called `experiment_config` with the following structure : -->

```python
experiment_config = dict(
    app = "x", # App name
    app_config = dict( ... ), # Config for the app x, load by the toml file specified by path_app_config
    dataset_id = 'Population_1234',
    simulation = False,
    run_with_nvflare = False
)
```

This `experiment_config` is then used by all the app (both server/client).


## To delete in future

### Debug 1
Run this commands if you have no output after you run `flwr run .`
```sh
# Kill any background SuperLink
flwr stop --all 2>/dev/null
pkill -f flower-superlink

# Foreground SuperLink with debug logs and simulation mode
FLWR_LOG_LEVEL=DEBUG flower-superlink --insecure --simulation
```
Then in another terminal run `flwr run .`

### NVFlare and Flower node config

See [here](https://github.com/NVIDIA/NVFlare/blob/51f9a59f8e7292ff57d1edb985a02176afde7d19/nvflare/app_opt/flower/applet.py#L227-L240) to see how flare create the custom node config
