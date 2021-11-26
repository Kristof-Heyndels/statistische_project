import numpy as np
import os

grid = []
row_size = 0
col_size = 0
concentration = 0.4
adhesion_prob = 1
dentric_height = 1
allowed_zone_height = 0
simulated_steps = pow(10,6)

free_particles = []
growth = []

def main():
    for k in range(10):
        init_grid(1000,50)

        N = int(concentration * allowed_zone_height * col_size)
        for i in range(N):
            fill_random_square()

        for t in range(simulated_steps):
            #print(f"{t:.2e}")
            move_random_particle()

        #print_grid()
        print_grid_to_file(k)
        print(f"Crystal size: {len(growth)}")
    
def init_grid(row_s, col_s):
    global row_size 
    row_size = row_s

    global col_size
    col_size = col_s

    global allowed_zone_height 
    allowed_zone_height = row_size * 0.2

    global growth
    growth.clear()

    global free_particles
    free_particles.clear()

    global grid
    grid.clear()

    global dentric_height
    dentric_height = 1

    grid.append(np.ones(col_size, dtype=int))
    for j in range (col_size):
      growth.append([0,j])

    for i in range(row_size - 1):
        grid.append(np.zeros(col_size, dtype=int))

def fill_random_square():
    b = True
    i = 0
    while b:
        i += 1
        upper_bound = min(dentric_height + allowed_zone_height, row_size)
        if dentric_height + 1 >= upper_bound:
          return
        row = np.random.randint(dentric_height + 1,upper_bound,dtype=int)
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
        #print(f"Selected random particle: {free_particles[p]} with index: {p}")
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

        #free_particles.remove([r,c])
        free_particles[p] = free_particles.pop()

def print_grid():
    for i in range(len(grid)):
        print(grid[i])

def print_grid_to_file(k):
    global adhesion_prob
    global concentration

    dirname = os.path.dirname(__file__)
    #dirname = ""
    filepath = os.path.join(dirname, f'material_S={adhesion_prob}_f={concentration}/')

    #cleaning free particles
    for p in free_particles:
        grid[p[0]][p[1]] = 0

    #creating dir
    if not os.path.exists(os.path.dirname(filepath)):
        try:
          os.makedirs(os.path.dirname(filepath))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(f'{filepath}mat_{k}_cleaned.txt', 'w') as file:
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                if grid[i][j] == 1:
                    file.write(str(grid[i][j]))
                else:
                    file.write(" ")
            file.write("\n")

    with open(f'{filepath}mat_{k}.txt', 'w') as file:
        for i in range(len(grid)):
            for j in range(len(grid[i])):
                file.write(str(grid[i][j]))
            file.write("\n")

if __name__ == "__main__":
    main()