import flet as ft

def main(page: ft.Page):
    page.title = "Sabrina Carpenter"
    page.bgcolor = "#32113C"  # Cor de fundo da página
    
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    card_email = ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.EMAIL, color="#FF00CC", size=30),
                    ft.Container(width=10), 
                    ft.Column(
                        [
                            ft.Text("E-mail para Contato", size=14, color="#A60085"),
                            ft.Text("sabrinacarpenter@gmail.com", size=16, weight=ft.FontWeight.BOLD, color="#A60085"),
                        ],
                        tight=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=15,
            width=350,
            bgcolor="#1A0822", 
            border_radius=11,
        )
    )

    card_telefone = ft.Card(
        content=ft.Container(
            content=ft.Row(
                [
                    ft.Icon(ft.Icons.PHONE, color="#FF00CC", size=30), 
                    ft.Container(width=10), 
                    ft.Column(
                        [
                            ft.Text("Telefone", size=14, color="#A60085"),
                            ft.Text("4002-8922", size=16, weight=ft.FontWeight.BOLD, color="#A60085"),
                        ],
                        tight=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            padding=15,
            width=350,
            bgcolor="#1A0822",
            border_radius=11,
        )
    )

    # Adiciona tudo na tela
    page.add(
        ft.Text(value="Sabrina Carpenter", size=50, weight=ft.FontWeight.BOLD, color="#FF00CC"),
        ft.Text(value="Bem-vinda ao app da Sabrina!", size=25, weight=ft.FontWeight.BOLD, color="#FCFBFB"),
        ft.Container(height=20), 
        card_email,
        card_telefone
    )

    page.update()

ft.app(target=main)
