import sky
from sky.exceptions import (
    ClusterNotUpError,
    ClusterOwnerIdentityMismatchError,
    ClusterOwnerIdentitiesMismatchError,
    CommandError,
    InvalidClusterNameError,
    NoCloudAccessError,
    NotSupportedError,
    ResourcesMismatchError,
    ResourcesUnavailableError,
    CloudUserIdentityError,
)


class SkyInterface:
    """

    SkyInterface is a wrapper around the sky Python API. It provides a
    simplified interface for launching, executing, stopping, starting, and
    tearing down clusters.


    """

    def __init__(self):
        self.clusters = {}

    def launch(self, task, cluster_name=None, **kwargs):
        """Launch a task on a cluster

        Args:
            task (_type_): _description_
            cluster_name (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        try:
            job_id, handle = sky.launch(task, cluster_name=cluster_name, **kwargs)
            if handle:
                self.clusters[cluster_name] = handle
            return job_id
        except (
            ClusterOwnerIdentityMismatchError,
            InvalidClusterNameError,
            ResourcesMismatchError,
            ResourcesUnavailableError,
            CommandError,
            NoCloudAccessError,
        ) as e:
            print("Error launching task:", e)

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
        except NotSupportedError as e:
            print("Error executing on cluster:", e)

    def stop(self, cluster_name, **kwargs):
        """Stop a cluster

        Args:
            cluster_name (_type_): _description_
        """
        try:
            sky.stop(cluster_name, **kwargs)
        except (ValueError, RuntimeError, NotSupportedError) as e:
            print("Error stopping cluster:", e)

    def start(self, cluster_name, **kwargs):
        """start a cluster

        Args:
            cluster_name (_type_): _description_
        """
        try:
            sky.start(cluster_name, **kwargs)
        except (
            ValueError,
            NotSupportedError,
            ClusterOwnerIdentitiesMismatchError,
        ) as e:
            print("Error starting cluster:", e)

    def down(self, cluster_name, **kwargs):
        """Down a cluster

        Args:
            cluster_name (_type_): _description_
        """
        try:
            sky.down(cluster_name, **kwargs)
            if cluster_name in self.clusters:
                del self.clusters[cluster_name]
        except (ValueError, RuntimeError, NotSupportedError) as e:
            print("Error tearing down cluster:", e)

    def status(self, **kwargs):
        """Save a cluster

        Returns:
            _type_: _description_
        """
        try:
            return sky.status(**kwargs)
        except Exception as e:
            print("Error getting status:", e)

    def autostop(self, cluster_name, **kwargs):
        """Autostop a cluster

        Args:
            cluster_name (_type_): _description_
        """
        try:
            sky.autostop(cluster_name, **kwargs)
        except (
            ValueError,
            ClusterNotUpError,
            NotSupportedError,
            ClusterOwnerIdentityMismatchError,
            CloudUserIdentityError,
        ) as e:
            print("Error setting autostop:", e)
