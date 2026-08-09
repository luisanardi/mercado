import sqlite3
import datetime
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window

# Fundo escuro para a interface
Window.clearcolor = (0.12, 0.12, 0.18, 1)

class SistemaValidadeApp(App):
    def build(self):
        self.title = "ITALO SUPERMERCADO - Validade"
        self.db_caminho = "validade_supermercado.db"
        self.conectar_banco()

        layout_principal = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # Topo / Banner 3D Simulado
        header = Label(
            text="[b][color=f38ba8]ITALO[/color] [color=ffffff]SUPERMERCADO[/color][/b]",
            markup=True,
            font_size='26sp',
            size_hint_y=None,
            height=60
        )
        layout_principal.add_widget(header)

        # Formulário de Cadastro
        form_layout = GridLayout(cols=2, spacing=8, size_hint_y=None, height=180)

        form_layout.add_widget(Label(text="Código:", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.txt_codigo = TextInput(multiline=False, write_tab=False)
        form_layout.add_widget(self.txt_codigo)

        form_layout.add_widget(Label(text="Nome:", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.txt_nome = TextInput(multiline=False, write_tab=False)
        form_layout.add_widget(self.txt_nome)

        form_layout.add_widget(Label(text="Validade (DD/MM/AAAA):", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.txt_validade = TextInput(multiline=False, write_tab=False)
        form_layout.add_widget(self.txt_validade)

        form_layout.add_widget(Label(text="Quantidade:", font_size='14sp', color=(0.8, 0.8, 0.8, 1)))
        self.txt_qtd = TextInput(multiline=False, write_tab=False, text="1")
        form_layout.add_widget(self.txt_qtd)

        layout_principal.add_widget(form_layout)

        # Botão Salvar
        btn_salvar = Button(
            text="💾 Salvar Produto",
            background_color=(0.65, 0.89, 0.63, 1),
            color=(0.06, 0.06, 0.1, 1),
            bold=True,
            size_hint_y=None,
            height=45
        )
        btn_salvar.bind(on_press=self.salvar_produto)
        layout_principal.add_widget(btn_salvar)

        # Tabela / Lista de Produtos
        self.tabela_layout = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.tabela_layout.bind(minimum_height=self.tabela_layout.setter('height'))

        scroll = ScrollView(size_hint=(1, 1))
        scroll.add_widget(self.tabela_layout)
        layout_principal.add_widget(scroll)

        self.carregar_produtos()
        return layout_principal

    def conectar_banco(self):
        self.conn = sqlite3.connect(self.db_caminho)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                validade DATE NOT NULL,
                quantidade INTEGER DEFAULT 1
            )
        """)
        self.conn.commit()

    def salvar_produto(self, instance):
        cod = self.txt_codigo.text.strip()
        nome = self.txt_nome.text.strip()
        val_str = self.txt_validade.text.strip()
        qtd = self.txt_qtd.text.strip() or "1"

        if not cod or not nome or not val_str:
            self.mostrar_popup("Erro", "Preencha Código, Nome e Validade!")
            return

        try:
            val_dt = datetime.datetime.strptime(val_str, "%d/%m/%Y").date()
        except ValueError:
            self.mostrar_popup("Erro", "Formato de data inválido! Use DD/MM/AAAA")
            return

        self.cursor.execute("""
            INSERT OR REPLACE INTO produtos (codigo, nome, validade, quantidade)
            VALUES (?, ?, ?, ?)
        """, (cod, nome, val_dt.strftime("%Y-%m-%d"), int(qtd)))
        self.conn.commit()

        self.txt_codigo.text = ""
        self.txt_nome.text = ""
        self.txt_validade.text = ""
        self.txt_qtd.text = "1"

        self.carregar_produtos()
        self.mostrar_popup("Sucesso", "Produto cadastrado com sucesso!")

    def carregar_produtos(self):
        self.tabela_layout.clear_widgets()
        hoje = datetime.date.today()

        self.cursor.execute("SELECT codigo, nome, validade, quantidade FROM produtos ORDER BY validade ASC")
        produtos = self.cursor.fetchall()

        if not produtos:
            self.tabela_layout.add_widget(Label(text="Nenhum produto cadastrado.", size_hint_y=None, height=30))
            return

        for row in produtos:
            cod, nome, val_txt, qtd = row
            val_dt = datetime.datetime.strptime(val_txt, "%Y-%m-%d").date()
            dias = (val_dt - hoje).days
            val_fmt = val_dt.strftime("%d/%m/%Y")

            if dias < 0:
                cor = "[color=ff4d4d]" # Vermelho
                status = f"🔴 VENCIDO ({abs(dias)}d)"
            elif dias <= 2:
                cor = "[color=ffaa00]" # Laranja
                status = f"⚠️ VENCE EM {dias}d"
            else:
                cor = "[color=2ecc71]" # Verde
                status = "🟢 NO PRAZO"

            texto_item = f"{cor}[b]{nome}[/b]\nCód: {cod} | Val: {val_fmt} | Qtd: {qtd} | {status}[/color]"
            lbl = Label(text=texto_item, markup=True, size_hint_y=None, height=50, font_size='13sp')
            self.tabela_layout.add_widget(lbl)

    def mostrar_popup(self, titulo, mensagem):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=mensagem))
        btn = Button(text="OK", size_hint_y=None, height=40)
        box.add_widget(btn)
        
        popup = Popup(title=titulo, content=box, size_hint=(0.8, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    SistemaValidadeApp().run()