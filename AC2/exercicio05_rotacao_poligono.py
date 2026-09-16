# Exercicio 5 - Rotacao de 45 graus no sentido horario no quadrado A(1,1), B(1,4), C(4,4), D(4,1)

import numpy as np
from transformacoes import rotate, plot_shapes

quadrado = np.array([[1, 1], [1, 4], [4, 4], [4, 1]])
# angulo negativo porque a rotacao e no sentido horario
quadrado_rotacionado = rotate(quadrado, -45)

print("Quadrado original:\n", quadrado)
print("Quadrado rotacionado:\n", np.round(quadrado_rotacionado, 4))

plot_shapes(quadrado, quadrado_rotacionado, "Exercicio 5 - Rotacao de 45 graus horario")
