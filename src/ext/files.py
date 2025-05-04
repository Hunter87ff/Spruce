


"""
File Operation Utilities for Spruce
This module provides file handling utilities for the Spruce application,
particularly focused on exporting and managing data files.
Functions:
    export_to_csv: Exports data to a CSV file in the 'exports' directory.
Note:
    All functions in this module follow an async pattern and provide
    error handling through callback functions.
"""

import os
from typing import Callable


def export_to_csv(data:str, filename:str, onError:Callable[[str, int, tuple[str]], None]) -> tuple[str, Callable[[], None]]:
    """
    Exports data as a CSV file to the 'exports' directory.
    This function creates an 'exports' directory if it doesn't exist,
    then writes the given data to a CSV file with the specified filename.
    Args:
        data (str): The content to write to the CSV file.
        filename (str): The name of the file without the extension.
        onError (Callable[[str, int, tuple[str]], None]): A function to call when an error occurs,
                                                    takes module name, line number, and error details.
    Returns:
        str: The path to the created CSV file if successful, None otherwise.

        callback: A callback function to call when the file operation is complete. Takes a boolean indicating success or failure.

    Raises:
        Exception: Any exception during file operation will be caught and passed to the onError callback.
    """
    _filepath = f"exports/{filename}.csv"

    try:
        if not os.path.exists("exports"):
            os.makedirs("exports")

        def cleanUp() -> None:
            """Clean up the created file after use."""
            os.remove(_filepath)

        with open(_filepath, "w") as f:
            f.write(data)

        return _filepath, cleanUp
    
    except Exception as e:
        # module, loc, error
        onError("ext.files.export_to_csv", 5, (str(e)))
        return None
