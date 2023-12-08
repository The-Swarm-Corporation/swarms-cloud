import os
from typing import Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def supabase_env():
    """Supabase environment variables

    Raises:
        RuntimeError: _description_

    Returns:
        _type_: _description_
    """
    try:
        supabase_env = {
            "supabase_url": os.environ.get("SUPABASE_URL"),
            "supabase_key": os.environ.get("SUPABASE_KEY"),
        }
        return supabase_env
    except Exception as error:
        raise RuntimeError(
            f"Error loading supabase env: {error} upload .env file to root directory with SUPABASE_URL and SUPABASE_KEY"
        )


class SwarmCloudUsageLogger:
    """Swarm Cloud Usage Logger



    Args:
        supabase_url (str): _description_
        supabase_key (str): _description_
        supabase_table (str, optional): _description_. Defaults to "swarm_cloud_usage".

    Methods:
        log_usage: _description_
        check_api_key: _description_

    Example:
    >>> from swarms_cloud.supabase_handler import SwarmCloudUsageLogger
    >>> logger = SwarmCloudUsageLogger(
    ...     supabase_url="https://<your_supabase_url>.supabase.co",
    ...     supabase_key="<your_supabase_key>"
    ... )
    >>> log_in = logger.log_usage(
    ...     user_id="user123",
    ...     api_key="sk-<your_api_key>",
    ...     endpoint="/agent",
    ...     usage_type="get",
    ...     tokens_used=1
    ... )
    >>> check_api_key = logger.check_api_key(
    ...     "sk-<your_api_key>"
    ... )



    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        supabase_table: Optional[str] = "swarm_cloud_usage",
        *args,
        **kwargs,
    ):
        self.supabase_url = supabase_url
        self.supabase_key = supabase_key
        self.supabase_table = supabase_table
        self.supabase: Client = create_client(
            supabase_url, supabase_key, *args, **kwargs
        )

    def log_usage(
        self,
        user_id: str,
        api_key: str,
        usage_type: str,
        tokens_used: int,
        *args,
        **kwargs,
    ):
        """Log usage of Swarm Cloud API

        Args:
            user_id (str): _description_
            api_key (str): _description_
            endpoint (str): _description_
            usage_type (str): _description_
            tokens_used (int): _description_

        Returns:
            _type_: _description_
        """
        try:
            data = {
                "user_id": user_id,
                "api_key": api_key,
                "usage_type": usage_type,
                "tokens_used": tokens_used,
            }
            response = self.supabase.table("swarm_cloud_usage").insert(data).execute()
            return response
        except Exception as error:
            print(f"Error logging usage: {error}")
            raise RuntimeError(f"Error logging usage: {error}")

    def check_api_key(self, api_key: str = None):
        """Check if api key is valid

        Args:
            api_key (str, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_

        Example:
        >>> from swarms_cloud.supabase_handler import SwarmCloudUsageLogger
        >>> logger = SwarmCloudUsageLogger(
        ...     supabase_url="https://<your_supabase_url>.supabase.co",
        ...     supabase_key="<your_supabase_key>"
        ... )
        >>>
        """
        try:
            query = (
                self.supabas.table("swarm_cloud_usage")
                .select("*")
                .eq("api_key", api_key)
                .execute()
            )
            return len(query.data) > 0
        except Exception as error:
            raise RuntimeError(f"Error checking api key: {error}")


# Usage example
logger = SwarmCloudUsageLogger(
    supabase_url="https://<your_supabase_url>.supabase.co",
    supabase_key="<your_supabase_key>",
)

log_in = logger.log_usage(
    user_id="user123",
    api_key="sk-<your_api_key>",
    endpoint="/agent",
    usage_type="get",
    tokens_used=1,
)

check_api_key = logger.check_api_key("sk-<your_api_key>")
