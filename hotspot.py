from benchmark import run_with_config

dims = [
    {'size': 64, 'iterations': 10},
    {'size': 128, 'iterations': 50},
    {'size': 256, 'iterations': 30},
    {'size': 512, 'iterations': 30},
    {'size': 1024, 'iterations': 20},
    {'size': 2048, 'iterations': 20},
    {'size': 4096, 'iterations': 10},
    {'size': 8192, 'iterations': 10},
]

path = "/opt/mango/usr/bin/cuda_hotspot"

run_configs = []
for d in dims:
    s = d['size']
    pyramid_height = 8
    total_iterations = 1 << 7
    tfile = f"/opt/mango/usr/local/share/cuda_hotspot/data/temp_{s}.bin"
    pfile = f"/opt/mango/usr/local/share/cuda_hotspot/data/power_{s}.bin"
    cmd = f"{s} {pyramid_height} {total_iterations} {tfile} {pfile}"
    run_configs.append({'params': cmd, 'iterations': d['iterations']})

run_with_config(path, run_configs, 'hotspot-experiments')