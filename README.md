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

To keep things simple, at present, `run_config` should only take two inputs :
- `app` is the name of the app you want to run
- `path_server_config` is the path to a `toml` file with all the config for the app you want to run
This allows me to keep the `pyproject.toml` file cleaner (only package related configurations, or flower settings) and any configuration related to scientific things is in dedicated files.

