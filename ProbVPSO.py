import random
import numpy as np

# Matrice des distances
dist = [
    [0, 2, 2, 7, 15, 2, 5, 7, 6, 5],
    [2, 0, 10, 4, 7, 3, 7, 15, 8, 2],
    [2, 10, 0, 1, 4, 3, 3, 4, 2, 3],
    [7, 4, 1, 0, 2, 15, 7, 7, 5, 4],
    [7, 10, 4, 2, 0, 7, 3, 2, 2, 7],
    [2, 3, 3, 7, 7, 0, 1, 7, 2, 10],
    [5, 7, 3, 7, 3, 1, 0, 2, 1, 3],
    [7, 7, 4, 7, 2, 7, 2, 0, 1, 10],
    [6, 8, 2, 5, 2, 2, 1, 1, 0, 15],
    [5, 2, 3, 4, 7, 10, 3, 10, 15, 0]
]


def calc_dist(route):
    """Calcule la distance totale d'une route"""
    total = sum(dist[route[i]][route[i + 1]] for i in range(len(route) - 1))
    return total + dist[route[-1]][route[0]]


def swap_operator(route, velocity):
    """Applique des échanges selon la vélocité"""
    new_route = route[:]
    n_swaps = int(abs(velocity) * len(route) / 2)

    for _ in range(n_swaps):
        i, j = random.sample(range(len(route)), 2)
        new_route[i], new_route[j] = new_route[j], new_route[i]

    return new_route


def path_difference(route1, route2):
    """Calcule la différence entre deux routes (pour la vélocité)"""
    diff = 0
    for i in range(len(route1)):
        if route1[i] != route2[i]:
            diff += 1
    return diff / len(route1)


class Particle:
    """Particule pour PSO"""

    def __init__(self, n_cities):
        self.position = list(range(n_cities))
        random.shuffle(self.position)
        self.velocity = random.uniform(0, 1)
        self.best_position = self.position[:]
        self.best_distance = calc_dist(self.position)

    def update_velocity(self, global_best, w=0.5, c1=1.5, c2=1.5):
        """Met à jour la vélocité"""
        r1, r2 = random.random(), random.random()

        # Composante cognitive (vers son meilleur)
        cognitive = c1 * r1 * path_difference(self.position, self.best_position)

        # Composante sociale (vers le meilleur global)
        social = c2 * r2 * path_difference(self.position, global_best)

        # Nouvelle vélocité
        self.velocity = w * self.velocity + cognitive + social

        # Limiter la vélocité
        self.velocity = max(-1, min(1, self.velocity))

    def update_position(self):
        """Met à jour la position"""
        self.position = swap_operator(self.position, self.velocity)

        # Mise à jour du meilleur personnel
        current_dist = calc_dist(self.position)
        if current_dist < self.best_distance:
            self.best_position = self.position[:]
            self.best_distance = current_dist


def pso_tsp(n_particles=30, n_iterations=500, w=0.5, c1=1.5, c2=1.5):
    """Optimisation par Essaim Particulaire pour TSP"""
    n_cities = len(dist)

    # Initialiser l'essaim
    swarm = [Particle(n_cities) for _ in range(n_particles)]

    # Meilleur global
    global_best = min(swarm, key=lambda p: p.best_distance)
    global_best_position = global_best.best_position[:]
    global_best_distance = global_best.best_distance

    print("━" * 50)
    print(f"PSO pour TSP")
    print(f"Particules: {n_particles}, Itérations: {n_iterations}")
    print(f"Distance initiale: {global_best_distance}")
    print(f"Paramètres: w={w}, c1={c1}, c2={c2}")
    print("━" * 50)

    for iteration in range(n_iterations):
        for particle in swarm:
            # Mise à jour vélocité et position
            particle.update_velocity(global_best_position, w, c1, c2)
            particle.update_position()

            # Mise à jour du meilleur global
            if particle.best_distance < global_best_distance:
                global_best_position = particle.best_position[:]
                global_best_distance = particle.best_distance
                print(f"Iter {iteration}: Amélioration → {global_best_distance:.2f}")

        # Affichage périodique
        if iteration % 100 == 0:
            avg_dist = sum(p.best_distance for p in swarm) / n_particles
            print(f"Iter {iteration}: Meilleure={global_best_distance:.2f}, Moyenne={avg_dist:.2f}")

    print("━" * 50)
    print(f"Solution finale: {global_best_position}")
    print(f"Distance: {global_best_distance:.2f}")
    print("━" * 50)

    return global_best_position, global_best_distance


# Exécution
solution, distance = pso_tsp(n_particles=30, n_iterations=500)