# Exercicio 6 - Reflexao do ponto P(2, 5) em relacao ao eixo y

import numpy as np
from transformacoes import reflect_y, plot_points

P = np.array([2, 5])
P_linha = reflect_y(P)

print("Ponto original:", P)
print("Ponto refletido:", P_linha)
print("So o x trocou de sinal, o y continua igual.")

plot_points(P, P_linha, "Exercicio 6 - Reflexao no eixo y")
