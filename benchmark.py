import os
from time import sleep
from utils import files_in_dir

class CommandFailed(Exception): pass

def run_with_config(exec_path, configs, dest_dir, mango=False):
    count = 0
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    try:
        for c in configs:
            config_str = c['params']
            save_as_str = c['save_as']
            iterations = c['iterations']
            pyramid_height = 20
            config_dir = f"{dest_dir}/{save_as_str}"
            if os.path.exists(config_dir):
                print(f"Config {config_str} already done, skipping...")
                continue
            print(f"Running {iterations} iterations for {config_str}")
            i = 0
            while i < c['iterations']:
                cmd = f"{exec_path} {config_str}"
                print(f"Running {cmd}...")
                count += 1
                res = os.system(cmd)
                if mango:
                    sleep(1)
                if (res == 0):
                    i += 1
            print(f"Ran all {iterations} iterations for {config_str}")
            os.makedirs(config_dir)
            for f in files_in_dir('.'):
                if '.json' in f:
                    os.rename(f, f"{config_dir}/{f}")
            if mango:
                os.makedirs(f"{config_dir}/hhal")
                for f in files_in_dir('hhal_profiling'):
                    if '.json' in f:
                        os.rename(f"hhal_profiling/{f}", f"{config_dir}/hhal/{f}")
                    
    except CommandFailed:
        print("Command Failed")

    print(f"Ran {count} commands")