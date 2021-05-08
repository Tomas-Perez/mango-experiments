import matplotlib.pyplot as plt
import json
from utils import files_in_dir
import statistics

exp_dir = 'experiments'

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
y_alloc = [statistics.mean(es) for es in resource_allocations]
y_dealloc = [statistics.mean(es) for es in resource_deallocations]
alloc_box_data = [r for es in resource_allocations for r in es]
dealloc_box_data = [r for es in resource_deallocations for r in es]
  
# plt.plot(x, y_duration)
# plt.show()

# plt.plot(x, y_alloc)
# plt.show()

# plt.plot(x, y_dealloc)
# plt.show()

plt.boxplot(resource_allocations)
plt.show()

plt.boxplot(resource_deallocations)
plt.show()