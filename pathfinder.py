from benchmark import run_with_config
import sys

executables = {
    'nvidia': {
        'path': '/opt/mango/usr/bin/rodinia/cuda/rodinia_pathfinder_cuda',
        'save_to': 'pathfinder/nvidia',
    },
    'opencl': {
        'path': '/opt/mango/usr/bin/rodinia/opencl/rodinia_pathfinder_opencl',
        'save_to': 'pathfinder/opencl',
    },
    'mango': {
        'path': '/opt/mango/usr/bin/cuda_pathfinder',
        'save_to': 'pathfinder/mango',
    },
}

dims = [
    {'size': 1<<8, 'iterations': 100},
    {'size': 1<<9, 'iterations': 50},
    {'size': 1<<10, 'iterations': 30},
    {'size': 1<<11, 'iterations': 20},
    {'size': 1<<12, 'iterations': 20},
    {'size': 1<<13, 'iterations': 10},
    {'size': 1<<14, 'iterations': 10},
]

run_configs = []

for d in dims:
    s = d['size']
    pyramid_size = 20
    cmd = f"{s} {s} {pyramid_size}"
    if sys.argv[1] != 'mango':
        run_configs.append({'params': f"{cmd} 0", 'iterations': d['iterations'], 'save_as': f"{s} 0"})
        run_configs.append({'params': f"{cmd} 1", 'iterations': d['iterations'], 'save_as': f"{s} 1"})
    else:
        run_configs.append({'params': f"{cmd}", 'iterations': d['iterations'], 'save_as': f"{s}"})


ex = executables[sys.argv[1]]
run_with_config(ex['path'], run_configs, ex['save_to'], mango=True)
