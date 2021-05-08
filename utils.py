import os

def files_in_dir(path, include_folders=False):
    return [f for f in os.listdir(path) if include_folders or os.path.isfile(os.path.join(path, f))]