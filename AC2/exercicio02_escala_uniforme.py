# Exercicio 2 - Escala uniforme de fator 2 no triangulo A(1,1), B(3,1), C(2,4)

import numpy as np
from transformacoes import scale, plot_shapes

triangulo = np.array([[1, 1], [3, 1], [2, 4]])
triangulo_escalado = scale(triangulo, 2, 2)

print("Triangulo original:\n", triangulo)
print("Triangulo escalado:\n", triangulo_escalado)
print("O triangulo dobrou de tamanho em x e em y, entao a area ficou 4 vezes maior.")

plot_shapes(triangulo, triangulo_escalado, "Exercicio 2 - Escala uniforme (fator 2)")
