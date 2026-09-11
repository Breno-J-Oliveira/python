import json
import time
import winsound
from pathlib import Path
from datetime import date

import flet as ft

PALETA = {
    "clara": {
        "fundo": "#FBF6F3", "cartao": "#FFFFFF", "texto": "#4A3A45",
        "titulo": "#9C6B8F", "subt": "#9C8F96",
        "nav_ativo": "#E9D6E5", "nav_ativo_t": "#7B4F78",
        "nav_inativo": "#F6F0E8", "nav_inativo_t": "#B8A9AE",
        "progresso": "#F0E3EB", "alerta": "#D98F8F",
        "play_bg": "#DCEFDF", "play_i": "#3F7A57",
        "pause_bg": "#FBEED9", "pause_i": "#A97A2F",
        "reset_bg": "#EFE9EF", "reset_i": "#8A7C88",
        "del": "#C97979", "ok_bg": "#E4F1E6", "ok_t": "#4F7A5F", "ok_i": "#5F8F6C",
        "alta": "#D97A7A", "media": "#D9B45A", "baixa": "#7FB98A",
    },
    "escura": {
        "fundo": "#26202B", "cartao": "#362E3B", "texto": "#F0E7EF",
        "titulo": "#D9BBD0", "subt": "#A99AA7",
        "nav_ativo": "#4A3B52", "nav_ativo_t": "#E9D4E6",
        "nav_inativo": "#332C38", "nav_inativo_t": "#9C8C9F",
        "progresso": "#4A3B48", "alerta": "#E3A1A1",
        "play_bg": "#2F4A38", "play_i": "#8FD4A8",
        "pause_bg": "#4A3D26", "pause_i": "#E7C46F",
        "reset_bg": "#3B323E", "reset_i": "#B8A6B6",
        "del": "#E0A3A3", "ok_bg": "#2E4636", "ok_t": "#AAD7B7", "ok_i": "#9DCBAB",
        "alta": "#D97A7A", "media": "#D9B45A", "baixa": "#7FB98A",
    },
}


def main(page: ft.Page):
    page.title = "Pomodoro Inteligente"
    page.window_width = 440
    page.window_height = 760
    page.padding = 14
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.PURPLE_100)

    # ---------------- Estado centralizado ----------------
    ESTADO = {
        "tema": "clara",
        "som": True,
        "auto_descanso": False,
        "filtro": "",
        "prio_nova": "media",
        "tarefas": [],
        "tarefa_atual": None,
        "tempo_total": 0,
        "tempo_restante": 0,
        "rodando": False,
        "sessoes": 0,
        "meta": 4,
        "historico": [],
    }

    def T():
        return PALETA[ESTADO["tema"]]

    # ---------------- Persistência ----------------
    ARQUIVO = Path(__file__).resolve().with_name("tarefas.json")

    def carregar_dados():
        if ARQUIVO.exists():
            try:
                ESTADO["tarefas"] = json.loads(ARQUIVO.read_text(encoding="utf-8"))
            except Exception:
                ESTADO["tarefas"] = []

    def salvar_dados():
        try:
            ARQUIVO.write_text(
                json.dumps(ESTADO["tarefas"], ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ---------------- Persistência do histórico e meta ----------------
    ARQH = Path(__file__).resolve().with_name("historico.json")

    def carregar_historicos():
        try:
            dados = json.loads(ARQH.read_text(encoding="utf-8")) if ARQH.exists() else {}
        except Exception:
            dados = {}
        ESTADO["meta"] = dados.get("meta", 4)
        ESTADO["historico"] = dados.get("historico", [])

    def salvar_historicos():
        try:
            ARQH.write_text(
                json.dumps({"meta": ESTADO["meta"], "historico": ESTADO["historico"]},
                           ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        except Exception:
            pass

    # ---------------- Helpers ----------------
    def formatar(seg):
        seg = max(0, int(seg))
        return f"{seg // 60:02d}:{seg % 60:02d}"

    def tocar_alarme():
        if not ESTADO["som"]:
            return
        try:
            winsound.Beep(880, 300)
            winsound.Beep(1175, 300)
            winsound.Beep(1568, 400)
        except Exception:
            pass

    def avisar(msg):
        page.snack_bar = ft.SnackBar(ft.Text(msg, weight=ft.FontWeight.BOLD))
        page.snack_bar.open = True
        page.update()

    def prio_cor(prio):
        return T().get(prio, T()["titulo"])

    # ---------------- Cabeçalho ----------------
    nav_itens = []  # (container, icone, texto) — preenchido na montagem

    icone_app = ft.Icon(ft.Icons.LOCAL_CAFE, size=30, color=T()["titulo"])
    titulo_app = ft.Text("Pomodoro", size=24, weight=ft.FontWeight.BOLD, color=T()["titulo"])
    subt_app = ft.Text("Estude com foco", size=12, color=T()["subt"])
    rotulo_sessoes = ft.Text("0 sessões", size=13, weight=ft.FontWeight.BOLD, color=T()["titulo"])
    chip_sessoes = ft.Container(
        content=rotulo_sessoes, bgcolor=T()["nav_ativo"],
        border_radius=20, padding=8,
    )
    botao_tema = ft.IconButton(icon=ft.Icons.DARK_MODE, icon_color=T()["titulo"], tooltip="Tema")

    # ---------------- Formulário de tarefa ----------------
    campo_nome = ft.TextField(hint_text="Nome da tarefa", expand=True)
    campo_min = ft.TextField(hint_text="min", width=72, keyboard_type=ft.KeyboardType.NUMBER)
    botao_adicionar = ft.ElevatedButton("Adicionar", icon=ft.Icons.ADD)

    def criar_chip_prio(label):
        tx = ft.Text(label, size=13, weight=ft.FontWeight.BOLD)
        cont = ft.Container(
            content=ft.Row([tx], alignment=ft.MainAxisAlignment.CENTER),
            padding=8, border_radius=8, expand=True,
        )
        return cont, tx

    chip_baixa, tx_baixa = criar_chip_prio("Baixa")
    chip_media, tx_media = criar_chip_prio("Média")
    chip_alta, tx_alta = criar_chip_prio("Alta")
    prio_chips = [  # (container, texto, prioridade)
        (chip_baixa, tx_baixa, "baixa"),
        (chip_media, tx_media, "media"),
        (chip_alta, tx_alta, "alta"),
    ]

    # ---------------- Cronômetro ----------------
    nome_tarefa_atual = ft.Text(
        "Nenhuma tarefa selecionada", size=19, weight=ft.FontWeight.BOLD, color=T()["titulo"],
    )
    tipo_atual = ft.Text("", size=13, weight=ft.FontWeight.BOLD, color=T()["subt"])
    relogio = ft.Text(
        "00:00", size=78, weight=ft.FontWeight.BOLD, font_family="Consolas", color=T()["titulo"],
    )
    barra_progresso = ft.ProgressBar(
        value=0, color=T()["titulo"], bgcolor=T()["progresso"], bar_height=10, border_radius=5,
    )
    rotulo_percent = ft.Text("0%", size=18, weight=ft.FontWeight.BOLD, color=T()["titulo"])
    rotulo_decorrido = ft.Text("Decorrido 00:00 · Falta 00:00", size=13, color=T()["subt"])

    botao_iniciar = ft.IconButton(
        icon=ft.Icons.PLAY_ARROW, icon_color=T()["play_i"], bgcolor=T()["play_bg"],
        icon_size=40, tooltip="Iniciar (espaço)",
    )
    botao_pausar = ft.IconButton(
        icon=ft.Icons.PAUSE, icon_color=T()["pause_i"], bgcolor=T()["pause_bg"],
        icon_size=40, tooltip="Pausar (espaço)",
    )
    botao_resetar = ft.IconButton(
        icon=ft.Icons.REFRESH, icon_color=T()["reset_i"], bgcolor=T()["reset_bg"],
        icon_size=40, tooltip="Resetar (R)",
    )
    botao_concluir = ft.OutlinedButton("Concluir", icon=ft.Icons.CHECK_CIRCLE)

    # ---------------- Configurações ----------------
    campo_estudo = ft.TextField(label="Estudo (min)", value="25", width=125,
                                keyboard_type=ft.KeyboardType.NUMBER)
    campo_descanso = ft.TextField(label="Descanso (min)", value="5", width=125,
                                  keyboard_type=ft.KeyboardType.NUMBER)
    botao_estudar = ft.FilledTonalButton("Estudar agora", icon=ft.Icons.PLAY_CIRCLE)
    botao_descansar = ft.FilledTonalButton("Descansar agora", icon=ft.Icons.LOCAL_CAFE)
    rotulo_som = ft.Text("Som", size=14, color=T()["texto"])
    switch_som = ft.Switch(value=True)
    rotulo_auto = ft.Text("Descanso automático", size=14, color=T()["texto"])
    switch_auto = ft.Switch(value=False)

    # ---------------- Diálogo de edição ----------------
    campo_edit_nome = ft.TextField(label="Nome", expand=True)
    campo_edit_min = ft.TextField(label="Tempo (min)", width=100,
                                  keyboard_type=ft.KeyboardType.NUMBER)

    def _fechar_edicao():
        dlg_edicao.open = False
        ESTADO["editando"] = None
        page.update()

    def salvar_edicao(e):
        t = ESTADO["editando"]
        if t is None:
            return
        nome = (campo_edit_nome.value or "").strip()
        try:
            mins = int((campo_edit_min.value or "").strip())
            if mins <= 0:
                raise ValueError
        except ValueError:
            avisar("Tempo inválido. Use minutos > 0.")
            return
        if not nome:
            avisar("O nome não pode ficar vazio.")
            return
        t["nome"] = nome
        t["tempo_total_s"] = mins * 60
        if t is ESTADO["tarefa_atual"]:
            ESTADO["tempo_total"] = mins * 60
            ESTADO["tempo_restante"] = mins * 60
            nome_tarefa_atual.value = nome
            atualizar_visual_cronometro()
        salvar_dados()
        atualizar_listas()
        dlg_edicao.open = False
        ESTADO["editando"] = None
        page.update()

    dlg_edicao = ft.AlertDialog(
        modal=True,
        title=ft.Text("Editar tarefa", weight=ft.FontWeight.BOLD),
        content=ft.Column([campo_edit_nome, campo_edit_min], spacing=12, width=280),
        actions=[
            ft.OutlinedButton("Cancelar", on_click=lambda e: _fechar_edicao()),
            ft.FilledTonalButton("Salvar", on_click=salvar_edicao),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )

    def abrir_edicao(t):
        campo_edit_nome.value = t["nome"]
        campo_edit_min.value = str(t["tempo_total_s"] // 60)
        ESTADO["editando"] = t
        dlg_edicao.open = True
        page.update()

    # ---------------- Cartões ----------------
    def criar_cartao_pendente(t):
        minutos = t["tempo_total_s"] // 60
        cor = prio_cor(t.get("prio", "media"))
        nome = ft.Text(t["nome"], size=16, weight=ft.FontWeight.BOLD, color=T()["texto"])
        meta = ft.Text(f"{minutos} min · {t.get('prio', 'media').capitalize()}",
                       size=12, color=T()["subt"])
        return ft.Container(
            bgcolor=T()["cartao"], border_radius=12, padding=10, ink=True,
            on_click=lambda e: carregar_tarefa(t),
            content=ft.Row([
                ft.Container(width=5, height=46, bgcolor=cor, border_radius=8),
                ft.Column([nome, meta], expand=True, spacing=2),
                ft.IconButton(icon=ft.Icons.EDIT, icon_color=T()["subt"], tooltip="Editar",
                              on_click=lambda e: abrir_edicao(t)),
                ft.IconButton(icon=ft.Icons.PLAY_ARROW, icon_color=T()["play_i"], tooltip="Executar",
                              on_click=lambda e: carregar_tarefa(t)),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color=T()["del"], tooltip="Apagar",
                              on_click=lambda e: apagar_tarefa(t)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    def criar_cartao_concluida(t):
        minutos = t["tempo_total_s"] // 60
        return ft.Container(
            bgcolor=T()["ok_bg"], border_radius=12, padding=10,
            content=ft.Row([
                ft.Icon(ft.Icons.CHECK_CIRCLE, color=T()["ok_i"], size=20),
                ft.Column([
                    ft.Text(t["nome"], size=16, weight=ft.FontWeight.BOLD, color=T()["ok_t"]),
                    ft.Text(f"{minutos} min · concluída", size=12, color=T()["ok_t"]),
                ], expand=True, spacing=2),
                ft.IconButton(icon=ft.Icons.REFRESH, icon_color=T()["ok_i"], tooltip="Refazer",
                              on_click=lambda e: refazer_tarefa(t)),
                ft.IconButton(icon=ft.Icons.DELETE, icon_color=T()["del"], tooltip="Apagar",
                              on_click=lambda e: apagar_tarefa(t)),
            ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
        )

    campo_pesquisa = ft.TextField(hint_text="Pesquisar tarefas", prefix_icon=ft.Icons.SEARCH)

    lista_pendentes = ft.ListView(expand=True, spacing=8, padding=4)
    lista_concluidas = ft.ListView(expand=True, spacing=8, padding=4)
    vazio_pendentes = ft.Text(
        "Nenhuma tarefa aqui.\nAdicione uma nova! ✨",
        text_align=ft.TextAlign.CENTER, size=14, color=T()["subt"], visible=True,
    )
    vazio_concluidas = ft.Text(
        "Nada concluído ainda.\nQue tal começar? 🚀",
        text_align=ft.TextAlign.CENTER, size=14, color=T()["subt"], visible=True,
    )
    botao_limpar_pendentes = ft.OutlinedButton("Limpar pendentes", icon=ft.Icons.CLEAR_ALL)
    botao_limpar_concluidas = ft.OutlinedButton("Limpar concluídas", icon=ft.Icons.CLEAR_ALL)

    # ---------------- Ações de tarefa ----------------
    def adicionar_tarefa(e):
        nome = (campo_nome.value or "").strip()
        try:
            mins = int((campo_min.value or "").strip())
            if mins <= 0:
                raise ValueError
        except ValueError:
            avisar("Digite um tempo válido (minutos > 0).")
            return
        if not nome:
            avisar("Digite um nome para a tarefa.")
            return
        ESTADO["tarefas"].append({
            "nome": nome,
            "tempo_total_s": mins * 60,
            "concluida": False,
            "prio": ESTADO["prio_nova"],
        })
        campo_nome.value = ""
        campo_min.value = ""
        salvar_dados()
        atualizar_listas()
        avisar(f"Tarefa \"{nome}\" adicionada!")

    def apagar_tarefa(t):
        if ESTADO["rodando"] and t is ESTADO["tarefa_atual"]:
            ESTADO["rodando"] = False
        if t in ESTADO["tarefas"]:
            ESTADO["tarefas"].remove(t)
        if t is ESTADO["tarefa_atual"]:
            ESTADO["tarefa_atual"] = None
            limpar_cronometro()
        salvar_dados()
        atualizar_listas()
        page.update()

    def refazer_tarefa(t):
        t["concluida"] = False
        salvar_dados()
        atualizar_listas()
        avisar(f"\"{t['nome']}\" voltou para pendentes.")

    def limpar_pendentes(e):
        ESTADO["tarefas"] = [t for t in ESTADO["tarefas"] if t["concluida"]]
        salvar_dados()
        atualizar_listas()
        avisar("Pendentes apagadas.")

    def limpar_concluidas(e):
        ESTADO["tarefas"] = [t for t in ESTADO["tarefas"] if not t["concluida"]]
        salvar_dados()
        atualizar_listas()
        avisar("Concluídas apagadas.")

    def ao_pesquisar(e):
        ESTADO["filtro"] = e.control.value or ""
        atualizar_listas()

    def selecionar_prio(prio):
        ESTADO["prio_nova"] = prio
        for cont, tx, p in prio_chips:
            ativo = p == prio
            cont.bgcolor = prio_cor(p) if ativo else T()["cartao"]
            tx.color = "#FFFFFF" if ativo else T()["texto"]
        page.update()

    # ---------------- Atualização das listas ----------------
    def atualizar_contadores():
        pend = sum(1 for t in ESTADO["tarefas"] if not t["concluida"])
        conc = sum(1 for t in ESTADO["tarefas"] if t["concluida"])
        if len(nav_itens) >= 4:
            nav_itens[0][2].value = f"Tarefas ({pend})"
            nav_itens[1][2].value = "Cronômetro"
            nav_itens[2][2].value = f"Concluídas ({conc})"
            nav_itens[3][2].value = "Estatísticas"
        rotulo_sessoes.value = f"{ESTADO['sessoes']} sessões"
        atualizar_estatisticas()
        page.update()

    def atualizar_listas():
        filtro = ESTADO["filtro"].lower()
        pendentes = [t for t in ESTADO["tarefas"]
                     if not t["concluida"] and (not filtro or filtro in t["nome"].lower())]
        concluidas = [t for t in ESTADO["tarefas"] if t["concluida"]]
        lista_pendentes.controls.clear()
        for t in pendentes:
            lista_pendentes.controls.append(criar_cartao_pendente(t))
        lista_concluidas.controls.clear()
        for t in concluidas:
            lista_concluidas.controls.append(criar_cartao_concluida(t))
        vazio_pendentes.visible = len(pendentes) == 0
        vazio_concluidas.visible = len(concluidas) == 0
        atualizar_contadores()
        page.update()

    # ---------------- Estatísticas ----------------
    def registrar_sessao(tipo, minutos, nome):
        ESTADO["historico"].append({
            "data": date.today().isoformat(),
            "hora": time.strftime("%H:%M"),
            "tipo": tipo,
            "min": minutos,
            "nome": nome,
        })
        salvar_historicos()
        atualizar_estatisticas()

    def atualizar_estatisticas():
        hoje = date.today().isoformat()
        hoje_list = [s for s in ESTADO["historico"] if s["data"] == hoje]
        foco_hoje = [s for s in hoje_list if s["tipo"] != "DESCANSO"]
        min_hoje = sum(s["min"] for s in foco_hoje)
        total = len(ESTADO["historico"])
        pend = sum(1 for t in ESTADO["tarefas"] if not t["concluida"])
        conc = sum(1 for t in ESTADO["tarefas"] if t["concluida"])
        taxa = int(round(100 * conc / (conc + pend))) if (conc + pend) else 0

        feitos = len(foco_hoje)
        meta = max(1, ESTADO["meta"])
        progresso_meta.value = f"{feitos}/{meta} hoje"
        barra_meta.value = min(1.0, feitos / meta)
        rotulo_hoje.value = f"{len(foco_hoje)} sessões de foco · {min_hoje} min hoje"
        rotulo_total.value = f"Total de sessões registradas: {total}"
        rotulo_concl.value = f"Taxa de conclusão: {taxa}%"

        lista_historico.controls.clear()
        for s in reversed(ESTADO["historico"][-20:]):
            lista_historico.controls.append(
                ft.Row([
                    ft.Icon(ft.Icons.CHECK_CIRCLE, color=T()["ok_i"], size=18),
                    ft.Text(f"{s['data'][5:]} {s['hora']} · {s['nome']}", size=13,
                            color=T()["texto"], expand=True),
                    ft.Text(f"{s['min']} min", size=12, color=T()["subt"]),
                ], vertical_alignment=ft.CrossAxisAlignment.CENTER, spacing=6)
            )
        vazio_historico.visible = len(ESTADO["historico"]) == 0
        page.update()

    def definir_meta(e):
        try:
            m = int((campo_meta.value or "").strip())
        except ValueError:
            m = 4
        ESTADO["meta"] = max(1, m)
        salvar_historicos()
        atualizar_estatisticas()
        avisar(f"Meta diária definida em {ESTADO['meta']} pomodoros.")

    def limpar_historico(e):
        ESTADO["historico"] = []
        salvar_historicos()
        atualizar_estatisticas()
        avisar("Histórico apagado.")

    def limpar_cronometro():
        ESTADO["tempo_total"] = 0
        ESTADO["tempo_restante"] = 0
        nome_tarefa_atual.value = "Nenhuma tarefa selecionada"
        tipo_atual.value = ""
        relogio.value = "00:00"
        relogio.color = T()["titulo"]
        barra_progresso.value = 0
        rotulo_percent.value = "0%"
        rotulo_decorrido.value = "Decorrido 00:00 · Falta 00:00"
        page.title = "Pomodoro"

    # ---------------- Cronômetro ----------------
    def atualizar_visual_cronometro():
        relogio.value = formatar(ESTADO["tempo_restante"])
        if ESTADO["tempo_total"] > 0:
            pct = ESTADO["tempo_restante"] / ESTADO["tempo_total"]
            barra_progresso.value = max(0.0, min(1.0, pct))
            rotulo_percent.value = f"{int(pct * 100)}%"
            decorrido = ESTADO["tempo_total"] - ESTADO["tempo_restante"]
            rotulo_decorrido.value = (f"Decorrido {formatar(decorrido)} · "
                                      f"Falta {formatar(ESTADO['tempo_restante'])}")
        else:
            barra_progresso.value = 0
            rotulo_percent.value = "0%"
            rotulo_decorrido.value = "Decorrido 00:00 · Falta 00:00"
        if ESTADO["tempo_total"] > 0 and ESTADO["tempo_restante"] <= ESTADO["tempo_total"] * 0.2:
            relogio.color = T()["alerta"]
        else:
            relogio.color = T()["titulo"]
        if ESTADO["rodando"]:
            page.title = f"{formatar(ESTADO['tempo_restante'])} · Pomodoro"
        else:
            page.title = "Pomodoro"
        page.update()

    def carregar_tarefa(t):
        ESTADO["rodando"] = False
        ESTADO["tarefa_atual"] = t
        ESTADO["tempo_total"] = t["tempo_total_s"]
        ESTADO["tempo_restante"] = t["tempo_total_s"]
        nome_tarefa_atual.value = t["nome"]
        tipo_atual.value = "TAREFA"
        atualizar_visual_cronometro()
        mostrar_aba(1)

    def carregar_sessao(tipo, minutos):
        ESTADO["rodando"] = False
        ESTADO["tarefa_atual"] = None
        ESTADO["tempo_total"] = minutos * 60
        ESTADO["tempo_restante"] = minutos * 60
        nome_tarefa_atual.value = f"Sessão de {tipo}"
        tipo_atual.value = tipo.upper()
        atualizar_visual_cronometro()
        mostrar_aba(1)

    def iniciar(e):
        if ESTADO["rodando"]:
            return
        if ESTADO["tempo_restante"] <= 0:
            avisar("Defina um tempo (tarefa ou estudo/descanso).")
            return
        ESTADO["rodando"] = True
        page.run_thread(tick)

    def pausar(e):
        ESTADO["rodando"] = False
        page.title = "Pomodoro"
        page.update()

    def resetar(e):
        ESTADO["rodando"] = False
        ESTADO["tempo_restante"] = ESTADO["tempo_total"]
        atualizar_visual_cronometro()

    def entrar_descanso():
        try:
            mins = int((campo_descanso.value or "").strip())
        except ValueError:
            mins = 5
        carregar_sessao("Descanso", max(1, mins))

    def finalizar():
        ESTADO["rodando"] = False
        tipo_fim = tipo_atual.value or "TAREFA"
        min_fim = max(1, ESTADO["tempo_total"] // 60)
        nome_fim = (ESTADO["tarefa_atual"]["nome"] if ESTADO["tarefa_atual"] is not None
                    else f"Sessão {tipo_fim.lower()}")
        tocar_alarme()
        if tipo_fim != "DESCANSO":
            ESTADO["sessoes"] += 1
        atualizar_contadores()
        if ESTADO["tarefa_atual"] is not None and not ESTADO["tarefa_atual"]["concluida"]:
            ESTADO["tarefa_atual"]["concluida"] = True
            salvar_dados()
            atualizar_listas()
        registrar_sessao(tipo_fim, min_fim, nome_fim)
        avisar("Pomodoro concluído! 🎉")
        if ESTADO["auto_descanso"]:
            entrar_descanso()
        else:
            limpar_cronometro()
            atualizar_visual_cronometro()
            mostrar_aba(0)

    def concluir_agora(e):
        ESTADO["rodando"] = False
        finalizar()

    def tick():
        while ESTADO["rodando"] and ESTADO["tempo_restante"] > 0:
            time.sleep(1)
            ESTADO["tempo_restante"] -= 1
            atualizar_visual_cronometro()
        if ESTADO["tempo_restante"] <= 0:
            finalizar()

    def ao_teclar(e):
        try:
            k = (e.key or "").strip().lower()
            if k in (" ", "space", "spacebar"):
                if ESTADO["rodando"]:
                    pausar(None)
                else:
                    iniciar(None)
            elif k == "r":
                resetar(None)
        except Exception:
            pass
    page.on_keyboard_event = ao_teclar

    # ---------------- Config / toggles ----------------
    def ao_som(e):
        ESTADO["som"] = switch_som.value

    def ao_auto(e):
        ESTADO["auto_descanso"] = switch_auto.value

    def estudar_agora(e):
        try:
            mins = int((campo_estudo.value or "").strip())
        except ValueError:
            mins = 25
        carregar_sessao("Estudo", max(1, mins))

    def descansar_agora(e):
        entrar_descanso()

    # ---------------- Navegação e tema ----------------
    def mostrar_aba(indice, mudar=True):
        ESTADO["aba_atual"] = indice
        aba_tarefas.visible = indice == 0
        aba_cronometro.visible = indice == 1
        aba_concluidas.visible = indice == 2
        aba_estatisticas.visible = indice == 3
        for i, (cont, ic, tx) in enumerate(nav_itens):
            ativo = i == indice
            cont.bgcolor = T()["nav_ativo"] if ativo else T()["nav_inativo"]
            cor = T()["nav_ativo_t"] if ativo else T()["nav_inativo_t"]
            ic.color = cor
            tx.color = cor
        if mudar:
            page.update()

    def aplicar_visual():
        page.bgcolor = T()["fundo"]
        icone_app.color = T()["titulo"]
        titulo_app.color = T()["titulo"]
        subt_app.color = T()["subt"]
        rotulo_sessoes.color = T()["titulo"]
        chip_sessoes.bgcolor = T()["nav_ativo"]
        botao_tema.icon_color = T()["titulo"]
        botao_tema.icon = (ft.Icons.LIGHT_MODE if ESTADO["tema"] == "escura"
                           else ft.Icons.DARK_MODE)
        nome_tarefa_atual.color = T()["titulo"]
        tipo_atual.color = T()["subt"]
        relogio.color = T()["titulo"]
        barra_progresso.color = T()["titulo"]
        barra_progresso.bgcolor = T()["progresso"]
        rotulo_percent.color = T()["titulo"]
        rotulo_decorrido.color = T()["subt"]
        botao_iniciar.icon_color = T()["play_i"]
        botao_iniciar.bgcolor = T()["play_bg"]
        botao_pausar.icon_color = T()["pause_i"]
        botao_pausar.bgcolor = T()["pause_bg"]
        botao_resetar.icon_color = T()["reset_i"]
        botao_resetar.bgcolor = T()["reset_bg"]
        vazio_pendentes.color = T()["subt"]
        vazio_concluidas.color = T()["subt"]
        rotulo_som.color = T()["texto"]
        rotulo_auto.color = T()["texto"]
        lbl_prioridade.color = T()["subt"]
        lbl_pendentes.color = T()["titulo"]
        lbl_sessoes_rapidas.color = T()["titulo"]
        lbl_concluidas.color = T()["titulo"]
        rotulo_hoje.color = T()["texto"]
        rotulo_total.color = T()["texto"]
        rotulo_concl.color = T()["texto"]
        rotulo_meta.color = T()["titulo"]
        progresso_meta.color = T()["titulo"]
        barra_meta.color = T()["titulo"]
        barra_meta.bgcolor = T()["progresso"]
        lbl_estatisticas.color = T()["titulo"]
        lbl_historico_recente.color = T()["titulo"]
        vazio_historico.color = T()["subt"]
        mostrar_aba(ESTADO.get("aba_atual", 0), mudar=False)
        selecionar_prio(ESTADO["prio_nova"])
        atualizar_listas()
        page.update()

    def mudar_tema(e):
        ESTADO["tema"] = "escura" if ESTADO["tema"] == "clara" else "clara"
        aplicar_visual()

    # ---------------- Labels auxiliares ----------------
    lbl_prioridade = ft.Text("Prioridade", size=12, color=T()["subt"])
    lbl_pendentes = ft.Text("Pendentes", weight=ft.FontWeight.BOLD, size=15, color=T()["titulo"])
    lbl_sessoes_rapidas = ft.Text("Sessões rápidas", weight=ft.FontWeight.BOLD, size=15, color=T()["titulo"])
    # ---------------- Estatísticas (controles) ----------------
    lbl_concluidas = ft.Text("Tarefas concluídas", weight=ft.FontWeight.BOLD, size=16, color=T()["titulo"])
    lbl_estatisticas = ft.Text("Estatísticas", weight=ft.FontWeight.BOLD, size=16, color=T()["titulo"])
    rotulo_hoje = ft.Text("0 sessões de foco · 0 min hoje", size=14, color=T()["texto"])
    rotulo_total = ft.Text("Total de sessões registradas: 0", size=14, color=T()["texto"])
    rotulo_concl = ft.Text("Taxa de conclusão: 0%", size=14, color=T()["texto"])
    rotulo_meta = ft.Text("Meta diária", size=15, weight=ft.FontWeight.BOLD, color=T()["titulo"])
    progresso_meta = ft.Text("0/4 hoje", size=16, weight=ft.FontWeight.BOLD, color=T()["titulo"])
    barra_meta = ft.ProgressBar(value=0, color=T()["titulo"], bgcolor=T()["progresso"],
                                bar_height=8, border_radius=4)
    campo_meta = ft.TextField(label="Meta/dia", value="4", width=90,
                              keyboard_type=ft.KeyboardType.NUMBER)
    botao_definir_meta = ft.FilledTonalButton("Definir", icon=ft.Icons.SAVE)
    lbl_historico_recente = ft.Text("Histórico recente", weight=ft.FontWeight.BOLD, size=15, color=T()["titulo"])
    lista_historico = ft.ListView(expand=True, spacing=6, padding=4)
    vazio_historico = ft.Text("Nenhuma sessão registrada ainda. É só começar! 🍅",
                              size=14, color=T()["subt"], text_align=ft.TextAlign.CENTER, visible=True)
    botao_limpar_historico = ft.OutlinedButton("Limpar histórico", icon=ft.Icons.DELETE_SWEEP)

    # ---------------- Barra de navegação ----------------
    def criar_nav(icone, rotulo, indice):
        ic = ft.Icon(icone, size=19)
        tx = ft.Text(rotulo, size=13, weight=ft.FontWeight.BOLD)
        cont = ft.Container(
            content=ft.Row([ic, tx], alignment=ft.MainAxisAlignment.CENTER, spacing=5),
            padding=8, border_radius=10, expand=True, ink=True,
            on_click=lambda e: mostrar_aba(indice),
        )
        nav_itens.append((cont, ic, tx))
        return cont

    header = ft.Row([
        icone_app,
        ft.Column([titulo_app, subt_app], spacing=0),
        ft.Container(expand=True),
        chip_sessoes,
        botao_tema,
    ], vertical_alignment=ft.CrossAxisAlignment.CENTER)

    barra_nav = ft.Row([
        criar_nav(ft.Icons.LIST, "Tarefas", 0),
        criar_nav(ft.Icons.TIMER, "Cronômetro", 1),
        criar_nav(ft.Icons.CHECK_CIRCLE, "Concluídas", 2),
        criar_nav(ft.Icons.TRENDING_UP, "Estatísticas", 3),
    ], spacing=6)

    # ---------------- Telas ----------------
    aba_tarefas = ft.Column([
        ft.Row([campo_nome, campo_min], spacing=8),
        botao_adicionar,
        lbl_prioridade,
        ft.Row([chip_baixa, chip_media, chip_alta], spacing=6),
        campo_pesquisa,
        ft.Row([lbl_pendentes, ft.Container(expand=True), botao_limpar_pendentes]),
        lista_pendentes,
        vazio_pendentes,
    ], spacing=10, expand=True)

    aba_cronometro = ft.Column([
        nome_tarefa_atual,
        tipo_atual,
        relogio,
        barra_progresso,
        ft.Row([rotulo_percent, ft.Container(expand=True), rotulo_decorrido]),
        ft.Row([botao_iniciar, botao_pausar, botao_resetar],
               alignment=ft.MainAxisAlignment.CENTER, spacing=26),
        botao_concluir,
        ft.Divider(),
        lbl_sessoes_rapidas,
        ft.Row([campo_estudo, campo_descanso], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        ft.Row([botao_estudar, botao_descansar], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        ft.Divider(),
        ft.Row([rotulo_som, switch_som], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
        ft.Row([rotulo_auto, switch_auto], alignment=ft.MainAxisAlignment.CENTER, spacing=8),
    ], spacing=14, expand=True, horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        scroll=ft.ScrollMode.AUTO)

    aba_concluidas = ft.Column([
        lbl_concluidas,
        ft.Row([ft.Container(expand=True), botao_limpar_concluidas]),
        lista_concluidas,
        vazio_concluidas,
    ], spacing=12, expand=True)

    aba_estatisticas = ft.Column([
        ft.Row([lbl_estatisticas, ft.Container(expand=True), botao_limpar_historico],
               vertical_alignment=ft.CrossAxisAlignment.CENTER),
        ft.Container(
            content=ft.Column([
                rotulo_hoje,
                rotulo_total,
                rotulo_concl,
            ], spacing=6),
            padding=12, border_radius=12, bgcolor=T()["cartao"],
        ),
        rotulo_meta,
        ft.Row([campo_meta, botao_definir_meta], spacing=8),
        progresso_meta,
        barra_meta,
        ft.Divider(),
        lbl_historico_recente,
        lista_historico,
        vazio_historico,
    ], spacing=12, expand=True)

    conteudo = ft.Column([
        header,
        barra_nav,
        aba_tarefas,
        aba_cronometro,
        aba_concluidas,
        aba_estatisticas,
    ], expand=True)

    # ---------------- Ligações (eventos) ----------------
    botao_adicionar.on_click = adicionar_tarefa
    campo_nome.on_submit = adicionar_tarefa
    campo_min.on_submit = adicionar_tarefa
    campo_pesquisa.on_change = ao_pesquisar
    botao_limpar_pendentes.on_click = limpar_pendentes
    botao_limpar_concluidas.on_click = limpar_concluidas
    botao_iniciar.on_click = iniciar
    botao_pausar.on_click = pausar
    botao_resetar.on_click = resetar
    botao_concluir.on_click = concluir_agora
    botao_estudar.on_click = estudar_agora
    botao_descansar.on_click = descansar_agora
    botao_tema.on_click = mudar_tema
    switch_som.on_change = ao_som
    switch_auto.on_change = ao_auto
    botao_definir_meta.on_click = definir_meta
    botao_limpar_historico.on_click = limpar_historico
    for cont, tx, p in prio_chips:
        cont.on_click = (lambda e, pr=p: selecionar_prio(pr))

    # ---------------- Inicialização ----------------
    carregar_dados()
    carregar_historicos()
    campo_meta.value = str(ESTADO["meta"])
    ESTADO["sessoes"] = 0
    selecionar_prio(ESTADO["prio_nova"])
    aplicar_visual()
    mostrar_aba(0)
    page.add(conteudo)


ft.app(target=main)
