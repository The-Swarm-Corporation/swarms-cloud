import torch
import threading
from queue import Queue, Empty
from typing import Optional, Callable


class ModelThreadWorker:
    """
    Represents a worker thread that processes tasks using a model.

    Args:
        worker_id (int): The ID of the worker.
        gpu_id (int): The ID of the GPU to be used by the worker.
        queue (Queue): The queue from which the worker retrieves tasks.
        model (Optional[Callable]): The model function to be used for processing tasks.

    Attributes:
        worker_id (int): The ID of the worker.
        gpu_id (int): The ID of the GPU used by the worker.
        queue (Queue): The queue from which the worker retrieves tasks.
        lock (threading.Lock): A lock used for thread synchronization.
        model (Callable): The model function used for processing tasks.
        thread (threading.Thread): The thread object representing the worker.
        device (str): The device string specifying the GPU used by the worker.

    """

    def __init__(
        self,
        worker_id: int,
        gpu_id: int,
        queue: Queue,
        model: Optional[Callable] = None,
        *args,
        **kwargs,
    ):
        self.worker_id = worker_id
        self.gpu_id = gpu_id
        self.queue = queue
        self.model = model
        self.lock = threading.Lock()
        self.model = None
        self.thread = threading.Thread(target=self.run, daemon=True)
        self.device = f"cuda:{gpu_id}" if torch.cuda.is_available() else "cpu"
        self.thread.start()

        # Availability
        self.available = threading.Event()
        self.available.set()

        # Task que
        self.task_queue = Queue()

        # Response queue
        self.response_queue = Queue()

    def run(self, *args, **kwargs):
        """
        The main method that runs in the worker thread.

        This method continuously retrieves tasks from the queue, processes them using the model,
        and puts the results into the response queue.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        while True:
            try:
                self.available.clear()
                task = self.queue.get()
                if task is None:
                    break
                task, response_queue = task
                print(f"Worker {self.worker_id} on GPU {self.gpu_id} processing {task}")
                result = self.model(task, *args, **kwargs)
                response_queue.put(result)
                self.queue.task_done()
                self.available.set()
            except Empty:
                continue


class Router:
    """
    A class that routes tasks to worker threads for parallel processing.

    Args:
        num_workers_per_gpu (int): The number of worker threads per GPU.
        model (Optional[Callable]): An optional callable representing the model.

    Attributes:
        queues (List[Queue]): A list of queues for each worker thread.
        workers (List[ModelThreadWorker]): A list of worker threads.
        num_gpus (int): The number of available GPUs.

    Methods:
        route_task: Routes a task to a worker thread.
        shutdown: Shuts down all worker threads.

    """

    def __init__(
        self,
        num_workers_per_gpu: int = None,
        model: Optional[Callable] = None,
        *args,
        **kwargs,
    ):
        self.num_workers = num_workers_per_gpu
        self.model = model
        self.queues = []
        self.workers = []
        self.num_gpus = torch.device_count()

        for gpu_id in range(self.num_gpus):
            for worker_id in range(num_workers_per_gpu):
                queue = Queue()
                worker = ModelThreadWorker(
                    f"{gpu_id}-{worker_id}",
                    gpu_id,
                    queue,
                    model=self.model,
                    *args,
                    **kwargs,
                )
                self.queues.append(queue)
                self.workers.append(worker)

    def route_task(self, task: str, *args, **kwargs):
        """
        Routes a task to a worker thread.

        Args:
            task (str): The task to be executed.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        """
        for worker in self.workers:
            if worker.available_is_set():
                worker.task_queue.put(task)
                return True

        # If no worker is available return False or queue the task differently
        return False

    def shutdown(self):
        """
        Shuts down all worker threads.

        """
        for worker in self.workers:
            worker.task_queue.put(None)
