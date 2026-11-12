# AC05 - Evolucao da Cena: Materiais PBR e Texturas
# Rafael Donner - Computacao Grafica
#
# Abre a cena da AC04, troca os materiais da comparacao (Lambert, Phong e
# Blinn-Phong) por materiais PBR no Principled BSDF, cria os UVs dos objetos
# texturizados, liga os mapas de imagem, empacota as texturas no .blend e salva
# como AC05_RafaelDonner.blend (os arquivos da AP1 e da AC04 nao sao alterados).
#
#   Obj_Escada_Construcao  -> MAT_Madeira_Carvalho_PBR (Base Color + Roughness + Normal)
#   Obj_Livro_Conhecimento -> MAT_Bronze_Escovado (paginas) e MAT_Bronze_Patinado (capa)
#   Obj_Portal_Futuro      -> MAT_Espelho_Polido (cor solida, sem textura)
#
# Uso: blender -b --factory-startup AC04/AC04_RafaelDonner.blend --python AC05/AC05_RafaelDonner.py
# Teste rapido (nao salva): AC05_TESTE=1 AC05_SAIDA=/caminho/teste.png AC05_RES=50 AC05_AMOSTRAS=64
#   AC05_MUNDO=AC04         mundo cinza da AC04, sem ajuste (comparacao 1)
#   AC05_MUNDO=HDRI_GLOSSY  HDRI no mundo so para reflexos (comparacao 2, descartado)
#   AC05_MUNDO=REFLEXO      cupula com Light Linking (padrao, versao final)

import bpy
import bmesh
import math
import os
from mathutils import Matrix, Vector

PASTA = os.path.dirname(os.path.abspath(__file__))
TEX = os.path.join(PASTA, "texturas")
IMG = os.path.join(PASTA, "imagens")
TESTE = os.environ.get("AC05_TESTE") == "1"
MUNDO = os.environ.get("AC05_MUNDO", "REFLEXO")
cena = bpy.context.scene


def linear(hex_srgb):
    """#RRGGBB (sRGB) -> RGBA linear, que e o que o Principled BSDF recebe."""
    h = hex_srgb.lstrip("#")
    canais = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255
        canais.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (*canais, 1.0)


# --- Imagens ---------------------------------------------------------------
# Cor e interpretada como sRGB; rugosidade e normal sao DADOS (Non-Color).
def imagem(arquivo, espaco):
    img = bpy.data.images.load(os.path.join(TEX, arquivo), check_existing=True)
    img.colorspace_settings.name = espaco
    return img


# --- Materiais ---------------------------------------------------------------
def material_novo(nome, cor_viewport, metalico, rugosidade):
    mat = bpy.data.materials.get(nome) or bpy.data.materials.new(nome)
    mat.use_nodes = True
    nos = mat.node_tree.nodes
    nos.clear()
    saida = nos.new("ShaderNodeOutputMaterial")
    saida.location = (320, 160)
    bsdf = nos.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (-40, 160)
    mat.node_tree.links.new(bsdf.outputs["BSDF"], saida.inputs["Surface"])
    # cores do modo Solid
    mat.diffuse_color = cor_viewport
    mat.metallic = metalico
    mat.roughness = rugosidade
    return mat, bsdf


def no(mat, tipo, x, y, rotulo=None):
    n = mat.node_tree.nodes.new(tipo)
    n.location = (x, y)
    if rotulo:
        n.label = rotulo
    return n


def ligar(mat, saida, entrada):
    mat.node_tree.links.new(saida, entrada)


def coordenadas_uv(mat, escala, x=-1260, y=120):
    """Texture Coordinate (UV) -> Mapping. A escala uniforme ajusta o tamanho real."""
    coord = no(mat, "ShaderNodeTexCoord", x, y)
    mapa = no(mat, "ShaderNodeMapping", x + 200, y)
    mapa.vector_type = "POINT"
    mapa.inputs["Scale"].default_value = (escala, escala, 1.0)
    ligar(mat, coord.outputs["UV"], mapa.inputs["Vector"])
    return mapa


def textura(mat, img, rotulo, x, y, vetor):
    t = no(mat, "ShaderNodeTexImage", x, y, rotulo)
    t.image = img
    t.width = 260
    ligar(mat, vetor, t.inputs["Vector"])
    return t


def mapa_normal(mat, cor, bsdf, forca, x, y):
    """Normal tangente: Image (Non-Color) -> Normal Map -> Normal do Principled."""
    nm = no(mat, "ShaderNodeNormalMap", x, y)
    nm.space = "TANGENT"
    nm.uv_map = "UVMap"
    nm.inputs["Strength"].default_value = forca
    ligar(mat, cor, nm.inputs["Color"])
    ligar(mat, nm.outputs["Normal"], bsdf.inputs["Normal"])
    return nm


def moldura(mat, rotulo, filhos):
    f = no(mat, "NodeFrame", 0, 0, rotulo)
    f.label_size = 16
    for n in filhos:
        n.parent = f
    return f


# Madeira de carvalho (escada): os tres canais vindos das imagens do Poly Haven.
def mat_madeira(escala):
    mat, bsdf = material_novo("MAT_Madeira_Carvalho_PBR", linear("#A1784F"), 0.0, 0.53)
    vet = coordenadas_uv(mat, escala).outputs["Vector"]
    cor = textura(mat, imagem("oak_veneer_01_diff_1k.jpg", "sRGB"), "Base Color (sRGB)", -760, 400, vet)
    rug = textura(mat, imagem("oak_veneer_01_rough_1k.jpg", "Non-Color"), "Roughness (Non-Color)", -760, 90, vet)
    nor = textura(mat, imagem("oak_veneer_01_nor_gl_1k.jpg", "Non-Color"), "Normal (Non-Color)", -760, -220, vet)
    ligar(mat, cor.outputs["Color"], bsdf.inputs["Base Color"])
    ligar(mat, rug.outputs["Color"], bsdf.inputs["Roughness"])
    mapa_normal(mat, nor.outputs["Color"], bsdf, 1.0, -400, -260)
    moldura(mat, "oak_veneer_01 - Poly Haven (CC0)", (cor, rug, nor))
    bsdf.inputs["Metallic"].default_value = 0.0      # madeira e dieletrico
    bsdf.inputs["IOR"].default_value = 1.5
    return mat


# Bronze (livro): cor solida de bronze + mapas de DADOS do Metal009 (escovado).
# O mapa de cor do Metal009 e de aco (cinza), por isso nao e usado aqui.
def mat_bronze(nome, cor_hex, rug_min, rug_max, escala, forca_normal):
    cor = linear(cor_hex)
    mat, bsdf = material_novo(nome, cor, 1.0, (rug_min + rug_max) / 2)
    vet = coordenadas_uv(mat, escala).outputs["Vector"]
    rug = textura(mat, imagem("Metal009_1K-JPG_Roughness.jpg", "Non-Color"), "Roughness (Non-Color)", -760, 230, vet)
    nor = textura(mat, imagem("Metal009_1K-JPG_NormalGL.jpg", "Non-Color"), "Normal (Non-Color)", -760, -100, vet)
    # o mapa vai de ~0,32 a ~0,68; o Map Range leva essa faixa para a rugosidade desejada
    faixa = no(mat, "ShaderNodeMapRange", -400, 260, "Faixa da rugosidade")
    faixa.inputs["From Min"].default_value = 0.32
    faixa.inputs["From Max"].default_value = 0.68
    faixa.inputs["To Min"].default_value = rug_min
    faixa.inputs["To Max"].default_value = rug_max
    ligar(mat, rug.outputs["Color"], faixa.inputs["Value"])
    ligar(mat, faixa.outputs["Result"], bsdf.inputs["Roughness"])
    mapa_normal(mat, nor.outputs["Color"], bsdf, forca_normal, -400, -140)
    moldura(mat, "Metal009 - ambientCG (CC0)", (rug, nor))
    bsdf.inputs["Base Color"].default_value = cor
    bsdf.inputs["Metallic"].default_value = 1.0
    return mat


# Espelho (portal): metal com rugosidade quase zero, sem textura.
def mat_espelho():
    cor = linear("#F2F2F2")
    mat, bsdf = material_novo("MAT_Espelho_Polido", cor, 1.0, 0.02)
    bsdf.inputs["Base Color"].default_value = cor
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.02
    return mat


# Palavra Ibmec: mesmas cores do SVG oficial, PBR acetinado, sem textura nem relevo.
def atualizar_ibmec():
    for nome, hexa, rug in (("MAT_Ibmec_Azul", "#002555", 0.4), ("MAT_Ibmec_Amarelo", "#F5AC00", 0.35)):
        mat = bpy.data.materials[nome]
        bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = linear(hexa)
        bsdf.inputs["Metallic"].default_value = 0.0
        bsdf.inputs["Roughness"].default_value = rug
        bsdf.inputs["Specular IOR Level"].default_value = 0.5
        mat.diffuse_color = linear(hexa)


# --- UV ----------------------------------------------------------------------
def modo_edicao(obj):
    if bpy.context.object and bpy.context.object.mode != "OBJECT":
        bpy.ops.object.mode_set(mode="OBJECT")
    for o in bpy.context.selected_objects:
        o.select_set(False)
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action="SELECT")


def modo_objeto():
    bpy.ops.object.mode_set(mode="OBJECT")


def girar_uv(obj, graus):
    c, s = math.cos(math.radians(graus)), math.sin(math.radians(graus))
    for d in obj.data.uv_layers.active.data:
        u, v = d.uv
        d.uv = (c * u - s * v, s * u + c * v)


def empacotar(obj, margem=0.03):
    """Pack Islands sem girar: as ilhas nao se sobrepoem e mantem a orientacao."""
    modo_edicao(obj)
    cena.tool_settings.use_uv_select_sync = True
    bpy.ops.uv.pack_islands(rotate=False, scale=True, margin_method="FRACTION", margin=margem)
    cena.tool_settings.use_uv_select_sync = False
    modo_objeto()


def ilhas(bm):
    """Faces ligadas por arestas que nao sao costura (seam) formam uma ilha."""
    resto, grupos = set(bm.faces), []
    while resto:
        pilha = [resto.pop()]
        grupo = list(pilha)
        while pilha:
            for e in pilha.pop().edges:
                if e.seam:
                    continue
                for g in e.link_faces:
                    if g in resto:
                        resto.remove(g)
                        pilha.append(g)
                        grupo.append(g)
        grupos.append(grupo)
    return grupos


def alinhar_ilhas(obj):
    """Gira cada ilha para que o eixo X do objeto (ou Y, se a ilha nao tem
    extensao em X) fique na direcao U: o escovado do Metal009 e horizontal na
    imagem e deve correr ao longo do comprimento do livro."""
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    uv = bm.loops.layers.uv.active
    for grupo in ilhas(bm):
        for eixo in (0, 1):
            direcao = Vector((0.0, 0.0))
            for f in grupo:
                for l in f.loops:
                    d3 = l.link_loop_next.vert.co[eixo] - l.vert.co[eixo]
                    direcao += (l.link_loop_next[uv].uv - l[uv].uv) * d3
            if direcao.length > 1e-6:
                break
        giro = Matrix.Rotation(-math.atan2(direcao.y, direcao.x), 2)
        loops = [l for f in grupo for l in f.loops]
        centro = sum((l[uv].uv for l in loops), Vector((0.0, 0.0))) / len(loops)
        for l in loops:
            l[uv].uv = giro @ (l[uv].uv - centro) + centro
    bm.to_mesh(obj.data)
    bm.free()


def uv_por_metro(obj, materiais=None):
    """Densidade media (unidades UV por metro), para acertar a escala real da textura."""
    dados = obj.data.uv_layers.active.data
    area_3d = area_uv = 0.0
    for p in obj.data.polygons:
        if materiais is not None and p.material_index not in materiais:
            continue
        pts = [dados[i].uv for i in p.loop_indices]
        area_3d += p.area
        area_uv += abs(sum(pts[i].x * pts[i - 1].y - pts[i - 1].x * pts[i].y for i in range(len(pts)))) / 2
    return math.sqrt(area_uv / area_3d)


def distorcao(obj, faces):
    """Esticamento por face: razao area UV / area 3D comparada com a media.
    1,00 = sem distorcao. Devolve (pior desvio, desvio medio) em %."""
    dados = obj.data.uv_layers.active.data
    razoes = []
    for i in faces:
        p = obj.data.polygons[i]
        pts = [dados[k].uv for k in p.loop_indices]
        a_uv = abs(sum(pts[k].x * pts[k - 1].y - pts[k - 1].x * pts[k].y for k in range(len(pts)))) / 2
        razoes.append(a_uv / p.area)
    media = sum(razoes) / len(razoes)
    desvios = [abs(r / media - 1) * 100 for r in razoes]
    return max(desvios), sum(desvios) / len(desvios)


def uv_escada(obj):
    """Degrau = caixa: Cube Projection. Depois gira 90 graus para o comprimento
    da tabua (X) seguir o veio, que e vertical na imagem, e empacota."""
    modo_edicao(obj)
    bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)
    modo_objeto()
    girar_uv(obj, 90)
    empacotar(obj)


PAGINAS_TOPO = range(11, 21)   # faces curvas do bloco de paginas (malha da metade direita)


def uv_livro(obj):
    """Livro: costuras nas arestas vivas (> 30 graus) + Unwrap (Angle Based).
    Antes, mede a distorcao que a Cube Projection deixaria nas paginas curvas."""
    modo_edicao(obj)
    bpy.ops.uv.cube_project(cube_size=1.0, correct_aspect=True, clip_to_bounds=False, scale_to_bounds=False)
    modo_objeto()
    antes = distorcao(obj, PAGINAS_TOPO)

    modo_edicao(obj)
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.mesh.select_mode(type="EDGE")
    bpy.ops.mesh.edges_select_sharp(sharpness=math.radians(30))
    bpy.ops.mesh.mark_seam(clear=False)
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", fill_holes=True, correct_aspect=True, margin=0.03)
    modo_objeto()
    alinhar_ilhas(obj)
    empacotar(obj)
    depois = distorcao(obj, PAGINAS_TOPO)
    print(f"[AC05] distorcao das paginas curvas: Cube Projection pior {antes[0]:.1f}% "
          f"(media {antes[1]:.1f}%) -> Unwrap pior {depois[0]:.1f}% (media {depois[1]:.1f}%)")
    return antes, depois


# --- Sombreamento --------------------------------------------------------------
def suavizar(obj):
    """Smooth by Angle (30 graus) + Harden Normals no Bevel: os chanfros e as
    paginas curvas refletem sem facetas, e as faces planas continuam planas."""
    modo_edicao(obj)
    modo_objeto()
    bpy.ops.object.shade_smooth_by_angle(angle=math.radians(30), keep_sharp_edges=True)
    for m in obj.modifiers:
        if m.type == "BEVEL":
            m.harden_normals = True


# --- Ambiente de reflexo ---------------------------------------------------------
def cupula_reflexo(forca, giro_graus):
    """Com o mundo cinza uniforme da AC04, o espelho reflete o mesmo cinza do
    fundo e some. Esta cupula (esfera de 60 m com o HDRI de estudio que vem com
    o Blender) da ao metal e ao espelho algo para refletir:
    - invisivel para a camera, para raios difusos e para sombras: so aparece
      em reflexos;
    - Light Linking: so o livro e o portal recebem a emissao dela. O chao, as
      letras e a madeira nao a enxergam, e a luz deles continua a da AC04."""
    raiz = bpy.data.collections["AP1_Ibmec_Conceito"]
    col = bpy.data.collections.get("AC05_Materiais_Texturas") or bpy.data.collections.new("AC05_Materiais_Texturas")
    if col.name not in raiz.children:
        raiz.children.link(col)

    malha = bpy.data.meshes.new("Aux_Cupula_Reflexo")
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=64, v_segments=32, radius=60.0)
    bmesh.ops.reverse_faces(bm, faces=bm.faces)      # normais para dentro
    bm.to_mesh(malha)
    bm.free()
    for p in malha.polygons:
        p.use_smooth = True
    cupula = bpy.data.objects.new("Aux_Cupula_Reflexo", malha)
    col.objects.link(cupula)
    cupula.visible_camera = False
    cupula.visible_diffuse = False
    cupula.visible_transmission = False
    cupula.visible_volume_scatter = False
    cupula.visible_shadow = False
    cupula.hide_select = True

    mat = bpy.data.materials.new("MAT_Aux_Ambiente_Reflexo")
    mat.use_nodes = True
    nos = mat.node_tree.nodes
    nos.clear()
    saida = no(mat, "ShaderNodeOutputMaterial", 300, 0)
    emis = no(mat, "ShaderNodeEmission", 80, 0)
    emis.inputs["Strength"].default_value = forca
    hdri = no(mat, "ShaderNodeTexEnvironment", -260, 0, "studio.exr (Blender / Poly Haven, CC0)")
    hdri.image = bpy.data.images.load(os.path.join(TEX, "studio_blender.exr"), check_existing=True)
    mapa = no(mat, "ShaderNodeMapping", -460, 0)
    mapa.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(giro_graus))
    coord = no(mat, "ShaderNodeTexCoord", -660, 0)
    # coordenada Object = direcao a partir do centro da esfera
    ligar(mat, coord.outputs["Object"], mapa.inputs["Vector"])
    ligar(mat, mapa.outputs["Vector"], hdri.inputs["Vector"])
    ligar(mat, hdri.outputs["Color"], emis.inputs["Color"])
    ligar(mat, emis.outputs["Emission"], saida.inputs["Surface"])
    mat.diffuse_color = (0.8, 0.8, 0.8, 0.05)
    malha.materials.append(mat)
    cupula.display_type = "BOUNDS"   # na viewport aparece so a caixa envolvente

    receptores = bpy.data.collections.new("AC05_Receptores_Reflexo")
    for nome in ("Obj_Portal_Futuro", "Obj_Livro_Conhecimento"):
        receptores.objects.link(bpy.data.objects[nome])
    receptores.use_fake_user = True
    cupula.light_linking.receiver_collection = receptores
    return cupula


def mundo_reflexo(forca, giro_graus):
    """(Teste descartado) HDRI no mundo so para raios Is Glossy Ray: o espelho
    fica bom, mas o chao e as letras tambem passam a refletir o estudio."""
    nt = cena.world.node_tree
    fundo = next(n for n in nt.nodes if n.type == "BACKGROUND" and n.name == "Background")
    saida = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    fundo.location = (0, 300)
    saida.location = (700, 300)
    coord = nt.nodes.new("ShaderNodeTexCoord")
    coord.location = (-700, 0)
    mapa = nt.nodes.new("ShaderNodeMapping")
    mapa.location = (-500, 0)
    mapa.inputs["Rotation"].default_value = (0.0, 0.0, math.radians(giro_graus))
    hdri = nt.nodes.new("ShaderNodeTexEnvironment")
    hdri.location = (-300, 0)
    hdri.image = bpy.data.images.load(os.path.join(TEX, "studio_blender.exr"), check_existing=True)
    hdri.label = "studio.exr (Blender/Poly Haven, CC0)"
    fundo_hdri = nt.nodes.new("ShaderNodeBackground")
    fundo_hdri.location = (0, 0)
    fundo_hdri.label = "Ambiente dos reflexos"
    fundo_hdri.inputs["Strength"].default_value = forca
    caminho = nt.nodes.new("ShaderNodeLightPath")
    caminho.location = (0, 620)
    mistura = nt.nodes.new("ShaderNodeMixShader")
    mistura.location = (400, 300)
    nt.links.new(coord.outputs["Generated"], mapa.inputs["Vector"])
    nt.links.new(mapa.outputs["Vector"], hdri.inputs["Vector"])
    nt.links.new(hdri.outputs["Color"], fundo_hdri.inputs["Color"])
    nt.links.new(caminho.outputs["Is Glossy Ray"], mistura.inputs["Fac"])
    nt.links.new(fundo.outputs["Background"], mistura.inputs[1])
    nt.links.new(fundo_hdri.outputs["Background"], mistura.inputs[2])
    nt.links.new(mistura.outputs["Shader"], saida.inputs["Surface"])


# --- Render --------------------------------------------------------------------
def configurar_cycles(amostras, porcentagem):
    cena.render.engine = "CYCLES"
    prefs = bpy.context.preferences.addons["cycles"].preferences
    try:
        prefs.compute_device_type = "METAL"
        prefs.get_devices()
        for d in prefs.devices:
            d.use = d.type == "METAL"
        cena.cycles.device = "GPU" if any(d.use for d in prefs.devices) else "CPU"
    except TypeError:
        cena.cycles.device = "CPU"
    cena.cycles.samples = amostras
    cena.cycles.use_adaptive_sampling = True
    cena.cycles.use_denoising = True
    cena.cycles.denoiser = "OPENIMAGEDENOISE"
    cena.render.resolution_percentage = porcentagem
    cena.render.image_settings.file_format = "PNG"


def renderizar(caminho):
    cena.render.filepath = caminho
    bpy.ops.render.render(write_still=True)


# --- Execucao --------------------------------------------------------------------
escada = bpy.data.objects["Obj_Escada_Construcao"]
livro = bpy.data.objects["Obj_Livro_Conhecimento"]
portal = bpy.data.objects["Obj_Portal_Futuro"]

uv_escada(escada)
uv_livro(livro)

# escala real: oak_veneer_01 cobre 1,83 m; o escovado do Metal009 foi
# ajustado para repetir a cada 0,6 m
madeira = mat_madeira(1 / (1.83 * uv_por_metro(escada)))
bronze_paginas = mat_bronze("MAT_Bronze_Escovado", "#D9A66B", 0.22, 0.42,
                            1 / (0.6 * uv_por_metro(livro, {1})), 0.6)
bronze_capa = mat_bronze("MAT_Bronze_Patinado", "#7A5634", 0.45, 0.7,
                         1 / (0.6 * uv_por_metro(livro, {0})), 0.6)
espelho = mat_espelho()

escada.material_slots[0].material = madeira
livro.material_slots[0].material = bronze_capa      # slot 0 = capa
livro.material_slots[1].material = bronze_paginas   # slot 1 = paginas
portal.material_slots[0].material = espelho
atualizar_ibmec()

# cada degrau do Array e cada metade do Mirror leem outro trecho da imagem,
# para a mesma figura do veio/escovado nao se repetir
array = escada.modifiers["Array_Degraus"]
array.offset_u, array.offset_v = 0.17, 0.31
espelhamento = livro.modifiers["Mirror"]
espelhamento.offset_u, espelhamento.offset_v = 0.21, 0.37

for obj in (escada, livro, portal):
    suavizar(obj)

# os materiais da comparacao continuam no arquivo da AC04
for nome in ("MAT_Lambert", "MAT_Phong", "MAT_BlinnPhong"):
    m = bpy.data.materials.get(nome)
    if m:
        m.use_fake_user = False
        bpy.data.materials.remove(m)
for m in (madeira, bronze_paginas, bronze_capa, espelho):
    m.use_fake_user = True

FORCA_HDRI = float(os.environ.get("AC05_HDRI_FORCA", "1.0"))
GIRO_HDRI = float(os.environ.get("AC05_HDRI_GIRO", "225"))
if MUNDO == "REFLEXO":
    cupula_reflexo(FORCA_HDRI, GIRO_HDRI)
elif MUNDO == "HDRI_GLOSSY":
    mundo_reflexo(FORCA_HDRI, GIRO_HDRI)

# o arquivo abre na vista da camera em Material Preview
for tela in bpy.data.screens:
    for area in tela.areas:
        if area.type == "VIEW_3D" and tela.name == "Layout":
            area.spaces.active.shading.type = "MATERIAL"
            area.spaces.active.region_3d.view_perspective = "CAMERA"

if TESTE:
    configurar_cycles(int(os.environ.get("AC05_AMOSTRAS", "64")), int(os.environ.get("AC05_RES", "50")))
    renderizar(os.environ.get("AC05_SAIDA", os.path.join(IMG, "teste.png")))
else:
    configurar_cycles(256, 100)
    renderizar(os.path.join(IMG, "AC05_RafaelDonner_01_render_final.png"))
    # File > External Data > Pack Resources: as imagens ficam dentro do .blend.
    # Os caminhos ficam relativos (//texturas/...), sem apontar para esta maquina.
    bpy.ops.file.pack_all()
    bpy.context.preferences.filepaths.save_version = 0     # sem copia .blend1
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PASTA, "AC05_RafaelDonner.blend"))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
