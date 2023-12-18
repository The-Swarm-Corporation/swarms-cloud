import sky


class SkyInterface:
    """

    SkyInterface is a wrapper around the sky Python API. It provides a
    simplified interface for launching, executing, stopping, starting, and
    tearing down clusters.

    Attributes:
        clusters (dict): A dictionary of clusters that have been launched.
        The keys are the names of the clusters and the values are the handles
        to the clusters.

    Methods:
        launch: Launch a cluster
        execute: Execute a task on a cluster
        stop: Stop a cluster
        start: Start a cluster
        down: Tear down a cluster
        status: Get the status of a cluster
        autostop: Set the autostop of a cluster

    Example:
        >>> sky_interface = SkyInterface()
        >>> job_id = sky_interface.launch("task", "cluster_name")
        >>> sky_interface.execute("task", "cluster_name")
        >>> sky_interface.stop("cluster_name")
        >>> sky_interface.start("cluster_name")
        >>> sky_interface.down("cluster_name")
        >>> sky_interface.status()
        >>> sky_interface.autostop("cluster_name")


    """

    def __init__(self):
        self.clusters = {}

    def launch(self, task, cluster_name=None, **kwargs):
        """Launch a task on a cluster

        Args:
            task (str): code to execute on the cluster
            cluster_name (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        try:
            job_id, handle = sky.launch(task, cluster_name=cluster_name, **kwargs)
            if handle:
                self.clusters[cluster_name] = handle
            return job_id
        except Exception as error:
            print("Error launching cluster:", error)

    def execute(self, task, cluster_name, **kwargs):
        """Execute a task on a cluster

        Args:
            task (_type_): _description_
            cluster_name (_type_): _description_

        Raises:
            ValueError: _description_

        Returns:
            _type_: _description_
        """
        if cluster_name not in self.clusters:
            raise ValueError("Cluster {} does not exist".format(cluster_name))
        try:
            return sky.exec(task, cluster_name, **kwargs)
        except Exception as e:
            print("Error executing on cluster:", e)

    def stop(self, cluster_name, **kwargs):
        """Stop a cluster

        Args:
            cluster_name (str): name of the cluster to stop
        """
        try:
            sky.stop(cluster_name, **kwargs)
        except (ValueError, RuntimeError) as e:
            print("Error stopping cluster:", e)

    def start(self, cluster_name, **kwargs):
        """start a cluster

        Args:
            cluster_name (str): name of the cluster to start
        """
        try:
            sky.start(cluster_name, **kwargs)
        except Exception as e:
            print("Error starting cluster:", e)

    def down(self, cluster_name, **kwargs):
        """Down a cluster

        Args:
            cluster_name (str): name of the cluster to tear down
        """
        try:
            sky.down(cluster_name, **kwargs)
            if cluster_name in self.clusters:
                del self.clusters[cluster_name]
        except (ValueError, RuntimeError) as e:
            print("Error tearing down cluster:", e)

    def status(self, **kwargs):
        """Save a cluster

        Returns:
            r: the status of the cluster
        """
        try:
            return sky.status(**kwargs)
        except Exception as e:
            print("Error getting status:", e)

    def autostop(self, cluster_name, **kwargs):
        """Autostop a cluster

        Args:
            cluster_name (str): name of the cluster to autostop
        """
        try:
            sky.autostop(cluster_name, **kwargs)
        except Exception as e:
            print("Error setting autostop:", e)
