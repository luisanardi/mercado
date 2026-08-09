import os
import sqlite3
import shutil
from datetime import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.core.audio import SoundLoader

# Fundo escuro ajustado para smartphone
Window.clearcolor = (0.07, 0.08, 0.11, 1)

class CardProduto(BoxLayout):
    """Card horizontal totalmente responsivo para tela de celular"""
    def __init__(self, codigo, nome, validade, qtd, status_txt, cor_fundo, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = None
        self.height = 75
        self.padding = [12, 8, 12, 8]
        self.spacing = 4

        with self.canvas.before:
            Color(*cor_fundo)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[8,])
        self.bind(pos=self._update_rect, size=self._update_rect)

        # Linha 1: Nome do produto e Badge do Status
        linha_topo = BoxLayout(orientation='horizontal', size_hint_y=None, height=26)
        
        lbl_nome = Label(
            text=f"[b]{nome}[/b]",
            markup=True,
            font_size='15sp',
            color=(1, 1, 1, 1),
            halign='left',
            valign='middle'
        )
        lbl_nome.bind(size=lbl_nome.setter('text_size'))

        lbl_status = Label(
            text=f"[b]{status_txt}[/b]",
            markup=True,
            font_size='11sp',
            size_hint_x=None,
            width=130,
            halign='right',
            valign='middle'
        )
        lbl_status.bind(size=lbl_status.setter('text_size'))

        linha_topo.add_widget(lbl_nome)
        linha_topo.add_widget(lbl_status)

        # Linha 2: Detalhes limpos (Cód / Validade / Qtd)
        lbl_detalhes = Label(
            text=f"Cód: {codigo}  |  Val: {validade}  |  Qtd: {qtd}",
            font_size='12sp',
            color=(0.88, 0.88, 0.88, 1),
            halign='left',
            valign='middle',
            size_hint_y=None,
            height=20
        )
        lbl_detalhes.bind(size=lbl_detalhes.setter('text_size'))

        self.add_widget(linha_topo)
        self.add_widget(lbl_detalhes)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size


class ItaloValidadeApp(App):

    def build(self):
        self.db_path = os.path.join(self.user_data_dir, "validade_supermercado.db")
        self.init_db()

        # Layout Principal com espaçamento adequado
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=8)

        # --- 1. CABEÇALHO ---
        header = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        
        lbl_title = Label(
            text="[b]ITALO[/b] SUPERMERCADO",
            markup=True,
            font_size='16sp',
            color=(0.95, 0.35, 0.3, 1),
            halign='left',
            valign='middle'
        )
        lbl_title.bind(size=lbl_title.setter('text_size'))

        btn_verificar = Button(
            text="VERIFICAR",
            size_hint_x=None,
            width=100,
            background_color=(0.7, 0.2, 0.3, 1),
            font_size='11sp',
            bold=True
        )
        btn_verificar.bind(on_press=self.verificar_validades_alerta)

        header.add_widget(lbl_title)
        header.add_widget(btn_verificar)
        main_layout.add_widget(header)

        # --- 2. BARRINHA DO BANCO DE DADOS ---
        db_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=36, spacing=4)
        
        btn_subir_db = Button(text="Subir DB", font_size='10sp', bold=True, background_color=(0.2, 0.4, 0.7, 1))
        btn_subir_db.bind(on_press=self.abrir_seletor_db)

        btn_import_sql = Button(text="Importar SQL", font_size='10sp', bold=True, background_color=(0.2, 0.6, 0.6, 1))
        btn_import_sql.bind(on_press=self.abrir_seletor_sql)

        btn_backup = Button(text="Backup", font_size='10sp', bold=True, background_color=(0.3, 0.5, 0.3, 1))
        btn_backup.bind(on_press=self.gerar_backup)

        db_bar.add_widget(btn_subir_db)
        db_bar.add_widget(btn_import_sql)
        db_bar.add_widget(btn_backup)
        main_layout.add_widget(db_bar)

        # --- 3. FORMULÁRIO ORGANIZADO ---
        form_grid = GridLayout(cols=2, size_hint_y=None, height=130, spacing=5)

        form_grid.add_widget(Label(text="Código:", font_size='12sp', halign='right', size_hint_x=0.35))
        self.txt_codigo = TextInput(hint_text="Ex: 7891000", multiline=False, font_size='12sp')
        form_grid.add_widget(self.txt_codigo)

        form_grid.add_widget(Label(text="Nome:", font_size='12sp', halign='right', size_hint_x=0.35))
        self.txt_nome = TextInput(hint_text="Ex: Leite Integral", multiline=False, font_size='12sp')
        form_grid.add_widget(self.txt_nome)

        form_grid.add_widget(Label(text="Validade:", font_size='12sp', halign='right', size_hint_x=0.35))
        self.txt_validade = TextInput(hint_text="DD/MM/AAAA", multiline=False, font_size='12sp')
        form_grid.add_widget(self.txt_validade)

        form_grid.add_widget(Label(text="Qtd:", font_size='12sp', halign='right', size_hint_x=0.35))
        self.txt_qtd = TextInput(hint_text="Ex: 10", multiline=False, input_filter='int', font_size='12sp')
        form_grid.add_widget(self.txt_qtd)

        main_layout.add_widget(form_grid)

        # Botão Salvar Produto
        btn_salvar = Button(
            text="SALVAR PRODUTO",
            size_hint_y=None,
            height=42,
            background_color=(0.15, 0.55, 0.25, 1),
            bold=True,
            font_size='13sp'
        )
        btn_salvar.bind(on_press=self.salvar_produto)
        main_layout.add_widget(btn_salvar)

        # --- 4. LISTA DE PRODUTOS (CARDS) ---
        self.scroll = ScrollView()
        self.list_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=6)
        self.list_container.bind(minimum_height=self.list_container.setter('height'))
        self.scroll.add_widget(self.list_container)

        main_layout.add_widget(self.scroll)

        # Carrega os produtos salvos
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

    # --- NAVEGADOR DE ARQUIVOS (PARA SUBIR .DB OU .SQL) ---
    def abrir_file_chooser(self, titulo, filtros, callback_sucesso):
        path_inicial = "/storage/emulated/0/Download"
        if not os.path.exists(path_inicial):
            path_inicial = os.path.expanduser("~")

        box = BoxLayout(orientation='vertical', padding=10, spacing=10)
        chooser = FileChooserListView(path=path_inicial, filters=filtros)
        box.add_widget(chooser)

        btn_bar = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=10)
        btn_cancelar = Button(text="Cancelar", background_color=(0.7, 0.2, 0.2, 1))
        btn_confirmar = Button(text="Carregar Arquivo", background_color=(0.2, 0.7, 0.3, 1), bold=True)

        popup = Popup(title=titulo, content=box, size_hint=(0.95, 0.9))

        def ao_confirmar(instance):
            if chooser.selection:
                arquivo_selecionado = chooser.selection[0]
                popup.dismiss()
                callback_sucesso(arquivo_selecionado)
            else:
                self.mostrar_popup("Aviso", "Selecione um arquivo na lista!")

        btn_cancelar.bind(on_press=popup.dismiss)
        btn_confirmar.bind(on_press=ao_confirmar)

        btn_bar.add_widget(btn_cancelar)
        btn_bar.add_widget(btn_confirmar)
        box.add_widget(btn_bar)

        popup.open()

    def abrir_seletor_db(self, instance):
        self.abrir_file_chooser("Selecione o arquivo .db", ["*.db", "*.sqlite"], self.importar_db_file)

    def abrir_seletor_sql(self, instance):
        self.abrir_file_chooser("Selecione o arquivo .sql", ["*.sql", "*.txt"], self.importar_sql_file)

    def importar_db_file(self, caminho_arquivo):
        try:
            shutil.copy(caminho_arquivo, self.db_path)
            self.init_db()
            self.carregar_produtos()
            self.mostrar_popup("Sucesso", "Banco de dados importado com sucesso!")
        except Exception as e:
            self.mostrar_popup("Erro", f"Falha ao importar .db:\n{str(e)}")

    def importar_sql_file(self, caminho_arquivo):
        try:
            with open(caminho_arquivo, 'r', encoding='utf-8') as f:
                sql_script = f.read()

            conn = self.get_connection()
            cursor = conn.cursor()
            cursor.executescript(sql_script)
            conn.commit()
            conn.close()

            self.carregar_produtos()
            self.mostrar_popup("Sucesso", "Script SQL importado com sucesso!")
        except Exception as e:
            self.mostrar_popup("Erro", f"Falha ao executar SQL:\n{str(e)}")

    def gerar_backup(self, instance):
        try:
            pasta_dest = "/storage/emulated/0/Download"
            if not os.path.exists(pasta_dest):
                pasta_dest = self.user_data_dir

            data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(pasta_dest, f"backup_validade_{data_str}.db")

            shutil.copy(self.db_path, backup_path)
            self.mostrar_popup("Backup Concluído", f"Salvo em Downloads:\nbackup_validade_{data_str}.db")
        except Exception as e:
            self.mostrar_popup("Erro", f"Falha ao gerar backup:\n{str(e)}")

    # --- CÁLCULO DE DIAS E ALERTAS ---
    def calcular_status(self, data_str):
        try:
            data_val = datetime.strptime(data_str, "%d/%m/%Y").date()
            hoje = datetime.now().date()
            dias = (data_val - hoje).days

            if dias < 0:
                return f"[ VENCIDO ({abs(dias)}d) ]", (0.45, 0.12, 0.12, 1)
            elif dias <= 3:
                return f"[ VENCE EM {dias}d ]", (0.55, 0.40, 0.08, 1)
            else:
                return "[ NO PRAZO ]", (0.10, 0.35, 0.18, 1)
        except ValueError:
            return "[ DATA INVÁLIDA ]", (0.25, 0.25, 0.25, 1)

    def carregar_produtos(self):
        self.list_container.clear_widgets()
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT codigo, nome, validade, qtd FROM produtos")
        produtos = cursor.fetchall()
        conn.close()

        for codigo, nome, validade, qtd in produtos:
            status_txt, cor_fundo = self.calcular_status(validade)
            card = CardProduto(
                codigo=codigo,
                nome=nome,
                validade=validade,
                qtd=qtd,
                status_txt=status_txt,
                cor_fundo=cor_fundo
            )
            self.list_container.add_widget(card)

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

    def tocar_som(self):
        try:
            sound = SoundLoader.load('alerta.wav')
            if sound:
                sound.play()
            else:
                print('\a')
        except Exception:
            pass

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

        if vencidos > 0 or vencendo > 0:
            self.tocar_som()

        msg = f"Produtos Vencidos: {vencidos}\nProdutos Vencendo (até 3 dias): {vencendo}"
        self.mostrar_popup("Resumo de Validades", msg)

    def mostrar_popup(self, titulo, mensagem):
        box = BoxLayout(orientation='vertical', padding=15, spacing=10)
        box.add_widget(Label(text=mensagem, halign='center', font_size='13sp'))
        btn_fechar = Button(text="OK", size_hint_y=None, height=40, bold=True)
        box.add_widget(btn_fechar)

        popup = Popup(title=titulo, content=box, size_hint=(0.85, 0.35))
        btn_fechar.bind(on_press=popup.dismiss)
        popup.open()

if __name__ == '__main__':
    ItaloValidadeApp().run()
