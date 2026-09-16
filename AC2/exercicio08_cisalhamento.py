# Exercicio 8 - Cisalhamento horizontal com k = 2 no ponto P(2, 3)

import numpy as np
from transformacoes import shear_x, plot_points

P = np.array([2, 3])
P_linha = shear_x(P, 2)

print("Ponto original:", P)
print("Ponto cisalhado:", P_linha)
print("O novo x e x + k * y = 2 + 2 * 3 = 8, e o y nao muda.")

plot_points(P, P_linha, "Exercicio 8 - Cisalhamento horizontal (k = 2)")
