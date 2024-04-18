# optimizer.py
import random
import numpy as np
import matplotlib.pyplot as plt
import os

class AirConditioner:
    def __init__(self, model, btu, cost):
        self.model = model
        self.btu = btu
        self.cost = cost

class RoomACOptimizer:
    def __init__(self, width, length, budget, min_ac, min_distance):
        self.width = width
        self.length = length
        self.budget = budget
        self.min_ac = min_ac
        self.min_distance = min_distance
        self.center = (width // 2, length // 2)  # Agregando el centro de la habitación
        self.fitness_history = {'max': [], 'avg': [], 'min': []}
        self.ac_types = [
            AirConditioner('Básico', 12000, 7000),
            AirConditioner('Intermedio', 18000, 10000),
            AirConditioner('Avanzado', 24000, 13500)
        ]
        self.population = []
        self.population_size = 200
        self.generations = 500
        self.mutation_rate = 0.1
        self.crossover_rate = 0.7
        self.elite_size = 20
        self.total_btu_needed = self.width * self.length * 600
        self.top_solutions = []

    def generate_individual(self):
        individual = []
        total_cost = 0
        while total_cost < self.budget:
            ac = random.choice(self.ac_types)
            if total_cost + ac.cost <= self.budget:
                valid = False
                attempts = 0
                while not valid and attempts < 100:
                    position = [random.randint(0, self.width-1), random.randint(0, self.length-1)]
                    if all(np.sqrt((position[0] - existing_ac[1][0])**2 + (position[1] - existing_ac[1][1])**2) >= self.min_distance for existing_ac in individual):
                        valid = True
                    attempts += 1
                if valid:
                    individual.append([ac, position])
                    total_cost += ac.cost
                else:
                    break
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
            return self.generate_individual()

    def fitness(self, individual):
        total_btu = sum(ac.btu for ac, pos in individual)
        total_cost = sum(ac.cost for ac, pos in individual)
        
        # Calcular la eficiencia de BTU en función del costo
        if total_cost > 0:  # Asegura que no haya división por cero
            btu_efficiency = total_btu / total_cost
        else:
            btu_efficiency = 0  # En caso de que el costo sea cero, evita la división por cero
        
        # Calcular el porcentaje de BTU requeridos que se logra cubrir
        btu_coverage = total_btu / self.total_btu_needed
        
        # Calcular el porcentaje del presupuesto utilizado
        budget_usage = total_cost / self.budget
        
        # Fitness es más alto cuando se acerca a 1 o lo supera (btu_coverage) y cuando el uso del presupuesto es menor
        # Aquí se utiliza una fórmula que considera ambos aspectos, priorizando alcanzar la cobertura de BTU necesaria
        # mientras se minimiza el uso del presupuesto.
        if total_btu >= self.total_btu_needed and total_cost <= self.budget and len(individual) >= self.min_ac:
            return btu_coverage * (1 - budget_usage)
        else:
            return 0  # Retorna 0 si no se cumplen los criterios mínimos

    def select_parents(self):
        elite = sorted(self.population, key=self.fitness, reverse=True)[:self.elite_size]
        parent1 = random.choice(elite)
        parent2 = random.choice(self.population)
        return parent1, parent2

    def crossover(self, parent1, parent2):
        min_length = min(len(parent1), len(parent2))
        if random.random() < self.crossover_rate and min_length > 1:
            num_cuts = random.randint(1, max(1, min_length - 1))
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
        new_population = [max(self.population, key=self.fitness)]
        self.update_top_solutions(new_population[0])

        fitness_values = [self.fitness(individual) for individual in self.population]
        self.fitness_history['max'].append(max(fitness_values))
        self.fitness_history['avg'].append(np.mean(fitness_values))
        self.fitness_history['min'].append(min(fitness_values))

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
        total_btu = sum(ac.btu for ac, pos in new_individual)
        total_cost = sum(ac.cost for ac, pos in new_individual)
        fitness_score = self.fitness(new_individual)
        
        if len(self.top_solutions) < 3 or fitness_score > self.top_solutions[0][0]:
            if len(self.top_solutions) >= 3:
                self.top_solutions.pop(0)
            self.top_solutions.append((fitness_score, new_individual, total_btu, total_cost))
            self.top_solutions.sort(reverse=True, key=lambda x: x[0])

    def plot_fitness_history(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.fitness_history['max'], label='Mejor Fitness')
        plt.plot(self.fitness_history['avg'], label='Fitness Promedio')
        plt.plot(self.fitness_history['min'], label='Peor Fitness')
        plt.xlabel('Generación')
        plt.ylabel('Fitness')
        plt.title('Evolución del Fitness a lo largo de las Generaciones')
        plt.legend()
        plt.grid(True)
        plt.show()

    def run(self):
        self.initialize_population()
        for _ in range(self.generations):
            self.evolve()
        
        print("Top solutions:")
        for idx, (fitness, config, total_btu, total_cost) in enumerate(self.top_solutions):
            print(f"Configuration {idx + 1}: Fitness = {fitness:.2f}, Total BTU = {total_btu}, Total Cost = ${total_cost}")
            for ac, pos in config:
                print(f"  Model: {ac.model}, BTU: {ac.btu}, Cost: {ac.cost}, Position: {pos}")
        return self.top_solutions
    
    def generate_heatmap(self, room_length, room_width, ac_configurations):
        # Asegurarse de que la carpeta 'Graph' existe
        if not os.path.exists('Graph'):
            os.makedirs('Graph')
            
        for idx, (fitness_score, configuration, total_btu, total_cost) in enumerate(ac_configurations):
            minisplit_powers = [ac.btu / 3412 for ac, pos in configuration]  # Conversión de BTU a kW aproximadamente
            minisplit_locations = [pos for ac, pos in configuration]
            base_temperature = 35 - sum(minisplit_powers)  # Estimación simplificada
            temperature_data = np.full((room_length, room_width), base_temperature)
            for i in range(room_length):
                for j in range(room_width):
                    for loc, power in zip(minisplit_locations, minisplit_powers):
                        distance = np.sqrt((i - loc[0]) ** 2 + (j - loc[1]) ** 2)
                        if power != 0:
                            temperature_data[i, j] -= power / (distance + 1)
            avg_temperature = np.mean(temperature_data)
            plt.figure(figsize=(10, 8))
            plt.imshow(temperature_data, cmap="cool", interpolation="spline16")
            cbar = plt.colorbar()
            cbar.set_label('Temperatura (°C)')
            for loc in minisplit_locations:
                plt.scatter(loc[1], loc[0], marker='o', color='red', s=100)
            for i in range(room_length):
                for j in range(room_width):
                    plt.text(j, i, f'{temperature_data[i, j]:.1f}', ha='center', va='center', color='black')
            plt.title(f'Mapa de Calor Configuración {idx + 1} (Fitness: {fitness_score:.2f})\nTemperatura Promedio: {avg_temperature:.1f} °C')
            plt.xlabel('X')
            plt.ylabel('Y')
            
            # Guardar el gráfico en la carpeta 'Graph'
            plt.savefig(f'Graph/heatmap_{idx + 1}.png')
            plt.close()  # Cerrar la figura para liberar memoria
