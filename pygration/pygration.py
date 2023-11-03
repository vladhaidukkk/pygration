import time
import pathlib
import tomllib


# TODO: functions should be independent from config or other global things!
def create(name):
    with open("pygration.toml", "rb") as config:
        data = tomllib.load(config)
        filename = pathlib.Path(data["dir"], f"{round(time.time())}_{name}.sql")
        with open(filename, "w") as file:
            file.write("-- UP\n\n\n-- DOWN\n\n")
