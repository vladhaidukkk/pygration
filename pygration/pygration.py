from time import time
from pathlib import Path
from math import floor


def create(name, *, directory):
    file = Path(directory, f"{floor(time())}_{name}.sql")
    with open(file, "w") as file_obj:
        file_obj.write("-- UP\n\n\n-- DOWN\n\n")
