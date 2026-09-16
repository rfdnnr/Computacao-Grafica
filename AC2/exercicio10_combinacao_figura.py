# Exercicio 10 - Combinacao de transformacoes no retangulo A(1,1), B(5,1), C(5,3), D(1,3)
# 1) translacao (-2, 3)  2) escala nao uniforme (1.5 em x, 0.5 em y)  3) reflexao no eixo y

import numpy as np
import matplotlib.pyplot as plt
from transformacoes import translate, scale, reflect_y

retangulo = np.array([[1, 1], [5, 1], [5, 3], [1, 3]])
passo1 = translate(retangulo, [-2, 3])
passo2 = scale(passo1, 1.5, 0.5)
passo3 = reflect_y(passo2)

print("Retangulo original:\n", retangulo)
print("Depois da translacao:\n", passo1)
print("Depois da escala:\n", passo2)
print("Depois da reflexao:\n", passo3)

plt.figure()
plt.plot(*zip(*retangulo, retangulo[0]), label="Original")
plt.plot(*zip(*passo1, passo1[0]), label="Transladado", linestyle="--")
plt.plot(*zip(*passo2, passo2[0]), label="Escalado", linestyle="-.")
plt.plot(*zip(*passo3, passo3[0]), label="Refletido", linestyle=":")
plt.title("Exercicio 10 - Combinacao de transformacoes")
plt.legend()
plt.grid(True)
plt.axhline(0, color="black", linewidth=0.5)
plt.axvline(0, color="black", linewidth=0.5)
plt.axis("equal")
plt.show()
