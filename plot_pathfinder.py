import matplotlib.pyplot as plt
import json
from utils import files_in_dir
import statistics

exp_dir = 'all-closed/pathfinder-experiments'

def to_int(a_str):
    return int(a_str)

total_durations = []
resource_allocations = []
resource_deallocations = []
exp_sizes = []
for idx, exp in enumerate(sorted(files_in_dir(exp_dir, include_folders=True), key=to_int)):
    print(exp)
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
    

x = exp_sizes

y_duration = [statistics.mean(es) for es in total_durations]
alloc_mean = [statistics.mean(es) for es in resource_allocations]
alloc_min = [min(es) for es in resource_allocations]
dealloc_mean = [statistics.mean(es) for es in resource_deallocations]
dealloc_min = [min(es) for es in resource_deallocations]

plt.title('Mean total duration')
plt.plot(x, y_duration, 'bo')
plt.show()

plt.title('Total duration')
plt.boxplot(total_durations, showfliers=True)
plt.show()

plt.title('Resource allocations')
plt.boxplot(resource_allocations, showfliers=False)
plt.show()



fig, ax = plt.subplots()
plt.title('Resource allocations')
ax.margins(0.05)
ax.plot(x, alloc_mean, marker='o', linestyle='', label='mean')
ax.plot(x, alloc_min, marker='o', linestyle='', label='min')
ax.legend()
plt.show()

plt.title('Resource deallocations')
plt.boxplot(resource_deallocations, showfliers=False)
plt.show()


fig, ax = plt.subplots()
plt.title('Resource deallocations')
ax.margins(0.05)
ax.plot(x, dealloc_mean, marker='o', linestyle='', label='mean')
ax.plot(x, dealloc_min, marker='o', linestyle='', label='min')
ax.legend()
plt.show()