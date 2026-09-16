# Exercicio 1 - Translacao simples do ponto P(2, 3) com vetor (4, -2)

import numpy as np
from transformacoes import translate, plot_points

P = np.array([2, 3])
P_linha = translate(P, [4, -2])

print("Ponto original:", P)
print("Ponto transladado:", P_linha)
print("As duas coordenadas mudaram: x de 2 para 6 e y de 3 para 1.")

plot_points(P, P_linha, "Exercicio 1 - Translacao de um ponto")
