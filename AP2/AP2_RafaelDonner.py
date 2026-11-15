# AP2 - Peca audiovisual "Ibmec em 15 segundos"
# Rafael Donner - Computacao Grafica
#
# Abre a cena da AC05 e monta a animacao de 15 s (quadros 1-360 a 24 fps)
# planejada no storyboard da AP1. Salva como AP2/AP2_RafaelDonner.blend; os
# arquivos da AP1, AC04 e AC05 nao sao alterados.
#
#   Ibmec_Ponto            o ponto do i: surge no livro, rola, sobe a escada e salta para o I
#   Obj_Escada_Construcao  os degraus crescem um a um a frente do ponto (Geometry Nodes)
#   Ibmec_Letra_1_I...5_c  as letras sobem do pedestal em sequencia
#   Obj_Portal_Futuro      sobe do chao e gira 60 graus ate encaixar
#   Cam_Principal_AP1      dolly + arco pela esquerda ate o enquadramento da AP1
#
# Uso:    blender -b --factory-startup AC05/AC05_RafaelDonner.blend --python AP2/AP2_RafaelDonner.py
# Teste:  AP2_TESTE=1 AP2_QUADROS=1,120,264 AP2_RES=25 AP2_AMOSTRAS=16 AP2_SAIDA=/pasta  (nao salva)
# Video:  blender -b AP2/AP2_RafaelDonner.blend -a   (MP4 H.264 configurado no arquivo)

import bpy
import bmesh
import math
import os
from mathutils import Vector

PASTA = os.path.dirname(os.path.abspath(__file__))
TESTE = os.environ.get("AP2_TESTE") == "1"
cena = bpy.context.scene

FPS = 24
INICIO, FIM = 1, 360


# --- Keyframes -----------------------------------------------------------------
# Cada chave: (quadro, valor, interpolacao do trecho que COMECA nela, opcoes).
# Opcoes: easing ("EASE_IN", "EASE_OUT"...), back (overshoot da interpolacao BACK),
# hl / hr = alca esquerda / direita (quadro, valor) para arcos exatos (alca FREE).
def achar_curva(idb, caminho, indice):
    acao = idb.animation_data.action
    try:
        fc = acao.fcurves.find(caminho, index=indice)
        if fc:
            return fc
    except AttributeError:
        pass
    for camada in acao.layers:
        for faixa in camada.strips:
            for cb in faixa.channelbags:
                fc = cb.fcurves.find(caminho, index=indice)
                if fc:
                    return fc
    raise KeyError(caminho)


def animar(idb, caminho, chaves, indice=0, grupo=None):
    # a primeira insercao cria a Action e a F-curve; depois os pontos entram direto
    try:
        idb.keyframe_insert(data_path=caminho, index=indice, frame=chaves[0][0], group=grupo)
    except (TypeError, RuntimeError):
        idb.keyframe_insert(data_path=caminho, index=-1, frame=chaves[0][0], group=grupo)
    fc = achar_curva(idb, caminho, indice)
    for k in list(fc.keyframe_points):
        fc.keyframe_points.remove(k)
    for chave in chaves:
        quadro, valor, interp = chave[:3]
        opc = chave[3] if len(chave) > 3 else {}
        k = fc.keyframe_points.insert(quadro, valor)
        k.interpolation = interp
        if "easing" in opc:
            k.easing = opc["easing"]
        if "back" in opc:
            k.back = opc["back"]
    fc.update()
    # alcas explicitas so depois do update (que recalcula as automaticas)
    for chave in chaves:
        opc = chave[3] if len(chave) > 3 else {}
        if "hl" not in opc and "hr" not in opc:
            continue
        k = next(p for p in fc.keyframe_points if abs(p.co.x - chave[0]) < 1e-4)
        if "hl" in opc:
            k.handle_left_type = "FREE"
            k.handle_left = opc["hl"]
        if "hr" in opc:
            k.handle_right_type = "FREE"
            k.handle_right = opc["hr"]
    return fc


def parabola(t0, z0, t1, z1):
    """Alcas Bezier que tornam o trecho (t0,z0)->(t1,z1) meia parabola com o
    vertice em (t1,z1): subida ate o apice (z1 maximo) ou queda a partir dele."""
    d = t1 - t0
    return (t0 + d / 3, z0 + 2 * (z1 - z0) / 3), (t1 - d / 3, z1)


# --- Palavra: uma letra por objeto ------------------------------------------------
LETRAS = (("I", -9.0, -2.43), ("b", -2.43, -1.06), ("m", -1.06, 0.79), ("e", 0.79, 1.955), ("c", 1.955, 9.0))


def separar_letras():
    """A AP1 deixou a palavra numa malha so. Para as letras subirem em sequencia,
    cada uma vira um objeto (filho do mesmo Empty), com a origem no centro da
    base. As faces sao separadas pela posicao em X (as letras nao se sobrepoem)."""
    original = bpy.data.objects["Ibmec_Letras"]
    pai = original.parent
    colecao = original.users_collection[0]
    letras = []
    for i, (nome, x0, x1) in enumerate(LETRAS, 1):
        bm = bmesh.new()
        bm.from_mesh(original.data)
        fora = [f for f in bm.faces if not (x0 <= f.calc_center_median().x < x1)]
        bmesh.ops.delete(bm, geom=fora, context="FACES")
        xs = [v.co.x for v in bm.verts]
        cx = (min(xs) + max(xs)) / 2
        bmesh.ops.translate(bm, vec=Vector((-cx, 0.0, 0.0)), verts=bm.verts)
        malha = bpy.data.meshes.new(f"Ibmec_Letra_{i}_{nome}")
        bm.to_mesh(malha)
        bm.free()
        for m in original.data.materials:
            malha.materials.append(m)
        obj = bpy.data.objects.new(f"Ibmec_Letra_{i}_{nome}", malha)
        colecao.objects.link(obj)
        obj.parent = pai
        obj.matrix_parent_inverse = original.matrix_parent_inverse.copy()
        obj.location = original.location + Vector((cx, 0.0, 0.0))
        for mod in original.modifiers:
            novo = obj.modifiers.new(mod.name, mod.type)
            for p in mod.bl_rna.properties:
                if not p.is_readonly and p.identifier not in ("name", "type"):
                    try:
                        setattr(novo, p.identifier, getattr(mod, p.identifier))
                    except (AttributeError, TypeError):
                        pass
        letras.append(obj)
    malha_antiga = original.data
    bpy.data.objects.remove(original)
    if malha_antiga.users == 0:
        bpy.data.meshes.remove(malha_antiga)
    return letras


# --- Escada: degraus que crescem (Geometry Nodes depois do Array) -----------------
def no(arvore, tipo, x, y, **props):
    n = arvore.nodes.new(tipo)
    n.location = (x, y)
    for chave, valor in props.items():
        setattr(n, chave, valor)
    return n


def crescimento_degraus(escada):
    """O Count do Array e inteiro: animado sozinho, o degrau aparece de uma vez.
    Este grupo le o indice de cada degrau pela posicao (passo de 0,5 m em Y) e
    escala o degrau i em torno do proprio centro por easeOutBack(Crescimento - i):
    o degrau surge com um pequeno overshoot e assenta. Fica entre o Array e o
    Bevel, para o chanfro continuar sendo calculado na forma final."""
    array = escada.modifiers["Array_Degraus"]
    passo = Vector(array.constant_offset_displace)          # (0; 0,5; 0,2)
    ng = bpy.data.node_groups.new("GN_Degraus_Crescimento", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    entrada = ng.interface.new_socket("Crescimento", in_out="INPUT", socket_type="NodeSocketFloat")
    entrada.default_value = float(array.count)
    entrada.min_value = 0.0
    entrada.max_value = float(array.count)
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    L = ng.links.new

    g_in = no(ng, "NodeGroupInput", -1400, 0)
    g_out = no(ng, "NodeGroupOutput", 900, 0)
    pos = no(ng, "GeometryNodeInputPosition", -1400, -260)
    sep = no(ng, "ShaderNodeSeparateXYZ", -1200, -260)
    div = no(ng, "ShaderNodeMath", -1000, -260, operation="DIVIDE", label="Y / passo")
    div.inputs[1].default_value = passo.y
    idx = no(ng, "ShaderNodeMath", -800, -260, operation="ROUND", label="indice do degrau")
    t = no(ng, "ShaderNodeMath", -600, -120, operation="SUBTRACT", use_clamp=True, label="t = Crescimento - i")
    u = no(ng, "ShaderNodeMath", -400, -120, operation="SUBTRACT", label="u = t - 1")
    u.inputs[1].default_value = 1.0
    u2 = no(ng, "ShaderNodeMath", -200, -40, operation="MULTIPLY", label="u^2")
    u3 = no(ng, "ShaderNodeMath", -200, -200, operation="MULTIPLY", label="u^3")
    c1 = 1.5                                                  # overshoot de ~8%
    a = no(ng, "ShaderNodeMath", 0, -200, operation="MULTIPLY_ADD", label="(c1+1) u^3 + 1")
    a.inputs[1].default_value = c1 + 1
    a.inputs[2].default_value = 1.0
    f = no(ng, "ShaderNodeMath", 200, -120, operation="MULTIPLY_ADD", label="easeOutBack(t)")
    f.inputs[1].default_value = c1
    f_min = no(ng, "ShaderNodeMath", 400, -120, operation="MAXIMUM", label="escala minima")
    f_min.inputs[1].default_value = 0.001                     # nunca zero: sem faces degeneradas
    cy = no(ng, "ShaderNodeMath", -600, -420, operation="MULTIPLY", label="i * 0,5")
    cy.inputs[1].default_value = passo.y
    cz = no(ng, "ShaderNodeMath", -600, -560, operation="MULTIPLY", label="i * 0,2")
    cz.inputs[1].default_value = passo.z
    centro = no(ng, "ShaderNodeCombineXYZ", -400, -480, label="centro do degrau i")
    rel = no(ng, "ShaderNodeVectorMath", 200, -360, operation="SUBTRACT")
    esc = no(ng, "ShaderNodeVectorMath", 450, -360, operation="SCALE")
    soma = no(ng, "ShaderNodeVectorMath", 650, -360, operation="ADD")
    setp = no(ng, "GeometryNodeSetPosition", 700, 0)

    L(g_in.outputs["Geometry"], setp.inputs["Geometry"])
    L(pos.outputs["Position"], sep.inputs["Vector"])
    L(sep.outputs["Y"], div.inputs[0])
    L(div.outputs[0], idx.inputs[0])
    L(g_in.outputs["Crescimento"], t.inputs[0])
    L(idx.outputs[0], t.inputs[1])
    L(t.outputs[0], u.inputs[0])
    L(u.outputs[0], u2.inputs[0])
    L(u.outputs[0], u2.inputs[1])
    L(u2.outputs[0], u3.inputs[0])
    L(u.outputs[0], u3.inputs[1])
    L(u3.outputs[0], a.inputs[0])
    L(u2.outputs[0], f.inputs[0])
    L(a.outputs[0], f.inputs[2])
    L(f.outputs[0], f_min.inputs[0])
    L(idx.outputs[0], cy.inputs[0])
    L(idx.outputs[0], cz.inputs[0])
    L(cy.outputs[0], centro.inputs["Y"])
    L(cz.outputs[0], centro.inputs["Z"])
    L(pos.outputs["Position"], rel.inputs[0])
    L(centro.outputs["Vector"], rel.inputs[1])
    L(rel.outputs["Vector"], esc.inputs[0])
    L(f_min.outputs[0], esc.inputs["Scale"])
    L(esc.outputs["Vector"], soma.inputs[0])
    L(centro.outputs["Vector"], soma.inputs[1])
    L(soma.outputs["Vector"], setp.inputs["Position"])
    L(setp.outputs["Geometry"], g_out.inputs["Geometry"])

    mod = escada.modifiers.new("GN_Crescimento", "NODES")
    mod.node_group = ng
    destino = list(escada.modifiers).index(array) + 1
    try:
        escada.modifiers.move(len(escada.modifiers) - 1, destino)
    except AttributeError:
        with bpy.context.temp_override(object=escada, active_object=escada):
            bpy.ops.object.modifier_move_to_index(modifier=mod.name, index=destino)
    return mod, entrada.identifier


# --- Linha do tempo ---------------------------------------------------------------
# Saltos: do livro para o degrau 0 e depois degrau a degrau. O intervalo entre
# saltos encurta (28, 25, 22, 20, 18 quadros): o ritmo acelera, como no storyboard.
# Cada voo dura 12 quadros (0,5 s).
DECOLA = (88, 116, 141, 163, 183, 201)   # salto k: livro/degrau k-1 -> degrau k
VOO, SUBIDA = 12, 7                      # quadros no ar; quadros ate o apice
CRESCE_ANTES, CRESCE_DUR = 15, 12        # o degrau k comeca a crescer 15 quadros antes do salto
LETRA_INICIO, LETRA_PASSO, LETRA_DUR = 160, 10, 36
SALTO_FINAL, APICE_FINAL, POUSO = 243, 257, 264
CAMERA_TRAVA = 288
Y_LIVRO = -1.80                          # onde o ponto surge, na lombada do livro
Y_PARADA = -1.05                         # fim da rolagem, na borda de tras das paginas


def animar_ponto(ponto, raio, x_escada, y0, passo, piso0, z_lombada, final):
    """Ibmec_Ponto e filho de Ibmec_Palavra (sem rotacao nem escala): local = mundo - pai.
    Cada canal guarda {quadro: (valor, interpolacao, opcoes)}; o dicionario evita
    chaves duplicadas quando o ritmo acelera e as poses de um salto encostam no proximo."""
    base = ponto.parent.matrix_world.translation
    px, py, pz, sxy, sz = {}, {}, {}, {}, {}

    def piso(k):
        return piso0 + passo.z * k

    def y_deg(k):
        return y0 + passo.y * k

    def escala(q, a, b):
        sxy[q] = (a, "BEZIER")
        sz[q] = (b, "BEZIER")

    # Q1 - surge sobre as paginas: escala 0 -> 1 com um quique, crescendo a partir do apoio
    contato = z_lombada - raio
    for q, s in ((1, 0.001), (12, 0.001), (21, 1.18), (26, 0.92), (30, 1.0)):
        escala(q, s, s)
        pz[q] = (contato + raio * s, "BEZIER")
    px[1] = (x_escada, "CONSTANT")
    py[1] = (Y_LIVRO, "CONSTANT")
    # rola pela lombada ate a borda das paginas: sai devagar e para devagar (Bezier)
    py[40] = (Y_LIVRO, "BEZIER")
    pz[40] = (z_lombada, "BEZIER")
    py[68] = (Y_PARADA, "CONSTANT")
    pz[68] = (z_lombada, "BEZIER")

    # saltos: livro -> degrau 0, os degraus seguintes e o salto final ate o I.
    # (atravessar rolando o vao entre o livro e o degrau fazia o ponto raspar a
    # borda de 2 cm do piso rebaixado; o salto resolve e mantem o ritmo)
    saltos = []
    origens = [(Y_PARADA, contato)] + [(y_deg(k), piso(k)) for k in range(len(DECOLA) - 1)]
    for k, t in enumerate(DECOLA):
        y_ini, apoio_ini = origens[k]
        saltos.append(dict(t=t, ap=t + SUBIDA, l=t + VOO, x0=x_escada, y0=y_ini, apoio0=apoio_ini,
                           x1=x_escada, y1=y_deg(k), apoio1=piso(k), z_ap=piso(k) + raio + 0.25,
                           antes=6, ant=(1.08, 0.86), estica=(0.93, 1.12), pousa=(1.1, 0.84)))
    n = len(DECOLA) - 1
    saltos.append(dict(t=SALTO_FINAL, ap=APICE_FINAL, l=POUSO, x0=x_escada, y0=y_deg(n), apoio0=piso(n),
                       x1=final.x, y1=final.y, apoio1=None, z_ap=final.z + 0.41,
                       antes=7, ant=(1.12, 0.78), estica=(0.9, 1.18), pousa=(1.1, 0.86)))

    ultimo = 68                                   # fim da rolagem
    for s in saltos:
        t, ap, l = s["t"], s["ap"], s["l"]
        z0 = s["apoio0"] + raio
        z1 = final.z if s["apoio1"] is None else s["apoio1"] + raio
        z_pouso = final.z if s["apoio1"] is None else s["apoio1"] + raio * s["pousa"][1]
        # entre o pouso anterior e esta decolagem: rebote e repouso so se couberem
        if t - s["antes"] >= ultimo + 5:
            pz[t - s["antes"]] = (z0, "BEZIER")
            escala(t - s["antes"], 1.0, 1.0)
        pz[t - 1] = (s["apoio0"] + raio * s["ant"][1], "BEZIER")       # antecipacao: squash
        escala(t - 1, *s["ant"])
        sobe_hr, sobe_hl = parabola(t, z0, ap, s["z_ap"])
        desce_hl, desce_hr_apice = parabola(l, z_pouso, ap, s["z_ap"])  # queda: espelho da subida
        pz[t] = (z0, "BEZIER", {"hr": sobe_hr})
        pz[ap] = (s["z_ap"], "BEZIER", {"hl": sobe_hl, "hr": desce_hr_apice})
        pz[l] = (z_pouso, "BEZIER", {"hl": desce_hl})
        escala(t + 2, *s["estica"])                                      # decola esticado
        escala(ap, 1.0, 1.0)
        escala(l - 1, 0.95, 1.08)
        escala(l, *s["pousa"])                                           # pouso: squash
        # no ar o deslocamento horizontal e uniforme (LINEAR); parado, CONSTANT
        py[t] = (s["y0"], "LINEAR")
        py[l] = (s["y1"], "CONSTANT")
        if s["x1"] != s["x0"]:
            px[t] = (s["x0"], "LINEAR")
            px[l] = (s["x1"], "CONSTANT")
        proximo = next((p["t"] for p in saltos if p["t"] > t), None)
        reb, rep = (4, 8) if s["apoio1"] is None else (3, 6)
        if proximo is None or proximo - 1 > l + reb:
            if s["apoio1"] is None:
                pz[l + reb] = (z1 + 0.016, "BEZIER")
            else:
                pz[l + reb] = (s["apoio1"] + raio * 1.04, "BEZIER")
            escala(l + reb, 0.97, 1.04)
        if proximo is None or proximo - s["antes"] >= l + rep:
            pz[l + rep] = (z1, "BEZIER")
            escala(l + rep, 1.0, 1.0)
            ultimo = l + rep
        else:
            ultimo = l + reb

    def chaves(canal, eixo=None):
        saida = []
        for q in sorted(canal):
            valor, interp, *opc = canal[q]
            opc = dict(opc[0]) if opc else {}
            if eixo is not None:
                valor -= base[eixo]
                for lado in ("hl", "hr"):
                    if lado in opc:
                        opc[lado] = (opc[lado][0], opc[lado][1] - base[eixo])
            saida.append((q, valor, interp, opc))
        return saida

    animar(ponto, "location", chaves(px, 0), 0, "Ponto")
    animar(ponto, "location", chaves(py, 1), 1, "Ponto")
    animar(ponto, "location", chaves(pz, 2), 2, "Ponto")
    animar(ponto, "scale", chaves(sxy), 0, "Ponto")
    animar(ponto, "scale", chaves(sxy), 1, "Ponto")
    animar(ponto, "scale", chaves(sz), 2, "Ponto")


def animar_degraus(escada, socket):
    caminho = f'modifiers["GN_Crescimento"]["{socket}"]'
    chaves = [(1, 1.0, "CONSTANT")]
    for k, t in enumerate(DECOLA[1:], 1):          # o degrau 0 ja existe (Count 1 da AP1)
        g = t - CRESCE_ANTES
        chaves += [(g, float(k), "LINEAR"), (g + CRESCE_DUR, float(k + 1), "CONSTANT")]
    animar(escada, caminho, chaves, 0, "Escada")


def animar_letras(letras, profundidade):
    """Sobem do pedestal em sequencia (10 quadros de defasagem), com ease-out."""
    for i, letra in enumerate(letras):
        q0 = LETRA_INICIO + LETRA_PASSO * i
        z = letra.location.z
        animar(letra, "location", [(1, z - profundidade, "CONSTANT"),
                                   (q0, z - profundidade, "QUART", {"easing": "EASE_OUT"}),
                                   (q0 + LETRA_DUR, z, "CONSTANT")], 2, "Letras")


def animar_portal(portal, profundidade):
    z = portal.location.z
    animar(portal, "location", [(1, z - profundidade, "CONSTANT"),
                                (130, z - profundidade, "CUBIC", {"easing": "EASE_OUT"}),
                                (276, z, "CONSTANT")], 2, "Portal")
    # hexagono: simetria de 60 graus, o giro termina encaixado
    animar(portal, "rotation_euler", [(1, math.radians(-60), "CONSTANT"),
                                      (170, math.radians(-60), "SINE", {"easing": "EASE_IN_OUT"}),
                                      (CAMERA_TRAVA, 0.0, "CONSTANT")], 1, "Portal")


def animar_camera(camera, alvo, poses, livres=()):
    """Bezier: a camera sai e chega com velocidade zero (Auto Clamped nas pontas).
    Nas poses de 'livres' a alca e Auto sem clamp: no ponto mais a esquerda do arco
    o Auto Clamped achata a curva e a camera quase parava; com Auto ela passa direto."""
    for eixo in range(3):
        for dono, i, grupo in ((camera, 1, "Camera"), (alvo, 2, "Alvo")):
            fc = animar(dono, "location", [(p[0], p[i][eixo], "BEZIER") for p in poses], eixo, grupo)
            for k in fc.keyframe_points:
                if int(round(k.co.x)) in livres:
                    k.handle_left_type = k.handle_right_type = "AUTO"
            fc.update()


def animar_brilho(mat):
    """O ponto acende quando completa o logo e volta a cor da marca."""
    bsdf = next(n for n in mat.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Emission Color"].default_value = bsdf.inputs["Base Color"].default_value[:]
    sock = bsdf.inputs["Emission Strength"]
    caminho = sock.path_from_id("default_value")
    animar(mat.node_tree, caminho, [(1, 0.0, "CONSTANT"), (POUSO - 1, 0.0, "LINEAR"),
                                    (POUSO + 2, 3.0, "EXPO", {"easing": "EASE_OUT"}),
                                    (POUSO + 36, 0.0, "CONSTANT")], 0, "Brilho")


def luz_recorte(potencia):
    """Rim light planejada na AP1: Area atras do portal, alta, apontada para a
    palavra. Desenha o contorno de cima das letras e as separa do fundo.
    - Light Linking: so as letras e o ponto recebem esta luz. Sem isso ela
      iluminava o chao atras do pedestal e abria faixas de luz pelo portal.
    - Shadow Linking: so a propria palavra bloqueia; o portal subindo e girando
      nao projeta sombras moveis sobre as letras.
    - Acende enquanto as letras sobem (a luz acompanha a chegada da marca)."""
    dados = bpy.data.lights.new("Luz_Recorte", "AREA")
    dados.shape = "RECTANGLE"
    dados.size, dados.size_y = 4.0, 1.5
    dados.energy = potencia
    luz = bpy.data.objects.new("Luz_Recorte", dados)
    bpy.data.collections["05_Iluminacao"].objects.link(luz)
    luz.location = (0.6, 7.6, 5.6)
    direcao = Vector((0.0, 3.0, 1.9)) - luz.location
    luz.rotation_euler = direcao.to_track_quat("-Z", "Y").to_euler()
    luz.visible_camera = False
    marca = bpy.data.collections.new("AP2_Receptores_Recorte")
    for o in bpy.data.objects:
        if o.name.startswith("Ibmec_Letra_") or o.name == "Ibmec_Ponto":
            marca.objects.link(o)
    marca.use_fake_user = True
    luz.light_linking.receiver_collection = marca
    luz.light_linking.blocker_collection = marca
    animar(dados, "energy", [(1, 0.0, "CONSTANT"), (LETRA_INICIO, 0.0, "SINE", {"easing": "EASE_IN_OUT"}),
                             (LETRA_INICIO + 4 * LETRA_PASSO + LETRA_DUR, potencia, "CONSTANT")], 0, "Recorte")
    return luz


# --- Render e saida -------------------------------------------------------------------
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
    cena.cycles.adaptive_threshold = 0.01
    cena.cycles.use_denoising = True
    cena.cycles.denoiser = "OPENIMAGEDENOISE"
    cena.cycles.seed = 0
    cena.cycles.use_animated_seed = False          # ruido fixo: o quadro parado do final nao cintila
    cena.render.use_persistent_data = True         # reaproveita a BVH entre quadros
    cena.render.use_motion_blur = True
    cena.render.motion_blur_shutter = 0.5
    cena.render.resolution_x, cena.render.resolution_y = 1920, 1080
    cena.render.resolution_percentage = porcentagem


def configurar_saida():
    cena.frame_start, cena.frame_end = INICIO, FIM
    cena.render.fps, cena.render.fps_base = FPS, 1.0
    r = cena.render
    r.image_settings.file_format = "FFMPEG"
    r.ffmpeg.format = "MPEG4"
    r.ffmpeg.codec = "H264"
    r.ffmpeg.constant_rate_factor = "HIGH"
    r.ffmpeg.ffmpeg_preset = "GOOD"
    r.ffmpeg.gopsize = FPS
    r.ffmpeg.audio_codec = "NONE"
    r.use_file_extension = True
    r.filepath = "//AP2_RafaelDonner.mp4"


def marcadores():
    cena.timeline_markers.clear()
    for nome, q in (("Q1 Inicio", 1), ("Q2 Transformacao", 73), ("Q3 Encerramento", 241),
                    ("Ponto no I", POUSO), ("Marca fixa", CAMERA_TRAVA)):
        cena.timeline_markers.new(nome, frame=q)


# --- Execucao ----------------------------------------------------------------------------
cena.frame_set(1)
ponto = bpy.data.objects["Ibmec_Ponto"]
escada = bpy.data.objects["Obj_Escada_Construcao"]
portal = bpy.data.objects["Obj_Portal_Futuro"]
camera = bpy.data.objects["Cam_Principal_AP1"]
alvo = bpy.data.objects["Cam_Alvo"]

final_ponto = ponto.matrix_world.translation.copy()      # lugar do ponto no logo (AP1)
raio = max(v.co.length for v in ponto.data.vertices)
array = escada.modifiers["Array_Degraus"]
passo = Vector(array.constant_offset_displace)

letras = separar_letras()
_, socket = crescimento_degraus(escada)

# medidas da cena (conferidas com ray cast na geometria da AC05)
PISO0 = 0.18          # piso rebaixado do primeiro degrau (z), depois do Inset de 2 cm
Z_LOMBADA = 0.4317    # centro do ponto apoiado na lombada do livro
animar_ponto(ponto, raio, escada.location.x, escada.location.y, passo, PISO0, Z_LOMBADA, final_ponto)
animar_degraus(escada, socket)
animar_letras(letras, 1.40)          # 1,40 m abaixo: escondidas no pedestal (1,2 m) e sob o chao
animar_portal(portal, 8.2)           # 8,2 m abaixo: o hexagono inteiro sob o chao, em qualquer giro
animar_brilho(bpy.data.materials["MAT_Ibmec_Amarelo"])
luz_recorte(900.0)

POSES_CAMERA = [   # (quadro, camera, alvo)
    (1,   (-2.00, -4.60, 0.85), (-2.75, -1.75, 0.32)),   # perto e baixo: o livro
    (40,  (-2.25, -4.95, 0.98), (-2.75, -1.55, 0.36)),   # afasta devagar
    (76,  (-3.20, -5.50, 1.40), (-2.75, -0.85, 0.45)),
    (135, (-6.10, -4.30, 2.35), (-2.65, 0.30, 0.85)),    # arco pela esquerda, na diagonal da escada
    (195, (-4.30, -8.00, 3.30), (-1.80, 1.70, 1.45)),
    (240, (-0.20, -10.50, 3.75), (-0.20, 2.45, 2.12)),   # quase parada antes do salto final
    (CAMERA_TRAVA, tuple(camera.location), tuple(alvo.location)),   # enquadramento da AP1
]
animar_camera(camera, alvo, POSES_CAMERA, livres=(135,))

configurar_saida()
marcadores()
cena.frame_set(1)

if TESTE:
    configurar_cycles(int(os.environ.get("AP2_AMOSTRAS", "16")), int(os.environ.get("AP2_RES", "25")))
    cena.render.image_settings.file_format = "PNG"
    saida = os.environ.get("AP2_SAIDA", os.path.join(PASTA, "teste"))
    quadros = []
    for parte in os.environ.get("AP2_QUADROS", "1,120,264,360").split(","):
        if "-" in parte:                                  # intervalo "a-b"
            a, b = parte.split("-")
            quadros += range(int(a), int(b) + 1)
        elif parte.strip():
            quadros.append(int(parte))
    for q in quadros:
        cena.frame_set(q)
        cena.render.filepath = os.path.join(saida, f"q{q:03d}.png")
        bpy.ops.render.render(write_still=True)
else:
    configurar_cycles(128, 100)
    for tela in bpy.data.screens:
        for area in tela.areas:
            if area.type == "VIEW_3D" and tela.name == "Layout":
                area.spaces.active.shading.type = "MATERIAL"
                area.spaces.active.region_3d.view_perspective = "CAMERA"
    bpy.context.preferences.filepaths.save_version = 0
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(PASTA, "AP2_RafaelDonner.blend"))
    bpy.ops.file.make_paths_relative()
    bpy.ops.wm.save_mainfile()
