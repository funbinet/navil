"""Simple genetic algorithm operations for payload evolution."""

from __future__ import annotations

import random
from collections.abc import Callable
from typing import cast


def crossover(parent_a: str, parent_b: str) -> str:
    if not parent_a or not parent_b:
        return parent_a or parent_b
    split_a = random.randint(0, len(parent_a) - 1)
    split_b = random.randint(0, len(parent_b) - 1)
    return parent_a[:split_a] + parent_b[split_b:]


def mutate(payload: str, mutation_rate: float = 0.25) -> str:
    if random.random() > mutation_rate or not payload:
        return payload
    mutations: list[Callable[[str], str]] = [
        lambda value: value + random.choice(["%00", "#", "/*x*/"]),
        lambda value: value.replace(" ", random.choice(["+", "%20", "/**/"])),
        lambda value: value[::-1],
        lambda value: value + random.choice(["--", ";", "\\n"]),
    ]
    mutation = random.choice(mutations)
    return cast(str, mutation(payload))


def evolve(population: list[str], fitness: dict[str, float], rounds: int = 1) -> list[str]:
    if not population:
        return []

    current = population[:]
    for _ in range(rounds):
        current.sort(key=lambda payload: fitness.get(payload, 0.0), reverse=True)
        elites = current[: max(2, len(current) // 4)]
        next_generation = elites[:]
        while len(next_generation) < len(current):
            parent_a = random.choice(elites)
            parent_b = random.choice(elites)
            child = mutate(crossover(parent_a, parent_b))
            next_generation.append(child)
        current = next_generation
    return current
