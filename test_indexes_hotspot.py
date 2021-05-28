import sys

class RangeChecker:
    def __init__(self, max_range):
        self.checked_idxs = []
        self.max_range = max_range

    def __getitem__(self, key):
        if key >= self.max_range or key < 0:
            print(f"ERROR: Index out of bounds: {key}")
        self.checked_idxs.append(key)
        return 1

    def __setitem__(self, key, value):
        if key >= self.max_range or key < 0:
            print(f"ERROR: Index out of bounds: {key}")


t_chip = 0.0005
chip_height = 0.016
chip_width = 0.016
amb_temp = 80.0

MAX_PD	= 3.0e6
PRECISION = 0.001
SPEC_HEAT_SI = 1.75e6
K_SI = 100
FACTOR_CHIP = 0.5


def print_calculate_temp_args(iteration, grid_cols, grid_rows, border_cols, border_rows, Cap, Rx, Ry, Rz, step, time_elapsed):
    print(iteration, grid_cols, grid_rows, border_cols, border_rows, Cap, Rx, Ry, Rz, step, time_elapsed)

def calculate_temp_thread(blockIdx, threadIdx, iteration, grid_cols, grid_rows, border_cols, border_rows, Cap, Rx, Ry, Rz, step, time_elapsed):
    temp_src = RangeChecker(grid_cols * grid_rows)
    temp_dst = RangeChecker(grid_cols * grid_rows)
    power = RangeChecker(grid_cols * grid_rows)
    temp_on_cuda = [[i for i in range(BLOCK_SIZE)] for _ in range(BLOCK_SIZE)] 
    power_on_cuda = [[i for i in range(BLOCK_SIZE)] for _ in range(BLOCK_SIZE)] 
    temp_t = [[i for i in range(BLOCK_SIZE)] for _ in range(BLOCK_SIZE)] 

    amb_temp = 80.0
    
    bx = blockIdx['x']
    by = blockIdx['y']

    tx=threadIdx['x']
    ty=threadIdx['y']
    
    step_div_Cap= step / Cap
    
    Rx_1 = 1 / Rx
    Ry_1 = 1 / Ry
    Rz_1 = 1 / Rz

    small_block_rows = BLOCK_SIZE-iteration*2
    small_block_cols = BLOCK_SIZE-iteration*2

    blkY = int(small_block_rows*by-border_rows)
    blkX = int(small_block_cols*bx-border_cols)
    blkYmax = blkY+BLOCK_SIZE-1
    blkXmax = blkX+BLOCK_SIZE-1

    yidx = blkY+ty
    xidx = blkX+tx

    loadYidx = yidx
    loadXidx = xidx
    index = grid_cols * loadYidx + loadXidx
    
    if loadYidx in range(0, grid_rows-1) and loadXidx in range(0, grid_cols-1):
        temp_on_cuda[ty][tx] = temp_src[index]
        power_on_cuda[ty][tx] = power[index]

    validYmin = -blkY if (blkY < 0) else 0
    validYmax = BLOCK_SIZE-1-(blkYmax-grid_rows+1) if (blkYmax > grid_rows-1) else BLOCK_SIZE-1
    validXmin = -blkX if (blkX < 0) else 0
    validXmax = BLOCK_SIZE-1-(blkXmax-grid_cols+1) if (blkXmax > grid_cols-1) else BLOCK_SIZE-1

    N = ty-1
    S = ty+1
    W = tx-1
    E = tx+1
    
    N = validYmin if (N < validYmin) else N
    S = validYmax if (S > validYmax) else S
    W = validXmin if (W < validXmin) else W
    E = validXmax if (E > validXmax) else E

    for i in range(iteration):
        computed = False
        if tx in range(i+1, BLOCK_SIZE-i-1) and \
            ty in range(i+1, BLOCK_SIZE-i-1) and \
            tx in range(validXmin, validXmax+1) and \
            ty in range(validYmin, validYmax+1): 
            computed = True
            temp_t[ty][tx] = temp_on_cuda[ty][tx] + \
                step_div_Cap * (power_on_cuda[ty][tx] + \
                (temp_on_cuda[S][tx] + temp_on_cuda[N][tx] - 2.0*temp_on_cuda[ty][tx]) * Ry_1 + \
                (temp_on_cuda[ty][E] + temp_on_cuda[ty][W] - 2.0*temp_on_cuda[ty][tx]) * Rx_1 + \
                (amb_temp - temp_on_cuda[ty][tx]) * Rz_1)
        if i == iteration-1:
            break
        if computed:
            temp_on_cuda[ty][tx] = temp_t[ty][tx]

    if computed:
        temp_dst[index] = temp_t[ty][tx]

def calculate_temp_thread(blockIdx, threadIdx, iteration, grid_cols, grid_rows, border_cols, border_rows, Cap, Rx, Ry, Rz, step, time_elapsed):
    amb_temp = 80.0
    
    bx = blockIdx['x']
    by = blockIdx['y']

    tx=threadIdx['x']
    ty=threadIdx['y']

    print("Bx", bx, "By", by, "Tx", tx, "Ty", ty)
    
    step_div_Cap= step / Cap
    
    Rx_1 = 1 / Rx
    Ry_1 = 1 / Ry
    Rz_1 = 1 / Rz

    small_block_rows = BLOCK_SIZE-iteration*2
    small_block_cols = BLOCK_SIZE-iteration*2

    blkY = int(small_block_rows*by-border_rows)
    blkX = int(small_block_cols*bx-border_cols)
    blkYmax = blkY+BLOCK_SIZE-1
    blkXmax = blkX+BLOCK_SIZE-1

    yidx = blkY+ty
    xidx = blkX+tx

    loadYidx = yidx
    loadXidx = xidx
    index = grid_cols * loadYidx + loadXidx

    validYmin = -blkY if (blkY < 0) else 0
    validYmax = BLOCK_SIZE-1-(blkYmax-grid_rows+1) if (blkYmax > grid_rows-1) else BLOCK_SIZE-1
    validXmin = -blkX if (blkX < 0) else 0
    validXmax = BLOCK_SIZE-1-(blkXmax-grid_cols+1) if (blkXmax > grid_cols-1) else BLOCK_SIZE-1

    N = ty-1
    S = ty+1
    W = tx-1
    E = tx+1
    
    N = validYmin if (N < validYmin) else N
    S = validYmax if (S > validYmax) else S
    W = validXmin if (W < validXmin) else W
    E = validXmax if (E > validXmax) else E

    print("validYmin", validYmin, "validYmax", validYmax, "validXmin", validXmin, "validXmax", validXmax)
    print("N", N, "S", S, "W", W, "E", E)
    print("loadYidx", loadYidx, "loadXidx", loadXidx)
    input()


def calculate_temp(dimBlock, dimGrid, iteration, grid_cols, grid_rows, border_cols, border_rows, Cap, Rx, Ry, Rz, step, time_elapsed):
    for blockX in range(dimGrid[0]):
        for blockY in range(dimGrid[1]): 
            for threadX in range(dimBlock[0]):
                for threadY in range(dimBlock[1]):
                    calculate_temp_thread({'x': blockX, 'y': blockY}, {'x': threadX, 'y': threadY}, iteration, grid_cols, grid_rows, border_cols, border_rows, Cap, Rx, Ry, Rz, step, time_elapsed)

def compute_tran_temp(col, row, total_iterations, num_iterations, blockCols, blockRows, borderCols, borderRows):
    dimBlock = (BLOCK_SIZE, BLOCK_SIZE)
    dimGrid = (blockCols, blockRows)

    print(dimBlock)
    print(dimGrid)

    grid_height = chip_height / row
    grid_width = chip_width / col

    Cap = FACTOR_CHIP * SPEC_HEAT_SI * t_chip * grid_width * grid_height
    Rx = grid_width / (2.0 * K_SI * t_chip * grid_height)
    Ry = grid_height / (2.0 * K_SI * t_chip * grid_width)
    Rz = t_chip / (K_SI * grid_height * grid_width)

    max_slope = MAX_PD / (FACTOR_CHIP * t_chip * SPEC_HEAT_SI)
    step = PRECISION / max_slope
    time_elapsed=0.001

    src = 1
    dst = 0
        
    for t in range(0, total_iterations, num_iterations):
        src, dst = dst, src
        print_calculate_temp_args(
            min(num_iterations, total_iterations-t), 
            col, row, borderCols, borderRows, Cap, Rx, Ry, Rz, step, time_elapsed
        )
        calculate_temp(dimBlock, dimGrid, 
            min(num_iterations, total_iterations-t), 
            col, row, borderCols, borderRows, Cap, Rx, Ry, Rz, step, time_elapsed)

grid_cols = int(sys.argv[1])
grid_rows = int(sys.argv[1])
pyramid_height = int(sys.argv[2])
total_iterations = int(sys.argv[3])

EXPAND_RATE = 2
BLOCK_SIZE = 32 

borderCols = (pyramid_height)*EXPAND_RATE/2
borderRows = (pyramid_height)*EXPAND_RATE/2
smallBlockCol = BLOCK_SIZE-(pyramid_height)*EXPAND_RATE
smallBlockRow = BLOCK_SIZE-(pyramid_height)*EXPAND_RATE
blockCols = grid_cols//smallBlockCol+(0 if (grid_cols%smallBlockCol==0) else 1)
blockRows = grid_rows//smallBlockRow+(0 if (grid_rows%smallBlockRow==0) else 1)

compute_tran_temp(grid_cols, grid_rows, total_iterations, pyramid_height, blockCols, blockRows, borderCols, borderRows)
