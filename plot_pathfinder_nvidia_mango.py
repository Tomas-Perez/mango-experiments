import matplotlib.pyplot as plt
import json
from utils import files_in_dir
import statistics
from plot_results import plot_results

exp_nvidia_dir = 'pathfinder/nvidia'
exp_mango_dir = 'pathfinder/mango'
exp_opencl_dir = 'pathfinder/opencl'

def to_int(a_str):
    return int(a_str)

def get_data(exp_dir, mango=False):
    total_durations = []
    buffer_reads = []
    buffer_writes = []
    kernel_execs = []
    exp_sizes = []
    if mango:
        buffer_reads_hhal = []
        buffer_writes_hhal = []
        kernel_execs_hhal = []
    for idx, exp in enumerate(sorted(files_in_dir(exp_dir, include_folders=True), key=to_int)):
        total_durations.append([])
        kernel_execs.append([])
        buffer_writes.append([])
        buffer_reads.append([])
        exp_sizes.append(int(exp))
        for run in files_in_dir(f'{exp_dir}/{exp}'):
            with open(f'{exp_dir}/{exp}/{run}', 'r') as f:
                run_data = json.load(f)
                if not 'operation_level_profiling' in run_data['params'] or run_data['params']['operation_level_profiling'] == '0':
                    total_durations[idx].append(run_data['total_duration'])
                if not 'operation_level_profiling' in run_data['params'] or run_data['params']['operation_level_profiling'] == '1':
                    kernel_execs[idx].append(list(map(lambda x: x['duration'], run_data['kernel_executions'])))
                    buffer_reads[idx].append(list(map(lambda x: {'size': x['size'], 'duration': x['duration']}, run_data['buffer_reads'])))
                    buffer_writes[idx].append(list(map(lambda x: {'size': x['size'], 'duration': x['duration']}, run_data['buffer_writes'])))
        if mango:
            kernel_execs_hhal.append([])
            buffer_reads_hhal.append([])
            buffer_writes_hhal.append([])
            for run in files_in_dir(f'{exp_dir}/{exp}/hhal'):
                with open(f'{exp_dir}/{exp}/hhal/{run}', 'r') as f:
                    run_data = json.load(f)
                    kernel_execs_hhal[idx].append(list(map(lambda x: x['duration'], run_data['kernel_executions'])))
                    buffer_reads_hhal[idx].append(list(map(lambda x: {'size': x['size'], 'duration': x['duration']}, run_data['buffer_reads'])))
                    buffer_writes_hhal[idx].append(list(map(lambda x: {'size': x['size'], 'duration': x['duration']}, run_data['buffer_writes'])))
                
    if mango:
        return exp_sizes, total_durations, buffer_reads, buffer_writes, kernel_execs, buffer_reads_hhal, buffer_writes_hhal, kernel_execs_hhal
    else:
        return exp_sizes, total_durations, buffer_reads, buffer_writes, kernel_execs
    
plot_results(exp_nvidia_dir, exp_mango_dir, exp_opencl_dir, get_data, 'pathfinder', buffer_write_unit='megabytes')