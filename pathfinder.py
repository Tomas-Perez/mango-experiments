from benchmark import run_with_config

dims = [
    {'size': 1<<8, 'iterations': 10},
    {'size': 1<<9, 'iterations': 50},
    {'size': 1<<10, 'iterations': 30},
    {'size': 1<<11, 'iterations': 20},
    {'size': 1<<12, 'iterations': 20},
    {'size': 1<<13, 'iterations': 10},
    {'size': 1<<14, 'iterations': 10},
]

path = "/opt/mango/usr/bin/cuda_pathfinder"
dest_dir = 'pathfinder-experiments'

run_configs = []

for d in dims:
    s = d['size']
    pyramid_size = 20
    run_configs.append({'params': f"{s} {s} {pyramid_size}", 'iterations': d['iterations']})

run_with_config(path, run_configs, dest_dir)