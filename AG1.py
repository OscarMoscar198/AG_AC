import random

class AirConditioner:
    def __init__(self, type, cost, capacity, x, y):
        self.type = type
        self.cost = cost
        self.capacity = capacity
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{self.type} (Cost: {self.cost}, Capacity: {self.capacity}, Position: ({self.x},{self.y}))"

AC_TYPES = {
    "Básico": {"cost": 6500, "capacity": 12000},
    "Intermedio": {"cost": 10000, "capacity": 18000},
    "Avanzado": {"cost": 13500, "capacity": 24000}
}

def generate_initial_population(pop_size, width, height, min_ac, budget):
    population = []
    required_btu = 600 * width * height
    while len(population) < pop_size:
        num_ac = random.randint(min_ac, min_ac + 5)
        individual = []
        total_cost = 0
        total_capacity = 0
        for _ in range(num_ac):
            ac_type = random.choice(list(AC_TYPES.keys()))
            cost = AC_TYPES[ac_type]["cost"]
            capacity = AC_TYPES[ac_type]["capacity"]
            x = random.randint(0, width - 1)
            y = random.randint(0, height - 1)
            if total_cost + cost > budget:
                continue
            individual.append(AirConditioner(ac_type, cost, capacity, x, y))
            total_cost += cost
            total_capacity += capacity
        if total_cost <= budget and total_capacity >= required_btu:
            population.append(individual)
    return population

def calculate_fitness(individual, width, height, budget, required_btu):
    total_btu = sum(ac.capacity for ac in individual)
    total_cost = sum(ac.cost for ac in individual)
    btu_excess = abs(total_btu - required_btu)
    if total_cost > budget or total_btu < required_btu:
        return float('-inf')
    return -btu_excess - total_cost

def mutate(individual, width, height, mutation_rate=0.2):  # Increased mutation rate
    if random.random() < mutation_rate:
        idx = random.randint(0, len(individual) - 1)
        ac_type = random.choice(list(AC_TYPES.keys()))
        cost = AC_TYPES[ac_type]["cost"]
        capacity = AC_TYPES[ac_type]["capacity"]
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        individual[idx] = AirConditioner(ac_type, cost, capacity, x, y)

def genetic_algorithm(width, height, budget, required_btu, min_ac=2, pop_size=100, generations=100):
    population = generate_initial_population(pop_size, width, height, min_ac, budget)
    best_individual = None
    best_fitness = float('-inf')
    for generation in range(generations):
        fitness_scores = [calculate_fitness(ind, width, height, budget, required_btu) for ind in population]
        new_population = []
        if best_individual:
            new_population.append(best_individual)  # Elitism
        for ind in population:
            if random.random() < 0.5:
                new_population.append(ind)
            else:
                mutate(ind, width, height)
                new_population.append(ind)
        current_best = max(population, key=lambda ind: calculate_fitness(ind, width, height, budget, required_btu))
        current_best_fitness = calculate_fitness(current_best, width, height, budget, required_btu)
        if current_best_fitness > best_fitness:
            best_fitness = current_best_fitness
            best_individual = current_best
        print(f"Generation {generation + 1}, Best fitness: {best_fitness}")
        population = new_population
    return best_individual

# Parámetros del problema
width = 10  # ancho de la habitación en metros
height = 10  # largo de la habitación en metros
budget = 40000
min_ac = 2
required_btu = width * height * 600

# Ejecutar el algoritmo genético
best_solution = genetic_algorithm(width, height, budget, required_btu, min_ac)
print("Best solution:", best_solution)