import random

SPANISH_NAMES = frozenset([
    "José",
    "Paco",
    "María",
    "Julia",
    "Miguel",
    "Rogelio",
    "Pedro",
    "Rafa",
    "Carmen",
    "Rosa",
    "Santiago",
    "Susana"
])


def two_random_names():
    return random.sample(SPANISH_NAMES, 2)
