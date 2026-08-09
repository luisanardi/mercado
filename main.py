import os
import sqlite3
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

# Define fundo escuro padronizado conforme o visual da imagem
Window.clearcolor = (0.08, 0.09, 0.12, 1)

class ItaloValidadeApp(App):

    def build(self):
        # Define o caminho do banco de dados na pasta do app (Android / Desktop)
        self.db_path = os.path.join(self.user_data_dir, "validade_supermercado.db")
        self.init_db()

        # Layout Principal (Vertical)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)

        # ------------------- 1. CABEÇALHO -------------------
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        
        lbl_title = Label(
            text="[b]ITALO SUPERMERCADO[/b]",
            markup=True,
            font_size='22sp',
            color=(1, 0.3, 0.2, 1),
            halign='left'
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))

        btn_verificar = Button(
            text="🔔 Verificar Validades",
            size_hint_x=None,
            width=170,
            background_color=(0.8, 0.2, 0.4, 1)
        )
        btn_verificar.bind(on_press=self.verificar_validades_alerta)

        header.add_widget(lbl_title)
        header.add_widget(btn_verificar)
        main_layout.add_widget(header)

        # ------------------- 2. GERENCIADOR DE BANCO DE DADOS -------------------
        db_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        
        btn_backup = Button(text="💾 Gerar Backup", background_color=(0.2, 0.5, 0.8, 1))
        btn_backup.bind(on_press=self.gerar_backup)
        
        lbl_db_status = Label(
            text=f"BD: {os.path.basename(self.db_path)}",
            font_size='11sp',
            color=(0.7, 0.7, 0.7, 1)
        )

        db_bar.add_widget(btn_backup)
        db_bar.add_widget(lbl_db_status)
        main_layout.add_widget(db_bar)

        # ------------------- 3. FORMULÁRIO DE CADASTRO -------------------
        form_box = BoxLayout(orientation='vertical', size_hint_y=None, height=130, spacing=5)
        
        # Linha 1: Código e Nome
        l1 = BoxLayout(orientation='horizontal', spacing=5)
        self.txt_codigo = TextInput(hint_text="Código", multiline=False)
        self.txt_nome = TextInput(hint_text="Nome do Produto", multiline=False)
        l1.add_widget(self.txt_codigo)
        l1.add_widget(self.txt_nome)

        # Linha 2: Validade e Quantidade
        l2 = BoxLayout(orientation='horizontal', spacing=5)
        self.txt_validade = TextInput(hint_text="Validade (DD/MM/AAAA)", multiline=False)
        self.txt_qtd = TextInput(hint_text="Qtd", multiline=False, input_filter='int')
        l2.add_widget(self.txt_validade)
        l2.add_widget(self.txt_qtd)

        # Botão Salvar
        btn_salvar = Button(
            text="💾 Salvar / Atualizar Produto",
            size_hint_y=None,
            height=40,
            background_color=(0.2, 0.7, 0.3, 1)
        )
        btn_salvar.bind(on_press=self.salvar_produto)

        form_box.add_widget(l1)
        form_box.add_widget(l2)
        form_box.add_widget(btn_salvar)
        main_layout.add_widget(form_box)

        # ------------------- 4. TABELA DE PRODUTOS -------------------
        # Títulos das Colunas
        grid_header = GridLayout(cols=5, size_hint_y=None, height=30)
        headers = ["Código", "Produto", "Validade", "Qtd", "Status"]
        for h in headers:
            grid_header.add_widget(Label(text=f"[b]{h}[/b]", markup=True, font_size='12sp', color=(0.8, 0.8, 0.8, 1)))
        main_layout.add_widget(grid_header)

        # Area de rolagem para os produtos
        self.scroll = ScrollView()
        self.grid_produtos = GridLayout(cols=1, size_hint_y=None, spacing=2)
        self.grid_produtos.bind(minimum_height=self.grid_produtos.setter('height'))
        self.scroll.add_widget(self.grid_produtos)
        
        main_layout.add_widget(self.scroll)

        # Carrega os dados na inicialização
        self.carregar_produtos()

        return main_layout

    # --- BANCO DE DADOS ---
    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS produtos (
                codigo TEXT PRIMARY KEY,
                nome TEXT NOT NULL,
                validade TEXT NOT NULL,
                qtd INTEGER NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    # --- REGRAS DE NEGÓCIO E ALERTAS ---
    def calcular_status(self, data_str):
        try:
            data_val = datetime.strptime(data_str, "%d/%m/%Y").date()
            hoje = datetime.now().date()
            dias = (data_val - hoje).days

            if dias < 0:
                return f"🔴 VENCIDO ({abs(dias)}d)", (0.5, 0.1, 0.1, 1)
            elif dias <= 3:
                return f"⚠️ VENCE EM {dias} DIA(S)", (0.6, 0.5, 0.1, 1)
            else:
                return f"🟢 NO PRAZO", (0.1, 0.4, 0.2, 1)
        except ValueError:
            return "❌ DATA INVÁLIDA", (0.3, 0.3, 0.3, 1)

    def carregar_produtos(self):
        self.grid_produtos.clear_widgets()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nome, validade, qtd FROM produtos")
        produtos = cursor.fetchall()
        conn.close()

        for prod in produtos:
            codigo, nome, validade, qtd = prod
            status_txt, cor_fundo = self.calcular_status(validade)

            row = GridLayout(cols=5, size_hint_y=None, height=35, spacing=2)
            
            # Aplica a cor de fundo correspondente ao status (Vermelho, Laranja ou Verde)
            with row.canvas.before:
                Color(*cor_fundo)
                Rectangle(pos=row.pos, size=row.size)
            row.bind(pos=self._update_rect, size=self._update_rect)

            row.add_widget(Label(text=str(codigo), font_size='11sp'))
            row.add_widget(Label(text=str(nome), font_size='11sp'))
            row.add_widget(Label(text=str(validade), font_size='11sp'))
            row.add_widget(Label(text=str(qtd), font_size='11sp'))
            row.add_widget(Label(text=status_txt, font_size='10sp', bold=True))

            self.grid_produtos.add_widget(row)

    def _update_rect(self, instance, value):
        instance.canvas.before.clear()
        with instance.canvas.before:
            # Pega a cor calculada ou padrão
            status_lbl = instance.children[0].text if instance.children else ""
            if "VENCIDO" in status_lbl:
                Color(0.4, 0.1, 0.1, 1)
            elif "VENCE" in status_lbl:
                Color(0.5, 0.4, 0.1, 1)
            else:
                Color(0.1, 0.3, 0.2, 1)
            Rectangle(pos=instance.pos, size=instance.size)

    def salvar_produto(self, instance):
        codigo = self.txt_codigo.text.strip()
        nome = self.txt_nome.text.strip()
        validade = self.txt_validade.text.strip()
        qtd = self.txt_qtd.text.strip()

        if not (codigo and nome and validade and qtd):
            self.mostrar_popup("Aviso", "Preencha todos os campos!")
            return

        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO produtos (codigo, nome, validade, qtd)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(codigo) DO UPDATE SET
                nome=excluded.nome,
                validade=excluded.validade,
                qtd=excluded.qtd
        ''', (codigo, nome, validade, int(qtd)))
        conn.commit()
        conn.close()

        self.txt_codigo.text = ""
        self.txt_nome.text = ""
        self.txt_validade.text = ""
        self.txt_qtd.text = ""

        self.carregar_produtos()
        self.mostrar_popup("Sucesso", "Produto salvo com sucesso!")

    def verificar_validades_alerta(self, instance):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT nome, validade FROM produtos")
        produtos = cursor.fetchall()
        conn.close()

        vencidos = 0
        vencendo = 0

        for nome, validade in produtos:
            try:
                data_val = datetime.strptime(validade, "%d/%m/%Y").date()
                dias = (data_val - datetime.now().date()).days
                if dias < 0:
                    vencidos += 1
                elif dias <= 3:
                    vencendo += 1
            except ValueError:
                pass

        msg = f"Produtos Vencidos: {vencidos}\nProdutos Vencendo (até 3 dias): {vencendo}"
        self.mostrar_popup("Resumo de Validades", msg)

    def gerar_backup(self, instance):
        backup_path = os.path.join(self.user_data_dir, "backup_validade.db")
        import shutil
        shutil.copy(self.db_path, backup_path)
        self.mostrar_popup("Backup Criado", f"Backup salvo em:\n{backup_path}")

    def mostrar_popup(self, titulo, mensagem):
        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        box.add_widget(Label(text=mensagem, halign='center'))
        btn_fechar = Button(text="OK", size_hint_y=None, height=40)
        box.add_widget(btn_fechar)

        popup = Popup(title=titulo, content=box, size_hint=(0.8, 0.4))
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    ItaloValidadeApp().run()
