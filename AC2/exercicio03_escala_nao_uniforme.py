# Exercicio 3 - Escala nao uniforme (2 em x e 0.5 em y) no triangulo do exercicio 2

import numpy as np
from transformacoes import scale, plot_shapes

triangulo = np.array([[1, 1], [3, 1], [2, 4]])
triangulo_escalado = scale(triangulo, 2, 0.5)

print("Triangulo original:\n", triangulo)
print("Triangulo escalado:\n", triangulo_escalado)
print("O triangulo ficou mais largo e mais baixo, perdendo a forma original.")

plot_shapes(triangulo, triangulo_escalado, "Exercicio 3 - Escala nao uniforme (2 em x, 0.5 em y)")
