# AC03 — Transformações Geométricas 2D e 3D

**Rafael Donner** — Computação Gráfica (IBMEC)
Cena: *Parque Geométrico*



## Texto de entrega

A cena "Parque Geométrico" tem três elementos 2D no plano XY (obj2d\_quadrado, obj2d\_triangulo, obj2d\_circulo) e três sólidos 3D (obj3d\_cubo, obj3d\_cilindro, obj3d\_esfera), todos na coleção AC03\_transformacoes. Nos objetos 2D apliquei escala de 0,8 em Y no quadrado, rotação de 180° em Z no triângulo e escala de 1,4 em X no círculo, que vira uma elipse. Nos sólidos, apliquei translação em Z até z = 1, rotação de 35° em Z no cubo e, no cilindro, rotação de 25° em Y com escala de 1,2 em Z. A esfera é filha do cilindro, então herda a rotação e a escala dele (transformação composta). A animação tem 120 frames a 24 fps: o quadrado translada em X de −4,5 para −3,0 e rotaciona 180° em Z, e o cubo escala de 1,0 para 1,9 em Z e rotaciona 360° em X, com keyframes nos frames 1 e 120. Por Python criei o triângulo, o cilindro e a esfera, com suas transformações, o parent e as cores. Manualmente, pela interface (G, R, S e I), fiz o quadrado, o círculo, o cubo, os keyframes, a câmera, a luz e o render.---

## Questões teóricas

### 1\. Diferença entre translação, rotação e escala

As três são transformações afins, representadas por matrizes 4×4 em coordenadas
homogêneas, o que permite compô-las por multiplicação de matrizes.

* **Translação**: soma um vetor constante às coordenadas de todos os pontos
(`x + tx`, `y + ty`, `z + tz`). Preserva forma, tamanho e orientação, muda só a
posição.
* **Rotação**: gira os pontos em torno de um eixo por um ângulo θ. Preserva forma e
tamanho (é uma transformação rígida), mas altera a orientação.
* **Escala**: multiplica as coordenadas por fatores (`sx`, `sy`, `sz`). Altera o
tamanho; se os fatores forem diferentes entre si (escala não uniforme), altera
também a proporção do objeto, foi o que transformou o círculo em elipse nesta cena.

### 2\. Espaço local vs. espaço global

No **espaço global** (ou *world space*) a transformação é feita em relação aos eixos
e à origem fixos do mundo. No **espaço local** ela é feita em relação aos eixos e à
origem do próprio objeto, que já carregam as rotações acumuladas dele.

A diferença só aparece quando o objeto já está rotacionado: um cubo girado 45° em Z
que translada 1 unidade no X *global* anda na horizontal do mundo, mas se transladar
1 unidade no X *local* anda na diagonal, seguindo o eixo inclinado dele. No Blender,
`G X` usa o eixo global e `G X X` usa o local. O mesmo vale para hierarquias: o
`obj3d\\\_esfera` desta cena tem coordenadas relativas ao `obj3d\\\_cilindro`, não ao mundo.

### 3\. Por que rotações em eixos diferentes geram resultados distintos

Porque **rotações 3D não são comutativas**: a composição é multiplicação de matrizes,
e `Rx · Ry ≠ Ry · Rx`. Girar 90° em X e depois 90° em Y leva a uma orientação final
diferente de girar 90° em Y e depois 90° em X, mesmo com os mesmos ângulos.

Ângulos de Euler aplicam as rotações numa ordem fixa (no Blender, XYZ por padrão), e
cada rotação seguinte age sobre eixos já girados pela anterior. Esse acoplamento é
também a origem do *gimbal lock*, quando dois eixos se alinham e se perde um grau de
Liberdade, motivo pelo qual quaternions são preferidos em animação mais complexa.

### 4\. Por que usar `math.radians()` no `rotation\\\_euler`

Porque a API do Blender armazena `rotation\\\_euler` **em radianos**, embora a interface
exiba os valores em graus. Escrever `cubo.rotation\\\_euler = (45, 0, 0)` não gera 45
graus e sim 45 *radianos*, o equivalente a cerca de 2578°, um resultado sem relação
com a intenção. `math.radians(45)` faz a conversão (≈ 0,7854) e mantém o script
legível, já que o ângulo continua escrito em graus no código.

### 5\. Quando vale mais a pena usar Python do que a interface

Quando a tarefa é **repetitiva, paramétrica ou precisa ser reproduzível**. Exemplo
prático: montar uma grade de 100 cubos com altura variando em função de um dataset e
rotação incremental de 3,6° por elemento. Na interface isso seria centenas de
operações manuais, sujeitas a erro de precisão e impossíveis de ajustar sem refazer
tudo; em Python são poucas linhas dentro de um laço, e mudar um parâmetro regenera a
cena inteira em segundos. O mesmo se aplica a esta AC: reposicionar a cena toda ou
ajustar o enquadramento da câmera exigiu apenas reexecutar o script.



