from dotenv import load_dotenv
from pydantic import BaseModel
from supabase import create_client, Client
import os

# Load environment variables from .env file
load_dotenv()


class SupabaseLogger:
    """
    A class for logging records to a Supabase table.

    Args:
        table_name (str): The name of the table to log records to.

    Attributes:
        supabase (Client): The Supabase client used for interacting with the Supabase service.
        table_name (str): The name of the table to log records to.

    Raises:
        ValueError: If the Supabase URL or key is not set in environment variables.

    """

    def __init__(
        self, table_name: str, supabase_url: str = None, supabase_key: str = None
    ):
        if not supabase_url:
            supabase_url = os.getenv("SUPABASE_URL")
        if not supabase_key:
            supabase_key = os.getenv("SUPABASE_KEY")
        if not supabase_url or not supabase_key:
            raise ValueError(
                "Supabase URL and key must be set in environment variables or provided as arguments."
            )
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name

    def log(self, record: BaseModel):
        """
        Logs a record to the Supabase table.

        Args:
            record (BaseModel): The record to be logged.

        Returns:
            Response: The response from the Supabase service.

        Raises:
            Exception: If there is an error while logging the record.

        """
        data = record.dict()
        response = self.supabase.table(self.table_name).insert(data).execute()
        if response.error:
            raise Exception(f"Failed to log record: {response.error}")
        return response


# # Usage
# class MyModel(BaseModel):
#     name: str
#     age: int

# logger = SupabaseLogger("my_table")

# record = MyModel(name="John Doe", age=30)
# response = logger.log(record)
