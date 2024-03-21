import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP


def setup_distributed_environment():
    """Set up the distributed environment variables."""
    master_addr = os.environ["MASTER_ADDR"] = "localhost"
    master_port = os.environ["MASTER_PORT"] = "12355"
    rank = int(os.getenv("RANK", "0"))
    world_size = int(os.getenv("WORLD_SIZE", "1"))
    # Ensure these are properly configured or dynamically set in a real-world scenario


def initialize_process_group(backend="nccl"):
    """Initialize the distributed environment."""
    dist.init_process_group(backend)


def prepare_model_for_ddp_inference(model):
    """Prepare and wrap the model for DDP execution in inference mode."""
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device).eval()  # Ensure the model is in eval mode

    if torch.cuda.is_available() and torch.cuda.device_count() > 1:
        setup_distributed_environment()
        initialize_process_group()

        rank = dist.get_rank()
        world_size = dist.get_world_size()

        print(f"Rank {rank}/{world_size} - Preparing model for DDP inference")

        model = DDP(
            model, device_ids=[rank], output_device=rank, find_unused_parameters=False
        )
    else:
        print("Single GPU/CPU detected. Proceeding without DDP.")

    return model


