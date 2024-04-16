import random
import matplotlib.pyplot as plt

class AirConditioner:
    def __init__(self, model, btu, cost):
        self.model = model
        self.btu = btu
        self.cost = cost

class RoomACOptimizer:
    def __init__(self, width, length, budget, min_ac):
        self.width = width
        self.length = length
        self.budget = budget
        self.min_ac = min_ac
        self.ac_types = [
            AirConditioner('Básico', 12000, 7000),
            AirConditioner('Intermedio', 18000, 10000),
            AirConditioner('Avanzado', 24000, 13500)
        ]
        self.population = []
        self.population_size = 100
        self.generations = 100
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = 20  # Top 10% of the population considered as elite
        self.total_btu_needed = self.width * self.length * 600

    def generate_individual(self):
        individual = []
        total_cost = 0
        while total_cost < self.budget:
            ac = random.choice(self.ac_types)
            if total_cost + ac.cost <= self.budget:
                position = [random.randint(0, self.width-1), random.randint(0, self.length-1)]
                individual.append([ac, position])
                total_cost += ac.cost
            else:
                break
        return individual

    def initialize_population(self):
        for _ in range(self.population_size):
            self.population.append(self.generate_individual())

    def fitness(self, individual):
        total_btu = sum(ac.btu for ac, pos in individual)
        total_cost = sum(ac.cost for ac, pos in individual)
        if total_btu >= self.total_btu_needed and total_cost <= self.budget and len(individual) >= self.min_ac:
            return total_btu - abs(self.total_btu_needed - total_btu) + (self.budget - total_cost)
        return 0

    def select_parents(self):
        # Sort and select elite
        elite = sorted(self.population, key=self.fitness, reverse=True)[:self.elite_size]
        # Allow elite to mate with anyone
        parent1 = random.choice(elite)
        parent2 = random.choice(self.population)
        return parent1, parent2

    def crossover(self, parent1, parent2):
        min_length = min(len(parent1), len(parent2))
        if random.random() < self.crossover_rate and min_length > 1:
            num_cuts = random.randint(1, max(1, min_length - 1))  # Ensure that we do not exceed the available slots
            cuts = sorted(random.sample(range(1, min_length), num_cuts))
            children = [parent1, parent2]
            for i in range(num_cuts):
                if i % 2 == 0:
                    children = [children[0][:cuts[i]] + children[1][cuts[i]:], children[1][:cuts[i]] + children[0][cuts[i]:]]
            return children
        return [parent1, parent2]

    def mutate(self, individual):
        for idx in range(len(individual)):
            if random.random() < self.mutation_rate:
                swap_idx = random.randint(0, len(individual)-1)
                individual[idx], individual[swap_idx] = individual[swap_idx], individual[idx]
        return individual

    def evolve(self):
        new_population = [max(self.population, key=self.fitness)]  # Keep the best
        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents()
            children = self.crossover(parent1, parent2)
            for child in children:
                if len(new_population) < self.population_size:
                    new_population.append(self.mutate(child))
        self.population = new_population

    def run(self):
        self.initialize_population()
        for _ in range(self.generations):
            self.evolve()
        best_solution = max(self.population, key=self.fitness)
        return best_solution, self.fitness(best_solution)

# Ejecución del algoritmo genético
optimizer = RoomACOptimizer(15, 15, 90000, 3)
best_configuration, fitness_score = optimizer.run()
print("Best configuration:", [[ac.model, pos, ac.btu, ac.cost] for ac, pos in best_configuration])
print("Fitness score:", fitness_score)
