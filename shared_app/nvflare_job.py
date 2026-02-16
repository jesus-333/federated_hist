"""
Copied and (slightly) modified from the script `job.py` at https://github.com/NVIDIA/NVFlare/tree/main/examples/hello-world/hello-flower

@author: Alberto Zancanaro (Jesus)
@organization: Luxembourg Centre for Systems Biomedicine (LCSB)
@contact : alberto.zancanaro@uni.lu
"""

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Imports

from argparse import ArgumentParser

from nvflare.app_opt.flower.recipe import FlowerRecipe
from nvflare.recipe import SimEnv

# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

def main():
    parser = ArgumentParser()
    parser.add_argument("--job_name"      , type = str, required = True)
    parser.add_argument("--flower_app_dir", type = str, required = True)
    parser.add_argument("--export_job"    , action = "store_true")
    parser.add_argument("--export_dir"    , type = str, default = "./nvflare_job")
    parser.add_argument("--workdir"       , type = str, default = "./nvflare_sim")
    parser.add_argument("--num_of_clients", type = int, default = 2)
    args = parser.parse_args()

    recipe = FlowerRecipe(
        name = args.job_name,
        flower_content = args.flower_app_dir,
        min_clients = args.num_of_clients,
    )

    if args.export_job:
        recipe.export(args.export_dir)
        print(f"Job exported to {args.export_dir}")
    else:
        env = SimEnv(num_clients = args.num_of_clients, workspace_root = args.workdir)
        run = recipe.execute(env)
        print("Result can be found in :", run.get_result())
        print("Job Status is:", run.get_status())
        print()


if __name__ == "__main__":
    main()
