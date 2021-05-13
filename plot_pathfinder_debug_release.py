import matplotlib.pyplot as plt
import json
from utils import files_in_dir
import statistics

exp_release_dir = 'pathfinder-experiments'
exp_debug_dir = 'bbque-debug/pathfinder-experiments'

def to_int(a_str):
    return int(a_str)

def get_data(exp_dir):
    total_durations = []
    resource_allocations = []
    resource_deallocations = []
    exp_sizes = []
    for idx, exp in enumerate(sorted(files_in_dir(exp_dir, include_folders=True), key=to_int)):
        total_durations.append([])
        resource_allocations.append([])
        resource_deallocations.append([])
        exp_sizes.append(int(exp))
        for run in files_in_dir(f'{exp_dir}/{exp}'):
            with open(f'{exp_dir}/{exp}/{run}', 'r') as f:
                run_data = json.load(f)
                total_durations[idx].append(run_data['total_duration'])
                resource_allocations[idx].append(run_data['resource_allocations'][0]['duration'])
                resource_deallocations[idx].append(run_data['resource_deallocations'][0]['duration'])
    return exp_sizes, total_durations, resource_allocations, resource_deallocations
    
def remove_outliers(data):
    stdev = statistics.stdev(data)
    mean = statistics.mean(data)

    res = []
    for d in data:
        if d < mean + stdev * 3 and d > mean - stdev * 3:
            res.append(d)
    return res

exp_sizes, total_durations, resource_allocations, resource_deallocations = get_data(exp_release_dir)
exp_sizes_dbg, total_durations_dbg, resource_allocations_dbg, resource_deallocations_dbg = get_data(exp_debug_dir)

x = exp_sizes

y_duration = [statistics.mean(remove_outliers(es)) for es in total_durations]
y_duration_dbg = [statistics.mean(remove_outliers(es)) for es in total_durations_dbg]
y_alloc = [statistics.mean(remove_outliers(es)) for es in resource_allocations]
y_alloc_dbg = [statistics.mean(remove_outliers(es)) for es in resource_allocations_dbg]
y_dealloc = [statistics.mean(remove_outliers(es)) for es in resource_deallocations]
y_dealloc_dbg = [statistics.mean(remove_outliers(es)) for es in resource_deallocations_dbg]
  
fig, ax = plt.subplots()
ax.margins(0.05)
ax.plot(x, y_duration, marker='o', linestyle='', label='release')
ax.plot(x, y_duration_dbg, marker='o', linestyle='', label='debug')
ax.legend()

plt.show()

fig, ax = plt.subplots()
ax.margins(0.05)
ax.plot(x, y_alloc, marker='o', linestyle='', label='release')
ax.plot(x, y_alloc_dbg, marker='o', linestyle='', label='debug')
ax.legend()

plt.show()

fig, ax = plt.subplots()
ax.margins(0.05)
ax.plot(x, y_dealloc, marker='o', linestyle='', label='release')
ax.plot(x, y_dealloc_dbg, marker='o', linestyle='', label='debug')
ax.legend()

plt.show()