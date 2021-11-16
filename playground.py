import numpy as np

#TODO: keep f above dentric_height constant

grid = []
row_size = 0
col_size = 0
concentration = 0.05
adhesion_prob = 0.01
dentric_height = 1
simulated_stepts = pow(10,6)

free_particles = []
growth = []

PRINT_GRID = True
    
def main():
    init_grid(100,35)

    N = int(concentration * row_size * col_size)
    for i in range(N):
        fill_random_square()
    
    for t in range(simulated_stepts):
        move_random_particle()

    print_grid(PRINT_GRID)
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
    b = True
    while b:
        row = np.random.randint(dentric_height,row_size,dtype=int)
        col = np.random.randint(0,col_size, dtype=int)
        b =  grid[row][col]
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

    dr = np.random.randint(-1,2,dtype=int)
    dc = np.random.randint(-1,2, dtype=int)    

    #checking collisions with borders
    if r+dr < 0: #This collision should never happen. Including it anyway.
        dr = 1
    elif r+dr >= row_size:
        dr = -1
    
    if c+dc < 0:
        dc = 1
    elif c+dc >= col_size:
        dc = -1
    
    #particles are not allowed to interact with each other
    if not grid[r+dr][c+dc] == 1:        
        grid[r][c] = 0
        grid[r+dr][c+dc] = 1
        #checking if particle attaches to growth
        if [r+dr+1,c+dc] in growth \
        or [r+dr-1,c+dc] in growth \
        or [r+dr,c+dc+1] in growth \
        or [r+dr,c+dc-1] in growth \
        or r+dr == 0:
            if np.random.uniform(0, 1) < adhesion_prob:
                growth.append([r+dr,c+dc])

                #updating height of dentric growth
                global dentric_height
                if r+dr > dentric_height:
                    dentric_height = r+dr

                global concentration
                #adjusting concentration
                if len(free_particles) / (row_size * col_size) < concentration:
                    fill_random_square()

            else:
                free_particles.append([r+dr,c+dc])
        else :
            free_particles.append([r+dr,c+dc])  

        free_particles.remove([r,c])
        #print(f"MOVING FROM: [{r},{c}] TO [{r+dr},{c+dc}]")

def print_grid(b):
    if b:
        for i in range(len(grid)):
            print(grid[i])

if __name__ == "__main__":
    main()