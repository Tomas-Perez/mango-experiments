from benchmark import run_with_config
import sys

executables = {
    'nvidia': {
        'path': '/opt/mango/usr/bin/axpy/cuda/axpy_cuda',
        'save_to': 'axpy/nvidia',
    },
    'opencl': {
        'path': '/opt/mango/usr/bin/axpy/opencl/axpy_opencl',
        'save_to': 'axpy/opencl',
    },
    'mango': {
        'path': '/opt/mango/usr/bin/cuda_axpy',
        'save_to': 'axpy/mango',
    },
}

if sys.argv[1] != 'mango':
    run_configs = [
        {'params': "0", 'iterations': 100, 'save_as': "0"},
        {'params': "1", 'iterations': 100, 'save_as': "1"},
    ]
else:
    run_configs = [
        {'params': "", 'iterations': 100, 'save_as': "0"},
    ]


ex = executables[sys.argv[1]]
run_with_config(ex['path'], run_configs, ex['save_to'], mango=sys.argv[1] == 'mango')