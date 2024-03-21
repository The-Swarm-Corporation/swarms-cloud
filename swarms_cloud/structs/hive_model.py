import torch
import torch.multiprocessing as mp
import queue







def model_worker(model_class, gpu_id, input_queue, output_queue):
    """
    Worker process to handle model inference.
    Loads the model onto the specified GPU and waits for inputs from the input_queue.
    Processes inputs and puts results into the output_queue.
    """
    device = torch.device(f'cuda:{gpu_id}')
    model = model_class().to(device)
    model.eval()

    with torch.no_grad():
        while True:
            try:
                data = input_queue.get(timeout=3)  # Adjust timeout as needed
                if data is None:
                    break  # None is sent as a signal to stop the worker
                data = data.to(device)
                output = model(data)
                output_queue.put(output.cpu())
            except queue.Empty:
                continue

def setup_model_on_gpus(model_class, num_models_per_gpu=1):
    """
    Sets up model instances across available GPUs, dividing the GPU memory to determine
    the number of models that can fit based on a simple heuristic.
    """
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is not available. This function requires a CUDA-enabled environment.")

    mp.set_start_method('spawn', force=True)
    num_gpus = torch.cuda.device_count()

    workers = []
    input_queues = []
    output_queue = mp.Queue()

    for gpu_id in range(num_gpus):
        for _ in range(num_models_per_gpu):
            input_q = mp.Queue()
            p = mp.Process(target=model_worker, args=(model_class, gpu_id, input_q, output_queue))
            p.start()
            workers.append(p)
            input_queues.append(input_q)

    return workers, input_queues, output_queue

def distribute_inference(workers, input_queues, output_queue, inputs):
    """
    Distributes inputs for inference across the available model instances,
    implementing a simple round-robin scheduling.
    """
    # Round-robin distribution of inputs
    for i, input_tensor in enumerate(inputs):
        q = input_queues[i % len(input_queues)]
        q.put(input_tensor)

    # Collecting results
    results = []
    for _ in range(len(inputs)):
        results.append(output_queue.get())

    # Sending stop signal to workers
    for q in input_queues:
        q.put(None)

    for p in workers:
        p.join()

    return results

# Example usage:
# Define your model class here, e.g., `MyModelClass`.
# workers, input_queues, output_queue = setup_model_on_gpus(MyModelClass, num_models_per_gpu=2)
# inputs = [torch.randn(1, 3, 224, 224) for _ in range(10)]  # Example input tensors
# results = distribute_inference(workers, input_queues, output_queue, inputs)
