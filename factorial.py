#!/usr/bin/env python3
"""
Script Python pentru calcularea factorialei unui număr.
Factorial de n (n!) = 1 × 2 × ... × n

Author: Senior Software Engineer
"""


def factorial_iterative(n: int) -> int:
    """Calculează factorialul folosind o abordare iterativă."""
    if n < 0:
        raise ValueError("Factorialul este definit doar pentru numere întregi non-negative.")
    if n == 0 or n == 1:
        return 1
    
    result = 1
    for i in range(2, n + 1):
        result *= i
    
    return result


def factorial_recursive(n: int) -> int:
    """Calculează factorialul folosind recursivitate."""
    if n < 0:
        raise ValueError("Factorialul este definit doar pentru numere întregi non-negative.")
    
    # Caz de bază
    if n == 0 or n == 1:
        return 1
    
    # Apel recursiv
    return n * factorial_recursive(n - 1)


def factorial_formula(n: int) -> int:
    """Calculează factorialul folosind formula directă."""
    from math import prod
    
    if n < 0:
        raise ValueError("Factorialul este definit doar pentru numere întregi non-negative.")
    
    return prod(range(1, n + 1))


if __name__ == "__main__":
    # Calculăm factorialul de 5 cu toate metodele
    number = 5
    
    result_iterative = factorial_iterative(number)
    result_recursive = factorial_recursive(number)
    result_formula = factorial_formula(number)
    
    print(f"{'='*40}")
    print(f"Factorial de {number} (calculated)")
    print(f"{'='*40}")
    print(f"\nMetoda iterativă:   {factorial_iterative(number)}")
    print(f"Metoda recursivă:   {factorial_recursive(number)}")
    print(f"Metoda formula:     {factorial_formula(number)}")
    print(f"\n{'Resultat final:'}")
    print(f"{number}! = {result_iterative}")
    print(f"{'='*40}\n")
