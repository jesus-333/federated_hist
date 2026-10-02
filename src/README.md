# Package Structure and philosophy

## Structure

The package structure of this project is organized as follows:

- [`clinnova_fl/`](./clinnova_fl/)
  - [`__init__.py`](./clinnova_fl/__init__.py)
  - [`apps/`](./clinnova_fl/apps/)
  - [`config/`](./clinnova_fl/config/)
  - [`data_connector/`](./clinnova_fl/data_connector/)
  - [`dataset/`](./clinnova_fl/dataset/)
  - [`ui/`](./clinnova_fl/ui/)

You can read more detailed information about each module in the following sections.

By the way, this package is based on the Flower framework, a widely used framework for implementing Federated Learning (FL) applications.
I have included some details about the Flower framework in the following sections, but I strongly recommend you to read the Flower documentation and tutorials to get a better understanding of how it works.
It will for sure help you to understand how to implement a new FL app using this package.

## Philosophy

The package is designed to be a framework for implementing Federated Learning (FL) applications, with a focus on simplicity and ease of use for scientists and researchers. 
The goal is to provide a set of tools and abstractions that allow users to implement FL applications without having to worry about the underlying technical details.

This is particularly visible in the `apps` module, which provides a high-level interface for implementing FL applications, and the `dataset` and `data_connector` modules, which provide a high-level interface for accessing and manipulating datasets.
See the sections below for more details.

# `apps` module

## Brief introduction to Federated Learning and Flower

Since you reading this, I assume that you have at least a basic understanding of Federated Learning (FL) and the Flower framework.
But just to be sure, I will provide a very quick overiew. FL is a machine learning paradigm that allows multiple clients to collaboratively train a model without sharing their data.
The usual workflow is something like this :
- A central server creates a model with random weights and send it to the clients.
- Each client trains the model on its local data and sends the updated weights back to the server.
- The server aggregates the updates from the clients and sends back the updated model to the clients.
- Repeat the process until the model converges or a stopping criterion is met.
Then, you can have more complex workflows, and even remove the central server, the so called decentralized FL. But the main idea of sharing the model until some convergence is reached remains the same.
For your information, this package (at least for the moment) would not consider decentralized FL. So all the FL workflows implemented in this package will have a central server that orchestrates the FL process.

So in general, the usual workflow have two main "components" :
- A server that orchestrates the FL process, i.e. it sends the model to the clients, receives the updates from the clients, aggregates them and sends back the updated model to the clients. The way the server aggregates the updates from the clients is usually called "strategy".
- A number of clients that train the model on their local data and send the updates to the server. Ideally, data client data should never leave the client, and the server should never have access to the client data.

Now, to understand the rest of the package, you should have at least a basic understanding of the Flower framework, which is a framework for implementing FL applications.
You could broadly divide the Flower framework in two "parts" : Logic and infrastructure (these are not official Flower terms, but they are useful to understand how Flower works).
- The "Logic" part is the practical implementation of the FL logic, i.e. local training, aggregation in the server, experiment tracking etc. Flower call this part "app", and it is the part that is usually implemented by the scientist/researcher. This part is also the main focus of this package.
- The "infrastructure" part is responsible for the communication between the server and the clients, and for the orchestration of the FL process. This part is implemented by Flower itself, and is not something that you need to worry about when implementing a new app. Also, with the integration of Flower with NVFlare, the infrastructure part could be substituted by the latter. So you can basically run Flower app on top of NVFlare.

Each Flower app is composed by two "sub-apps" :
- A server app that implements the server logic, i.e. aggregation, eventual experiment tracking, etc.
- A client app that implements the client logic, i.e. it trains the model on local data.

Another things that you should know is that Flower already provides a number of "ready-to-use" strategy for the server app, e.g. FedAvg, FedProx, etc.
These are methods that already implement the aggregation logic for the server app, and you can use them in your app without having to implement them yourself.

## `app` module implementation

The [`apps`](./clinnova_fl/apps/) module, as the name suggests, use Flower to implement FL applications for this package. The module is designed to be modular and extensible, allowing for the addition of new FL applications with ease. 
Each application is organized into its own folder, containing the necessary files for both the server and client components. 
The general structure of the `apps` module is as follows :
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
Based on the configuration loaded when they are instantiated, they call the app-specific client and server functions (For more detail see the section on the `config` module).
(this means that the root "app" is the only "true" Flower app, and the other apps are just specific implementations called from the root app).

Each specific implementation of MUST have the same internal structure, with a `client.py` and `server.py` file that implement the client and server logic for that specific app.
The `cli.py` file is an optional file that include the logic to call the app directly from the command line.
Once implemented the app functions calls must be added to the generic [`client.py`](./clinnova_fl/apps/client.py) and [`server.py`](./clinnova_fl/apps/server.py) files, so they can be called from the root app.

E.g., if you use the histogram app, the [root `client.py`](./clinnova_fl/apps/client.py) calls the function in [`./clinnova_fl/apps/flower_hist/client.py`](./clinnova_fl/apps/flower_hist/client.py) and the [root `server.py`](./clinnova_fl/apps/server.py) calls the function in [`./clinnova_fl/apps/flower_hist/server.py`](./clinnova_fl/apps/flower_hist/server.py).

## How do you implement a new app?

Supposed you have an idea for a new app that you want to implement. The first step is to create a new folder inside the [`apps`](./clinnova_fl/apps/) module, with the name of your app. Inside this folder you must create the following files :
- `__init__.py` : the init file for the app folder.
- `client.py`: the file that implements the client logic for your app.
- `server.py`: the file that implements the server logic for your app.

For the next steps you need a little bit more knowledge about how Flower app works. 
I will provide you some details to allow you to understand how this package works and interact with Flower, but as mentioned above, I strongly recommend you to read the Flower documentation and tutorials to get a better understanding of how it works.

## Server app implementation

In Flower the main server app must always be function with a specific decorator, called precisely `@app.main()`.
In general the signature of the function is as follows :

```python
# Import the necessary modules from Flower
from flwr.common import Context
from flwr.server import Grid, ServerApp

app = ServerApp() # ServerApp is a class provided by Flower

@app.main() # Decorator that registers the function as the entry point of the server app
def main(grid: Grid, context: Context) -> None :
    # Server app logic goes here
    ...
```

The decorator register the function as the entry point of the server app, i.e. when Flower executes the app that function will be the first one to be called.
This is also the reason why the function is called `main()`, as it is the main function of the server app (to be fair the function can have any name, it's the decorator that makes it the entry point of the app... but I think that it is a good practice to call it `main()` to avoid confusion).
The function with the decorator takes in input two arguments, `grid` and `context`, which are custom objects provided by Flower to allow the app to interact with the Flower framework.
- `grid` : a `Grid` object that provides access to the grid of clients (i.e. the federated network). The grid is a collection of clients that are available for training. The `Grid` object provides methods to access the clients, e.g. to get the list of clients, to get a specific client, etc. See [here](https://flower.ai/docs/framework/ref-api/flwr.serverapp.Grid.html) for more details.
- `context` : a `Context` object that provides access to the context for your app. Practically, it's an object that contains some defined properties that can be used by used to access configurations and information about the app. See [here](https://flower.ai/docs/framework/ref-api/flwr.app.Context.html) and Flower Tutorials for more details.

Now, you do not have to implement this server app inside your `server.py` file, as it is already implemented in the root [`server.py`](./clinnova_fl/apps/server.py) file.
But what you need to implement in your `server.py` file is something quite similar. It is a function that will be called by the root server app, and that will implement the specific logic of your app.
The function MUST have a specific signature, as it will be called by the root server app with specific arguments. The signature of the function is as follows :

```python
from flwr.common import Context
from flwr.server import Grid, ServerApp

def main(grid: Grid, context : Context, experiment_config) -> None :
    ...
```

So the main differences are the absence of the decorator, and the presence of a third argument called `experiment_config`, which is a dictionary or a dataclass that contains the configuration for the experiment. For more details about the configuration see the section on the `config` module.
After that, inside the function you could do whatever things you want, e.g. you could implement the logic, to evaluate a model, to aggregate the updates from the clients, to save the results etc.
You can see the implementation of a server app that use a flower defined strategy in the [`flower_ml_tabular`](./clinnova_fl/apps/flower_ml_tabular/server.py) and an app that implement a custom strategy in the [`flower_hist`](./clinnova_fl/apps/flower_hist/server.py) app, which is a simple app that implements a histogram computation on the clients and aggregates the results on the server.

If you need to visualize the workflow of the server app, here there is a simple diagram :
```
flwr run --run_config app="app_name" path_server_config="path/to/server_config.toml"
    |
    v
root server.py main() function
    |
    v
your app server.py main() function
```

Here a more detailed breakdown :
- `flwr run --run_config app="app_name" path_server_config="path/to/server_config.toml"`
    - `flwr run` is a Flower command. When it is executed, it runs the app specified in the `pyproject.toml`. In this case the `pyproject.toml` included in this package will always run the root server app.
    - `--run_config` is an argument that allows to specify custom values for your app. In general, it allows you to pass any configuration values to your app. It must have a key-value structure.
    - In this package it will always have only two values :
        - `app` : the name of the app to run. It must be the same as the name of the folder that contains your app implementation inside the [`apps`](./clinnova_fl/apps/) module.
        - `path_server_config` : the path to the server config file. It must be a valid path to a config file that contains the configuration for your app. See the section on the `config` module for more details about the config file.
    - Note that this design choice regarding the `--run_config` argument was done to keep the `flwr run` command the as "lean" as possible and to save the majority of the configuration in files that could be easily backed up.
- When the `flwr run` it is executed, Flower will try to run the app specified in the `pyproject.toml` file.
    - `pyproject.toml`, must have a section called `[tool.flwr.app.components]` that specifies the server and client app to run. 
    - In this package, the `pyproject.toml` file is already configured to run the root server and client app, which are implemented in the [`apps`](./clinnova_fl/apps/) module. 
- When the root server app is executed, it will check the `--run_config`, and more precisely the value of the field `app`.
    - If the value of the field `app` is equal to the name of an app inside the package, then it will call the `main()` function of the `server.py` file of that app, passing the `grid`, `context` and `experiment_config` arguments to it.
    - `experiment_config` config are created in automatic way by the root server app, from the config file you specified in the `--run_config` argument. See the section on the `config` module for more details about the config file.

## Client app implementation

For all intents and purposes, the client app is very similar to the server app, with the main difference that it implements the client logic instead of the server logic.
The connection between the root client app and the specific client app follow the same structure as the server app, i.e. the root client app execute its required function and then call the specific client app function, passing the required arguments to it.

The main difference is the possible number of entry points for the client app.
For the server app, Flower provides a single decorator, `@app.main()`, that we already explained above (there is a side note about this... for those interested, it's at the end of the section.)
For the client app, instead, Flower provides three decorators : `@app.train()`, `@app.evaluate()` and `@app.query()`. 
So the root client app will call one (or more) of these three functions, which, in turn, will call the corresponding implementation within the server app.

What are the differences between these decorators? 
Depends on how you analyze them. From the point of view of strategies already implemented in Flower (e.g. FedAvg, FedProx, etc.), the `@app.train()` and `@app.evaluate()` decorators are the most important ones, as they are the ones that will be called by the strategy at each federated round.
Otherwise, if you want to implement your own strategy, they are (technically) interchangeable, but it is a good practice to use them as they are intended, i.e. `@app.train()` for the training logic and `@app.evaluate()` for the evaluation logic.
A little bit more detailed explanation about the three decorators is provided below.

### `@app.train()` and `@app.evaluate()` decorators

These are the most common decorators, and, as the name suggests, they are used to implement the training and evaluation logic of the client app.

Flower requires that the functions with these decorators have a specific signature, i.e.
```python
# Flower imports
from flwr.client import ClientApp
from flwr.common import Context, Message

app = ClientApp() # ClientApp is a class provided by Flower

@app.train()
def train(msg : Message, context : Context) :
    # Implement the training logic here
    ...

@app.evaluate()
def evaluate(msg : Message, context : Context) :
    # Implement the evaluation logic here
    ...
```

The two objects `msg` and `context` are provided by Flower to allow the app to interact with the Flower framework.
- `msg` : a `Message` object that contains the message between the server and the client. They were introduced by the with the [Message API Update](https://flower.ai/docs/framework/how-to-upgrade-to-message-api.html) and now they constitute the backbone of the communications in the federated network.
- `context` : same as the `context` object in the server app.

By the way, when you use strategies already implemented in Flower, e.g. FedAvg, FedProx, etc., these two functions are the one that will be called automatically by the strategy.
More specifically, at each round the strategy will call, in order, the `train()` function and then the `evaluate()` (in case you do not implement the latter, you will receive a warning).

But how does the Flower framework know which function to call each time?
Well, through the `msg` object. As mentioned above these objects are the backbone of the communications in the federated network. Between all the various fields there are two that are very important.
- One is called `content`, and contains the actual information of the message. Again, I will not go into details. Check Flower documentation for more details.
- The other is called `message_type`, and it is a string that indicates the type of message. Now the message type can have only 3 possible values : `train`, `evaluate` and `query`. 
So, when the client app receives a message from the server, it will check the `message_type` field of the `msg` object, and based on its value it will call the corresponding function, i.e. `train()` for `train`, `evaluate()` for `evaluate` and `query()` for `query`.

### `@app.query()` decorator

The `@app.query()` decorator is a little bit different from the other two, as it is not used by default by any Flower strategy. You can use it to implement custom communication logic between the server and the client to retrieve specific information.

If you want a full example you could check the [Histogram app](./clinnova_fl/apps/flower_hist/), which implements a histogram computation on the clients and aggregates the results on the server.
This app will always execute two custom rounds. 
In the first, the server sends a query message to the clients, asking for max and min values of the dataset.
Then, the clients will reply and the server will use these results to compute common histogram bins for all clients.
In the second round, the server will send another query message to the clients, asking for the histogram of the dataset using the common bins computed in the first round.
Then, the clients will reply and the server will aggregate the results to compute the final histogram.

# `config` module

# `data_connector` module and the `dataset` module

As mentioned above, the `data_connector` and `dataset` modules provide a high-level interface for accessing and manipulating datasets. 
So the decision behind the design of these two modules is to provide a clear separation between the raw data and the dataset used in the FL apps, and thus allow the researcher to focus solely on app development, without worrying about direct data access.


## `dataset` module overview

The `dataset` module provides a high-level interface for accessing and manipulating datasets, while the `data_connector` module provides a high-level interface for accessing raw data.
The scientist/researcher that implement a new app must only use the `dataset` module, and not the `data_connector` module, which is used internally by the `dataset` module to access the raw data.
Still, knowing how this two modules work is important to understand how to implement a new app, and how to use the `dataset` module.

So, the `dataset` module provides an high-level interface for accessing and manipulating dataset. What does this even mean? 
If you go inside the [`dataset`](./clinnova_fl/dataset/) module, you will find a number of classes that represent different types of datasets, e.g. [`image.py`](./clinnova_fl/dataset/images.py) for dataset whose data is composed by images.
At the moment the implemented datasets are :
- [`image.py`](./clinnova_fl/dataset/images.py) : for accessing image datasets.
- [`tabular.py`](./clinnova_fl/dataset/tabular.py) : for accessing tabular datasets.

All of these classes inherit from a base class called [`generic.py`](./clinnova_fl/dataset/generic.py), which provides a common interface for accessing and manipulating datasets.
The common methods provided by the base class are :
- `__init__` : the constructor, which takes a `dataset_id` string and a `data_connector` object as input. `dataset_id` is a unique identifier for the dataset, and `data_connector` is an object that provides access to the raw data. You do not have to worry about the `data_connector` object, as it is used internally by the `dataset` module to access the raw data. You just need to specify the `dataset_id` in your config.
- `__getitem__` : a method that allows to access the dataset using the `[]` operator. The method takes in input a generic `key` that can be used to access the dataset with `dataset_obj[key]` and returns the corresponding data. The `key` can be a string, an integer or other data type, depending on the specific dataset implementation.
- `__len__` : a method that allows to get the length of the dataset using the `len()` function. The method returns the number of data points in the dataset.

But how do you use concretely the `dataset` module? Well, when you develop an app you will develop it for a specific dataset type, e.g. image. 
Then in the code you will simply call the corresponding class and use its method. 
When you later will execute a federated app, during the execution the root client app will instantiate the corresponding dataset class, passing the `dataset_id` and the `data_connector` object to it.

## `data_connector` module overview

Ok. Now you know about the `dataset` module, but how does it access the raw data? Well, this is where the `data_connector` module comes into play.

As mentioned above, the `data_connector` module provides a way to access the raw data.
Concretely, it has a similar structure to the `dataset` module, with an abstract base class called [`generic.py`](./clinnova_fl/data_connector/generic.py) and a number of classes that inherit from it, e.g. [`csv.py`](./clinnova_fl/data_connector/csv.py) for accessing csv files.
At the moment the implemented data connectors are : 
- [`csv.py`](./clinnova_fl/data_connector/csv.py) : for accessing csv files.
- [`synthetic.py`](./clinnova_fl/data_connector/synthetic.py) : for generating synthetic data (this is not really used in federated deployments but it can be useful for testing and debugging). 

The base class interface has the same methods of the base class of the `dataset` module, i.e. `__init__`, `__getitem__` and `__len__`.
Then each child class has its own implementation of these methods, depending on the type of raw data it is designed to access.

When the dataset class is instantiated, it will also receive as input a `data_connector` object, specific for the type of raw data of the dataset defined by `dataset_id`.
Later the dataset class will simply call the corresponding method of the `data_connector` object to access the raw data.

Now you could ask... but when the dataset class is instantiated, how does it know which `data_connector` object to use? Well, this is where the `node-config` property of the client comes into play.
In Flower, each client has a property called `node-config`. This is a permanent "configuration" that exists on each client, and contains general information that can be used by each app that runs on that client.
The main idea behind this package is that each client has will have a `node-config` that contains the information about the data stored in that client. 

`node_config` will have a dictionary-like structure, with the `dataset_id` as keys and the corresponding config for that specific dataset as values. E.g.
```python
node_config = {
    "awesome_dataset" : {
        "dataset_connector_config_file_path" : "path/to/data_connector/config/in/the/client.toml",
        "dataset_types" : "tabular",
    }
    "wonderful_dataset" : {
        "dataset_connector_config_file_path" : "path/to/data_connector/config/in/the/client.toml",
        "dataset_types" : "image",
    }
```

Then, when the dataset class is instantiated, it will use the `dataset_id` to get the corresponding config from the `node_config`.
The config that it retrieves is another dictionary that contains two entries :
- `dataset_types` : the type of dataset, e.g. `tabular`, `image`, etc. This is used to instantiate the corresponding dataset class.
- `dataset_connector_config_file_path` : the path to the config file that contains the configuration

E.g. suppose you have a tabular dataset stored in a csv file. The dataset is called `awesome_dataset`. 
Then you specify in the config file the `dataset_id` as `awesome_dataset`

# `ui` module






