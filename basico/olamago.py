import flet as ft

def main(pagina: ft.Page):
    pagina.title = "Ola Mago"
    pagina.add(ft.Text("Ola Mago"))
    pagina.add(ft.Text("Bem-vindo ao Flet!"))

ft.run(main, view=ft.AppView.WEB_BROWSER)