# AC03 - Transformacoes Geometricas 2D e 3D
# Rafael Donner - Computacao Grafica
#
# Parte em Python da atividade: cria o triangulo (2D), o cilindro (3D)
# e a esfera UV (3D), aplicando transformacoes em cada um.
# Rodar com a colecao AC03_transformacoes selecionada no Outliner,
# assim os objetos ja sao criados dentro dela.

import bpy
import math

# Triangulo (2D): circulo com so 3 vertices, no plano XY
bpy.ops.mesh.primitive_circle_add(vertices=3, radius=1.3, fill_type='NGON', location=(0, -2, 0))
triangulo = bpy.context.active_object
triangulo.name = "obj2d_triangulo"
# rotacao de 180 graus no eixo Z (inverte o sentido da ponta)
triangulo.rotation_euler = (0, 0, math.radians(180))

# Cilindro (3D)
bpy.ops.mesh.primitive_cylinder_add(radius=0.7, depth=2, location=(0, 2, 1))
cilindro = bpy.context.active_object
cilindro.name = "obj3d_cilindro"
cilindro.rotation_euler = (0, math.radians(25), 0)  # inclina 25 graus no eixo Y
cilindro.scale = (1, 1, 1.2)  # estica no eixo Z

# Esfera UV (3D) - bonus: esfera filha do cilindro
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.8)
esfera = bpy.context.active_object
esfera.name = "obj3d_esfera"
esfera.parent = cilindro
# essa location e no espaco local do cilindro, entao a esfera fica ao lado dele
esfera.location = (2.4, 0, 0)
# como e filha, a esfera herda a rotacao e a escala do cilindro
# (fica inclinada junto com ele e um pouco esticada em Z)

# Cores dos tres objetos criados acima
cores = {
    triangulo: (0.95, 0.70, 0.15, 1),
    cilindro: (0.60, 0.35, 0.80, 1),
    esfera: (0.90, 0.45, 0.55, 1),
}

for obj, cor in cores.items():
    material = bpy.data.materials.new("mat_" + obj.name)
    material.use_nodes = True
    material.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = cor
    obj.data.materials.append(material)
