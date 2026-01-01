


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


def export_to_csv(data:str, filename:str, on_error:Callable[[str, int, tuple[str]], None]) -> tuple[str, Callable[[], None]]:
    _filepath = f"exports/{filename}.csv"

    try:
        if not os.path.exists("exports"):
            os.makedirs("exports")

        def cleanup() -> None:
            """Clean up the created file after use."""
            os.remove(_filepath)

        with open(_filepath, "w") as f:
            f.write(data)

        return _filepath, cleanup

    except Exception as e:
        # module, loc, error
        on_error("ext.files.export_to_csv", 5, (str(e)))
        return None
