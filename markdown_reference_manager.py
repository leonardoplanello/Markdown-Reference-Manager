import sys
import os
import re
import unicodedata
import shutil
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel,
    QFileDialog, QDialog, QComboBox, QDialogButtonBox, QLineEdit
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QHeaderView


def remover_acentos(texto):
    """
    Remove acentos de uma string e normaliza para minúsculas.
    """
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)]).lower().strip()


def extrair_referencias(linha):
    """
    Extrai todas as referências dentro de colchetes duplos em uma linha.
    Retorna uma lista de tuplas (exact_ref, normalized_ref).
    """
    matches = re.findall(r'\[\[(.*?)\]\]', linha)
    referencias = []
    for match in matches:
        exact_ref = match.strip()
        normalized_ref = remover_acentos(match)
        if exact_ref:
            referencias.append((exact_ref, normalized_ref))
    return referencias


def agrupar_por_palavras_comuns(referencias):
    """
    Agrupa referências por palavras em comum, sem ignorar stopwords.
    :param referencias: Dicionário {arquivo: [(linha, exact_text)]}.
    :return: Dicionário {palavra_comum: [(arquivo, linha, exact_text)]}.
    """
    grupos = defaultdict(list)

    for arquivo, ocorrencias in referencias.items():
        for linha, exact_text in ocorrencias:
            # Extrair todas as palavras (incluindo stopwords)
            palavras = set(remover_acentos(exact_text).split())
            for palavra in palavras:
                grupos[palavra].append((arquivo, linha, exact_text))

    # Filtrar grupos com textos distintos
    grupos_filtrados = {
        palavra: lista
        for palavra, lista in grupos.items()
        if len({oc[2] for oc in lista}) > 1  # Verifica se há textos diferentes
    }

    return grupos_filtrados


# Dicionário de traduções para as duas línguas suportadas
LANGUAGES = {
    'english': {
        'window_title': "Markdown Reference Manager",
        'instruction': "Select the directory containing your .md files.",
        'button_delete': "Delete",
        'button_undo': "Undo",
        'button_merge': "Rewrite",
        'feedback_deleted': "Deleted references: {files}",
        'feedback_merged': "Rewrote references to: {filename}",
        'feedback_undone': "Action undone: {action}",
        'error_no_files_selected': "No directory selected.",
        'error_merge_failed': "Error rewriting references: {error}",
        'error_delete_failed': "Error deleting references: {error}",
        'merge_dialog_title': "New Reference Name",
        'merge_dialog_instruction': "Enter the new name for the selected references:",
        'merge_dialog_ok': "OK",
        'merge_dialog_cancel': "Cancel",
        'warning_no_files_selected_delete': "No references selected to delete.",
        'warning_no_files_selected_merge': "No references selected to rewrite.",
        'info_no_common_words': "No repeated references found.",
        'language_selection_title': "Select Language",
        'language_selection_instruction': "Choose the application language:",
        'language_english': "English",
        'language_portuguese': "Portuguese (Brazilian)",
        'close_confirmation_title': "Quit",
        'close_confirmation_question': "Are you sure you want to quit?",
        'close_confirmation_yes': "Yes",
        'close_confirmation_no': "No",
    },
    'portuguese': {
        'window_title': "Gerenciador de Referências de Markdown",
        'instruction': "Selecione a pasta contendo seus arquivos .md.",
        'button_delete': "Apagar",
        'button_undo': "Desfazer",
        'button_merge': "Reescrever",
        'feedback_deleted': "Referências apagadas: {files}",
        'feedback_merged': "Referências reescritas para: {filename}",
        'feedback_undone': "Ação desfeita: {action}",
        'error_no_files_selected': "Nenhuma pasta selecionada.",
        'error_merge_failed': "Erro ao reescrever referências: {error}",
        'error_delete_failed': "Erro ao apagar referências: {error}",
        'merge_dialog_title': "Novo Nome da Referência",
        'merge_dialog_instruction': "Digite o novo nome para as referências selecionadas:",
        'merge_dialog_ok': "OK",
        'merge_dialog_cancel': "Cancelar",
        'warning_no_files_selected_delete': "Nenhuma referência selecionada para apagar.",
        'warning_no_files_selected_merge': "Nenhuma referência selecionada para reescrever.",
        'info_no_common_words': "Nenhuma referência repetida encontrada.",
        'language_selection_title': "Selecione o Idioma",
        'language_selection_instruction': "Escolha o idioma do aplicativo:",
        'language_english': "Inglês",
        'language_portuguese': "Português (Brasil)",
        'close_confirmation_title': "Sair",
        'close_confirmation_question': "Tem certeza de que deseja sair?",
        'close_confirmation_yes': "Sim",
        'close_confirmation_no': "Não",
    }
}


class LanguageSelectionDialog(QDialog):
    """
    Dialog para selecionar o idioma do aplicativo no início.
    """
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setWindowTitle(self.translations['language_selection_title'])
        self.setModal(True)
        self.selected_language = 'english'  # Padrão
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Label de instrução
        instruction = QLabel(self.translations['language_selection_instruction'])
        instruction.setFont(QFont("Arial", 12))
        layout.addWidget(instruction)

        # ComboBox para seleção de idioma
        self.combo_languages = QComboBox()
        self.combo_languages.addItem(self.translations['language_english'], 'english')
        self.combo_languages.addItem(self.translations['language_portuguese'], 'portuguese')
        self.combo_languages.setCurrentIndex(0)  # Padrão para inglês
        layout.addWidget(self.combo_languages)

        # Botões OK e Cancelar
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected_language(self):
        return self.combo_languages.currentData()


class NameSuggestionDialog(QDialog):
    """
    Dialog para sugerir e inserir novos nomes de referência.
    """
    def __init__(self, suggested_names, translations, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setWindowTitle(self.translations['merge_dialog_title'])
        self.setModal(True)
        self.suggested_names = suggested_names
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Label de instrução
        instruction = QLabel(self.translations['merge_dialog_instruction'])
        instruction.setFont(QFont("Arial", 12))
        layout.addWidget(instruction)

        # Campo de texto para inserir o novo nome
        self.input_new_name = QLineEdit()
        self.input_new_name.setText(self.suggested_names[0] if self.suggested_names else "")
        layout.addWidget(self.input_new_name)

        # Botões OK e Cancelar
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(self.translations['merge_dialog_ok'])
        buttons.button(QDialogButtonBox.Cancel).setText(self.translations['merge_dialog_cancel'])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_new_name(self):
        return self.input_new_name.text().strip()


class MarkdownReferenceManager(QWidget):
    def __init__(self, translations):
        super().__init__()
        self.translations = translations
        self.setWindowTitle(self.translations['window_title'])
        self.setGeometry(100, 100, 1200, 800)  # Ajustado para melhor visualização
        self.action_history = []  # Histórico para funcionalidade de desfazer
        self.initUI()

    def initUI(self):
        # Aplicar tema escuro
        self.apply_dark_theme()

        layout = QVBoxLayout()

        # Label de instrução
        instruction = QLabel(self.translations['instruction'])
        instruction.setFont(QFont("Arial", 14))
        instruction.setStyleSheet("color: white;")
        layout.addWidget(instruction)

        # Tree Widget para exibir referências
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Freq.", "Common Word", "File", "Line", "Exact Text"])
        self.tree.setColumnWidth(0, 50)    # Frequência
        self.tree.setColumnWidth(1, 300)   # Palavra Comum
        self.tree.setColumnWidth(2, 200)   # Arquivo
        self.tree.setColumnWidth(3, 100)   # Linha
        self.tree.setColumnWidth(4, 700)   # Texto Exato
        self.tree.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)  # Permitir seleção múltipla
        self.tree.setSelectionBehavior(QTreeWidget.SelectRows)     # Seleção por linha
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(False)  # Sem setas de expansão

        # Ajustar cabeçalhos para ajustar ao conteúdo
        self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)

        # Remover conexão de seleção personalizada
        # self.tree.itemClicked.connect(self.handle_item_clicked)  # Removido para usar seleção nativa

        layout.addWidget(self.tree)

        # Botões de ação
        button_layout = QHBoxLayout()

        self.btn_delete = QPushButton(self.translations['button_delete'])
        self.btn_delete.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_delete.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
        """)
        self.btn_delete.clicked.connect(self.delete_references)
        button_layout.addWidget(self.btn_delete)

        self.btn_undo = QPushButton(self.translations['button_undo'])
        self.btn_undo.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_undo.setStyleSheet("""
            QPushButton {
                background-color: #f0ad4e;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ec971f;
            }
        """)
        self.btn_undo.clicked.connect(self.undo_action)
        button_layout.addWidget(self.btn_undo)

        self.btn_merge = QPushButton(self.translations['button_merge'])
        self.btn_merge.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_merge.setStyleSheet("""
            QPushButton {
                background-color: #5cb85c;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #4cae4c;
            }
        """)
        self.btn_merge.clicked.connect(self.rewrite_reference)
        button_layout.addWidget(self.btn_merge)

        # Remoção do botão "Save Changes"
        # self.btn_save = QPushButton(self.translations['button_save'])
        # self.btn_save.setFont(QFont("Arial", 12, QFont.Bold))
        # self.btn_save.setStyleSheet("""
        #     QPushButton {
        #         background-color: #0275d8;
        #         color: white;
        #         padding: 10px;
        #         border-radius: 5px;
        #     }
        #     QPushButton:hover {
        #         background-color: #025aa5;
        #     }
        # """)
        # self.btn_save.clicked.connect(self.save_changes)
        # button_layout.addWidget(self.btn_save)

        layout.addLayout(button_layout)

        # Label de feedback
        self.feedback = QLabel("")
        self.feedback.setFont(QFont("Arial", 12))
        self.feedback.setStyleSheet("color: #28a745;")
        layout.addWidget(self.feedback)

        self.setLayout(layout)

        # Carregar e analisar arquivos
        self.load_and_analyze_files()

    def apply_dark_theme(self):
        """
        Aplica um tema escuro ao aplicativo.
        """
        dark_palette = QPalette()

        # Definir paleta de cores
        dark_palette.setColor(QPalette.Window, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.WindowText, Qt.white)
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
        dark_palette.setColor(QPalette.ToolTipText, Qt.white)
        dark_palette.setColor(QPalette.Text, Qt.white)
        dark_palette.setColor(QPalette.Button, QColor(43, 43, 43))
        dark_palette.setColor(QPalette.ButtonText, Qt.white)
        dark_palette.setColor(QPalette.BrightText, Qt.red)

        # Links
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, Qt.black)

        QApplication.instance().setPalette(dark_palette)
        QApplication.instance().setStyle("Fusion")

    def load_and_analyze_files(self):
        """
        Solicita ao usuário que selecione um diretório e analisa os arquivos .md nele.
        """
        # Abrir diálogo para selecionar diretório
        if self.translations['language_english'] == "English":
            directory = QFileDialog.getExistingDirectory(self, "Select folder with .md files")
        else:
            directory = QFileDialog.getExistingDirectory(self, "Selecione a pasta com arquivos .md")

        if not directory:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['error_no_files_selected']
            )
            sys.exit()

        # Listar todos os arquivos .md no diretório
        md_files = [f for f in os.listdir(directory) if f.lower().endswith('.md')]

        if not md_files:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['info_no_common_words']
            )
            sys.exit()

        # Analisar referências em todos os arquivos
        self.references = defaultdict(list)  # {arquivo: [(linha, exact_text)]}

        for file in md_files:
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        referencias = extrair_referencias(line)
                        for exact_ref, normalized_ref in referencias:
                            self.references[file].append((line_num, exact_ref))
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error" if self.translations['language_english'] == "English" else "Erro",
                    self.translations['error_merge_failed'].format(error=str(e))
                )
                sys.exit()

        # Agrupar referências por palavras em comum
        grupos_filtrados = agrupar_por_palavras_comuns(self.references)

        if not grupos_filtrados:
            QMessageBox.information(
                self,
                "Information" if self.translations['language_english'] == "English" else "Informação",
                self.translations['info_no_common_words']
            )
            sys.exit()

        # Ordenar grupos por frequência (decrescente)
        sorted_groups = sorted(grupos_filtrados.items(), key=lambda x: len(x[1]), reverse=True)

        # Preencher o Tree Widget
        for palavra, ocorrencias in sorted_groups:
            # Cada grupo é baseado em uma palavra comum
            freq = len(ocorrencias)
            # Para exibir referências distintas, coletar textos únicos
            refs_unicos = set([oc[2] for oc in ocorrencias])
            ref_combined = ", ".join(refs_unicos)

            group_item = QTreeWidgetItem([str(freq), palavra, "", "", ""])
            group_item.setFont(1, QFont("Arial", 12, QFont.Bold))
            group_item.setForeground(1, QColor(255, 255, 255))
            group_item.setExpanded(False)  # Inicialmente colapsado

            for oc in ocorrencias:
                arquivo, linha, exact_text = oc
                occurrence_item = QTreeWidgetItem(["", "", arquivo, str(linha), exact_text])
                # Remover checkboxes para utilizar seleção múltipla padrão
                occurrence_item.setFlags(occurrence_item.flags() | Qt.ItemIsSelectable | Qt.ItemIsEnabled)
                group_item.addChild(occurrence_item)

            self.tree.addTopLevelItem(group_item)

        self.directory = directory

    def delete_references(self):
        """
        Apaga as referências selecionadas de todas as ocorrências nos arquivos.
        """
        selected_items = self.tree.selectedItems()

        if not selected_items:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['warning_no_files_selected_delete']
            )
            return

        # Agrupar referências selecionadas por "Common Word" para deletar em lote
        common_words = set()
        for item in selected_items:
            common_word = item.parent().text(1)
            common_words.add(common_word)

        # Fazer backup dos arquivos originais
        backup_dir = os.path.join(self.directory, ".backup_reference_manager")
        os.makedirs(backup_dir, exist_ok=True)

        try:
            for ref in common_words:
                # Encontrar todas as ocorrências desta referência
                for i in range(self.tree.topLevelItemCount()):
                    group_item = self.tree.topLevelItem(i)
                    if group_item.text(1) == ref:
                        # Iterar pelos itens filhos (ocorrências)
                        for j in range(group_item.childCount()):
                            occurrence_item = group_item.child(j)
                            arquivo = occurrence_item.text(2)
                            linha = int(occurrence_item.text(3))
                            exact_text = occurrence_item.text(4)

                            src = os.path.join(self.directory, arquivo)
                            backup_path = os.path.join(backup_dir, arquivo)
                            shutil.copy2(src, backup_path)  # Backup do arquivo

                            # Ler o arquivo e remover a referência na linha específica
                            with open(src, 'r', encoding='utf-8') as f:
                                lines = f.readlines()

                            if 0 < linha <= len(lines):
                                # Remover a referência da linha
                                pattern = re.escape(exact_text)
                                lines[linha - 1] = re.sub(r'\[\[' + pattern + r'\]\]', '', lines[linha - 1], flags=re.IGNORECASE)
                                with open(src, 'w', encoding='utf-8') as f:
                                    f.writelines(lines)

            # Atualizar o Tree Widget e o histórico
            for ref in common_words:
                self.action_history.append({
                    'action': 'delete',
                    'reference': ref,
                    'backup_dir': backup_dir
                })
                self.remove_reference_from_tree(ref)

            # Fornecer feedback
            feedback_msg = self.translations['feedback_deleted'].format(files=", ".join(common_words))
            self.feedback.setText(feedback_msg)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error" if self.translations['language_english'] == "English" else "Erro",
                self.translations['error_delete_failed'].format(error=str(e))
            )

    def rewrite_reference(self):
        """
        Reescreve as referências selecionadas em todas as ocorrências nos arquivos.
        """
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['warning_no_files_selected_merge']
            )
            return

        # Agrupar referências selecionadas por "Common Word"
        common_words = set()
        for item in selected_items:
            common_word = item.parent().text(1)
            common_words.add(common_word)

        if len(common_words) > 1:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                "Selected references have different common words. Please select references with the same common word."
                if self.translations['language_english'] == "English" else
                "As referências selecionadas possuem palavras comuns diferentes. Por favor, selecione referências com a mesma palavra comum."
            )
            return

        common_word = common_words.pop()
        # Obter todas as ocorrências selecionadas
        selected_occurrences = [item for item in selected_items]

        # Dialog para inserir o novo nome da referência
        dialog = NameSuggestionDialog([common_word], self.translations, self)
        if dialog.exec_() == QDialog.Accepted:
            new_ref = dialog.get_new_name()
            if not new_ref:
                QMessageBox.warning(
                    self,
                    "Warning" if self.translations['language_english'] == "English" else "Aviso",
                    self.translations['warning_no_files_selected_merge']
                )
                return

            # Fazer backup dos arquivos originais
            backup_dir = os.path.join(self.directory, ".backup_reference_manager")
            os.makedirs(backup_dir, exist_ok=True)

            try:
                for occurrence_item in selected_occurrences:
                    arquivo = occurrence_item.text(2)
                    linha = int(occurrence_item.text(3))
                    exact_text = occurrence_item.text(4)

                    src = os.path.join(self.directory, arquivo)
                    backup_path = os.path.join(backup_dir, arquivo)
                    shutil.copy2(src, backup_path)  # Backup do arquivo

                    # Ler o arquivo e substituir a referência na linha específica
                    with open(src, 'r', encoding='utf-8') as f:
                        lines = f.readlines()

                    if 0 < linha <= len(lines):
                        # Substituir a referência na linha
                        pattern = re.escape(exact_text)
                        replacement = f'[[{new_ref}]]'
                        lines[linha - 1] = re.sub(r'\[\[' + pattern + r'\]\]', replacement, lines[linha - 1], flags=re.IGNORECASE)
                        with open(src, 'w', encoding='utf-8') as f:
                            f.writelines(lines)

                    # Atualizar o Tree Widget com o novo texto
                    occurrence_item.setText(4, new_ref)
                    # Desmarcar automaticamente a seleção após reescrever
                    occurrence_item.setSelected(False)

                # Atualizar o histórico de ações
                self.action_history.append({
                    'action': 'rewrite',
                    'old_references': [item.text(4) for item in selected_occurrences],
                    'new_reference': new_ref,
                    'backup_dir': backup_dir
                })

                # Fornecer feedback
                feedback_msg = self.translations['feedback_merged'].format(filename=new_ref)
                self.feedback.setText(feedback_msg)

                # Desmarcar as seleções
                self.tree.clearSelection()

            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error" if self.translations['language_english'] == "English" else "Erro",
                    self.translations['error_merge_failed'].format(error=str(e))
                )

    def undo_action(self):
        """
        Desfaz a última ação realizada (apagar ou reescrever).
        """
        if not self.action_history:
            QMessageBox.information(
                self,
                "Information" if self.translations['language_english'] == "English" else "Informação",
                "No action to undo." if self.translations['language_english'] == "English" else "Nenhuma ação para desfazer."
            )
            return

        last_action = self.action_history.pop()

        try:
            if last_action['action'] == 'delete':
                ref = last_action['reference']
                backup_dir = last_action['backup_dir']
                # Restaurar referências a partir do backup
                for file in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, file)
                    dest = os.path.join(self.directory, file)
                    shutil.copy2(src, dest)

                # Remover o diretório de backup se estiver vazio
                if not os.listdir(backup_dir):
                    os.rmdir(backup_dir)

                # Recarregar e analisar arquivos
                self.tree.clear()
                self.load_and_analyze_files()

                # Fornecer feedback
                action_text = "Delete" if self.translations['language_english'] == "English" else "Apagar"
                feedback_msg = self.translations['feedback_undone'].format(action=action_text)
                self.feedback.setText(feedback_msg)

            elif last_action['action'] == 'rewrite':
                old_refs = last_action['old_references']
                new_ref = last_action['new_reference']
                backup_dir = last_action['backup_dir']

                # Restaurar referências originais a partir do backup
                for file in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, file)
                    dest = os.path.join(self.directory, file)
                    shutil.copy2(src, dest)

                # Remover o diretório de backup se estiver vazio
                if not os.listdir(backup_dir):
                    os.rmdir(backup_dir)

                # Recarregar e analisar arquivos
                self.tree.clear()
                self.load_and_analyze_files()

                # Fornecer feedback
                action_text = "Rewrite" if self.translations['language_english'] == "English" else "Reescrever"
                feedback_msg = self.translations['feedback_undone'].format(action=action_text)
                self.feedback.setText(feedback_msg)

            else:
                QMessageBox.warning(
                    self,
                    "Warning" if self.translations['language_english'] == "English" else "Aviso",
                    "Unknown action type." if self.translations['language_english'] == "English" else "Tipo de ação desconhecido."
                )
                return

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error" if self.translations['language_english'] == "English" else "Erro",
                self.translations['error_merge_failed'].format(error=str(e))
            )

    def remove_reference_from_tree(self, ref):
        """
        Remove uma referência da Tree Widget.
        """
        for i in range(self.tree.topLevelItemCount()):
            group_item = self.tree.topLevelItem(i)
            if group_item.text(1) == ref:
                self.tree.takeTopLevelItem(i)
                break

    def update_reference_in_tree(self, old_ref, new_ref):
        """
        Atualiza o nome de uma referência na Tree Widget após reescrever.
        """
        for i in range(self.tree.topLevelItemCount()):
            group_item = self.tree.topLevelItem(i)
            if group_item.text(1) == old_ref:
                group_item.setText(1, new_ref)
                break

    def closeEvent(self, event):
        """
        Sobrescreve o evento de fechamento para garantir que todas as alterações sejam salvas ou tratadas.
        """
        if self.translations['language_english'] == "English":
            title = self.translations['close_confirmation_title']
            question = self.translations['close_confirmation_question']
            yes_text = self.translations['close_confirmation_yes']
            no_text = self.translations['close_confirmation_no']
        else:
            title = self.translations['close_confirmation_title']
            question = self.translations['close_confirmation_question']
            yes_text = self.translations['close_confirmation_yes']
            no_text = self.translations['close_confirmation_no']

        reply = QMessageBox.question(
            self,
            title,
            question,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


def main():
    app = QApplication(sys.argv)

    # Traduções temporárias para o diálogo de seleção de idioma (padrão para inglês)
    temp_translations = LANGUAGES['english']

    # Criar e exibir o diálogo de seleção de idioma
    selection_dialog = LanguageSelectionDialog(temp_translations, None)
    if selection_dialog.exec_() == QDialog.Accepted:
        selected_language = selection_dialog.get_selected_language()
    else:
        # Se o usuário cancelar, sair do aplicativo
        sys.exit()

    # Obter as traduções com base no idioma selecionado
    translations = LANGUAGES.get(selected_language, LANGUAGES['english'])

    # Inicializar o aplicativo principal com as traduções selecionadas
    manager = MarkdownReferenceManager(translations)
    manager.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
