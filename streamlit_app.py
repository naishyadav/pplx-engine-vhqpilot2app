import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def objective_function(x):
    return -(x**2) + 5*x + 10  # Simple quadratic function

def create_individual():
    return np.random.uniform(-10, 10)

def crossover(parent1, parent2):
    return (parent1 + parent2) / 2

def mutate(individual, mutation_rate):
    if np.random.random() < mutation_rate:
        return individual + np.random.normal(0, 1)
    return individual

def genetic_algorithm(population_size, generations, mutation_rate):
    population = [create_individual() for _ in range(population_size)]
    best_fitness_history = []

    for gen in range(generations):
        fitness_scores = [objective_function(ind) for ind in population]
        best_fitness = max(fitness_scores)
        best_fitness_history.append(best_fitness)

        selected_indices = np.random.choice(range(population_size), size=population_size, p=np.array(fitness_scores)/sum(fitness_scores))
        selected = [population[i] for i in selected_indices]

        new_population = []
        for i in range(0, population_size, 2):
            parent1, parent2 = selected[i], selected[i+1]
            child1 = mutate(crossover(parent1, parent2), mutation_rate)
            child2 = mutate(crossover(parent1, parent2), mutation_rate)
            new_population.extend([child1, child2])

        population = new_population

    return population, best_fitness_history

def main():
    st.title("Genetic Algorithm Proof-of-Concept")
    st.write("This app demonstrates a simple genetic algorithm optimizing a quadratic function.")

    population_size = st.slider("Population Size", min_value=10, max_value=200, value=50, step=10)
    generations = st.slider("Number of Generations", min_value=10, max_value=500, value=100, step=10)
    mutation_rate = st.slider("Mutation Rate", min_value=0.0, max_value=1.0, value=0.1, step=0.05)

    if st.button("Run Genetic Algorithm"):
        final_population, fitness_history = genetic_algorithm(population_size, generations, mutation_rate)

        # Plot fitness history
        fig, ax = plt.subplots()
        ax.plot(range(generations), fitness_history)
        ax.set_xlabel("Generation")
        ax.set_ylabel("Best Fitness")
        ax.set_title("Fitness History")
        st.pyplot(fig)

        # Plot final population
        x = np.linspace(-10, 10, 200)
        y = [objective_function(xi) for xi in x]

        fig, ax = plt.subplots()
        ax.plot(x, y, label='Objective Function')
        ax.scatter(final_population, [objective_function(ind) for ind in final_population], color='red', label='Final Population')
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.set_title("Final Population")
        ax.legend()
        st.pyplot(fig)

        st.write(f"Best solution found: x = {max(final_population, key=objective_function):.4f}")
        st.write(f"Best fitness: {objective_function(max(final_population, key=objective_function)):.4f}")

if __name__ == "__main__":
    main()
