# Exercicio 4 - Rotacao do ponto P(1, 0) em 90 graus anti-horario em torno da origem

import numpy as np
from transformacoes import rotate, plot_points

P = np.array([1, 0])
P_linha = rotate(P, 90)

print("Ponto original:", P)
print("Ponto rotacionado:", np.round(P_linha, 4))
print("O ponto saiu do eixo x e foi parar no eixo y, em (0, 1).")

plot_points(P, P_linha, "Exercicio 4 - Rotacao de 90 graus anti-horario")
