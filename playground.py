import numpy as np
import os
import timeit

grid = []
row_size = 0
col_size = 0
concentration = 0.4
adhesion_prob = 0.01
dentric_height = 1
simulated_stepts = pow(10,0)

free_particles = []
growth = []

PRINT_GRID = True
RUN_TIMES = []
    
def main():
    init_grid(1000,10)

    N = int(concentration * row_size * col_size)
    for i in range(N):
        fill_random_square()
    
    for t in range(simulated_stepts):
        move_random_particle()

    print_grid(not PRINT_GRID)
    print_grid_to_file(PRINT_GRID)

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
    start = timeit.default_timer()
    l = len(free_particles)
    if l > 0:
        p = np.random.randint(0,len(free_particles))
        #print(f"Selected random particle: {free_particles[p]}")
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
        
        #print(f"MOVING FROM: [{r},{c}] TO [{r+dr},{c+dc}]")     
        grid[r][c] = 0
        grid[r+dr][c+dc] = 1

        #checking if particle attaches to growth
        if [r+dr+1,c+dc] in growth \
        or [r+dr-1,c+dc] in growth \
        or [r+dr,c+dc+1] in growth \
        or [r+dr,c+dc-1] in growth:
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
        elif r+dr == 0:
            growth.append([r+dr,c+dc])
        else :
            free_particles.append([r+dr,c+dc])  

        #print(f"particle to pop: {free_particles[p]}")
        free_particles[p] = free_particles.pop()

    
    stop = timeit.default_timer()
    RUN_TIMES.append(stop - start)

def print_grid(b):
    if b:
        for i in range(len(grid)):
            print(grid[i])

def print_grid_to_file(b):
    global adhesion_prob
    global concentration

    dirname = os.path.dirname(__file__)
    filepath = os.path.join(dirname, f'material_S={adhesion_prob}_f={concentration}/')

    if b:
        #cleaning free particles
        #for p in free_particles:
            #grid[p[0]][p[1]] = 0
        print(RUN_TIMES)

        #creating dir
        if not os.path.exists(os.path.dirname(filepath)):
            try:
              os.makedirs(os.path.dirname(filepath))
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                   raise

        with open(f'{filepath}test.txt', 'w') as file:
            for i in range(len(grid)):
                for j in range(len(grid[i])):
                    file.write(str(grid[i][j]))
                file.write("\n")

if __name__ == "__main__":
    main()