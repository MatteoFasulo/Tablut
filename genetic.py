from play import play_game
import time
import random
import copy
import sys

def cutoff_depth(d):
    return lambda game, state, depth: depth > d

def fitness(turns):
    return 30-turns

def create_starting_population(elements = 10):
    population = []
    for i in range(elements):
        population.append([random.uniform(0, 2), random.uniform(0, 2), random.uniform(0, 10), random.uniform(0, 2), random.uniform(0, 3)])
    return population

def cross_chromosome(chromosome1, chromosome2):
    alpha0, beta0, gamma0, theta0, epsilon0 = chromosome1
    alpha1, beta1, gamma1, theta1, epsilon1 = chromosome2
    new_chromosome1 = [alpha0, beta1, gamma0, theta1, epsilon0]
    new_chromosome2 = [alpha1, beta0, gamma1, theta0, epsilon1]
    return new_chromosome1, new_chromosome2

def mate(elements):
    random1 = copy.deepcopy(random.choice(elements))
    random2 = copy.deepcopy(random.choice(elements))

    alpha0, beta0, gamma0, theta0, epsilon0 = random1
    alpha1, beta1, gamma1, theta1, epsilon1 = random2

    new_chromosome = [(alpha0+alpha1)/2, (beta0+beta1)/2, (gamma0+gamma1)/2, (theta0+theta1)/2, (epsilon0+epsilon1)/2]
    return new_chromosome

def create_random_chromosome():
    return [random.uniform(0, 5), random.uniform(0, 5), random.uniform(0, 5), random.uniform(0, 5), random.uniform(0, 5)]

def mutate(population, mutation_rate=0.6):
    print(population)
    for i in range(1, len(population)):
        if random.random() < mutation_rate:
            alpha, beta, gamma, theta, epsilon = population[i]
            alpha += random.uniform(-1, 1)
            beta += random.uniform(-1, 1)
            gamma += random.uniform(-1, 1)
            theta += random.uniform(-1, 1)
            epsilon += random.uniform(-1, 1)
            population[i] = [alpha, beta, gamma, theta, epsilon]
    return population

def create_starting_from_params(alpha, beta, gamma, theta, epsilon, elements=10):
    population = []

    for i in range(elements):
        population.append([alpha+random.uniform(-1,1), beta+random.uniform(-1,1), gamma+random.uniform(-1,1), theta+random.uniform(-1,1), epsilon+random.uniform(-1,1)])
    return population
    

iterations = 50
elements = 10
max_moves = 30
cod = cutoff_depth(2)
population = create_starting_population(elements)


for iteration in range(iterations):
    results = []
    for pop in population:
        print(pop)
        alpha0, beta0, gamma0, theta0, epsilon0 = pop
        result, turns = play_game(alpha0, beta0, gamma0, theta0, epsilon0, cod, max_moves, name="Player", team=sys.argv[1], server_ip="127.0.0.1", timeout=60)
        #If result = 0, white wins
        #If result = 1, black wins
        #If result = 2, draw
        #If result = 3, max moves reached
        if result == 0:
            results.append([pop, fitness(turns)])
        else:
            results.append([pop, -1])
        time.sleep(15)

    
    results = sorted(results, key=lambda x: x[1], reverse=True)
    print("Best fitness: ", results[0][1])
    print("Best parameters: ", results[0][0])
    with open("results.txt", "a") as f:
        f.write("Generation: " + str(iteration) + "\n")
        f.write("Best fitness: " + str(results[0][1]) + "\n")
        f.write("Best parameters: " + str(results[0][0]) + "\n\n")
    


    #I copy the first element of the population
    new_population = []
    new_population.append(copy.deepcopy(results[0][0]))

    #I cross the first element with the second and the third
    e1, e2 = cross_chromosome(results[0][0], results[1][0])
    new_population.append(e1)
    new_population.append(e2)
    e1, e2 = cross_chromosome(results[0][0], results[2][0])
    new_population.append(e1)
    new_population.append(e2)


    #I mate from the top 5 elements creating the remaining-3 elements
    top_five = copy.deepcopy(results[:5])
    random.shuffle(top_five)
    top_five = [x[0] for x in top_five]

    new_population.append(mate(top_five))
    new_population.append(mate(top_five))
    new_population.append(mate(top_five))

    #I add three random elements
    new_population.append(create_random_chromosome())
    new_population.append(create_random_chromosome())

    #I mutate everything except the first element
    new_population = mutate(new_population)

    #I update the population
    population = copy.deepcopy(new_population)

    


