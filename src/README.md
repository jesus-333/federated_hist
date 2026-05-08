# Package Structure

The package structure of this project is organized as follows:


- [`clinnova_fl/`](./clinnova_fl/)
  - [`__init__.py`](./clinnova_fl/__init__.py)
  - [`fl_apps/`](./clinnova_fl/fl_apps/)
  - [`generic/`](./clinnova_fl/generic/)
  - [`ui/`](./clinnova_fl/ui/)

## `generic` module

The [`generic`](./clinnova_fl/generic/) module contains basic helper functions used by other modules, such as data loading and ML definitions.

## `fl_apps` module

The [`fl_apps`](./clinnova_fl/fl_apps/) module contains the implementation of the Federated Learning (FL) applications. Its internal structure is as follows:


- [`fl_apps/`](./clinnova_fl/fl_apps/)
  - [`__init__.py`](./clinnova_fl/fl_apps/__init__.py)
  - [`client.py`](./clinnova_fl/fl_apps/client.py)
  - [`server.py`](./clinnova_fl/fl_apps/server.py)
  - [`app_1_folder/`](./clinnova_fl/fl_apps/app_1_folder/)
    - [`__init__.py`](./clinnova_fl/fl_apps/app_1_folder/__init__.py)
    - [`client.py`](./clinnova_fl/fl_apps/app_1_folder/client.py)
    - [`server.py`](./clinnova_fl/fl_apps/app_1_folder/server.py)
  - ...
  - [`app_n_folder/`](./clinnova_fl/fl_apps/app_n_folder/)
    - [`__init__.py`](./clinnova_fl/fl_apps/app_n_folder/__init__.py)
    - [`client.py`](./clinnova_fl/fl_apps/app_n_folder/client.py)
    - [`server.py`](./clinnova_fl/fl_apps/app_n_folder/server.py)

The root [`client.py`](./clinnova_fl/fl_apps/client.py) and [`server.py`](./clinnova_fl/fl_apps/server.py) files are generic wrappers for the Flower client and server logic.
Based on the configuration loaded when they are instantiated, they call the app-specific client and server functions.

For example, if you use the histogram app, [`client.py`](./clinnova_fl/fl_apps/client.py) calls the function in [`./clinnova_fl/fl_apps/flower_hist/client.py`](./clinnova_fl/fl_apps/flower_hist/client.py) and [`server.py`](./clinnova_fl/fl_apps/server.py) calls the function in [`./clinnova_fl/fl_apps/flower_hist/server.py`](./clinnova_fl/fl_apps/flower_hist/server.py).

### How to add a new app?
