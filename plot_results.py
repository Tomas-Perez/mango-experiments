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

def group_operations_by_input(idx, kernel_execs, buffer_writes, buffer_reads):
    return (kernel_execs[idx], buffer_writes[idx], buffer_reads[idx])

def operation_means(ops):
    k_execs, buffer_writes, buffer_reads = ops
    buffer_writes = [list(map(lambda x: x['duration'], lst)) for lst in buffer_writes]
    buffer_reads = [list(map(lambda x: x['duration'], lst)) for lst in buffer_reads]

    total_k_execs = [sum(lst) for lst in k_execs]
    total_buffer_writes = [sum(lst) for lst in buffer_writes]
    total_buffer_reads = [sum(lst) for lst in buffer_reads]
    return (statistics.mean(total_k_execs), statistics.mean(total_buffer_writes), statistics.mean(total_buffer_reads))

def plot_results(exp_nvidia_dir, exp_mango_dir, exp_opencl_dir, get_data, exp_name, buffer_write_unit='kilobytes', buffer_read_unit='kilobytes'):
    dest_dir = f'figures/{exp_name}'
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    
    exp_sizes, total_durations, buffer_reads_by_input_size, buffer_writes_by_input_size, kernel_execs_by_input_size = get_data(exp_nvidia_dir)
    exp_sizes_mango, total_durations_mango, buffer_reads_mango_by_input_size, buffer_writes_mango_by_input_size, kernel_execs_mango_by_input_size, buffer_reads_hhal_by_input_size, buffer_writes_hhal_by_input_size, kernel_execs_hhal_by_input_size = get_data(exp_mango_dir, mango=True)
    exp_sizes_opencl, total_durations_opencl, buffer_reads_opencl_by_input_size, buffer_writes_opencl_by_input_size, kernel_execs_opencl_by_input_size = get_data(exp_opencl_dir)

    kernel_execs = [flatten_list(lst) for lst in kernel_execs_by_input_size]
    kernel_execs_mango = [flatten_list(lst) for lst in kernel_execs_mango_by_input_size]
    kernel_execs_opencl = [flatten_list(lst) for lst in kernel_execs_opencl_by_input_size]
    kernel_execs_hhal = [flatten_list(lst) for lst in kernel_execs_hhal_by_input_size]

    buffer_reads, buffer_writes = flatten_list(flatten_list(buffer_reads_by_input_size)), flatten_list(flatten_list(buffer_writes_by_input_size))
    buffer_reads_mango, buffer_writes_mango = flatten_list(flatten_list(buffer_reads_mango_by_input_size)), flatten_list(flatten_list(buffer_writes_mango_by_input_size))
    buffer_reads_opencl, buffer_writes_opencl = flatten_list(flatten_list(buffer_reads_opencl_by_input_size)), flatten_list(flatten_list(buffer_writes_opencl_by_input_size))
    buffer_reads_hhal, buffer_writes_hhal = flatten_list(flatten_list(buffer_reads_hhal_by_input_size)), flatten_list(flatten_list(buffer_writes_hhal_by_input_size))

    nvidia_ops_biggest = group_operations_by_input(len(exp_sizes)-1, kernel_execs_by_input_size, buffer_writes_by_input_size, buffer_reads_by_input_size)
    mango_ops_biggest = group_operations_by_input(len(exp_sizes)-1, kernel_execs_mango_by_input_size, buffer_writes_mango_by_input_size, buffer_reads_mango_by_input_size)
    hhal_ops_biggest = group_operations_by_input(len(exp_sizes)-1, kernel_execs_hhal_by_input_size, buffer_writes_hhal_by_input_size, buffer_reads_hhal_by_input_size)
    opencl_ops_biggest = group_operations_by_input(len(exp_sizes)-1, kernel_execs_opencl_by_input_size, buffer_writes_opencl_by_input_size, buffer_reads_opencl_by_input_size)

    nvidia_ops_means = operation_means(nvidia_ops_biggest)
    mango_ops_means = operation_means(mango_ops_biggest)
    hhal_ops_means = operation_means(hhal_ops_biggest)
    opencl_ops_means = operation_means(opencl_ops_biggest)

    to_ms = lambda duration: duration / 1_000_000

    x = exp_sizes

    y_duration = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in total_durations]))
    y_duration_mango = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in total_durations_mango]))
    y_duration_opencl = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in total_durations_opencl]))
    y_duration_min = list(map(to_ms, [min(es) for es in total_durations]))
    y_duration_mango_min = list(map(to_ms, [min(es) for es in total_durations_mango]))
    y_duration_opencl_min = list(map(to_ms, [min(es) for es in total_durations_opencl]))
    y_kernel_execs = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in kernel_execs]))
    y_kernel_execs_mango = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in kernel_execs_mango]))
    y_kernel_execs_hhal = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in kernel_execs_hhal]))
    y_kernel_execs_opencl = list(map(to_ms, [statistics.mean(remove_outliers(es)) for es in kernel_execs_opencl]))
    y_kernel_execs_min = list(map(to_ms, [min(es) for es in kernel_execs]))
    y_kernel_execs_mango_min = list(map(to_ms, [min(es) for es in kernel_execs_mango]))
    y_kernel_execs_hhal_min = list(map(to_ms, [min(es) for es in kernel_execs_hhal]))
    y_kernel_execs_opencl_min = list(map(to_ms, [min(es) for es in kernel_execs_opencl]))


    fig, ax = plt.subplots()
    plt.title("Total duration (mean)")
    ax.margins(0.05)
    ax.plot(x, y_duration, marker='o', color='green', label='nvidia')
    ax.plot(x, y_duration_opencl, marker='x', color='red', label='opencl')
    ax.plot(x, y_duration_mango, marker='^', color='orange', label='mango')
    ax.set_ylabel("Total duration (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/total_duration_mean.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Total duration (min)")
    ax.margins(0.05)
    ax.plot(x, y_duration_min, marker='o', color='green', label='nvidia')
    ax.plot(x, y_duration_opencl_min, marker='x', color='red', label='opencl')
    ax.plot(x, y_duration_mango_min, marker='^', color='orange', label='mango')
    ax.set_ylabel("Total duration (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/total_duration_min.tex')
    plt.show()


    fig, ax = plt.subplots()
    plt.title("Kernel executions (mean)")
    ax.margins(0.05)
    ax.plot(x, y_kernel_execs, marker='o', color='green', label='nvidia')
    ax.plot(x, y_kernel_execs_opencl, marker='x', color='red', label='opencl')
    ax.plot(x, y_kernel_execs_mango, marker='^', color='orange', label='mango')
    ax.plot(x, y_kernel_execs_hhal, marker='v', color='blue', label='mango (no IPC)')
    ax.set_ylabel("Kernel execution time (ms)")
    ax.set_xlabel("Input size (grid size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/kernel_executions_mean.tex')
    plt.show()


    fig, ax = plt.subplots()
    plt.title("Kernel executions (min)")
    ax.margins(0.05)
    ax.plot(x, y_kernel_execs_min, marker='o', color='green', label='nvidia')
    ax.plot(x, y_kernel_execs_opencl_min, marker='x', color='red', label='opencl')
    ax.plot(x, y_kernel_execs_mango_min, marker='^', color='orange', label='mango')
    ax.plot(x, y_kernel_execs_hhal_min, marker='v', color='blue', label='mango (no IPC)')
    ax.set_ylabel("Kernel execution time (ms)")
    ax.set_xlabel("Input size (grid_size)")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/kernel_executions_min.tex')
    plt.show()

    grouped_writes = sorted(group_buffer_operations_by_size(buffer_writes).items(), key=lambda t: t[0])
    grouped_writes_mango = sorted(group_buffer_operations_by_size(buffer_writes_mango).items(), key=lambda t: t[0])
    grouped_writes_hhal = sorted(group_buffer_operations_by_size(buffer_writes_hhal).items(), key=lambda t: t[0])
    grouped_writes_opencl = sorted(group_buffer_operations_by_size(buffer_writes_opencl).items(), key=lambda t: t[0])

    writes = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes]
    writes_mango = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes_mango]
    writes_hhal = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes_hhal]
    writes_opencl = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_writes_opencl]
    writes_min = [(s, to_ms(min(es))) for s, es in grouped_writes]
    writes_mango_min = [(s, to_ms(min(es))) for s, es in grouped_writes_mango]
    writes_hhal_min = [(s, to_ms(min(es))) for s, es in grouped_writes_hhal]
    writes_opencl_min = [(s, to_ms(min(es))) for s, es in grouped_writes_opencl]

    if buffer_write_unit == 'kilobytes':
        div_unit = 1024
    elif buffer_write_unit == 'megabytes':
        div_unit = 1024 * 1024
    else:
        raise RuntimeError("Unknown buffer read unit")

    fig, ax = plt.subplots()
    plt.title("Buffer writes (mean)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes)), list(map(lambda x: x[1], writes)), marker='o', color='green', label='nvidia')
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_opencl)), list(map(lambda x: x[1], writes_opencl)), marker='x', color='red', label='opencl')
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_mango)), list(map(lambda x: x[1], writes_mango)), marker='^', color='orange', label='mango')
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_hhal)), list(map(lambda x: x[1], writes_hhal)), marker='v', color='blue', label='mango (no IPC)')
    ax.set_ylabel("Buffer write time (ms)")
    ax.set_xlabel(f"Buffer size ({buffer_write_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_writes_mean.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer writes (min)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_min)), list(map(lambda x: x[1], writes_min)), marker='o', color='green', label='nvidia')
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_opencl_min)), list(map(lambda x: x[1], writes_opencl_min)), marker='x', color='red', label='opencl')
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_mango_min)), list(map(lambda x: x[1], writes_mango_min)), marker='^', color='orange', label='mango')
    ax.plot(list(map(lambda x: x[0] / div_unit, writes_hhal_min)), list(map(lambda x: x[1], writes_hhal_min)), marker='v', color='blue', label='mango (no IPC)')
    ax.set_ylabel("Buffer write time (ms)")
    ax.set_xlabel(f"Buffer size ({buffer_write_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_writes_min.tex')
    plt.show()

    grouped_reads = sorted(group_buffer_operations_by_size(buffer_reads).items(), key=lambda t: t[0])
    grouped_reads_mango = sorted(group_buffer_operations_by_size(buffer_reads_mango).items(), key=lambda t: t[0])
    grouped_reads_hhal = sorted(group_buffer_operations_by_size(buffer_reads_hhal).items(), key=lambda t: t[0])
    grouped_reads_opencl = sorted(group_buffer_operations_by_size(buffer_reads_opencl).items(), key=lambda t: t[0])

    reads = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads]
    reads_mango = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads_mango]
    reads_hhal = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads_hhal]
    reads_opencl = [(s, to_ms(statistics.mean(remove_outliers(es)))) for s, es in grouped_reads_opencl]

    reads_min = [(s, to_ms(min(es))) for s, es in grouped_reads]
    reads_mango_min = [(s, to_ms(min(es))) for s, es in grouped_reads_mango]
    reads_hhal_min = [(s, to_ms(min(es))) for s, es in grouped_reads_hhal]
    reads_opencl_min = [(s, to_ms(min(es))) for s, es in grouped_reads_opencl]

    if buffer_read_unit == 'kilobytes':
        div_unit = 1024
    elif buffer_read_unit == 'megabytes':
        div_unit = 1024 * 1024
    else:
        raise RuntimeError("Unknown buffer read unit")

    fig, ax = plt.subplots()
    plt.title("Buffer reads (mean)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads)), list(map(lambda x: x[1], reads)), marker='o', color='green', label='nvidia')
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_opencl)), list(map(lambda x: x[1], reads_opencl)), marker='x', color='red', label='opencl')
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_mango)), list(map(lambda x: x[1], reads_mango)), marker='^', color='orange', label='mango')
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_hhal)), list(map(lambda x: x[1], reads_hhal)), marker='v', color='blue', label='mango (no IPC)')
    ax.set_ylabel("Buffer read time (ms)")
    ax.set_xlabel(f"Buffer size ({buffer_read_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_reads_mean.tex')
    plt.show()

    fig, ax = plt.subplots()
    plt.title("Buffer reads (min)")
    ax.margins(0.05)
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_min)), list(map(lambda x: x[1], reads_min)), marker='o', color='green', label='nvidia')
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_opencl_min)), list(map(lambda x: x[1], reads_opencl_min)), marker='x', color='red', label='opencl')
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_mango_min)), list(map(lambda x: x[1], reads_mango_min)), marker='^', color='orange', label='mango')
    ax.plot(list(map(lambda x: x[0] / div_unit, reads_hhal_min)), list(map(lambda x: x[1], reads_hhal_min)), marker='v', color='blue', label='mango (no IPC)')
    ax.set_ylabel("Buffer read time (ms)")
    ax.set_xlabel(f"Buffer size ({buffer_read_unit})")
    ax.yaxis.grid(True)
    ax.legend()
    tikz.save(f'{dest_dir}/buffer_reads_min.tex')
    plt.show()

    labels = ['NVIDIA', 'OPENCL', 'MANGO', 'MANGO (No IPC)']
    kernel_execution_means = list(map(to_ms, [nvidia_ops_means[0], opencl_ops_means[0], mango_ops_means[0], hhal_ops_means[0]]))
    buffer_write_means = list(map(to_ms, [nvidia_ops_means[1], opencl_ops_means[1], mango_ops_means[1], hhal_ops_means[1]]))
    buffer_read_means = list(map(to_ms, [nvidia_ops_means[2], opencl_ops_means[2], mango_ops_means[2], hhal_ops_means[2]]))

    width = 0.35       # the width of the bars: can also be len(x) sequence

    fig, ax = plt.subplots()

    ax.bar(labels, kernel_execution_means, width, label='Kernel Executions')
    ax.bar(labels, buffer_write_means, width, bottom=kernel_execution_means, label='Buffer writes')
    ax.bar(labels, buffer_read_means, width, bottom=[kernel_execution_means[i] + buffer_write_means[i] for i in range(len(kernel_execution_means))], label='Buffer reads')
    ax.set_ylabel('Time (ms)')
    ax.set_title('Benchmark breakdown')
    ax.yaxis.grid(True)
    ax.legend()

    plt.show()