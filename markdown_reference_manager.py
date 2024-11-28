import sys
import os
import re
import unicodedata
import shutil
from collections import defaultdict
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTreeWidget, QTreeWidgetItem, QMessageBox, QLabel,
    QFileDialog, QDialog, QComboBox, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette


# Lista de stopwords em Português e Inglês, incluindo artigos, pronomes, adjetivos, verbos, números, numerais
STOPWORDS = {
    # Artigos em Português
    'a', 'à', 'as', 'ao', 'aos', 'um', 'uma', 'uns', 'umas',
    'o', 'os', 'da', 'das', 'do', 'dos', 'de', 'em', 'para',
    'por', 'com', 'sem', 'sobre', 'entre', 'até', 'desde',
    'pela', 'pelas', 'pelo', 'pelos',

    # Artigos em Inglês
    'a', 'an', 'the',

    # Pronomes em Português
    'eu', 'tu', 'ele', 'ela', 'nós', 'vós', 'eles', 'elas',
    'me', 'te', 'se', 'nos', 'vos', 'lhe', 'lhes',
    'este', 'esta', 'estes', 'estas', 'esse', 'essa', 'esses', 'essas',
    'aquele', 'aquela', 'aqueles', 'aquelas',

    # Pronomes em Inglês
    'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'me', 'him', 'her', 'us', 'them',
    'this', 'that', 'these', 'those',

    # Preposições e Conjunções em Português
    'que', 'como', 'se', 'mais', 'menos', 'também', 'sempre',
    'quando', 'onde', 'porque', 'para', 'com', 'sem', 'sobre',
    'entre', 'até', 'desde',

    # Preposições e Conjunções em Inglês
    'and', 'or', 'but', 'because', 'as', 'until', 'while',
    'of', 'at', 'by', 'for', 'with', 'about', 'against',
    'between', 'into', 'through', 'during', 'before', 'after',

    # Adjetivos Comuns em Português
    'grande', 'pequeno', 'bom', 'ruim', 'novo', 'velho',
    'primeiro', 'último', 'melhor', 'pior',

    # Adjetivos Comuns em Inglês
    'big', 'small', 'good', 'bad', 'new', 'old',
    'first', 'last', 'better', 'worse',

    # Verbos Comuns em Português
    'ser', 'estar', 'ter', 'fazer', 'poder', 'dizer',
    'ir', 'ver', 'dar', 'saber', 'querer', 'chegar',
    'passar', 'dever', 'ficar', 'contar', 'começar',

    # Verbos Comuns em Inglês
    'be', 'have', 'do', 'say', 'go', 'see', 'get',
    'make', 'know', 'think', 'take', 'come', 'want',
    'look', 'use', 'find', 'give', 'tell', 'work',

    # Números e Numerais em Português
    'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete',
    'oito', 'nove', 'dez', 'primeiro', 'segundo', 'terceiro',
    'quarto', 'quinto',

    # Números e Numerais em Inglês
    'one', 'two', 'three', 'four', 'five', 'six', 'seven',
    'eight', 'nine', 'ten', 'first', 'second', 'third',
    'fourth', 'fifth',

    # Preposição 'x' usada como 'versus' em Português
    'x',
}

def remover_acentos(texto):
    """
    Remove acentos de uma string.
    """
    nfkd = unicodedata.normalize('NFKD', texto)
    return ''.join([c for c in nfkd if not unicodedata.combining(c)])

def extrair_referencias(line):
    """
    Extrai todas as referências dentro de colchetes duplos em uma linha.
    Retorna uma lista de tuplas (exata_referencia, referencia_normalizada).
    """
    matches = re.findall(r'\[\[(.*?)\]\]', line)
    referencias = []
    for match in matches:
        exact_ref = match.strip()
        normalized_ref = remover_acentos(match.lower()).strip()
        if normalized_ref and normalized_ref not in STOPWORDS:
            referencias.append((exact_ref, normalized_ref))
    return referencias

# Dicionário de traduções para as duas línguas suportadas
LANGUAGES = {
    'english': {
        'window_title': "Markdown Reference Manager",
        'instruction': "Select the files you want to analyze.",
        'button_delete': "Delete",
        'button_undo': "Undo",
        'button_merge': "Rewrite",
        'button_save': "Save Changes",
        'feedback_deleted': "Deleted references: {files}",
        'feedback_merged': "Rewrote references to: {filename}",
        'feedback_undone': "Action undone: {action}",
        'error_no_files_selected': "No files selected.",
        'error_merge_failed': "Error rewriting references: {error}",
        'error_delete_failed': "Error deleting references: {error}",
        'merge_dialog_title': "New Reference Name",
        'merge_dialog_instruction': "Select a suggested name or enter a new name for the reference:",
        'merge_dialog_ok': "OK",
        'merge_dialog_cancel': "Cancel",
        'warning_no_files_selected_delete': "No references selected to delete.",
        'warning_no_files_selected_merge': "No references selected to rewrite.",
        'info_no_common_words': "No repeated references found.",
        'language_selection_title': "Select Language",
        'language_selection_instruction': "Choose the application language:",
        'language_english': "English",
        'language_portuguese': "Portuguese (Brazilian)",
        'select_rewrite_action': "Choose an action for the selected reference:",
        'action_rewrite': "Rewrite",
        'action_delete': "Delete",
        'action_skip': "Skip",
        'close_confirmation_title': "Quit",
        'close_confirmation_question': "Are you sure you want to quit?",
        'close_confirmation_yes': "Yes",
        'close_confirmation_no': "No",
    },
    'portuguese': {
        'window_title': "Gerenciador de Referências de Markdown",
        'instruction': "Selecione os arquivos que deseja analisar.",
        'button_delete': "Apagar",
        'button_undo': "Desfazer",
        'button_merge': "Reescrever",
        'button_save': "Salvar Alterações",
        'feedback_deleted': "Referências apagadas: {files}",
        'feedback_merged': "Referências reescritas para: {filename}",
        'feedback_undone': "Ação desfeita: {action}",
        'error_no_files_selected': "Nenhum arquivo selecionado.",
        'error_merge_failed': "Erro ao reescrever referências: {error}",
        'error_delete_failed': "Erro ao apagar referências: {error}",
        'merge_dialog_title': "Novo Nome da Referência",
        'merge_dialog_instruction': "Selecione um nome sugerido ou digite um novo nome para a referência:",
        'merge_dialog_ok': "OK",
        'merge_dialog_cancel': "Cancelar",
        'warning_no_files_selected_delete': "Nenhuma referência selecionada para apagar.",
        'warning_no_files_selected_merge': "Nenhuma referência selecionada para reescrever.",
        'info_no_common_words': "Nenhuma referência repetida encontrada.",
        'language_selection_title': "Selecione o Idioma",
        'language_selection_instruction': "Escolha o idioma do aplicativo:",
        'language_english': "Inglês",
        'language_portuguese': "Português (Brasil)",
        'select_rewrite_action': "Escolha uma ação para a referência selecionada:",
        'action_rewrite': "Reescrever",
        'action_delete': "Apagar",
        'action_skip': "Ignorar",
        'close_confirmation_title': "Sair",
        'close_confirmation_question': "Tem certeza de que deseja sair?",
        'close_confirmation_yes': "Sim",
        'close_confirmation_no': "Não",
    }
}

class LanguageSelectionDialog(QDialog):
    """
    Dialog for selecting the application language at startup.
    """
    def __init__(self, translations, parent=None):
        super().__init__(parent)
        self.translations = translations
        self.setWindowTitle(self.translations['language_selection_title'])
        self.setModal(True)
        self.selected_language = 'english'  # Default
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        # Instruction Label
        instruction = QLabel(self.translations['language_selection_instruction'])
        instruction.setFont(QFont("Arial", 12))
        layout.addWidget(instruction)

        # Language ComboBox
        self.combo_languages = QComboBox()
        self.combo_languages.addItem(self.translations['language_english'], 'english')
        self.combo_languages.addItem(self.translations['language_portuguese'], 'portuguese')
        self.combo_languages.setCurrentIndex(0)  # Default to English
        layout.addWidget(self.combo_languages)

        # OK and Cancel Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_selected_language(self):
        return self.combo_languages.currentData()

class NameSuggestionDialog(QDialog):
    """
    Dialog for suggesting and inputting new reference names.
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

        # Instruction Label
        instruction = QLabel(self.translations['merge_dialog_instruction'])
        instruction.setFont(QFont("Arial", 12))
        layout.addWidget(instruction)

        # ComboBox with Suggestions
        self.combo_suggestions = QComboBox()
        self.combo_suggestions.addItems(self.suggested_names)
        self.combo_suggestions.setEditable(True)
        layout.addWidget(self.combo_suggestions)

        # OK and Cancel Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText(self.translations['merge_dialog_ok'])
        buttons.button(QDialogButtonBox.Cancel).setText(self.translations['merge_dialog_cancel'])
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def get_new_name(self):
        return self.combo_suggestions.currentText().strip()

class MarkdownReferenceManager(QWidget):
    def __init__(self, translations):
        super().__init__()
        self.translations = translations
        self.setWindowTitle(self.translations['window_title'])
        self.setGeometry(100, 100, 1600, 900)  # Increased width for more columns
        self.action_history = []  # History for undo functionality
        self.initUI()

    def initUI(self):
        # Apply dark theme
        self.apply_dark_theme()

        layout = QVBoxLayout()

        # Instruction Label
        instruction = QLabel(self.translations['instruction'])
        instruction.setFont(QFont("Arial", 14))
        instruction.setStyleSheet("color: white;")
        layout.addWidget(instruction)

        # Tree Widget to Display References
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Freq.", "Reference", "File", "Line", "Exact Text"])
        self.tree.setColumnWidth(0, 50)    # Frequency
        self.tree.setColumnWidth(1, 300)   # Reference
        self.tree.setColumnWidth(2, 200)   # File
        self.tree.setColumnWidth(3, 100)   # Line
        self.tree.setColumnWidth(4, 800)   # Exact Text
        self.tree.setStyleSheet("background-color: #2b2b2b; color: white;")
        self.tree.setSelectionMode(QTreeWidget.NoSelection)
        self.tree.setAlternatingRowColors(True)
        self.tree.setRootIsDecorated(True)  # Show expand arrows

        layout.addWidget(self.tree)

        # Action Buttons
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

        self.btn_save = QPushButton(self.translations['button_save'])
        self.btn_save.setFont(QFont("Arial", 12, QFont.Bold))
        self.btn_save.setStyleSheet("""
            QPushButton {
                background-color: #0275d8;
                color: white;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #025aa5;
            }
        """)
        self.btn_save.clicked.connect(self.save_changes)
        button_layout.addWidget(self.btn_save)

        layout.addLayout(button_layout)

        # Feedback Label
        self.feedback = QLabel("")
        self.feedback.setFont(QFont("Arial", 12))
        self.feedback.setStyleSheet("color: #28a745;")
        layout.addWidget(self.feedback)

        self.setLayout(layout)

        # Load and Analyze Files
        self.load_and_analyze_files()

    def apply_dark_theme(self):
        """
        Apply a dark theme to the application.
        """
        dark_palette = QPalette()

        # Define color palette
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
        Prompt the user to select a directory and analyze .md files within it.
        """
        # Open a dialog to select the directory
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

        # List all .md files in the directory
        md_files = [f for f in os.listdir(directory) if f.lower().endswith('.md')]

        if not md_files:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['info_no_common_words']
            )
            sys.exit()

        # Analyze references across all files
        self.references = defaultdict(list)  # Normalized Reference -> List of occurrences (exact_ref, file, line number)

        for file in md_files:
            file_path = os.path.join(directory, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line_num, line in enumerate(f, start=1):
                        referencias = extrair_referencias(line)
                        for exact_ref, normalized_ref in referencias:
                            self.references[normalized_ref].append((exact_ref, file, line_num))
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error" if self.translations['language_english'] == "English" else "Erro",
                    self.translations['error_merge_failed'].format(error=str(e))
                )
                sys.exit()

        # Filter references that appear more than once
        self.filtered_references = {ref: occurrences for ref, occurrences in self.references.items() if len(occurrences) > 1}

        if not self.filtered_references:
            QMessageBox.information(
                self,
                "Information" if self.translations['language_english'] == "English" else "Informação",
                self.translations['info_no_common_words']
            )
            sys.exit()

        # Sort references by frequency (descending)
        sorted_refs = sorted(self.filtered_references.items(), key=lambda x: len(x[1]), reverse=True)

        # Populate the Tree Widget
        for ref, occurrences in sorted_refs:
            ref_item = QTreeWidgetItem([str(len(occurrences)), ref, "", "", ""])
            ref_item.setFont(1, QFont("Arial", 12, QFont.Bold))
            ref_item.setForeground(1, QColor(255, 255, 255))
            for occ in occurrences:
                exact_ref, file, line_num = occ
                occurrence_item = QTreeWidgetItem(["", "", file, str(line_num), exact_ref])
                occurrence_item.setCheckState(4, Qt.Unchecked)
                ref_item.addChild(occurrence_item)
            self.tree.addTopLevelItem(ref_item)

        self.directory = directory

    def delete_references(self):
        """
        Delete selected references from all occurrences in all files.
        """
        selected_refs = []
        for i in range(self.tree.topLevelItemCount()):
            ref_item = self.tree.topLevelItem(i)
            # Check if the reference or any of its occurrences are checked
            if ref_item.checkState(0) == Qt.Checked or ref_item.checkState(1) == Qt.Checked:
                selected_refs.append(ref_item.text(1))

        if not selected_refs:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['warning_no_files_selected_delete']
            )
            return

        # Backup original files
        backup_dir = os.path.join(self.directory, ".backup_reference_manager")
        os.makedirs(backup_dir, exist_ok=True)

        try:
            for ref in selected_refs:
                occurrences = self.filtered_references[ref]
                for exact_ref, file, line_num in occurrences:
                    src = os.path.join(self.directory, file)
                    backup_path = os.path.join(backup_dir, file)
                    shutil.copy2(src, backup_path)  # Backup the file

                    # Read the file and remove the reference
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read()
                    # Remove the exact reference, case-insensitive
                    updated_content = re.sub(r'\[\[' + re.escape(exact_ref) + r'\]\]', '', content, flags=re.IGNORECASE)
                    with open(src, 'w', encoding='utf-8') as f:
                        f.write(updated_content)

            # Update the Tree Widget and history
            for ref in selected_refs:
                self.action_history.append({
                    'action': 'delete',
                    'reference': ref,
                    'backup_dir': backup_dir
                })
                self.remove_reference_from_tree(ref)

            # Provide feedback
            feedback_msg = self.translations['feedback_deleted'].format(files=", ".join(selected_refs))
            self.feedback.setText(feedback_msg)

        except Exception as e:
            QMessageBox.critical(
                self,
                "Error" if self.translations['language_english'] == "English" else "Erro",
                self.translations['error_delete_failed'].format(error=str(e))
            )

    def rewrite_reference(self):
        """
        Rewrite selected references across all occurrences in all files.
        """
        selected_refs = []
        for i in range(self.tree.topLevelItemCount()):
            ref_item = self.tree.topLevelItem(i)
            # Check if the reference or any of its occurrences are checked
            if ref_item.checkState(0) == Qt.Checked or ref_item.checkState(1) == Qt.Checked:
                selected_refs.append(ref_item.text(1))

        if not selected_refs:
            QMessageBox.warning(
                self,
                "Warning" if self.translations['language_english'] == "English" else "Aviso",
                self.translations['warning_no_files_selected_merge']
            )
            return

        for ref in selected_refs:
            # Prompt user to input new reference name
            suggested_names = [ref]  # Current reference as the default suggestion
            dialog = NameSuggestionDialog(suggested_names, self.translations, self)
            if dialog.exec_() == QDialog.Accepted:
                new_ref = dialog.get_new_name()
                if not new_ref:
                    QMessageBox.warning(
                        self,
                        "Warning" if self.translations['language_english'] == "English" else "Aviso",
                        self.translations['error_no_files_selected'] if self.translations['language_english'] == "English" else "Nome da referência inválido."
                    )
                    continue

                # Backup original files
                backup_dir = os.path.join(self.directory, ".backup_reference_manager")
                os.makedirs(backup_dir, exist_ok=True)

                try:
                    occurrences = self.filtered_references[ref]
                    for exact_ref, file, line_num in occurrences:
                        src = os.path.join(self.directory, file)
                        backup_path = os.path.join(backup_dir, file)
                        shutil.copy2(src, backup_path)  # Backup the file

                        # Read the file and replace the exact reference
                        with open(src, 'r', encoding='utf-8') as f:
                            content = f.read()
                        # Replace the exact reference, case-insensitive
                        updated_content = re.sub(r'\[\[' + re.escape(exact_ref) + r'\]\]', f'[[{new_ref}]]', content, flags=re.IGNORECASE)
                        with open(src, 'w', encoding='utf-8') as f:
                            f.write(updated_content)

                    # Update the Tree Widget and history
                    self.action_history.append({
                        'action': 'rewrite',
                        'old_reference': ref,
                        'new_reference': new_ref,
                        'backup_dir': backup_dir
                    })
                    self.update_reference_in_tree(ref, new_ref)

                    # Provide feedback
                    feedback_msg = self.translations['feedback_merged'].format(filename=new_ref)
                    self.feedback.setText(feedback_msg)

                except Exception as e:
                    QMessageBox.critical(
                        self,
                        "Error" if self.translations['language_english'] == "English" else "Erro",
                        self.translations['error_merge_failed'].format(error=str(e))
                    )

    def save_changes(self):
        """
        Save all changes made to the files.
        """
        QMessageBox.information(
            self,
            "Information" if self.translations['language_english'] == "English" else "Informação",
            self.translations['feedback_merged']
        )

    def undo_action(self):
        """
        Undo the last action performed (delete or rewrite).
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
                # Restore references from backup
                for file in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, file)
                    dest = os.path.join(self.directory, file)
                    shutil.copy2(src, dest)

                # Remove the backup directory if empty
                if not os.listdir(backup_dir):
                    os.rmdir(backup_dir)

                # Reload and analyze files
                self.tree.clear()
                self.load_and_analyze_files()

                # Provide feedback
                action_text = "Delete" if self.translations['language_english'] == "English" else "Apagar"
                feedback_msg = self.translations['feedback_undone'].format(action=action_text)
                self.feedback.setText(feedback_msg)

            elif last_action['action'] == 'rewrite':
                old_ref = last_action['old_reference']
                new_ref = last_action['new_reference']
                backup_dir = last_action['backup_dir']

                # Restore original references from backup
                for file in os.listdir(backup_dir):
                    src = os.path.join(backup_dir, file)
                    dest = os.path.join(self.directory, file)
                    shutil.copy2(src, dest)

                # Remove the backup directory if empty
                if not os.listdir(backup_dir):
                    os.rmdir(backup_dir)

                # Reload and analyze files
                self.tree.clear()
                self.load_and_analyze_files()

                # Provide feedback
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
        Remove a reference from the Tree Widget.
        """
        for i in range(self.tree.topLevelItemCount()):
            ref_item = self.tree.topLevelItem(i)
            if ref_item.text(1) == ref:
                self.tree.takeTopLevelItem(i)
                break

    def update_reference_in_tree(self, old_ref, new_ref):
        """
        Update a reference name in the Tree Widget after rewriting.
        """
        for i in range(self.tree.topLevelItemCount()):
            ref_item = self.tree.topLevelItem(i)
            if ref_item.text(1) == old_ref:
                ref_item.setText(1, new_ref)
                break

    def closeEvent(self, event):
        """
        Override the close event to ensure all changes are saved or handled.
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

    # Temporary translations for the language selection dialog (default to English)
    temp_translations = LANGUAGES['english']

    # Create and display the language selection dialog
    selection_dialog = LanguageSelectionDialog(temp_translations, None)
    if selection_dialog.exec_() == QDialog.Accepted:
        selected_language = selection_dialog.get_selected_language()
    else:
        # If the user cancels, exit the application
        sys.exit()

    # Get the translations based on the selected language
    translations = LANGUAGES.get(selected_language, LANGUAGES['english'])

    # Initialize the main application with the selected translations
    manager = MarkdownReferenceManager(translations)
    manager.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
