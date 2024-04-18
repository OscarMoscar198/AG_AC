# gui.py
import tkinter as tk
from tkinter import ttk, scrolledtext
from optimizer import RoomACOptimizer

class RoomACGUI:
    def __init__(self, master):
        self.master = master
        master.title("Optimizador de Aire Acondicionado para Habitaciones")

        # Configuración de los widgets
        ttk.Label(master, text="Ancho de la habitación (metros):").grid(row=0, column=0)
        ttk.Label(master, text="Largo de la habitación (metros):").grid(row=1, column=0)
        ttk.Label(master, text="Presupuesto:").grid(row=2, column=0)
        ttk.Label(master, text="Mínimo de ACs:").grid(row=3, column=0)
        ttk.Label(master, text="Distancia mínima (metros):").grid(row=4, column=0)
        ttk.Label(master, text="BTU Necesarios:").grid(row=5, column=0)

        self.width_var = tk.IntVar()
        self.length_var = tk.IntVar()
        self.budget_var = tk.IntVar()
        self.min_ac_var = tk.IntVar()
        self.min_distance_var = tk.IntVar()
        self.btu_needed_var = tk.StringVar(value="Ingrese medidas")

        width_entry = ttk.Entry(master, textvariable=self.width_var)
        width_entry.grid(row=0, column=1)
        width_entry.bind('<FocusOut>', lambda e: self.update_btu_display())

        length_entry = ttk.Entry(master, textvariable=self.length_var)
        length_entry.grid(row=1, column=1)
        length_entry.bind('<FocusOut>', lambda e: self.update_btu_display())

        ttk.Entry(master, textvariable=self.budget_var).grid(row=2, column=1)
        ttk.Entry(master, textvariable=self.min_ac_var).grid(row=3, column=1)
        ttk.Entry(master, textvariable=self.min_distance_var).grid(row=4, column=1)
        ttk.Label(master, textvariable=self.btu_needed_var).grid(row=5, column=1)

        ttk.Button(master, text="Optimizar", command=self.run_optimizer).grid(row=6, columnspan=2)

        # Widget de texto para mostrar los resultados
        self.result_text = scrolledtext.ScrolledText(master, width=80, height=10)
        self.result_text.grid(row=7, column=0, columnspan=2, pady=10)

        # Añadir el display de información de ACs
        self.ac_info_text = scrolledtext.ScrolledText(master, width=80, height=5)
        self.ac_info_text.grid(row=8, column=0, columnspan=2, pady=10)
        self.display_ac_info()

        # Botón para mostrar la evolución del fitness
        ttk.Button(master, text="Mostrar Evolución Fitness", command=self.show_fitness_evolution).grid(row=9, columnspan=2)

    def display_ac_info(self):
        # Muestra la información sobre los AC disponibles en la interfaz
        ac_types = [
            {'model': 'Básico', 'btu': 12000, 'cost': 7000},
            {'model': 'Intermedio', 'btu': 18000, 'cost': 10000},
            {'model': 'Avanzado', 'btu': 24000, 'cost': 13500}
        ]
        self.ac_info_text.insert(tk.END, "Tipos de Aires Acondicionados Disponibles:\n")
        for ac in ac_types:
            self.ac_info_text.insert(tk.END, f"Modelo: {ac['model']}, BTU: {ac['btu']}, Costo: ${ac['cost']}\n")
        self.ac_info_text.config(state=tk.DISABLED)  # Hacer el texto no editable

    def update_btu_display(self):
        width = self.width_var.get()
        length = self.length_var.get()
        if width > 0 and length > 0:
            btu_needed = width * length * 600  # 600 BTU por metro cuadrado
            self.btu_needed_var.set(f"{btu_needed} BTU")
        else:
            self.btu_needed_var.set("Ingrese medidas válidas")
        return True  # Necesario para validaciones en Tkinter

    def run_optimizer(self):
        # Limpia el texto antes de cada optimización
        self.result_text.delete('1.0', tk.END)
        
        self.optimizer = RoomACOptimizer(
            self.width_var.get(),
            self.length_var.get(),
            self.budget_var.get(),
            self.min_ac_var.get(),
            self.min_distance_var.get()
        )
        top_solutions = self.optimizer.run()
        
        # Llama a la función para mostrar resultados en el widget de texto
        self.display_results(top_solutions)
        self.optimizer.generate_heatmap(self.length_var.get(), self.width_var.get(), top_solutions)

    def display_results(self, top_solutions):
        self.result_text.insert(tk.END, "Top 3 AC Configurations:\n")
        for idx, (fitness, config, total_btu, total_cost) in enumerate(top_solutions):
            self.result_text.insert(tk.END, f"Configuration {idx + 1}: Fitness = {fitness:.2f}, Total BTU = {total_btu}, Total Cost = ${total_cost}\n")
            for ac, pos in config:
                self.result_text.insert(tk.END, f"  Model: {ac.model}, BTU: {ac.btu}, Cost: {ac.cost}, Position: {pos}\n")
            self.result_text.insert(tk.END, "\n")

    def show_fitness_evolution(self):
        self.optimizer.plot_fitness_history()

def main():
    root = tk.Tk()
    app = RoomACGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
