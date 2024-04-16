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
        self.elite_size = 20
        self.total_btu_needed = self.width * self.length * 600
        self.top_solutions = []  # Inicializa la lista de mejores soluciones

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

    def validate_individual(self, individual):
        total_cost = sum(ac.cost for ac, pos in individual)
        if total_cost <= self.budget and len(individual) >= self.min_ac:
            return individual
        else:
            return self.generate_individual()  # Regenera un individuo válido

    def fitness(self, individual):
        total_btu = sum(ac.btu for ac, pos in individual)
        total_cost = sum(ac.cost for ac, pos in individual)
        # Prioriza la eficiencia en coste y BTU
        if total_btu >= self.total_btu_needed and total_cost <= self.budget and len(individual) >= self.min_ac:
            return (total_btu / self.total_btu_needed) * 100 - (total_cost / self.budget) * 100
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
        self.update_top_solutions(new_population[0])
        while len(new_population) < self.population_size:
            parent1, parent2 = self.select_parents()
            children = self.crossover(parent1, parent2)
            for child in children:
                valid_child = self.validate_individual(child)
                if len(new_population) < self.population_size:
                    new_population.append(self.mutate(valid_child))
                    self.update_top_solutions(valid_child)
        self.population = new_population

    def update_top_solutions(self, new_individual):
        # Asumiendo que top_solutions es una lista de tuplas (fitness, individual) y siempre está ordenada
        if len(self.top_solutions) < 3 or self.fitness(new_individual) > self.top_solutions[0][0]:
            if len(self.top_solutions) >= 3:
                self.top_solutions.pop(0)
            self.top_solutions.append((self.fitness(new_individual), new_individual))
            self.top_solutions.sort(reverse=True, key=lambda x: x[0])  # Mantener ordenado


    def run(self):
        self.initialize_population()
        for _ in range(self.generations):
            self.evolve()
        return self.top_solutions  # Devuelve las tres mejores soluciones

# Ejecución del algoritmo genético
optimizer = RoomACOptimizer(5, 5, 40000, 3)
top_solutions = optimizer.run()

# Imprimir las tres mejores configuraciones
for index, (fitness_score, best_configuration) in enumerate(top_solutions):
    print(f"Top {index + 1} Configuration: Fitness Score: {fitness_score}")
    for ac, pos in best_configuration:
        print(f"Model: {ac.model}, Position: {pos}, BTU: {ac.btu}, Cost: {ac.cost}")
    print()  # Espacio entre configuraciones
