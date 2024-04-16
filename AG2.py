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
        self.population_size = 150
        self.generations = 500
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
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
        weighted_population = [(self.fitness(ind), ind) for ind in self.population]
        weights = [fit for fit, _ in weighted_population]
        total = sum(weights)
        pick = random.uniform(0, total)
        current = 0
        for weight, individual in weighted_population:
            current += weight
            if current > pick:
                return individual
        return weighted_population[0][1]  # Fallback

    def crossover(self, parent1, parent2):
        if random.random() < self.crossover_rate:
            point = random.randint(1, min(len(parent1), len(parent2)) - 1)
            child1 = parent1[:point] + parent2[point:]
            child2 = parent2[:point] + parent1[point:]
            return child1, child2
        return parent1, parent2

    def mutate(self, individual):
        if random.random() < self.mutation_rate:
            idx = random.randint(0, len(individual) - 1)
            new_ac = self.generate_individual()[0]
            individual[idx][0] = new_ac[0]  # Actualiza el tipo de AC
            individual[idx][1] = new_ac[1]  # Actualiza la posición
        return individual

    def evolve(self):
        new_population = []
        while len(new_population) < self.population_size:
            parent1 = self.select_parents()
            parent2 = self.select_parents()
            child1, child2 = self.crossover(parent1, parent2)
            new_population.append(self.mutate(child1))
            if len(new_population) < self.population_size:
                new_population.append(self.mutate(child2))
        self.population = new_population

    def run(self):
        self.initialize_population()
        for _ in range(self.generations):
            self.evolve()
        best_solution = max(self.population, key=self.fitness)
        return best_solution, self.fitness(best_solution)

# Ejecución del algoritmo genético
optimizer = RoomACOptimizer(10, 10, 40000, 2)
best_configuration, fitness_score = optimizer.run()
print("Best configuration:", [[ac.model, pos, ac.btu, ac.cost] for ac, pos in best_configuration])
print("Fitness score:", fitness_score)
