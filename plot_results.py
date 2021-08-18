import statistics
import matplotlib.pyplot as plt
import tikzplotlib as tikz
import os

def remove_outliers(data):
    stdev = statistics.stdev(data)
    mean = statistics.mean(data)

    res = []
    for d in data:
        if d < mean + stdev * 3 and d > mean - stdev * 3:
            res.append(d)
    return res

def group_buffer_operations_by_size(buffer_ops):
    grouped = {}
    for op in buffer_ops:
        if not op['size'] in grouped:
            grouped[op['size']] = []
        grouped[op['size']].append(op['duration'])
    return grouped
                
def flatten_list(lst):
    return [e for sublist in lst for e in sublist]
    
def group_operations_by_input(idx, total_durations, kernel_execs, buffer_writes, buffer_reads, resource_allocations=None):
    if resource_allocations:
        return (total_durations[idx], kernel_execs[idx], buffer_writes[idx], buffer_reads[idx], resource_allocations[idx])
    else:
        return (total_durations[idx], kernel_execs[idx], buffer_writes[idx], buffer_reads[idx])

def operation_means(ops, mango=False):
    if mango:
        total_durations, k_execs, buffer_writes, buffer_reads, resource_allocs = ops
    else:
        total_durations, k_execs, buffer_writes, buffer_reads = ops
    buffer_writes = [list(map(lambda x: x['duration'], lst)) for lst in buffer_writes]
    buffer_reads = [list(map(lambda x: x['duration'], lst)) for lst in buffer_reads]

    total_k_execs = [sum(lst) for lst in k_execs]
    total_buffer_writes = [sum(lst) for lst in buffer_writes]
    total_buffer_reads = [sum(lst) for lst in buffer_reads]
    if mango:
        total_resource_allocs = [sum(lst) for lst in resource_allocs]
        return (
            statistics.mean(total_durations), 
            statistics.mean(total_k_execs), 
            statistics.mean(total_buffer_writes), 
            statistics.mean(total_buffer_reads),
            statistics.mean(total_resource_allocs),
        )
    else:
        return (statistics.mean(total_durations), statistics.mean(total_k_execs), statistics.mean(total_buffer_writes), statistics.mean(total_buffer_reads))

def with_extra_duration(base, ops):
    if len(base) == 5:
        return (ops[0] - sum(ops[1:]), base[1], base[2], base[3], base[4])
    else:
        return (ops[0] - sum(ops[1:]), base[1], base[2], base[3])

def compute_hhal_total_durations(mango_total_durations, ops_mango, ops_hhal):
    buffer_reads_mango, buffer_writes_mango, kernel_execs_mango = ops_mango
    buffer_reads_hhal, buffer_writes_hhal, kernel_execs_hhal = ops_hhal
    
    hhal_total_durations = []
    for idx in range(len(mango_total_durations)):
        hhal_total_durations.append([])
        curr_total_durations = mango_total_durations[idx]
        curr_kernel_execs_mango = kernel_execs_mango[idx]
        curr_kernel_execs_hhal = kernel_execs_hhal[idx]
        curr_buffer_writes_mango = [list(map(lambda x: x['duration'], lst)) for lst in buffer_writes_mango[idx]]
        curr_buffer_reads_mango = [list(map(lambda x: x['duration'], lst)) for lst in buffer_reads_mango[idx]]
        curr_buffer_writes_hhal = [list(map(lambda x: x['duration'], lst)) for lst in buffer_writes_hhal[idx]]
        curr_buffer_reads_hhal = [list(map(lambda x: x['duration'], lst)) for lst in buffer_reads_hhal[idx]]
        for exp_idx in range(len(curr_total_durations)):
            hhal_total_durations[idx].append(
                curr_total_durations[exp_idx] -
                    (sum(curr_buffer_writes_mango[exp_idx]) + sum(curr_buffer_reads_mango[exp_idx]) + sum(curr_kernel_execs_mango[exp_idx])) +
                    (sum(curr_buffer_writes_hhal[exp_idx]) + sum(curr_buffer_reads_hhal[exp_idx]) + sum(curr_kernel_execs_hhal[exp_idx]))
            )
    return hhal_total_durations


def plot_results(exp_nvidia_dir, exp_mango_dir, exp_opencl_dir, get_data, exp_name, buffer_write_unit='kilobytes', buffer_read_unit='kilobytes', kernel_executions_time_unit='ms', buffer_writes_time_unit='ms', buffer_reads_time_unit='ms'):
    dest_dir = f'figures/{exp_name}'
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    exp_sizes, total_durations, buffer_reads_by_input_size, buffer_writes_by_input_size, kernel_execs_by_input_size = get_data(exp_nvidia_dir)
    exp_sizes_mango, total_durations_mango, buffer_reads_mango_by_input_size, buffer_writes_mango_by_input_size, kernel_execs_mango_by_input_size, resource_allocations_mango, buffer_reads_hhal_by_input_size, buffer_writes_hhal_by_input_size, kernel_execs_hhal_by_input_size = get_data(exp_mango_dir, mango=True)
    exp_sizes_opencl, total_durations_opencl, buffer_reads_opencl_by_input_size, buffer_writes_opencl_by_input_size, kernel_execs_opencl_by_input_size = get_data(exp_opencl_dir)

    total_durations_hhal = compute_hhal_total_durations(total_durations_mango, 
        (buffer_reads_mango_by_input_size, buffer_writes_mango_by_input_size, kernel_execs_mango_by_input_size),
        (buffer_reads_hhal_by_input_size, buffer_writes_hhal_by_input_size, kernel_execs_hhal_by_input_size),
    )

    kernel_execs = [flatten_list(lst) for lst in kernel_execs_by_input_size]
    kernel_execs_mango = [flatten_list(lst) for lst in kernel_execs_mango_by_input_size]
    kernel_execs_opencl = [flatten_list(lst) for lst in kernel_execs_opencl_by_input_size]
    kernel_execs_hhal = [flatten_list(lst) for lst in kernel_execs_hhal_by_input_size]

    buffer_reads, buffer_writes = flatten_list(flatten_list(buffer_reads_by_input_size)), flatten_list(flatten_list(buffer_writes_by_input_size))
    buffer_reads_mango, buffer_writes_mango = flatten_list(flatten_list(buffer_reads_mango_by_input_size)), flatten_list(flatten_list(buffer_writes_mango_by_input_size))
    buffer_reads_opencl, buffer_writes_opencl = flatten_list(flatten_list(buffer_reads_opencl_by_input_size)), flatten_list(flatten_list(buffer_writes_opencl_by_input_size))
    buffer_reads_hhal, buffer_writes_hhal = flatten_list(flatten_list(buffer_reads_hhal_by_input_size)), flatten_list(flatten_list(buffer_writes_hhal_by_input_size))

    nvidia_ops_biggest = group_operations_by_input(len(exp_sizes)-1, total_durations, kernel_execs_by_input_size, buffer_writes_by_input_size, buffer_reads_by_input_size)
    mango_ops_biggest = group_operations_by_input(len(exp_sizes)-1, total_durations_mango, kernel_execs_mango_by_input_size, buffer_writes_mango_by_input_size, buffer_reads_mango_by_input_size, resource_allocations_mango)
    hhal_ops_biggest = group_operations_by_input(len(exp_sizes)-1, total_durations_mango, kernel_execs_hhal_by_input_size, buffer_writes_hhal_by_input_size, buffer_reads_hhal_by_input_size, resource_allocations_mango)
    opencl_ops_biggest = group_operations_by_input(len(exp_sizes)-1, total_durations_opencl, kernel_execs_opencl_by_input_size, buffer_writes_opencl_by_input_size, buffer_reads_opencl_by_input_size)

    nvidia_ops_means = operation_means(nvidia_ops_biggest)
    nvidia_ops_means = with_extra_duration(nvidia_ops_means, nvidia_ops_means)
    mango_ops_means_og = operation_means(mango_ops_biggest, mango=True)
    mango_ops_means = with_extra_duration(mango_ops_means_og, mango_ops_means_og)
    hhal_ops_means = operation_means(hhal_ops_biggest, mango=True)
    hhal_ops_means = with_extra_duration(hhal_ops_means, mango_ops_means_og)
    opencl_ops_means = operation_means(opencl_ops_biggest)
    opencl_ops_means = with_extra_duration(opencl_ops_means, opencl_ops_means)

    to_ms = lambda duration: duration / 1_000_000
    to_us = lambda duration: duration / 1_000

    rescale_time_total_duration = to_ms
    rescale_time_bars = to_ms

    if kernel_executions_time_unit == 'ms':
        rescale_time_kernel_executions = to_ms
    elif kernel_executions_time_unit == 'μs':
        rescale_time_kernel_executions = to_us
    else:
        raise RuntimeError("Unknown kernel execs time unit")

    if buffer_writes_time_unit == 'ms':
        rescale_time_buffer_writes = to_ms
    elif buffer_writes_time_unit == 'μs':
        rescale_time_buffer_writes = to_us
    else:
        raise RuntimeError("Unknown buffer writes time unit")

    if buffer_reads_time_unit == 'ms':
        rescale_time_buffer_reads = to_ms
    elif buffer_reads_time_unit == 'μs':
        rescale_time_buffer_reads = to_us
    else:
        raise RuntimeError("Unknown buffer reads time unit")
    
    x = exp_sizes

    y_duration = list(map(rescale_time_total_duration, [statistics.mean(remove_outliers(es)) for es in total_durations]))
    y_duration_mango = list(map(rescale_time_total_duration, [statistics.mean(remove_outliers(es)) for es in total_durations_mango]))
    y_duration_hhal = list(map(rescale_time_total_duration, [statistics.mean(remove_outliers(es)) for es in total_durations_hhal]))
    y_duration_opencl = list(map(rescale_time_total_duration, [statistics.mean(remove_outliers(es)) for es in total_durations_opencl]))
    y_duration_min = list(map(rescale_time_total_duration, [min(es) for es in total_durations]))
    y_duration_mango_min = list(map(rescale_time_total_duration, [min(es) for es in total_durations_mango]))
    y_duration_hhal_min = list(map(rescale_time_total_duration, [min(es) for es in total_durations_hhal]))
    y_duration_opencl_min = list(map(rescale_time_total_duration, [min(es) for es in total_durations_opencl]))
    y_kernel_execs = list(map(rescale_time_kernel_executions, [statistics.mean(remove_outliers(es)) for es in kernel_execs]))
    y_kernel_execs_mango = list(map(rescale_time_kernel_executions, [statistics.mean(remove_outliers(es)) for es in kernel_execs_mango]))
    y_kernel_execs_hhal = list(map(rescale_time_kernel_executions, [statistics.mean(remove_outliers(es)) for es in kernel_execs_hhal]))
    y_kernel_execs_opencl = list(map(rescale_time_kernel_executions, [statistics.mean(remove_outliers(es)) for es in kernel_execs_opencl]))
    y_kernel_execs_min = list(map(rescale_time_kernel_executions, [min(es) for es in kernel_execs]))
    y_kernel_execs_mango_min = list(map(rescale_time_kernel_executions, [min(es) for es in kernel_execs_mango]))
    y_kernel_execs_hhal_min = list(map(rescale_time_kernel_executions, [min(es) for es in kernel_execs_hhal]))
    y_kernel_execs_opencl_min = list(map(rescale_time_kernel_executions, [min(es) for es in kernel_execs_opencl]))

    nvidia_label = 'NVIDIA'
    opencl_label = 'OPENCL'
    mango_label = 'MANGO (+IPC)'
    hhal_label = 'MANGO'

    fig, ax = plt.subplots()
    plt.title("Total duration (mean)")
    ax.margins(0.05)
    ax.plot(x, y_duration_mango, marker='^', color='blue', label=mango_label)
    ax.plot(x, y_duration_hhal, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel("Total duration (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/total_duration_mean_ipc.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Total duration (min)")
    ax.margins(0.05)
    ax.plot(x, y_duration_mango_min, marker='^', color='blue', label=mango_label)
    ax.plot(x, y_duration_hhal_min, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel("Total duration (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/total_duration_min_ipc.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Total duration (mean)")
    ax.margins(0.05)
    ax.plot(x, y_duration, marker='o', color='green', label=nvidia_label)
    ax.plot(x, y_duration_opencl, marker='x', color='red', label=opencl_label)
    ax.plot(x, y_duration_hhal, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel("Total duration (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/total_duration_mean.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Total duration (min)")
    ax.margins(0.05)
    ax.plot(x, y_duration_min, marker='o', color='green', label=nvidia_label)
    ax.plot(x, y_duration_opencl_min, marker='x', color='red', label=opencl_label)
    ax.plot(x, y_duration_hhal_min, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel("Total duration (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/total_duration_min.tex')
    plt.show()


    fig, ax = plt.subplots()
    plt.title("Kernel executions (mean)")
    ax.margins(0.05)
    ax.plot(x, y_kernel_execs, marker='o', color='green', label=nvidia_label)
    ax.plot(x, y_kernel_execs_opencl, marker='x', color='red', label=opencl_label)
    ax.plot(x, y_kernel_execs_hhal, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Kernel execution time ({kernel_executions_time_unit})")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/kernel_executions_mean.tex')
    plt.show()


    fig, ax = plt.subplots()
    plt.title("Kernel executions (min)")
    ax.margins(0.05)
    ax.plot(x, y_kernel_execs_min, marker='o', color='green', label=nvidia_label)
    ax.plot(x, y_kernel_execs_opencl_min, marker='x', color='red', label=opencl_label)
    ax.plot(x, y_kernel_execs_hhal_min, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Kernel execution time ({kernel_executions_time_unit})")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/kernel_executions_min.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Kernel executions (mean)")
    ax.margins(0.05)
    ax.plot(x, y_kernel_execs_mango, marker='^', color='blue', label=mango_label)
    ax.plot(x, y_kernel_execs_hhal, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Kernel execution time ({kernel_executions_time_unit})")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/kernel_executions_mean_ipc.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Kernel executions (min)")
    ax.margins(0.05)
    ax.plot(x, y_kernel_execs_mango_min, marker='^', color='blue', label=mango_label)
    ax.plot(x, y_kernel_execs_hhal_min, marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Kernel execution time ({kernel_executions_time_unit})")
    ax.set_xlabel("Input size (grid_size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/kernel_executions_min_ipc.tex')
    plt.show()

    grouped_writes = sorted(group_buffer_operations_by_size(buffer_writes).items(), key=lambda t: t[0])
    grouped_writes_mango = sorted(group_buffer_operations_by_size(buffer_writes_mango).items(), key=lambda t: t[0])
    grouped_writes_hhal = sorted(group_buffer_operations_by_size(buffer_writes_hhal).items(), key=lambda t: t[0])
    grouped_writes_opencl = sorted(group_buffer_operations_by_size(buffer_writes_opencl).items(), key=lambda t: t[0])

    writes = [(s, rescale_time_buffer_writes(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes]
    writes_mango = [(s, rescale_time_buffer_writes(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes_mango]
    writes_hhal = [(s, rescale_time_buffer_writes(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes_hhal]
    writes_opencl = [(s, rescale_time_buffer_writes(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes_opencl]
    writes_min = [(s, rescale_time_buffer_writes(min(es))) for s, es in grouped_writes]
    writes_mango_min = [(s, rescale_time_buffer_writes(min(es))) for s, es in grouped_writes_mango]
    writes_hhal_min = [(s, rescale_time_buffer_writes(min(es))) for s, es in grouped_writes_hhal]
    writes_opencl_min = [(s, rescale_time_buffer_writes(min(es))) for s, es in grouped_writes_opencl]

    if buffer_write_unit == 'kilobytes':
        div_unit = 1024
    elif buffer_write_unit == 'megabytes':
        div_unit = 1024 * 1024
    else:
        raise RuntimeError("Unknown buffer read unit")

    fig, ax = plt.subplots()
    plt.title("Buffer writes (mean)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes)), list(map(lambda x: x[1], writes)), marker='o', color='green', label=nvidia_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_opencl)), list(map(lambda x: x[1], writes_opencl)), marker='x', color='red', label=opencl_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_hhal)), list(map(lambda x: x[1], writes_hhal)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer write time ({buffer_writes_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_write_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_writes_mean.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer writes (min)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_min)), list(map(lambda x: x[1], writes_min)), marker='o', color='green', label=nvidia_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_opencl_min)), list(map(lambda x: x[1], writes_opencl_min)), marker='x', color='red', label=opencl_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_hhal_min)), list(map(lambda x: x[1], writes_hhal_min)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer write time ({buffer_writes_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_write_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_writes_min.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer writes (mean)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_mango)), list(map(lambda x: x[1], writes_mango)), marker='^', color='blue', label=mango_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_hhal)), list(map(lambda x: x[1], writes_hhal)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer write time ({buffer_writes_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_write_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_writes_mean_ipc.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer writes (min)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_mango_min)), list(map(lambda x: x[1], writes_mango_min)), marker='^', color='blue', label=mango_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_hhal_min)), list(map(lambda x: x[1], writes_hhal_min)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer write time ({buffer_writes_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_write_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_writes_min_ipc.tex')
    plt.show()

    grouped_reads = sorted(group_buffer_operations_by_size(buffer_reads).items(), key=lambda t: t[0])
    grouped_reads_mango = sorted(group_buffer_operations_by_size(buffer_reads_mango).items(), key=lambda t: t[0])
    grouped_reads_hhal = sorted(group_buffer_operations_by_size(buffer_reads_hhal).items(), key=lambda t: t[0])
    grouped_reads_opencl = sorted(group_buffer_operations_by_size(buffer_reads_opencl).items(), key=lambda t: t[0])

    reads = [(s, rescale_time_buffer_reads(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads]
    reads_mango = [(s, rescale_time_buffer_reads(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads_mango]
    reads_hhal = [(s, rescale_time_buffer_reads(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads_hhal]
    reads_opencl = [(s, rescale_time_buffer_reads(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads_opencl]

    reads_min = [(s, rescale_time_buffer_reads(min(es))) for s, es in grouped_reads]
    reads_mango_min = [(s, rescale_time_buffer_reads(min(es))) for s, es in grouped_reads_mango]
    reads_hhal_min = [(s, rescale_time_buffer_reads(min(es))) for s, es in grouped_reads_hhal]
    reads_opencl_min = [(s, rescale_time_buffer_reads(min(es))) for s, es in grouped_reads_opencl]

    if buffer_read_unit == 'kilobytes':
        div_unit = 1024
    elif buffer_read_unit == 'megabytes':
        div_unit = 1024 * 1024
    else:
        raise RuntimeError("Unknown buffer read unit")

    fig, ax = plt.subplots()
    plt.title("Buffer reads (mean)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads)), list(map(lambda x: x[1], reads)), marker='o', color='green', label=nvidia_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_opencl)), list(map(lambda x: x[1], reads_opencl)), marker='x', color='red', label=opencl_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_hhal)), list(map(lambda x: x[1], reads_hhal)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer read time ({buffer_reads_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_read_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_reads_mean.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer reads (min)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_min)), list(map(lambda x: x[1], reads_min)), marker='o', color='green', label=nvidia_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_opencl_min)), list(map(lambda x: x[1], reads_opencl_min)), marker='x', color='red', label=opencl_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_hhal_min)), list(map(lambda x: x[1], reads_hhal_min)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer read time ({buffer_reads_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_read_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_reads_min.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer reads (mean)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_mango)), list(map(lambda x: x[1], reads_mango)), marker='^', color='blue', label=mango_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_hhal)), list(map(lambda x: x[1], reads_hhal)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer read time ({buffer_reads_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_read_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_reads_mean_ipc.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer reads (min)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_mango_min)), list(map(lambda x: x[1], reads_mango_min)), marker='^', color='blue', label=mango_label)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_hhal_min)), list(map(lambda x: x[1], reads_hhal_min)), marker='v', color='orange', label=hhal_label)
    ax.set_ylabel(f"Buffer read time ({buffer_reads_time_unit})")
    ax.set_xlabel(f"Buffer size ({buffer_read_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_reads_min_ipc.tex')
    plt.show()

    labels = [nvidia_label, opencl_label, hhal_label]
    extra_duration_means = list(map(rescale_time_bars, [nvidia_ops_means[0], opencl_ops_means[0], hhal_ops_means[0]]))
    kernel_execution_means = list(map(rescale_time_bars, [nvidia_ops_means[1], opencl_ops_means[1], hhal_ops_means[1]]))
    buffer_write_means = list(map(rescale_time_bars, [nvidia_ops_means[2], opencl_ops_means[2], hhal_ops_means[2]]))
    buffer_read_means = list(map(rescale_time_bars, [nvidia_ops_means[3], opencl_ops_means[3], hhal_ops_means[3]]))
    resource_allocation_means = list(map(rescale_time_bars, [0, 0, hhal_ops_means[4]]))

    width = 0.35

    fig, ax = plt.subplots()

    ax.bar(labels, buffer_read_means, width, bottom=[kernel_execution_means[i] + buffer_write_means[i] + extra_duration_means[i] + resource_allocation_means[i] for i in range(len(kernel_execution_means))], label='Buffer reads')
    ax.bar(labels, buffer_write_means, width, bottom=[kernel_execution_means[i] + extra_duration_means[i] + resource_allocation_means[i] for i in range(len(kernel_execution_means))], label='Buffer writes')
    ax.bar(labels, kernel_execution_means, width, bottom=[extra_duration_means[i] + resource_allocation_means[i] for i in range(len(kernel_execution_means))], label='Kernel executions')
    ax.bar(labels, resource_allocation_means, width, bottom=[extra_duration_means[i] for i in range(len(kernel_execution_means))], label='Resource allocation')
    ax.bar(labels, extra_duration_means, width, label='Miscellaneous')
    
    ax.set_ylabel('Time (ms)')
    ax.set_title('Benchmark breakdown')
    ax.yaxis.grid(True)
    # Shrink current axis by 30%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.70, box.height])
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    tikz.save(f'{dest_dir}/breakdown.tex')

    plt.show()