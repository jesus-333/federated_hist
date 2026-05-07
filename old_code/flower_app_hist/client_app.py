"""
@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
@date: September 2025
"""
import numpy as np
import pandas as pd

from flwr.client import ClientApp
from flwr.common import Context, Message, MetricRecord, RecordDict

app = ClientApp()

@app.query()
def query(msg : Message, context : Context):
    path_client_data = context.node_config["path_client_data"]
    my_config = msg.content.config_records["my_config"]
    server_round = my_config["server_round"]
    bins_variable = my_config["bins_variable"]
    data_hist_all, _ = get_data(path_client_data, bins_variable)
    data_hist_UC, _ = get_data(path_client_data, bins_variable, 'UC')
    data_hist_CD, _ = get_data(path_client_data, bins_variable, 'CD')
    data_hist_control, _ = get_data(path_client_data, bins_variable, 'Control')

    query_results = {}
    if server_round == 0 :
        query_results["min"] = np.min(data_hist_all).item()
        query_results["max"] = np.max(data_hist_all).item()
    elif server_round == 1 :
        bins = my_config["bins"]
        freqs_all, _     = np.histogram(data_hist_all, bins = bins)
        freqs_UC, _      = np.histogram(data_hist_UC, bins = bins)
        freqs_CD, _      = np.histogram(data_hist_CD, bins = bins)
        freqs_control, _ = np.histogram(data_hist_control, bins = bins)
        query_results["histogram_all"]     = freqs_all.tolist()
        query_results["histogram_UC"]      = freqs_UC.tolist()
        query_results["histogram_CD"]      = freqs_CD.tolist()
        query_results["histogram_control"] = freqs_control.tolist()
        query_results["average_all"]     = np.mean(data_hist_all).item()
        query_results["std_all"]         = np.std(data_hist_all).item()
        query_results["average_UC"]      = np.mean(data_hist_UC).item()
        query_results["std_UC"]          = np.std(data_hist_UC).item()
        query_results["average_CD"]      = np.mean(data_hist_CD).item()
        query_results["std_CD"]          = np.std(data_hist_CD).item()
        query_results["average_control"] = np.mean(data_hist_control).item()
        query_results["std_control"]     = np.std(data_hist_control).item()
    else :
        raise ValueError(f"Server round {server_round} not supported.")

    reply_content = RecordDict({"query_results": MetricRecord(query_results)})
    return Message(reply_content, reply_to = msg)

def get_data(path_client_data : str, bins_variable : str, class_to_filter : str = None) -> tuple[np.ndarray, np.ndarray]:
    dataset_client = pd.read_csv(path_client_data)
    data_hist = dataset_client[bins_variable].to_numpy()
    labels_per_sample = dataset_client['Diagnosis'].to_numpy()
    if class_to_filter is not None :
        idx_to_keep = labels_per_sample == class_to_filter
        data_hist = data_hist[idx_to_keep]
        labels_per_sample = labels_per_sample[idx_to_keep]
    return data_hist, labels_per_sample
