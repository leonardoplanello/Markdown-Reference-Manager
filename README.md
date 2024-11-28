# Markdown Reference Manager

## Brief Description
The **Markdown Reference Manager** is a GUI tool to manage references in Markdown (`.md`) files. It helps users locate and rewrite terms in double brackets (`[[ ]]`), and allows deleting, merging, or rewriting repeated references efficiently with an intuitive interface. Integrated backup ensures data safety during modifications.

## Features
- **Locate and Rewrite References**: Automatically detects references enclosed in double brackets (`[[ ]]`) within Markdown files, allowing users to modify or replace them.
- **Common Word Grouping**: Groups references that share common words, enabling easier selection for merging or rewriting.
- **Rewrite Suggestions**: Suggests reference names for rewriting based on common words among selected references.
- **Batch Operations**: Supports rewriting multiple references simultaneously, updating all occurrences in the corresponding files.
- **Delete and Undo**: Delete selected references and undo the last action for safety.
- **Automatic Checkbox Clearing**: After rewriting, the checkboxes are automatically cleared, improving the user experience.
- **Backup**: Creates backups of original Markdown files before modifications, allowing actions to be undone.
- **Multi-language Support**: Offers language options for the interface, including English (default) and Portuguese (Brazilian).

## System Requirements
- Python 3.x
- **PyQt5** library (for GUI support)

To install PyQt5, run:
```sh
pip install PyQt5
```

## How to Use
### 1. Initial Setup
- Download or clone the repository containing `markdown_reference_manager.py`.
- Ensure Python 3.x and PyQt5 are installed.

### 2. Running the Application
- Open a terminal in the directory where `markdown_reference_manager.py` is located.
- Run the application with the command:
  ```sh
  python markdown_reference_manager.py
  ```

### 3. Language Selection
- Upon starting, a **Language Selection** dialog box will appear.
- Select **English** or **Portuguese (Brazilian)**. The interface and prompts will be displayed in the chosen language.

### 4. Selecting Markdown Files
- You will be prompted to choose the folder that contains the Markdown (`.md`) files to analyze.
- The application will automatically locate references enclosed within double brackets (`[[ ]]`).

### 5. Using the GUI
#### Overview of GUI Elements:
- **Tree Widget**: Displays references grouped by common words. Click on the **Common Word** to expand the group and view individual references.
- **Buttons**:
  - **Delete**: Deletes selected references from the original files.
  - **Undo**: Reverts the last action performed (either delete or rewrite).
  - **Rewrite**: Rewrites selected references. When clicked, prompts you to enter a new reference name.

#### Instructions:
1. **Select References**: Expand a **Common Word** group to view specific references, and use the checkbox in the **Exact Text** column to select them.
2. **Rewrite References**:
   - Click **Rewrite**.
   - A prompt will appear with a suggested new name for the references based on common words. You can modify it or enter a new name.
   - Click **OK** to apply changes. All instances of the selected reference in the corresponding file will be updated, and checkboxes will be automatically cleared.
3. **Delete References**: Click **Delete** to remove selected references from the files. References will be deleted from all occurrences within the Markdown files.
4. **Undo Action**: If an error was made, click **Undo** to revert the last action.

### 6. Saving Changes
- Changes are saved automatically after each modification. A backup of the original files is created in a folder named `.backup_reference_manager` within the selected directory.

## Important Notes
- **Backup Files**: All modifications to files are preceded by creating backups in the `.backup_reference_manager` folder. If something goes wrong, you can restore the original files from this directory.
- **Undo Limit**: The **Undo** button only reverts the **last action**. If multiple actions were performed, only the most recent one can be undone.

## Example Workflow
1. Run the tool and choose a folder containing Markdown files.
2. Expand groups to view references.
3. Select references with the same common word.
4. Click **Rewrite**, modify the name, and confirm.
5. Check updated files in the selected folder.

## Customization
### Language Customization
- The application supports **English** and **Portuguese (Brazilian)** languages for all user prompts and buttons.
- The default language is **English**, but you can change it upon startup.

### Theme
- The application uses a **dark theme** by default for better visual comfort. This can be modified in the code if necessary.

## Troubleshooting
- **No Directory Selected**: Ensure a valid folder is chosen when prompted to select the directory.
- **Error in Rewrite Operation**: If references aren't updating, verify the formatting is correct (`[[reference]]`), and ensure no special characters are blocking the regex.
- **Undo Limitations**: Only the most recent action can be undone.

## License
This project is open-source and distributed under the MIT License.

---

## Descrição Breve
O **Markdown Reference Manager** é uma ferramenta baseada em GUI projetada para ajudar os usuários a gerenciar referências dentro de arquivos Markdown (`.md`). Ele permite localizar e reescrever termos específicos entre colchetes duplos (`[[ ]]`). A ferramenta também permite excluir, mesclar ou reescrever referências repetidas de maneira eficiente, com uma interface amigável, atraente e interativa. Recursos de backup também estão integrados, garantindo a segurança dos dados durante as modificações.

## Funcionalidades
- **Localizar e Reescrever Referências**: Detecta automaticamente referências entre colchetes duplos (`[[ ]]`) em arquivos Markdown, permitindo modificar ou substituí-las.
- **Agrupamento por Palavras Comuns**: Agrupa referências que compartilham palavras comuns, facilitando a seleção para mesclar ou reescrever.
- **Sugestões de Reescrita**: Sugere nomes de referências para reescrever com base em palavras comuns entre as referências selecionadas.
- **Operações em Lote**: Suporta a reescrita de múltiplas referências simultaneamente, atualizando todas as ocorrências nos arquivos correspondentes.
- **Excluir e Desfazer**: Exclui as referências selecionadas e desfaz a última ação para segurança.
- **Limpeza Automática dos Checkboxes**: Após reescrever, os checkboxes são automaticamente limpos, melhorando a experiência do usuário.
- **Backup**: Cria backups dos arquivos Markdown originais antes das modificações, permitindo que as ações sejam desfeitas.
- **Suporte a Vários Idiomas**: Oferece opções de idioma para a interface, incluindo inglês (padrão) e português (brasileira).

## Requisitos do Sistema
- Python 3.x
- Biblioteca **PyQt5** (para suporte GUI)

Para instalar o PyQt5, execute:
```sh
pip install PyQt5
```

## Como Usar
### 1. Configuração Inicial
- Baixe ou clone o repositório contendo o `markdown_reference_manager.py`.
- Certifique-se de que o Python 3.x e o PyQt5 estejam instalados.

### 2. Executando o Aplicativo
- Abra um terminal no diretório onde está localizado o `markdown_reference_manager.py`.
- Execute o aplicativo com o comando:
  ```sh
  python markdown_reference_manager.py
  ```

### 3. Seleção de Idioma
- Ao iniciar, uma caixa de diálogo de **Seleção de Idioma** aparecerá.
- Selecione **Inglês** ou **Português (Brasil)**. A interface e as mensagens serão exibidas no idioma escolhido.

### 4. Selecionando Arquivos Markdown
- Você será solicitado a escolher a pasta que contém os arquivos Markdown (`.md`) a serem analisados.
- O aplicativo localizará automaticamente as referências entre colchetes duplos (`[[ ]]`).

### 5. Usando a GUI
#### Visão Geral dos Elementos da GUI:
- **Tree Widget**: Exibe referências agrupadas por palavras comuns. Clique na **Palavra Comum** para expandir o grupo e ver referências individuais.
- **Botões**:
  - **Apagar**: Exclui as referências selecionadas dos arquivos originais.
  - **Desfazer**: Reverte a última ação realizada (exclusão ou reescrita).
  - **Reescrever**: Reescreve as referências selecionadas. Quando clicado, solicita um novo nome de referência.

#### Instruções:
1. **Selecionar Referências**: Expanda um grupo de **Palavra Comum** para ver referências específicas e use o checkbox na coluna **Texto Exato** para selecioná-las.
2. **Reescrever Referências**:
   - Clique em **Reescrever**.
   - Um prompt aparecerá com um nome sugerido para as referências, baseado em palavras comuns. Você pode modificá-lo ou inserir um novo nome.
   - Clique em **OK** para aplicar as alterações. Todas as instâncias da referência selecionada serão atualizadas no arquivo correspondente, e os checkboxes serão automaticamente limpos.
3. **Excluir Referências**: Clique em **Apagar** para remover as referências selecionadas dos arquivos. Elas serão apagadas de todas as ocorrências dentro dos arquivos Markdown.
4. **Desfazer Ação**: Se houver um erro, clique em **Desfazer** para reverter a última ação.

### 6. Salvando as Alterações
- As alterações são salvas automaticamente após cada modificação. Um backup dos arquivos originais é criado em uma pasta chamada `.backup_reference_manager` dentro do diretório selecionado.

## Notas Importantes
- **Arquivos de Backup**: Todas as modificações nos arquivos são precedidas pela criação de backups na pasta `.backup_reference_manager`. Se algo der errado, você pode restaurar os arquivos originais a partir deste diretório.
- **Limitação do Desfazer**: O botão **Desfazer** apenas reverte a **última ação**. Se várias ações foram realizadas, apenas a mais recente pode ser desfeita.

## Exemplo de Fluxo de Trabalho
1. Execute a ferramenta e escolha uma pasta contendo arquivos Markdown.
2. Expanda grupos para visualizar referências.
3. Selecione referências com a mesma palavra comum.
4. Clique em **Reescrever**, modifique o nome e confirme.
5. Verifique os arquivos atualizados na pasta selecionada.

## Customização
### Customização de Idioma
- O aplicativo oferece suporte aos idiomas **Inglês** e **Português (Brasil)** para todos os prompts e botões.
- O idioma padrão é **Inglês**, mas você pode alterá-lo ao iniciar.

### Tema
- O aplicativo usa um **tema escuro** por padrão, para maior conforto visual. Este tema pode ser modificado no código, se necessário.

## Solução de Problemas
- **Nenhum Diretório Selecionado**: Certifique-se de escolher uma pasta válida quando solicitado a selecionar o diretório.
- **Erro na Operação de Reescrita**: Se as referências não estão sendo atualizadas, verifique se a formatação está correta (`[[referencia]]`) e certifique-se de que não há caracteres especiais bloqueando a regex.
- **Limitação do Desfazer**: Apenas a ação mais recente pode ser desfeita.

## Licença
Este projeto é open-source e distribuído sob a Licença MIT.

