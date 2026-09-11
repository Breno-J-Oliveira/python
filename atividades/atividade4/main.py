import flet as ft

def main(page: ft.Page):
    page.title = "Lista de Compras"
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.WHITE)

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    LARGURA = 360

    input_produto = ft.TextField(
        hint_text="Insira o produto aqui",
        color=ft.Colors.PURPLE,
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD),
        width=LARGURA,
    )

    lista_produtos = ft.Column(alignment=ft.MainAxisAlignment.CENTER)

    def remover_linha(linha):
        # Botão "-": remove a linha inteira do produto da lista.
        if linha in lista_produtos.controls:
            lista_produtos.controls.remove(linha)
            page.update()

    def criar_linha(produto):
        nome = ft.Text(
            produto, size=18, weight=ft.FontWeight.BOLD, color=ft.Colors.PINK, expand=True,
        )
        qtd_texto = ft.Text("1", size=18, weight=ft.FontWeight.BOLD)

        def adicionar(e):
            # Botão "+": soma 1 ao contador de quantidade.
            qtd_texto.value = str(int(qtd_texto.value) + 1)
            page.update()

        grupo_quantidade = ft.Row(
            [
                ft.IconButton(
                    icon=ft.Icons.REMOVE,
                    icon_color=ft.Colors.RED,
                    tooltip="Remover item",
                    on_click=lambda e: remover_linha(linha),
                ),
                qtd_texto,
                ft.IconButton(
                    icon=ft.Icons.ADD,
                    icon_color=ft.Colors.GREEN,
                    tooltip="Adicionar 1",
                    on_click=adicionar,
                ),
            ],
            spacing=4,
            alignment=ft.MainAxisAlignment.CENTER,
        )

        linha = ft.Row(
            [
                nome,
                grupo_quantidade,
            ],
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            width=LARGURA,
        )
        return linha

    def adicionar_produto(e):
        if input_produto.value and input_produto.value.strip():
            lista_produtos.controls.append(
                criar_linha(input_produto.value.strip())
            )
            input_produto.value = ""
            page.update()

    botao_inserir = ft.ElevatedButton("Inserir", on_click=adicionar_produto)

    page.add(
        input_produto,
        botao_inserir,
        lista_produtos,
    )


ft.app(target=main)