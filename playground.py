import numpy as np

grid = []
row_size = 0
col_size = 0
fraction = 0.4
adhesion_prob = 1
dentric_height = 0
simulated_stepts = pow(10,6)

free_particles = []
growth = []
    
def main():
    init_grid(20,20)

    N = int(fraction * row_size * col_size)
    for i in range(N):
        fill_random_square()
    
    for t in range(simulated_stepts):
        move_random_particle()

    print_grid(1)
    print("Free Particles: ", len(free_particles))
    print("Growth Size: ", len(growth))

def init_grid(row_s, col_s):
    global row_size 
    row_size = row_s

    global col_size
    col_size = col_s

    for i in range(row_size):
        grid.append(np.zeros(col_size, dtype=int))

def fill_random_square():
    row = np.random.randint(dentric_height,row_size,dtype=int)
    col = np.random.randint(0,col_size, dtype=int)
    grid[row][col] = 1

    if row == 0:
        growth.append([row,col])
    else:
        free_particles.append([row,col])

def move_random_particle():
    l = len(free_particles)
    if l > 0:
        p = np.random.randint(0,len(free_particles))
    else:
        return
    
    r = free_particles[p][0]
    c = free_particles[p][1]

    dr = 0
    dc = 0    
    #particles are not allowed to interact with each other
    while [r+dr,c+dc] in free_particles or [r+dr,c+dc] in growth:
        dr = np.random.randint(-1,2,dtype=int)
        dc = np.random.randint(-1,2, dtype=int)
        
        #checking collisions with borders
        if r+dr < 0 + dentric_height:
            dr = 1
        elif r+dr >= row_size:
            dr = -1
        
        if c+dc < 0:
            dc = 1
        elif c+dc >= col_size:
            dc = -1

    grid[r][c] = 0
    grid[r+dr][c+dc] = 1
    #checking if particle attaches to growth
    if [r+dr+1,c+dc] in growth \
    or [r+dr-1,c+dc] in growth \
    or [r+dr,c+dc+1] in growth \
    or [r+dr,c+dc-1] in growth \
    or r+dr == 0:
        growth.append([r+dr,c+dc])
    else :
        free_particles.append([r+dr,c+dc])  

    free_particles.remove([r,c])
    #print(f"MOVING FROM: [{r},{c}] TO [{r+dr},{c+dc}]")

def print_grid(b):
    if b:
        print("================================================================")
        for i in range(len(grid)):
            print(grid[i])
        print("================================================================")

if __name__ == "__main__":
    main()