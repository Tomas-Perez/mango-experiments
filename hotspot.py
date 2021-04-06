import os
from time import sleep

class CommandFailed(Exception): pass

data_files = [f for f in os.listdir('/opt/mango/usr/local/share/cuda_hotspot/data') if ".bin" in f] 
sizes = set()
for f in data_files:
    sizes.add(int((f.split("_")[1])[:-4]))

sorted_sizes = sorted(sizes)

path = "/opt/mango/usr/bin/cuda_hotspot"

count = 0

try:
    for s in sorted_sizes:
        for t_ord in range(5, 8):
            for pyramid_height in [2, 4, 8]:
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
except CommandFailed:
    print("Command Failed")

print(f"Ran {count} commands")