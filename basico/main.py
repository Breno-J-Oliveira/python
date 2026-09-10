import flet as ft

# Contadora de números com flet

def main(pagina: ft.Page):
    pagina.title = "Contador de Números"

    # Centraliza na vertical e horizontal
    pagina.vertical_alignment = ft.MainAxisAlignment.CENTER
    pagina.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Define a cor de fundo da página
    pagina.bgcolor = "#F5F5F5"  # Cor de fundo da página

    # Contador de números
    contador = ft.Text("0", size=200, weight=ft.FontWeight.BOLD, color="#323232")  # Cor do texto do contador

    def adicionar(e):
        contador.value = str(int(contador.value) + 1)
        pagina.update()
        # aqui ao clicar adicionar +1

    def remover(e):
        contador.value = str(int(contador.value) - 1)
        pagina.update()
        # aqui ao clicar remover -1

    pagina.add(
        contador,
        ft.Row(
            [
                ft.ElevatedButton("Remover -1", on_click=remover),
                ft.ElevatedButton("Adicionar +1", on_click=adicionar),
            ],
            alignment=ft.MainAxisAlignment.CENTER
        )
    )

ft.app(main, view=ft.AppView.WEB_BROWSER)