# AC04 - Evolucao da Cena: Modelos de Iluminacao
# Rafael Donner - Computacao Grafica
#
# Abre a cena da AP1, cria os materiais MAT_Lambert, MAT_Phong e MAT_BlinnPhong,
# aplica um em cada objeto autoral, adiciona a luz principal e a de preenchimento
# e salva como AC04_RafaelDonner.blend (o arquivo da AP1 nao e alterado).
#
# Uso: blender -b AP1/AP1_RafaelDonner.blend --python AC04/AC04_RafaelDonner.py
# Variavel AC04_TESTE=1 faz so um render rapido, sem salvar.

import bpy
import math
import os
from mathutils import Vector

PASTA = os.path.dirname(os.path.abspath(__file__))
TESTE = os.environ.get("AC04_TESTE") == "1"
cena = bpy.context.scene

# --- Materiais -------------------------------------------------------------
# Aproximacoes no Principled BSDF: o que muda entre os tres e a rugosidade
# (tamanho do brilho) e o Specular IOR Level (intensidade do brilho).
MATERIAIS = {
    "MAT_Lambert":    {"cor": (0.55, 0.16, 0.07), "rugosidade": 1.0, "ior_level": 0.0},
    "MAT_Phong":      {"cor": (0.05, 0.32, 0.14), "rugosidade": 0.2, "ior_level": 0.5},
    "MAT_BlinnPhong": {"cor": (0.30, 0.12, 0.52), "rugosidade": 0.1, "ior_level": 1.0},
}

# objeto autoral da AP1 -> material
ATRIBUICAO = {
    "Obj_Livro_Conhecimento": "MAT_Lambert",
    "Obj_Escada_Construcao":  "MAT_Phong",
    "Obj_Portal_Futuro":      "MAT_BlinnPhong",
}

for nome, p in MATERIAIS.items():
    mat = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    mat.use_nodes = True
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (*p["cor"], 1.0)
    bsdf.inputs["Roughness"].default_value = p["rugosidade"]
    bsdf.inputs["Specular IOR Level"].default_value = p["ior_level"]
    bsdf.inputs["Metallic"].default_value = 0.0
    mat.diffuse_color = (*p["cor"], 1.0)  # cor no modo Solid
    mat.use_fake_user = True

for nome_obj, nome_mat in ATRIBUICAO.items():
    obj = bpy.data.objects[nome_obj]
    mat = bpy.data.materials[nome_mat]
    # o livro tinha dois slots (capa e paginas): todos recebem o mesmo material
    for slot in obj.material_slots:
        slot.material = mat

# --- Iluminacao ------------------------------------------------------------
raiz = bpy.data.collections["AP1_Ibmec_Conceito"]
col_luz = bpy.data.collections.get("05_Iluminacao") or bpy.data.collections.new("05_Iluminacao")
if col_luz.name not in raiz.children:
    raiz.children.link(col_luz)

ALVO = Vector((-1.0, 2.0, 1.2))  # centro aproximado dos tres objetos autorais


def criar_luz(nome, tipo, local, energia, tamanho, cor=(1, 1, 1)):
    luz = bpy.data.objects.get(nome)
    if luz is None:
        dados = bpy.data.lights.new(nome, tipo)
        luz = bpy.data.objects.new(nome, dados)
        col_luz.objects.link(luz)
    luz.data.energy = energia
    luz.data.color = cor
    luz.data.size = tamanho
    luz.location = local
    mirar(luz, ALVO)
    return luz


def mirar(obj, alvo):
    direcao = alvo - obj.location
    obj.rotation_euler = direcao.to_track_quat("-Z", "Y").to_euler()


# principal: frente-esquerda, perto da camera, para o reflexo aparecer no portal
LUZ_PRINCIPAL = dict(local=Vector((-5.0, -9.0, 7.0)), energia=1000, tamanho=3.0)
# preenchimento: grande e fraca, do lado direito, so para abrir as sombras
LUZ_PREENCHIMENTO = dict(local=Vector((9.0, -9.0, 4.0)), energia=300, tamanho=8.0)

principal = criar_luz("Luz_Principal", "AREA", LUZ_PRINCIPAL["local"],
                      LUZ_PRINCIPAL["energia"], LUZ_PRINCIPAL["tamanho"])
preench = criar_luz("Luz_Preenchimento", "AREA", LUZ_PREENCHIMENTO["local"],
                    LUZ_PREENCHIMENTO["energia"], LUZ_PREENCHIMENTO["tamanho"])

# --- Render ----------------------------------------------------------------
try:
    cena.render.engine = "BLENDER_EEVEE_NEXT"   # Blender 4.2 a 4.5
except TypeError:
    cena.render.engine = "BLENDER_EEVEE"        # Blender 5.x
cena.render.resolution_percentage = 50 if TESTE else 100
cena.eevee.taa_render_samples = 32 if TESTE else 128


def renderizar(caminho):
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


IMG = os.path.join(PASTA, "imagens")
if TESTE:
    renderizar(os.environ.get("AC04_SAIDA", os.path.join(IMG, "teste.png")))
    raise SystemExit

renderizar(os.path.join(IMG, "AC04_RafaelDonner_01_render_final.png"))

# Teste do angulo: gira a luz principal em torno do eixo Z que passa pelo
# alvo (mesma distancia, altura e intensidade) e depois restaura a posicao.
cena.render.resolution_percentage = 50
original = principal.location.copy()
for graus, nome in ((-90, "lateral_esquerda"), (180, "contraluz")):
    rel = original - ALVO
    ang = math.radians(graus)
    principal.location = ALVO + Vector((rel.x * math.cos(ang) - rel.y * math.sin(ang),
                                        rel.x * math.sin(ang) + rel.y * math.cos(ang),
                                        rel.z))
    mirar(principal, ALVO)
    renderizar(os.path.join(IMG, f"angulo_{nome}.png"))
principal.location = original
mirar(principal, ALVO)
cena.render.resolution_percentage = 100

bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PASTA, "AC04_RafaelDonner.blend"))
