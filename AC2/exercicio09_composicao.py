# Exercicio 9 - Composicao de transformacoes no ponto P(3, 2)
# 1) translacao (1, -1)  2) rotacao de 90 graus anti-horario  3) escala uniforme de fator 2

import numpy as np
import matplotlib.pyplot as plt
from transformacoes import translate, rotate, scale

P = np.array([3, 2])
P1 = translate(P, [1, -1])
P2 = rotate(P1, 90)
P3 = scale(P2, 2, 2)

print("Ponto original:", P)
print("Depois da translacao:", P1)
print("Depois da rotacao:", np.round(P2, 4))
print("Depois da escala:", np.round(P3, 4))

plt.figure()
plt.scatter(P[0], P[1], label="Original")
plt.scatter(P1[0], P1[1], label="Transladado", marker="x")
plt.scatter(P2[0], P2[1], label="Rotacionado", marker="^")
plt.scatter(P3[0], P3[1], label="Escalado", marker="s")
plt.title("Exercicio 9 - Composicao de transformacoes")
plt.legend()
plt.grid(True)
plt.axhline(0, color="black", linewidth=0.5)
plt.axvline(0, color="black", linewidth=0.5)
plt.axis("equal")
plt.show()
