import flet as ft

def main(page: ft.Page):
    page.title = "Sabrina Carpenter"
    page.bgcolor = "#32113C"  # Cor de fundo da página
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    input_nome = ft.TextField(
        hint_text="Insira seu nome aqui", 
        color="#A60085",
        text_style=ft.TextStyle(weight=ft.FontWeight.BOLD)
    )

    card_input = ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Container(width=10), 
                    ft.Column(
                        [
                            ft.Text("Insira seu nome abaixo", size=14, color="#A60085"),
                            input_nome,
                        ],
                        tight=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=15,
            width=380,
            bgcolor="#1A0822", 
            border_radius=11,
        )
    )

    texto_resultado = ft.Text(value="", size=20, weight=ft.FontWeight.BOLD, color="#FF00CC")
    
    card_resultado = ft.Card(
        visible=False,
        content=ft.Container(
            content=texto_resultado,
            padding=20,
            bgcolor="#1A0822",
            border_radius=11,
        )
    )

    def salvar_clique(e):
        if input_nome.value:
            texto_resultado.value = f"Olá, {input_nome.value}!"
            card_resultado.visible = True
            input_nome.value = ""
            page.update()

    # Botão corrigido
    botao_salvar = ft.ElevatedButton(
        "Salvar Nome", 
        style=ft.ButtonStyle(
            color="#FFFFFF",
            bgcolor="#FF00CC"
        ),
        on_click=salvar_clique
    )

    page.add(
        ft.Text(value="Sabrina Carpenter", size=50, weight=ft.FontWeight.BOLD, color="#FF00CC"),
        ft.Text(value="Bem-vinda ao app da Sabrina!", size=25, weight=ft.FontWeight.BOLD, color="#FCFBFB"),
        ft.Container(height=20),
        card_input,
        botao_salvar,
        card_resultado
    )

ft.app(main, view=ft.AppView.WEB_BROWSER)