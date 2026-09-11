import flet as ft

def main(page: ft.Page):
    page.title = "Sabrina Carpenter"
    page.bgcolor = "#000000"  # Cor de fundo da página

    # Configurações de tamanho da janela
    page.window.width = 390
    page.window.height = 844

    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    page.add(
        ft.Text(value="Sabrina Carpenter", size=40, weight=ft.FontWeight.BOLD, color="#FF00CC"),
        ft.Text(value="Bem-vinda ao app da Sabrina!", size=24, weight=ft.FontWeight.BOLD, color="#B4B4B4")
    )
    page.update()

ft.app(target=main)
