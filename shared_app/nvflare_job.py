"""
Copied and (slightly) modified from the script `job.py` at https://github.com/NVIDIA/NVFlare/tree/main/examples/hello-world/hello-flower

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from argparse import ArgumentParser

from nvflare.app_opt.flower.flower_job import FlowerJob

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main():
    parser = ArgumentParser()
    parser.add_argument("--job_name"      , type = str, required = True)
    parser.add_argument("--flower_app_dir", type = str, required = True)
    parser.add_argument("--export_job"    , action = "store_true")
    parser.add_argument("--export_dir"    , type = str, default = "./nvflare_job")
    parser.add_argument("--work_dir"      , type = str, default = "./nvflare_sim")
    parser.add_argument("--num_of_clients", type = int, default = 2)
    args = parser.parse_args()

    job = FlowerJob(
        name = args.job_name,
        flower_content = args.flower_app_dir,
        min_clients = args.num_of_clients,
    )

    if args.export_job:
        job.export_job(args.export_dir)
        print(f"Job exported to {args.export_dir}")
    else:
        job.simulator_run(
            workspace = args.work_dir,
            n_clients = args.num_of_clients
        )

if __name__ == "__main__":
    main()
