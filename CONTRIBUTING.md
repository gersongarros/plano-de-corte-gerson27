# Como contribuir

Obrigado pelo interesse no Plano de Corte Gerson27!

O objetivo é melhorar o aplicativo com a colaboração de outros desenvolvedores, tornando-o mais útil, confiável e fácil de usar. São bem-vindas correções, melhorias no otimizador, interface, acessibilidade, documentação e testes.

Não é necessário receber acesso de escrita ao repositório: faça suas alterações em um fork e envie uma pull request. O mantenedor revisará as propostas antes de incorporá-las à versão oficial.

## Relatar problemas e sugerir melhorias

Antes de abrir uma [Issue](https://github.com/gersongarros/plano-de-corte-gerson27/issues), procure relatos semelhantes.

Para um problema, informe:

- Versão do aplicativo e distribuição Linux utilizada.
- O que você fez, o que esperava e o que aconteceu.
- Dimensões da chapa e das peças, quantidades, corte da serra e regras de veios/rotação relevantes.
- Mensagem de erro, se houver.
- Resolução da tela e escala de exibição, quando o problema for visual.

Um projeto JSON mínimo que reproduza o problema ajuda muito. Remova nomes de clientes e outros dados pessoais antes de compartilhar arquivos ou imagens.

Para uma sugestão, explique qual dificuldade ela resolve e dê um exemplo de uso. Não é necessário saber programar para contribuir.

## Preparar o ambiente

A aplicação utiliza Python, GTK4, PyGObject e Cairo. A versão 1.1.2 foi utilizada e testada no Fedora 44.

No Fedora, instale as dependências:

```bash
sudo dnf install git python3-gobject gtk4 python3-cairo
```

1. Crie um fork do repositório na sua conta do GitHub.
2. Clone seu fork. No comando abaixo, substitua `SEU_USUARIO` pelo seu usuário:

```bash
git clone https://github.com/SEU_USUARIO/plano-de-corte-gerson27.git
cd plano-de-corte-gerson27
git switch -c melhoria/descricao-curta
```

3. Execute a cópia de desenvolvimento diretamente:

```bash
python3 plano_corte.py
```

Feche outras instâncias antes de testar: a aplicação usa um identificador único e pode ativar a janela já aberta. Salve seu trabalho antes de fechá-la.

Não é necessário executar `instalar.sh` para cada alteração. Esse script atualiza a instalação do usuário; use-o quando precisar testar especificamente a instalação ou a integração com o ambiente gráfico.

## Organização do código

| Arquivo | Responsabilidade |
| --- | --- |
| `plano_corte.py` | Interface GTK, leitura e gravação de projetos, desenho e PDF. |
| `otimizador.py` | Validação, distribuição das peças, cortes e sobras. |
| `instalar.sh` | Instalação por usuário, ícones, lançador e backup. |
| `README.md` | Apresentação e instruções de uso e instalação. |
| `LEIA-ME.txt` | Notas da versão distribuída. |

## Orientações para alterações

- Prefira uma melhoria ou correção coerente por pull request, facilitando a revisão.
- Para mudanças grandes de arquitetura, formato dos projetos ou dependências, abra uma Issue antes para discutir a proposta.
- Preserve a leitura dos projetos JSON existentes. Se uma mudança exigir migração, documente e teste o caminho de atualização.
- Mantenha a interface e as instruções compreensíveis para quem não programa.
- Evite adicionar dependências quando a funcionalidade puder ser resolvida com as existentes. Explique a necessidade de novas dependências.
- Não inclua caches, arquivos temporários, credenciais ou projetos pessoais. A pasta `__pycache__` não deve ser enviada.
- Atualize a documentação quando mudar o funcionamento de um recurso.
- Evite misturar reformatações extensas com mudanças de comportamento.

## Testar sua contribuição

A profundidade dos testes deve acompanhar o impacto da alteração. Registre na pull request o que foi testado e o que ainda não pôde ser verificado.

### Verificações básicas

```bash
python3 -m py_compile plano_corte.py otimizador.py
bash -n instalar.sh
```

Esses comandos verificam sintaxe; não substituem os testes de funcionamento.

### Interface e projetos

Quando relevante para a mudança, verifique:

- Início com projeto vazio e comportamento dos botões Novo e Abrir.
- Cancelamento de diálogos sem perda dos dados atuais.
- Adição, edição e remoção de peças.
- Salvar, reabrir e editar um projeto JSON existente.
- Otimização, navegação entre chapas e apresentação das sobras.
- Exportação e leitura do PDF gerado.
- Janela em 1366×768 e em tamanhos menores, sem esconder ações essenciais.
- Uso com teclado, textos legíveis e mensagens de erro claras.

### Otimizador

Mudanças no algoritmo precisam de casos reproduzíveis, preferencialmente com testes automatizados. Confira:

- Todas as peças solicitadas são colocadas na quantidade correta, ou o problema é informado claramente.
- Peças não se sobrepõem e permanecem dentro da chapa.
- Espessura do corte, permissão de giro e restrições dos veios são respeitadas.
- A sequência mantém a possibilidade de execução por cortes guilhotina, se esse for o modelo utilizado.
- Sobras têm dimensões válidas e não se sobrepõem às peças.
- Entradas inválidas, peças que não cabem e projetos com várias chapas são tratados.

Ao propor melhor aproveitamento ou maior velocidade, forneça os mesmos projetos de teste para comparar antes e depois. Informe chapas necessárias, aproveitamento e tempo de execução, com as condições do teste. Uma estratégia heurística não deve ser apresentada como garantia de solução ótima sem demonstração.

### Instalação

Se alterar o instalador, confira a instalação inicial, atualização, backup e associação entre ícone, lançador e janela. Preserve os projetos do usuário e a instalação sem privilégios administrativos, exceto a instalação das dependências do sistema.

## Enviar uma pull request

1. Faça o commit das alterações no seu fork e envie sua branch para o GitHub.
2. Abra uma pull request para a branch `main` deste repositório.
3. Descreva:
   - O problema ou necessidade atendida.
   - O comportamento antes e depois.
   - Como testar e quais verificações você executou.
   - Limitações, novas dependências ou impactos na compatibilidade.
4. Vincule a Issue relacionada, se houver.
5. Inclua imagens para mudanças visuais e exemplos de entrada/resultado para mudanças no otimizador.

O mantenedor pode pedir ajustes ou esclarecimentos. A proposta será avaliada antes de entrar na versão oficial; o envio não significa aprovação automática.

## Ideias de contribuição

- Melhorias de aproveitamento, desempenho e testes do otimizador.
- Visualização da chapa na horizontal e na vertical, com medidas legíveis.
- Melhorias de acessibilidade e adaptação a diferentes telas.
- Validação de arquivos e proteção contra perda de alterações não salvas.
- Melhor apresentação e paginação dos relatórios PDF.
- Documentação, exemplos e testes em outras distribuições Linux.

Estas são possibilidades de evolução, não recursos já disponíveis ou compromissos de implementação. Outras ideias são bem-vindas.

## Comunicação

Mantenha uma comunicação respeitosa, objetiva e acolhedora. Explique decisões técnicas, aceite perguntas e concentre as críticas no código e no comportamento do programa, não nas pessoas.

## Licença

A escolha de uma licença para o projeto ainda está pendente. Este documento orienta a colaboração e não concede, por si só, uma licença sobre o código. A política de licenciamento será documentada pelo mantenedor em um arquivo próprio.
