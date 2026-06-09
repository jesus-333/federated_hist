TO UPDATE

# Package Structure

The package structure of this project is organized as follows:


- [`clinnova_fl/`](./clinnova_fl/)
  - [`__init__.py`](./clinnova_fl/__init__.py)
  - [`apps/`](./clinnova_fl/apps/)
  - [`config/`](./clinnova_fl/config/)
  - [`data_connector/`](./clinnova_fl/data_connector/)
  - [`dataset/`](./clinnova_fl/dataset/)
  - [`ui/`](./clinnova_fl/ui/)


## `apps` module

The [`apps`](./clinnova_fl/apps/) module contains the implementation of the Federated Learning (FL) applications. Its internal structure is as follows:

- [`apps/`](./clinnova_fl/apps/)
  - [`__init__.py`](./clinnova_fl/apps/__init__.py)
  - [`client.py`](./clinnova_fl/apps/client.py)
  - [`server.py`](./clinnova_fl/apps/server.py)
  - [`app_1_folder/`](./clinnova_fl/apps/app_1_folder/)
    - [`__init__.py`](./clinnova_fl/apps/app_1_folder/__init__.py)
    - [`cli.py`](./clinnova_fl/apps/app_1_folder/cli.py)
    - [`client.py`](./clinnova_fl/apps/app_1_folder/client.py)
    - [`server.py`](./clinnova_fl/apps/app_1_folder/server.py)
  - ...
  - [`app_n_folder/`](./clinnova_fl/apps/app_n_folder/)
    - [`__init__.py`](./clinnova_fl/apps/app_n_folder/__init__.py)
    - [`cli.py`](./clinnova_fl/apps/app_n_folder/cli.py)
    - [`client.py`](./clinnova_fl/apps/app_n_folder/client.py)
    - [`server.py`](./clinnova_fl/apps/app_n_folder/server.py)

The root [`client.py`](./clinnova_fl/apps/client.py) and [`server.py`](./clinnova_fl/apps/server.py) files are generic wrappers for the Flower client and server logic.
Based on the configuration loaded when they are instantiated, they call the app-specific client and server functions.

For example, if you use the histogram app, [`client.py`](./clinnova_fl/apps/client.py) calls the function in [`./clinnova_fl/apps/flower_hist/client.py`](./clinnova_fl/apps/flower_hist/client.py) and [`server.py`](./clinnova_fl/apps/server.py) calls the function in [`./clinnova_fl/apps/flower_hist/server.py`](./clinnova_fl/apps/flower_hist/server.py).

The `cli.py` file is an optional file that include the logic to call the app directly from the command line.

### How to add a new app?

## `config` module

## `data_connector` module

Provide the interaction between raw data and dataset

## `dataset` module

Provide the interface between data federated app and data

## CLI Interface
