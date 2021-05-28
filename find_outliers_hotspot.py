import numpy as np
import statistics
import matplotlib.pyplot as plt

def find_outliers(data):
    stdev = statistics.stdev(data)
    mean = statistics.mean(data)

    res = []
    for idx, d in enumerate(data):
        if d > mean + stdev * 3 or d < mean - stdev * 3:
            res.append((idx, d))
    return res

size = 2048

# it = list(np.unique(np.float64(np.fromfile(f'hotspot-binaries/results_512.bin', dtype=np.float32))))
# print(f"512 grid 128 iteration")
# print(find_outliers(it))

def make_outliers_map(it):
    outliers_map = np.zeros(it.shape, dtype=np.bool)

    for x in range(0, it.shape[0]):
        for y in range(0, it.shape[1]):
            neighborhood = it[max(0, x - 2) : min(it.shape[0] - 1, x + 2), max(0, y - 2) : min(it.shape[1] - 1, y + 2)]
            mean = np.mean(neighborhood)
            stdev = np.std(neighborhood)
            outliers_map[x, y] = it[x, y] > mean + 3 * stdev or it[x, y] < mean - 3 * stdev

    return outliers_map
    

# it = np.fromfile(f'/opt/mango/usr/local/share/cuda_hotspot/data/temp_64.bin', dtype=np.float32)
# it = np.resize(it, (64, 64))
# outliers_map = make_outliers_map(it)

# plt.subplot(1, 2, 1)
# plt.imshow(it, cmap='hot', interpolation='none')

# plt.subplot(1, 2, 2)
# plt.imshow(outliers_map, cmap='hot', interpolation='none', vmax=1, vmin=0)

# # plt.show()

# plt.savefig(f'outliers_512_dual.png', dpi=300, bbox_inches='tight')

# it = np.fromfile(f'/opt/mango/usr/local/share/cuda_hotspot/data/temp_2048.bin', dtype=np.float32)
# it = np.resize(it, (2048, 2048))
# outliers_map = make_outliers_map(it)

# plt.subplot(1, 2, 1)
# plt.imshow(it, cmap='hot', interpolation='none')

# plt.subplot(1, 2, 2)
# plt.imshow(outliers_map, cmap='hot', interpolation='none', vmax=1, vmin=0)

# plt.show()

# plt.savefig(f'outliers_2048_dual.png', dpi=300, bbox_inches='tight')

for i in range(1, 7):
    it = np.fromfile(f'hotspot-binaries/results_{size}_{i}.bin', dtype=np.float32)
    it = np.resize(it, (size, size))
    it = it[:size-2, :size-2]
    outliers_map = make_outliers_map(it)
    
    plt.subplot(1, 2, 1)
    plt.imshow(it, cmap='hot', interpolation='none', vmax=np.amax(it), vmin=np.amin(it))

    plt.subplot(1, 2, 2)
    plt.imshow(outliers_map, cmap='hot', interpolation='none', vmax=1, vmin=0)
    plt.savefig(f'outliers_{size}_{i}_dual_3stdev.png', dpi=300, bbox_inches='tight')
    