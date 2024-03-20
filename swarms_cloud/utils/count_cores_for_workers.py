import multiprocessing


def calculate_workers() -> int:
    """
    Calculates the number of workers based on the number of CPU cores.

    Returns:
        int: The number of workers.
    """
    cores = multiprocessing.cpu_count()
    workers = 2 * cores + 1

    return workers
