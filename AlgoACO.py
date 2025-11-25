import random

# ------------------------------
# Classe problème : Sac à dos
# ------------------------------
class SacADos:
    def __init__(self, valeurs, poids, capacite):
        assert len(valeurs) == len(poids), "valeurs et poids doivent avoir même longueur"
        self.n = len(valeurs)
        self.valeurs = valeurs
        self.poids = poids
        self.capacite = capacite

        # Heuristique simple : ratio valeur/poids (avec protection division par zéro)
        self.heuristique = [ (v / p) if p > 0 else 0.0 for v, p in zip(valeurs, poids) ]

    def evaluer_solution(self, solution):
        """Retourne (valeur_totale, poids_total, est_valide) pour une solution binaire."""
        valeur_totale = sum(solution[i] * self.valeurs[i] for i in range(self.n))
        poids_total = sum(solution[i] * self.poids[i] for i in range(self.n))
        est_valide = (poids_total <= self.capacite)
        return valeur_totale, poids_total, est_valide


# ------------------------------
# Classe Fourmi
# ------------------------------
class Fourmi:
    def __init__(self, n):
        self.n = n
        self.reset()

    def reset(self):
        """Réinitialise l'état de la fourmi."""
        self.solution = [0] * self.n
        self.valeur = 0.0
        self.poids = 0.0
        self.est_valide = True

    def construire_solution(self, probleme, pheromones, alpha, beta, q0=0.0):
        """
        Construit une solution séquentiellement.
        q0 : probabilité d'exploitation (choisir le meilleur score local)
        """
        self.reset()
        objets_disponibles = list(range(probleme.n))

        while objets_disponibles:
            candidats = []
            scores = []

            for i in objets_disponibles:
                if self.poids + probleme.poids[i] <= probleme.capacite:
                    tau = pheromones[i] ** alpha  # influence phéromone
                    eta = (probleme.heuristique[i] ** beta) if probleme.heuristique[i] > 0 else 0.0
                    score = tau * eta
                    candidats.append(i)
                    scores.append(score)

            if not candidats:
                break


            if q0 > 0 and random.random() < q0:

                idx_max = max(range(len(scores)), key=lambda k: scores[k])
                choisi = candidats[idx_max]
            else:

                somme = sum(scores)
                if somme <= 0:
                    choisi = random.choice(candidats)
                else:

                    probs = [s / somme for s in scores]
                    choisi = random.choices(candidats, weights=probs, k=1)[0]


            self.solution[choisi] = 1
            self.poids += probleme.poids[choisi]

            # retirer l'objet de la liste disponible
            objets_disponibles.remove(choisi)

        # évaluer
        self.valeur, self.poids, self.est_valide = probleme.evaluer_solution(self.solution)



def aco_sac_a_dos(valeurs, poids, capacite,
                  nombre_fourmis=20, iterations=100,
                  alpha=1.0, beta=2.0, rho=0.1, Q=100.0,
                  q0=0.0, tau_min=0.01, tau_max=10.0,
                  afficher_progress=True):
    """
    Résout le problème du sac à dos avec ACO (version compacte, paramètres exposés).

    Paramètres importants :
    - q0 : probabilité d'exploitation (0 -> purement probabiliste)
    - tau_min / tau_max : bornes des phéromones
    - rho : taux d'évaporation (0 < rho < 1)
    """

    probleme = SacADos(valeurs, poids, capacite)
    n = probleme.n


    pheromones = [1.0 for _ in range(n)]

    meilleure_solution = None
    meilleure_valeur = 0.0


    for it in range(iterations):

        fourmis = [Fourmi(n) for _ in range(nombre_fourmis)]
        for f in fourmis:
            f.construire_solution(probleme, pheromones, alpha, beta, q0=q0)
            # mise à jour de la meilleure solution globale
            if f.est_valide and f.valeur > meilleure_valeur:
                meilleure_valeur = f.valeur
                meilleure_solution = f.solution.copy()


        pheromones = [p * (1.0 - rho) for p in pheromones]


        somme_valeurs = sum(probleme.valeurs) if sum(probleme.valeurs) != 0 else 1.0
        for f in fourmis:
            if f.est_valide and f.valeur > 0:
                delta = (Q * f.valeur) / somme_valeurs
                for i in range(n):
                    if f.solution[i] == 1:
                        pheromones[i] += delta


        if meilleure_solution is not None:
            delta_best = (Q * meilleure_valeur) / somme_valeurs
            for i in range(n):
                if meilleure_solution[i] == 1:
                    pheromones[i] += delta_best


        for i in range(n):
            if pheromones[i] < tau_min:
                pheromones[i] = tau_min
            elif pheromones[i] > tau_max:
                pheromones[i] = tau_max

        # affichage du progrès
        if afficher_progress and (it % 10 == 0 or it == iterations - 1):
            print(f"Itération {it+1:3d}/{iterations}: meilleure valeur = {meilleure_valeur:.1f}")

    return meilleure_solution, meilleure_valeur


# ------------------------------
# Fonction d'affichage propre
# ------------------------------
def afficher_solution(solution, valeurs, poids, capacite):
    if solution is None:
        print("Aucune solution valide trouvée.")
        return

    objets = [i for i, val in enumerate(solution) if val == 1]
    valeur_totale = sum(valeurs[i] for i in objets)
    poids_total = sum(poids[i] for i in objets)

    print("\n" + "=" * 60)
    print("=== SOLUTION TROUVÉE ===")
    print("=" * 60)
    if objets:
        print("Objets sélectionnés (ID, Valeur, Poids):")
        for i in objets:
            print(f"  - {i+1:2d} : valeur={valeurs[i]:.1f}, poids={poids[i]:.1f}")
    else:
        print("Aucun objet sélectionné.")
    print("-" * 60)
    print(f"Nombre objets: {len(objets)}")
    print(f"Valeur totale: {valeur_totale:.1f}")
    print(f"Poids total: {poids_total:.1f} / {capacite}")
    print(f"Taux d'utilisation: { (poids_total / capacite * 100) if capacite>0 else 0:.1f}%")
    print("=" * 60)


# ------------------------------
# Exemple d'utilisation (modèle)
# ------------------------------
if __name__ == "__main__":

    valeurs = [10, 5, 15, 7, 6, 18, 3, 12, 8, 14]
    poids =   [ 2, 3, 5, 7, 1, 4, 1, 6, 3, 8]
    capacite = 20

    # Paramètres ACO
    nombre_fourmis = 30
    iterations = 100
    alpha = 1.0
    beta = 2.0
    rho = 0.1
    Q = 100.0
    q0 = 0.05
    tau_min = 0.01
    tau_max = 20.0

    sol, val = aco_sac_a_dos(
        valeurs, poids, capacite,
        nombre_fourmis=nombre_fourmis,
        iterations=iterations,
        alpha=alpha, beta=beta,
        rho=rho, Q=Q,
        q0=q0, tau_min=tau_min, tau_max=tau_max,
        afficher_progress=True
    )

    afficher_solution(sol, valeurs, poids, capacite)
