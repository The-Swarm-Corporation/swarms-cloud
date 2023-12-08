import pytest
from swarms_cloud.sky_api import SkyInterface
from sky.exceptions import (
    ClusterNotUpError,
    ClusterOwnerIdentityMismatchError,
    CommandError,
    InvalidClusterNameError,
    NoCloudAccessError,
    NotSupportedError,
    ResourcesMismatchError,
    ResourcesUnavailableError,
    CloudUserIdentityError,
)


# Create a SkyInterface instance for testing
@pytest.fixture
def sky_interface():
    return SkyInterface()


# Test launching tasks
def test_launch_successful(sky_interface):
    job_id = sky_interface.launch("sample_task", cluster_name="test_cluster")
    assert isinstance(job_id, str)


def test_launch_invalid_cluster_name(sky_interface):
    with pytest.raises(InvalidClusterNameError):
        sky_interface.launch("sample_task", cluster_name="invalid-cluster")


def test_launch_owner_identity_mismatch(sky_interface):
    with pytest.raises(ClusterOwnerIdentityMismatchError):
        sky_interface.launch("sample_task", cluster_name="owner-mismatch")


# Test executing tasks
def test_execute_successful(sky_interface):
    result = sky_interface.execute("sample_task", cluster_name="test_cluster")
    assert isinstance(result, str)


def test_execute_cluster_not_exist(sky_interface):
    with pytest.raises(ValueError):
        sky_interface.execute("sample_task", cluster_name="non-existent-cluster")


def test_execute_not_supported(sky_interface):
    with pytest.raises(NotSupportedError):
        sky_interface.execute("unsupported_task", cluster_name="test_cluster")


# Test stopping clusters
def test_stop_successful(sky_interface):
    sky_interface.stop("test_cluster")
    # No assertion needed, just check for exceptions


def test_stop_value_error(sky_interface):
    with pytest.raises(ValueError):
        sky_interface.stop("non-existent-cluster")


# Test starting clusters
def test_start_successful(sky_interface):
    sky_interface.start("test_cluster")
    # No assertion needed, just check for exceptions


def test_start_not_supported(sky_interface):
    with pytest.raises(NotSupportedError):
        sky_interface.start("unsupported-cluster")


# Test tearing down clusters
def test_down_successful(sky_interface):
    sky_interface.down("test_cluster")
    # No assertion needed, just check for exceptions


def test_down_value_error(sky_interface):
    with pytest.raises(ValueError):
        sky_interface.down("non-existent-cluster")


# Test getting status
def test_status_successful(sky_interface):
    status = sky_interface.status()
    assert isinstance(status, dict)


def test_status_exception(sky_interface):
    with pytest.raises(Exception):
        sky_interface.status()


# Test autostop
def test_autostop_successful(sky_interface):
    sky_interface.autostop("test_cluster")
    # No assertion needed, just check for exceptions


def test_autostop_not_supported(sky_interface):
    with pytest.raises(NotSupportedError):
        sky_interface.autostop("unsupported-cluster")


# Additional tests for various exceptions
def test_cluster_not_up_error():
    with pytest.raises(ClusterNotUpError):
        raise ClusterNotUpError("Cluster is not up")


def test_resources_mismatch_error():
    with pytest.raises(ResourcesMismatchError):
        raise ResourcesMismatchError("Resources mismatch")


def test_command_error():
    with pytest.raises(CommandError):
        raise CommandError("Command failed")


def test_no_cloud_access_error():
    with pytest.raises(NoCloudAccessError):
        raise NoCloudAccessError("No cloud access")


def test_cluster_owner_identities_mismatch_error():
    with pytest.raises(ClusterOwnerIdentityMismatchError):
        raise ClusterOwnerIdentityMismatchError("Cluster owner identities mismatch")


def test_resources_unavailable_error():
    with pytest.raises(ResourcesUnavailableError):
        raise ResourcesUnavailableError("Resources unavailable")


def test_cloud_user_identity_error():
    with pytest.raises(CloudUserIdentityError):
        raise CloudUserIdentityError("Cloud user identity error")
