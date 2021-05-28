from benchmark import run_with_config
import sys

executables = {
    'nvidia': {
        'path': '/opt/mango/usr/bin/rodinia/cuda/rodinia_hotspot_cuda',
        'save_to': 'hotspot/nvidia',
    },
    'opencl': {
        'path': '/opt/mango/usr/bin/rodinia/opencl/rodinia_hotspot_opencl',
        'save_to': 'hotspot/opencl',
    },
    'mango': {
        'path': '/opt/mango/usr/bin/cuda_hotspot',
        'save_to': 'hotspot/mango',
    },
}

dims = [
    {'size': 64, 'iterations': 100},
    {'size': 128, 'iterations': 50},
    {'size': 256, 'iterations': 30},
    {'size': 512, 'iterations': 30},
    {'size': 1024, 'iterations': 20},
    {'size': 2048, 'iterations': 20},
    {'size': 4096, 'iterations': 10},
    {'size': 8192, 'iterations': 10},
]

run_configs = []
for d in dims:
    s = d['size']
    pyramid_height = 8
    total_iterations = 1 << 7
    tfile = f"/opt/mango/usr/local/share/cuda_hotspot/data/temp_{s}.bin"
    pfile = f"/opt/mango/usr/local/share/cuda_hotspot/data/power_{s}.bin"
    cmd = f"{s} {pyramid_height} {total_iterations} {tfile} {pfile}"
    if sys.argv[1] != 'mango':
        run_configs.append({'params': f"{cmd} 0", 'iterations': d['iterations'], 'save_as': f"{s} 0"})
        run_configs.append({'params': f"{cmd} 1", 'iterations': d['iterations'], 'save_as': f"{s} 1"})
    else:
        run_configs.append({'params': f"{cmd}", 'iterations': d['iterations'], 'save_as': f"{s}"})

ex = executables[sys.argv[1]]
run_with_config(ex['path'], run_configs, ex['save_to'], mango=True)
