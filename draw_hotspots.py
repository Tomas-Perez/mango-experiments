import numpy as np
import matplotlib.pyplot as plt
import math
import copy

size = 2048

power = np.fromfile(f'/opt/mango/usr/local/share/cuda_hotspot/data/power_{size}.bin', dtype=np.float32)
power = np.reshape(power, (size, size))
power = power[:size-2, :size-2]

before = np.fromfile(f'/opt/mango/usr/local/share/cuda_hotspot/data/temp_{size}.bin', dtype=np.float32)
before = np.reshape(before, (size, size))
before = before[:size-2, :size-2]
max_before = np.amax(before)
min_before = np.amin(before)

after = np.fromfile(f'hotspot-binaries/results_{size}_8.bin', dtype=np.float32)
after = np.reshape(after, (size, size))
after = after[:size-2, :size-2]
max_after = np.amax(after)
min_after = np.amin(after)


show_power = False

fig, axes = plt.subplots(nrows=1, ncols=3 if show_power else 2, figsize=(10, 10))

if show_power:
    power_ax = axes.flat[0]
    power_ax.title.set_text('Power')
    power_ax.set_axis_off()
    im_pow = power_ax.imshow(power, cmap='viridis', interpolation='none')



before_ax = axes.flat[1 if show_power else 0]
before_ax.title.set_text('Initial Temp')
before_ax.set_axis_off()
hot_cmap = copy.copy(plt.cm.get_cmap("hot"))
im_before = before_ax.imshow(before, cmap=hot_cmap, interpolation='none', vmax=max_before, vmin=min_before)
im_before.cmap.set_under('k')
im_before.cmap.set_over('k')
im_before.set_clim(min_before, max_before)

after_ax = axes.flat[2 if show_power else 1]
after_ax.title.set_text('After temp')
after_ax.set_axis_off()
hot_cmap2 = copy.copy(plt.cm.get_cmap("hot"))
im_after = after_ax.imshow(after, cmap=hot_cmap2, interpolation='none', vmax=max_before, vmin=min_before)
im_after.cmap.set_under('k')
im_after.cmap.set_over('k')
im_after.set_clim(min_before, max_before)

cbar3 = fig.colorbar(im_after, ax=axes.ravel().tolist(), shrink=0.5)
cbar2 = fig.colorbar(im_before, ax=axes.ravel().tolist(), shrink=0.5)

if show_power:
    cbar1 = fig.colorbar(im_pow, ax=axes.ravel().tolist(), shrink=0.5)


    

# notice that here we use ax param of figure.colorbar method instead of

# the cax param as the above example




plt.show()