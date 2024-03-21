import torch
import torch.distributed as dist
from torch.cuda import memory_allocated, get_device_properties


def get_world_size_rank():
    """
    Calculate the world size and rank in a distributed environment.
    """
    if not dist.is_initialized():
        # Assuming a default setup if not running in a distributed context
        world_size = 1
        rank = 0
    else:
        world_size = dist.get_world_size()
        rank = dist.get_rank()
    return world_size, rank

def get_num_gpus_available():
    """
    Return the number of GPUs available in the system.
    """
    return torch.cuda.device_count()

def calculate_available_memory(gpu_id=0):
    """
    Calculates the available memory on a specified GPU.
    """
    if not torch.cuda.is_available() or gpu_id >= get_num_gpus_available():
        raise RuntimeError("CUDA is not available or the specified GPU ID is out of bounds.")
    
    torch.cuda.set_device(gpu_id)
    total_memory = torch.cuda.get_device_properties(gpu_id).total_memory
    allocated_memory = torch.cuda.memory_allocated(gpu_id)
    cached_memory = torch.cuda.memory_reserved(gpu_id)
    available_memory = total_memory - (allocated_memory + cached_memory)
    return available_memory


def calculate_model_memory_consumption(model, gpu_id=0):
    """
    Calculates the memory consumption of a model on a specific GPU by temporarily moving it to the GPU.
    Args:
        model (torch.nn.Module): The model to calculate memory consumption for.
        gpu_id (int): GPU ID to use for the calculation.
    Returns:
        model_memory_consumption (int): Memory consumption in bytes.
    """
    original_device = next(model.parameters()).device
    model.to(f'cuda:{gpu_id}')
    torch.cuda.synchronize(gpu_id)
    
    allocated_memory_before = memory_allocated(gpu_id)
    with torch.no_grad():
        # Forward pass to ensure any additional memory allocations are accounted for
        try:
            # Assuming model has a dummy forward pass method for memory calculation
            input_size = (1, *model.input_shape)  # Example input size, adjust as needed
            dummy_input = torch.zeros(input_size).cuda(gpu_id)
            model(dummy_input)
        except AttributeError:
            pass  # Model does not have .input_shape or cannot perform a dummy forward pass
    
    torch.cuda.synchronize(gpu_id)
    allocated_memory_after = memory_allocated(gpu_id)
    model_memory_consumption = allocated_memory_after - allocated_memory_before

    # Clean up and move model back to original device
    dummy_input = dummy_input.cpu()
    model.to(original_device)
    
    return model_memory_consumption


def available_memory_after_model_load(model, gpu_id=0):
    """
    Calculates available GPU memory after loading a model onto it.
    Args:
        model (torch.nn.Module): The model to be loaded onto the GPU.
        gpu_id (int): GPU ID where the model will be loaded.
    Returns:
        available_memory_after_load (int): Available memory in bytes on the GPU after loading the model.
    """
    model_memory_consumption = calculate_model_memory_consumption(model, gpu_id)
    available_memory_before_load = calculate_available_memory(gpu_id)
    available_memory_after_load = available_memory_before_load - model_memory_consumption
    return available_memory_after_load



