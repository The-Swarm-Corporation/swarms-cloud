import os
import torch
import torch.distributed as dist
from torch.nn.parallel import DistributedDataParallel as DDP

def setup_distributed_environment():
    """Set up the distributed environment variables with fallbacks."""
    # Default to localhost and a common port if not specified
    master_addr = os.getenv("MASTER_ADDR", "localhost")
    master_port = os.getenv("MASTER_PORT", "12355")
    
    # Ensure the MASTER_ADDR and MASTER_PORT are set for the current process
    os.environ["MASTER_ADDR"] = master_addr
    os.environ["MASTER_PORT"] = master_port
    
    print(f"Using MASTER_ADDR={master_addr} and MASTER_PORT={master_port}")

def initialize_process_group(backend='nccl'):
    """Initialize the distributed environment."""
    # Here, no need to manually set rank and world_size as they should be handled by the launch utility
    if "RANK" in os.environ and "WORLD_SIZE" in os.environ:
        dist.init_process_group(backend)
    else:
        raise RuntimeError("RANK and WORLD_SIZE environment variables need to be set.")

def prepare_model_for_ddp_inference(model):
    """Prepare and wrap the model for DDP execution in inference mode, considering bitsandbytes models."""
    model.eval()  # Ensure the model is in eval mode
    
    if torch.cuda.is_available() and torch.cuda.device_count() > 1:
        setup_distributed_environment()
        initialize_process_group()
        
        rank = dist.get_rank()
        world_size = dist.get_world_size()
        
        print(f"Rank {rank}/{world_size} - Preparing model for DDP inference")
        
        model = DDP(model, device_ids=[rank], output_device=rank, find_unused_parameters=False)
    else:
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model.to(device)
        print("Single GPU/CPU detected. Proceeding without DDP.")
    
    return model

