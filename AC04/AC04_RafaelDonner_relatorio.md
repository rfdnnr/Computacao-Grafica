# AC04 — Evolução da Cena: Modelos de Iluminação

**Nome:** Rafael Senra Donner Jorge
**Software:** Blender 4.5 LTS (4.5.14), render em Eevee
**Arquivo:** `AC04_RafaelDonner.blend`, cópia da `AP1_RafaelDonner.blend` (o arquivo da AP1 não foi alterado)

A cena, a câmera, a composição e a palavra Ibmec são as da AP1. Os testes foram feitos só nos três objetos autorais. O script `AC04_RafaelDonner.py` documenta tudo o que foi feito sobre a cena da AP1: materiais, luzes, renders e o teste de ângulo.

---

## 1. Objetos e materiais

| Objeto autoral (AP1) | Material | Motivo da escolha |
|---|---|---|
| `Obj_Livro_Conhecimento` | `MAT_Lambert` | papel e capa de tecido são superfícies foscas |
| `Obj_Escada_Construcao` | `MAT_Phong` | placas de acrílico polido |
| `Obj_Portal_Futuro` | `MAT_BlinnPhong` | moldura grande e lisa, onde o reflexo da luz aparece melhor |

O livro tinha dois slots de material (capa e páginas) e os dois receberam `MAT_Lambert`. A palavra Ibmec (`MAT_Ibmec_Azul` e `MAT_Ibmec_Amarelo`), o pedestal e o chão ficaram exatamente como na AP1.

## 2. Valores dos materiais

Os três usam o Principled BSDF, com Metallic 0 e IOR 1,5.

| Material | Base Color (sRGB) | Roughness | Specular IOR Level |
|---|---|---|---|
| `MAT_Lambert` | `#C46F4B` (terracota) | 1,0 | 0,0 |
| `MAT_Phong` | `#3F9969` (verde) | 0,2 | 0,5 |
| `MAT_BlinnPhong` | `#9561BF` (roxo) | 0,1 | 1,0 |

No Blender 4.5 o nó mostra **Specular IOR Level** no lugar do antigo Specular. O valor 0,5 é o padrão (sem ajuste), 0,0 remove a camada especular e 1,0 dobra a reflexão na incidência normal. Com IOR Level 0,0 o `MAT_Lambert` fica só com a componente difusa, e como a Diffuse Roughness está em 0 essa componente é a de Lambert.

Os materiais aparecem no Outliner em *Blender File › Materials*, com o prefixo `MAT_` e fake user ativado. As luzes ficam na coleção `05_Iluminacao`, criada dentro de `AP1_Ibmec_Conceito`.

## 3. Iluminação

| | Luz principal | Luz de preenchimento |
|---|---|---|
| Nome | `Luz_Principal` | `Luz_Preenchimento` |
| Tipo | Area quadrada, 3 m | Area quadrada, 8 m |
| Potência e cor | 1000 W, branca | 300 W, branca |
| Posição | (−5; −9; 7) | (9; −9; 4) |
| Rotação | (63,6°; 0°; −20°) | (79,3°; 0°; 42,3°) |

As duas miram o ponto (−1; 2; 1,2), o centro aproximado dos três objetos. A principal fica à frente, à esquerda e acima da câmera. Nessa posição ela ilumina o livro e a escada com sombras visíveis atrás deles, e o reflexo dela cai na parte de cima, à esquerda, da face frontal do portal. A de preenchimento é grande e fraca e só clareia as sombras do lado direito.

O mundo (cinza 0,05) e a câmera `Cam_Principal_AP1` são os da AP1, e a transformação de cor continua em *Standard*. Render em Eevee, 128 amostras, 1920 × 1080. Luz, câmera e mundo ficaram iguais em todas as imagens de comparação, exceto no teste de ângulo descrito abaixo.

## 4. Comparação observada

**Mesma iluminação** (`AC04_RafaelDonner_02_comparacao_materiais.png`, recortes do render final):

- **Lambert (livro):** totalmente fosco. A cor só muda com a inclinação da face em relação à luz: o topo das páginas é mais claro e as laterais mais escuras, sem nenhum ponto de brilho. É o que diz o modelo, I = k_d · máx(0, N·L): o resultado depende da normal e da luz, não da posição da câmera.
- **Phong (escada):** o corpo das placas tem o mesmo sombreado difuso, e as bordas chanfradas de cima ganham um brilho claro e espalhado, onde a normal se aproxima da direção que reflete a luz para a câmera. O brilho é suave porque a rugosidade 0,2 alarga o lobo especular.
- **Blinn-Phong (portal):** highlight branco, pequeno e intenso na parte de cima, à esquerda, da moldura, com transição curta para a cor-base. É o reflexo da luz Area na face lisa: a rugosidade 0,1 estreita o lobo e o IOR Level 1,0 dobra a intensidade.

**Ângulo da luz** (`AC04_RafaelDonner_03_angulo_da_luz.png`): a luz principal foi girada em torno do eixo Z que passa pelo alvo, com a mesma distância, altura e potência.

- **−90° (lateral esquerda):** o reflexo some da face frontal do portal e sobra só um fio na borda esquerda. O portal e as letras escurecem, porque a luz passa a bater rasante na frente deles. No livro e na escada muda só o sombreado: topo claro, frente escura. Isso mostra que o especular depende da direção de observação (V) e o difuso depende só de L e N.
- **180° (contraluz):** as faces voltadas para a câmera escurecem e o brilho especular aparece apenas como fios nas bordas de cima do portal e das letras (efeito *rim light*). O livro continua sem brilho em todos os ângulos.

Depois do teste a luz voltou à posição de 0°, que é a salva no arquivo e a usada no render final.

## 5. Limitação: aproximações, não as equações clássicas

No Phong clássico, I = k_a + k_d(N·L) + k_s(R·V)^n. O Blinn-Phong troca R·V por N·H, com H = (L + V)/|L + V|. O Principled BSDF não implementa nenhuma das duas. Ele é um modelo físico de microfacetas (GGX), com Fresnel e conservação de energia. A Roughness cumpre um papel parecido com o do expoente n (menor rugosidade, brilho mais estreito) e o Specular IOR Level um papel parecido com o de k_s, mas não existe conversão exata entre esses números, nem um parâmetro que escolha entre R·V e N·H.

Por isso `MAT_Phong` e `MAT_BlinnPhong` são aproximações visuais: o que os diferencia nesta cena é só a rugosidade e a intensidade especular. Nas equações clássicas, com o mesmo expoente, o Blinn-Phong produz um brilho **mais largo** que o Phong (precisa de um expoente cerca de 4 vezes maior para ficar parecido). A diferença de nitidez vista na cena vem dos valores escolhidos, não da fórmula. O Lambert é o caso mais fiel, porque com IOR Level 0 sobra só a componente difusa, equivalente ao nó Diffuse BSDF.

## 6. Arquivos entregues

- `AC04_RafaelDonner.blend`: cena da AP1 com os três materiais e as luzes
- `imagens/AC04_RafaelDonner_01_render_final.png`: render final, com a palavra Ibmec e os três objetos
- `imagens/AC04_RafaelDonner_02_comparacao_materiais.png`: os três materiais sob a mesma luz
- `imagens/AC04_RafaelDonner_03_angulo_da_luz.png`: teste de ângulo da luz principal
- `AC04_RafaelDonner.py`: script com as alterações feitas sobre a cena da AP1
