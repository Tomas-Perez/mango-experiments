import os
from time import sleep
from utils import files_in_dir

class CommandFailed(Exception): pass

data_files = [f for f in os.listdir('/opt/mango/usr/local/share/cuda_hotspot/data') if ".bin" in f] 
sizes = set()
for f in data_files:
    sizes.add(int((f.split("_")[1])[:-4]))

sorted_sizes = sorted(sizes)

path = "/opt/mango/usr/bin/cuda_hotspot"

count = 0

exp_dir = 'experiments'
if not os.path.exists(exp_dir):
    os.makedirs(exp_dir)

try:
    for s in sorted_sizes:
        t_ord = 7
        pyramid_height = 8
        config_str = f"{s}"
        config_dir = f"{exp_dir}/{config_str}"
        if os.path.exists(config_dir):
            print(f"Config {config_str} already done, skipping...")
            continue
        print(f"Running 10 iterations for {config_str}")
        os.makedirs(config_dir)
        for _ in range(10):
            total_iterations = 1 << t_ord
            tfile = f"/opt/mango/usr/local/share/cuda_hotspot/data/temp_{s}.bin"
            pfile = f"/opt/mango/usr/local/share/cuda_hotspot/data/power_{s}.bin"
            cmd = f"{path} {s} {pyramid_height} {total_iterations} {tfile} {pfile}"
            print(f"Running {cmd}...")
            count += 1
            res = os.system(cmd)
            sleep(1)
            if (res != 0):
                raise CommandFailed
        print(f"Ran all 10 iterations for {config_str}")
        for f in files_in_dir('.'):
            if '.json' in f:
                os.rename(f, f"{config_dir}/{f}")
                
except CommandFailed:
    print("Command Failed")

print(f"Ran {count} commands")