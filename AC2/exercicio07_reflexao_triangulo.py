# Exercicio 7 - Reflexao do triangulo A(2,3), B(4,3), C(3,5) em relacao ao eixo x

import numpy as np
from transformacoes import reflect_x, plot_shapes

triangulo = np.array([[2, 3], [4, 3], [3, 5]])
triangulo_refletido = reflect_x(triangulo)

print("Triangulo original:\n", triangulo)
print("Triangulo refletido:\n", triangulo_refletido)
print("Todos os y trocaram de sinal, o triangulo foi para baixo do eixo x.")

plot_shapes(triangulo, triangulo_refletido, "Exercicio 7 - Reflexao no eixo x")
