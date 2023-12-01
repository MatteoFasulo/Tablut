# VERY IMPORTANT NOTICE

running the program as it is now will not execute correctly, since the weights are now assigned statically. The file that has been kept in the repository must be interpreted as read-only

# Genetic Algorithm for Refining AI Weights

Within this section, we delve into the intricacies of employing a genetic algorithm to fine-tune the weights of an artificial intelligence system within the specific domain of Tablut gameplay. The primary objective of this algorithm is to iteratively evolve a population of weight sets, refining the AI's performance over time. These weights serve as crucial hyperparameters for the associated heuristics.

## Concise Overview of the Algorithm

[Genetic algorithms](https://en.wikipedia.org/wiki/Genetic_algorithm), commonly applied in optimization scenarios, found utility in our context by framing an optimization problem around Tablut matches. This involved formulating a fitness function, which, given a match with a set of hyperparameters and the count of moves required for victory, yields a value denoted as N.

```python title="genetic.py" linenums="1"
def fitness(turns):
    return 30 - turns
```

The algorithm's primary objective is to maximize the derived value N. Notably, 30 represents the maximum allowable moves per game, and if the game extends beyond this limit, the fitness is constrained to -1.

### Algorithmic Workflow

Initiating with a starting population of hyperparameters comprising 10 tuples, the algorithm orchestrates 10 games, recording the move count for each victory. Subsequently, it calculates a new population by selecting the best-performing elements and subjecting them to mutations. Noteworthy is the inclusion of two entirely random elements in each population, strategically introduced to mitigate the risk of converging into a local minimum.

## Genetic Algorithm Components

### Crossover

The `cross_chromosome` function performs crossover between two parent chromosomes, generating two new chromosomes.

```python title="genetic.py"
def cross_chromosome(chromosome1, chromosome2):
    alpha0, beta0, gamma0, theta0, epsilon0 = chromosome1
    alpha1, beta1, gamma1, theta1, epsilon1 = chromosome2
    new_chromosome1 = [alpha0, beta1, gamma0, theta1, epsilon0]
    new_chromosome2 = [alpha1, beta0, gamma1, theta0, epsilon1]
    return new_chromosome1, new_chromosome2
```

### Mate Selection

The `mate` function randomly selects two chromosomes from the population and creates a new chromosome through averaging their values.

```python title="genetic.py"
def mate(elements):
    random1 = copy.deepcopy(random.choice(elements))
    random2 = copy.deepcopy(random.choice(elements))

    alpha0, beta0, gamma0, theta0, epsilon0 = random1
    alpha1, beta1, gamma1, theta1, epsilon1 = random2

    new_chromosome = [(alpha0+alpha1)/2, (beta0+beta1)/2, (gamma0+gamma1)/2, (theta0+theta1)/2, (epsilon0+epsilon1)/2]
    return new_chromosome
```

### Mutation

The `mutate` function introduces random mutations to the population, affecting the weights of each chromosome.

```python title="genetic.py"
def mutate(population, mutation_rate=0.6):
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
```

### Population Initialization

The `create_starting_population` function initializes the population with random chromosomes.

```python title="genetic.py"
def create_starting_population(elements=10):
    population = []
    for i in range(elements):
        population.append([random.uniform(0, 2), random.uniform(0, 2), random.uniform(0, 10), random.uniform(0, 2), random.uniform(0, 3)])
    return population
```



## Main Loop

The genetic algorithm iterates over a predefined number of generations, evaluating the fitness of each chromosome in the population by playing games. The top-performing chromosomes are selected for crossover, mating, and mutation to produce the next generation.

```python title="genetic.py" linenums="1"
iterations = 50
elements = 10
max_moves = 30
cod = cutoff_depth(2)
population = create_starting_population(elements)

for iteration in range(iterations):
    results = []
    for pop in population:
        # Play a game with the current chromosome
        alpha0, beta0, gamma0, theta0, epsilon0 = pop
        result, turns = play_game(alpha0, beta0, gamma0, theta0, epsilon0, cod, max_moves, name="Player", team=sys.argv[1], server_ip="127.0.0.1", timeout=60)
        if result == 0:
            results.append([pop, fitness(turns)])
        else:
            results.append([pop, -1])
        time.sleep(5)

    # Sort results by fitness in descending order
    results = sorted(results, key=lambda x: x[1], reverse=True)

    # Print and record the best fitness and parameters
    print("Generation:", iteration)
    print("Best fitness:", results[0][1])
    print("Best parameters:", results[0][0])

    with open("results.txt", "a") as f:
        f.write("Generation: " + str(iteration) + "\n")
        f.write("Best fitness: " + str(results[0][1]) + "\n")
        f.write("Best parameters: " + str(results[0][0]) + "\n\n")

    # Create a new population for the next generation
    new_population = [copy.deepcopy(results[0][0])]

    # Crossover the top-performing chromosomes
    e1, e2 = cross_chromosome(results[0][0], results[1][0])
    new_population.extend([e1, e2])
    e1, e2 = cross_chromosome(results[0][0], results[2][0])
    new_population.extend([e1, e2])

    # Mate from the top 5 elements to create the remaining-3 elements
    top_five = copy.deepcopy(results[:5])
    random.shuffle(top_five)
    top_five = [x[0] for x in top_five]
    new_population.extend([mate(top_five) for _ in range(3)])

    # Add three random elements
    new_population.extend([create_random_chromosome() for _ in range(2)])

    # Mutate everything except the first element
    new_population = mutate(new_population)

    # Update the population for the next generation
    population = copy.deepcopy(new_population)
```
