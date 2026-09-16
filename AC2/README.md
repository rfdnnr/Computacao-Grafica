# AC02 - Transformacoes Geometricas

Exercicios de transformacoes geometricas em 2D feitos com numpy e matplotlib.
Cada exercicio esta em um arquivo separado e as funcoes de transformacao ficam
todas em `transformacoes.py`.

## Como rodar

```
pip install numpy matplotlib
python exercicio01_translacao.py
```

Cada script mostra os valores no terminal e abre o grafico com a figura antes e
depois da transformacao.

## Respostas

### Exercicio 1 - Translacao simples
P(2, 3) com vetor (4, -2) vira P'(6, 1).
As duas coordenadas mudaram: x somou 4 e y somou -2.

### Exercicio 2 - Escala uniforme
Com fator 2 o triangulo A(1,1), B(3,1), C(2,4) vira A'(2,2), B'(6,2), C'(4,8).
Os lados dobraram de tamanho e a area ficou 4 vezes maior, mas a forma continua
a mesma porque a escala foi igual nos dois eixos.

### Exercicio 3 - Escala nao uniforme
Com fator 2 em x e 0,5 em y: A'(2, 0.5), B'(6, 0.5), C'(4, 2).
O triangulo fica mais largo e mais achatado, entao a forma muda.

### Exercicio 4 - Rotacao em torno da origem
P(1, 0) rotacionado 90 graus no anti-horario vira P'(0, 1).

### Exercicio 5 - Rotacao de um poligono
Quadrado A(1,1), B(1,4), C(4,4), D(4,1) rotacionado 45 graus no sentido horario:

| Vertice | Original | Depois |
|---------|----------|--------|
| A | (1, 1) | (1.414, 0) |
| B | (1, 4) | (3.536, 2.121) |
| C | (4, 4) | (5.657, 0) |
| D | (4, 1) | (3.536, -2.121) |

### Exercicio 6 - Reflexao simples
P(2, 5) refletido no eixo y vira P'(-2, 5). So o x troca de sinal.

### Exercicio 7 - Reflexao de um triangulo
Refletindo A(2,3), B(4,3), C(3,5) no eixo x: A'(2,-3), B'(4,-3), C'(3,-5).

### Exercicio 8 - Cisalhamento horizontal
P(2, 3) com k = 2 vira P'(8, 3), porque x' = x + k * y = 2 + 2 * 3 = 8.

### Exercicio 9 - Composicao de transformacoes
Partindo de P(3, 2):

1. translacao (1, -1): (4, 1)
2. rotacao de 90 graus anti-horario: (-1, 4)
3. escala uniforme de fator 2: (-2, 8)

Resultado final: P'(-2, 8).

### Exercicio 10 - Combinacao de transformacoes em uma figura
Retangulo A(1,1), B(5,1), C(5,3), D(1,3):

1. translacao (-2, 3): (-1,4), (3,4), (3,6), (-1,6)
2. escala 1,5 em x e 0,5 em y: (-1.5,2), (4.5,2), (4.5,3), (-1.5,3)
3. reflexao no eixo y: (1.5,2), (-4.5,2), (-4.5,3), (1.5,3)

Coordenadas finais: A'(1.5, 2), B'(-4.5, 2), C'(-4.5, 3), D'(1.5, 3).
