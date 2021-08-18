import matplotlib.pyplot as plt
import numpy as np
import json
from utils import files_in_dir
import statistics
from plot_results import plot_results
import tikzplotlib as tikz
import os

exp_nvidia_dir = 'axpy/nvidia'
exp_mango_dir = 'axpy/mango'
exp_opencl_dir = 'axpy/opencl'

def to_int(a_str):
    return int(a_str)

to_ms = lambda duration: duration / 1_000_000

def get_data(exp_dir, mango=False):
    total_durations = []
    buffer_reads = []
    buffer_writes = []
    kernel_execs = []
    if mango:
        buffer_reads_hhal = []
        buffer_writes_hhal = []
        kernel_execs_hhal = []
    for run in files_in_dir(exp_dir):
        with open(f'{exp_dir}/{run}', 'r') as f:
            run_data = json.load(f)
            if not 'operation_level_profiling' in run_data['params'] or run_data['params']['operation_level_profiling'] == '0':
                total_durations.append(run_data['total_duration'])
            if not 'operation_level_profiling' in run_data['params'] or run_data['params']['operation_level_profiling'] == '1':
                kernel_execs.append(list(map(lambda x: x['duration'], run_data['kernel_executions'])))
                buffer_reads.append(list(map(lambda x: x['duration'], run_data['buffer_reads'])))
                buffer_writes.append(list(map(lambda x: x['duration'], run_data['buffer_writes'])))
    if mango:
        for run in files_in_dir(f'{exp_dir}/hhal'):
            with open(f'{exp_dir}/hhal/{run}', 'r') as f:
                run_data = json.load(f)
                kernel_execs_hhal.append(list(map(lambda x: x['duration'], run_data['kernel_executions'])))
                buffer_reads_hhal.append(list(map(lambda x: x['duration'], run_data['buffer_reads'])))
                buffer_writes_hhal.append(list(map(lambda x: x['duration'], run_data['buffer_writes'])))
                
    if mango:
        return total_durations, buffer_reads, buffer_writes, kernel_execs, buffer_reads_hhal, buffer_writes_hhal, kernel_execs_hhal
    else:
        return total_durations, buffer_reads, buffer_writes, kernel_execs
    
def flatten_list(lst):
    return [e for sublist in lst for e in sublist]

total_durations, buffer_reads_by_input_size, buffer_writes_by_input_size, kernel_execs_by_input_size = get_data(exp_nvidia_dir)
total_durations_mango, buffer_reads_mango_by_input_size, buffer_writes_mango_by_input_size, kernel_execs_mango_by_input_size, buffer_reads_hhal_by_input_size, buffer_writes_hhal_by_input_size, kernel_execs_hhal_by_input_size = get_data(exp_mango_dir, mango=True)
total_durations_opencl, buffer_reads_opencl_by_input_size, buffer_writes_opencl_by_input_size, kernel_execs_opencl_by_input_size = get_data(exp_opencl_dir)

buffer_reads, buffer_writes, kernel_execs = flatten_list(buffer_reads_by_input_size), flatten_list(buffer_writes_by_input_size), flatten_list(kernel_execs_by_input_size)
buffer_reads_mango, buffer_writes_mango, kernel_execs_mango = flatten_list(buffer_reads_mango_by_input_size), flatten_list(buffer_writes_mango_by_input_size), flatten_list(kernel_execs_mango_by_input_size)
buffer_reads_opencl, buffer_writes_opencl, kernel_execs_opencl = flatten_list(buffer_reads_opencl_by_input_size), flatten_list(buffer_writes_opencl_by_input_size), flatten_list(kernel_execs_opencl_by_input_size)
buffer_reads_hhal, buffer_writes_hhal, kernel_execs_hhal = flatten_list(buffer_reads_hhal_by_input_size), flatten_list(buffer_writes_hhal_by_input_size), flatten_list(kernel_execs_hhal_by_input_size)

def operation_means(ops):
    k_execs, buffer_writes, buffer_reads = ops

    total_k_execs = [sum(lst) for lst in k_execs]
    total_buffer_writes = [sum(lst) for lst in buffer_writes]
    total_buffer_reads = [sum(lst) for lst in buffer_reads]
    return (statistics.mean(total_k_execs), statistics.mean(total_buffer_writes), statistics.mean(total_buffer_reads))

n = 20971520
size_of_double = 8
amount_of_references = 3
bytes_accessed = n * size_of_double * amount_of_references
bytes_transferred = n * size_of_double

max_theoretical_bandwidth = 112.128
max_theoretical_transfer_speed = 15.754

kernel_execs_ms = list(map(to_ms, kernel_execs))
kernel_execs_mango_ms = list(map(to_ms, kernel_execs_mango))
kernel_execs_hhal_ms = list(map(to_ms, kernel_execs_hhal))
kernel_execs_opencl_ms = list(map(to_ms, kernel_execs_opencl))

buffer_reads_ms = list(map(to_ms, buffer_reads))
buffer_reads_mango_ms = list(map(to_ms, buffer_reads_mango))
buffer_reads_hhal_ms = list(map(to_ms, buffer_reads_hhal))
buffer_reads_opencl_ms = list(map(to_ms, buffer_reads_opencl))

transfer_speed_reads = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_reads))
transfer_speed_reads_mango = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_reads_mango))
transfer_speed_reads_hhal = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_reads_hhal))
transfer_speed_reads_opencl = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_reads_opencl))

buffer_writes_ms = list(map(to_ms, buffer_writes))
buffer_writes_mango_ms = list(map(to_ms, buffer_writes_mango))
buffer_writes_hhal_ms = list(map(to_ms, buffer_writes_hhal))
buffer_writes_opencl_ms = list(map(to_ms, buffer_writes_opencl))

transfer_speed_writes = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_writes))
transfer_speed_writes_mango = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_writes_mango))
transfer_speed_writes_hhal = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_writes_hhal))
transfer_speed_writes_opencl = list(map(lambda duration: (bytes_transferred / duration) / max_theoretical_transfer_speed, buffer_writes_opencl))

bandwidths = list(map(lambda duration: (bytes_accessed / duration) / max_theoretical_bandwidth, kernel_execs))
bandwidths_mango = list(map(lambda duration: (bytes_accessed / duration) / max_theoretical_bandwidth, kernel_execs_mango))
bandwidths_hhal = list(map(lambda duration: (bytes_accessed / duration) / max_theoretical_bandwidth, kernel_execs_hhal))
bandwidths_opencl = list(map(lambda duration: (bytes_accessed / duration) / max_theoretical_bandwidth, kernel_execs_opencl))

dest_dir = f'figures/axpy'
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

def bars(title, y_label, save_name, nvidia_vals, mango_vals, hhal_vals, opencl_vals):
    nvidia_mean = np.mean(nvidia_vals)
    mango_mean = np.mean(mango_vals)
    hhal_mean = np.mean(hhal_vals)
    opencl_mean = np.mean(opencl_vals)

    nvidia_std = np.std(nvidia_vals)
    mango_std = np.std(mango_vals)
    hhal_std = np.std(hhal_vals)
    opencl_std = np.std(opencl_vals)

    models = ['NVIDIA', 'OPENCL', 'MANGO']
    x_pos = np.arange(len(models))

    means = [nvidia_mean, opencl_mean, hhal_mean]
    error = [nvidia_std, opencl_std, hhal_std]

    fig, ax = plt.subplots()
    ax.yaxis.grid(True)
    rects = ax.bar(x_pos, means, align='center', alpha=0.5, ecolor='black', color=['green', 'red', 'orange'], capsize=10)
    heights = list(map(lambda rect: rect.get_height(), rects))
    mean_height = np.mean(heights)
    max_height = 0
    for rect in rects:
        height = rect.get_height()
        text_height = height + mean_height * 0.05
        max_height = max(max_height, text_height)
        ax.text(rect.get_x() + rect.get_width()/2., text_height, '%.2f' % height, ha='center', va='bottom', clip_on=True)
    ax.set_ylabel(y_label)
    ax.set_xlabel("Programming Model")
    ax.set_xticks(x_pos)
    ax.set_xticklabels(models)
    ax.set_title(title)
        
    xmin, xmax, ymin, ymax = ax.axis()
    ax.axis([xmin, xmax, ymin, max_height * 1.1])
    tikz.save(f'{dest_dir}/{save_name}.tex')
    plt.show()

def stacked_bars(nvidia_ops_means, opencl_ops_means, mango_ops_means, hhal_ops_means):
    labels = ['NVIDIA', 'OPENCL', 'MANGO']
    kernel_execution_means = list(map(to_ms, [nvidia_ops_means[0], opencl_ops_means[0], hhal_ops_means[0]]))
    buffer_write_means = list(map(to_ms, [nvidia_ops_means[1], opencl_ops_means[1], hhal_ops_means[1]]))
    buffer_read_means = list(map(to_ms, [nvidia_ops_means[2], opencl_ops_means[2], hhal_ops_means[2]]))

    width = 0.35

    fig, ax = plt.subplots()
    
    ax.bar(labels, buffer_read_means, width, bottom=[kernel_execution_means[i] + buffer_write_means[i] for i in range(len(kernel_execution_means))], label='Buffer reads')
    ax.bar(labels, buffer_write_means, width, bottom=kernel_execution_means, label='Buffer writes')
    ax.bar(labels, kernel_execution_means, width, label='Kernel executions')
    ax.set_ylabel('Time (ms)')
    ax.set_xlabel("Programming Model")
    ax.set_title('Benchmark breakdown')
    ax.yaxis.grid(True)
    # Shrink current axis by 30%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.70, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    tikz.save(f'{dest_dir}/breakdown.tex')

    plt.show()


nvidia_ops = (kernel_execs_by_input_size, buffer_writes_by_input_size, buffer_reads_by_input_size)
mango_ops = (kernel_execs_mango_by_input_size, buffer_writes_mango_by_input_size, buffer_reads_mango_by_input_size)
opencl_ops = (kernel_execs_opencl_by_input_size, buffer_writes_opencl_by_input_size, buffer_reads_opencl_by_input_size)
hhal_ops = (kernel_execs_hhal_by_input_size, buffer_writes_hhal_by_input_size, buffer_reads_hhal_by_input_size)

stacked_bars(operation_means(nvidia_ops), operation_means(opencl_ops), operation_means(mango_ops), operation_means(hhal_ops))
bars('Kernel Executions', 'Kernel Execution time (ms)', 'kernel_executions_mean', kernel_execs_ms, kernel_execs_mango_ms, kernel_execs_hhal_ms, kernel_execs_opencl_ms)
bars('Bandwidth (mean)', '% of theoretical peak bandwidth', 'bandwidth_mean', bandwidths, bandwidths_mango, bandwidths_hhal, bandwidths_opencl)
bars('Bandwidth (max)', '% of theoretical peak bandwidth', 'bandwidth_max', [max(bandwidths)], [max(bandwidths_mango)], [max(bandwidths_hhal)], [max(bandwidths_opencl)])
bars('Buffer writes', 'Transfer time HtoD (ms)', 'transfer_time_writes_mean', buffer_writes_ms, buffer_writes_mango_ms, buffer_writes_hhal_ms, buffer_writes_opencl_ms)
bars('Buffer reads', 'Transfer time DtoH (ms)', 'transfer_time_reads_mean', buffer_reads_ms, buffer_reads_mango_ms, buffer_reads_hhal_ms, buffer_reads_opencl_ms)
bars('Transfer bandwidth HtoD (mean)', '% of theoretical peak PCI-E bandwidth', 'transfer_bandwidth_htod_mean', transfer_speed_writes, transfer_speed_writes_mango, transfer_speed_writes_hhal, transfer_speed_writes_opencl)
bars('Transfer bandwidth DtoH (mean)', '% of theoretical peak PCI-E bandwidth', 'transfer_bandwidth_dtoh_mean', transfer_speed_reads, transfer_speed_reads_mango, transfer_speed_reads_hhal, transfer_speed_reads_opencl)
bars('Transfer bandwidth HtoD (max)', '% of theoretical peak PCI-E bandwidth', 'transfer_bandwidth_htod_max', [max(transfer_speed_writes)], [max(transfer_speed_writes_mango)], [max(transfer_speed_writes_hhal)], [max(transfer_speed_writes_opencl)])
bars('Transfer bandwidth DtoH (max)', '% of theoretical peak PCI-E bandwidth', 'transfer_bandwidth_dtoh_max', [max(transfer_speed_reads)], [max(transfer_speed_reads_mango)], [max(transfer_speed_reads_hhal)], [max(transfer_speed_reads_opencl)])


