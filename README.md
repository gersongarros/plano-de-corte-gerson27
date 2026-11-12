<p align="center">
  <img src="icone.png" alt="Ícone G27 — Plano de Corte Gerson27" width="128">
</p>

# Plano de Corte Gerson27

Aplicativo para Linux que organiza peças retangulares em chapas, desenha o plano de corte e mostra as medidas das sobras. Desenvolvido em Python com interface GTK4, utilizado e testado no Fedora 44.

**Versão atual: 1.1.2**

## Recursos

- Cadastro de chapas: material, comprimento, largura, espessura e quantidade prevista.
- Cadastro de peças com nome, dimensões e quantidade.
- Configuração da espessura do corte da serra.
- Restrições de sentido dos veios e permissão de giro das peças em 90°.
- Otimização por cortes guilhotina: cada corte atravessa o retângulo que está sendo dividido.
- Visualização das peças e das sobras retangulares, com suas medidas.
- Navegação entre chapas quando o projeto exige mais de uma.
- Resumo da quantidade de peças, chapas necessárias e aproveitamento.
- Projetos salvos em JSON e exportação do plano em PDF.
- Botão **Otimizar plano de corte** fixo, acessível mesmo quando a lista de peças precisa rolar.

Todas as dimensões são informadas em **milímetros**.

## Compatibilidade com Linux

**Testado no Fedora 44. O funcionamento em outras distribuições ainda não foi validado.**

O aplicativo depende de Python 3, GTK4, PyGObject e Cairo. Outras distribuições podem executá-lo se tiverem versões compatíveis dessas dependências, mas os nomes dos pacotes e os comandos de instalação variam.

**Os comandos com `dnf` deste README são destinados ao Fedora.** Não os utilize como instrução de instalação para Ubuntu, Debian, Linux Mint, Arch ou outras distribuições. Consulte a documentação da sua distribuição para instalar as dependências correspondentes.

O script `instalar.sh` verifica as dependências e instala o aplicativo para o usuário atual. Ele não instala essas dependências automaticamente. Se elas estiverem ausentes, a sugestão de comando exibida pelo script também é específica do Fedora.

Relatos de testes em outras distribuições são bem-vindos nas Issues. Informe a distribuição, sua versão e os passos utilizados; isso ajudará a documentar o suporte com precisão.

## Instalação no Fedora

### 1. Baixe o projeto

No início desta página, clique em **Code → Download ZIP** e extraia o arquivo.

Abra a pasta extraída que contém `instalar.sh`, `plano_corte.py`, `otimizador.py` e `icone.png`. Abra um terminal nessa pasta.

### 2. Instale as dependências

```bash
sudo dnf install python3-gobject gtk4 python3-cairo
```

### 3. Execute o instalador

```bash
bash instalar.sh
```

Execute o instalador com seu usuário normal, **sem sudo**. Ele cria a instalação e o atalho para o usuário atual.

### 4. Abra o aplicativo

Procure **Plano de Corte Gerson27** no menu de aplicativos do Fedora.

Se estiver atualizando uma versão já aberta, salve seu projeto, feche a janela antiga e abra novamente. Confira a versão no título da janela.

## Como usar

1. O aplicativo começa com um projeto sem peças e sem plano calculado. As medidas iniciais da chapa podem ser alteradas.
2. Informe o nome do projeto e configure a chapa e o corte da serra.
3. Clique em **+ Peça** para cadastrar cada tipo de peça e sua quantidade.
4. Ajuste os veios e a opção **Permitir giro 90°** conforme o material.
5. Clique em **Otimizar plano de corte**.
6. Confira o desenho, o aproveitamento e as sobras. Use as setas para consultar outras chapas.
7. Clique em **Salvar** ou **Salvar como** para guardar o projeto em JSON.
8. Use **Exportar PDF** para gerar um documento para consulta ou impressão.

### Continuar um projeto salvo

Clique em **Abrir** e selecione o arquivo `.json`. O aplicativo carrega os dados e recalcula o plano de corte.

O JSON guarda os dados do projeto. O PDF é o documento de consulta e impressão; ele não substitui o JSON para edição posterior.

### Iniciar outro projeto

Clique em **Novo** e confirme **Novo projeto**. As peças, o desenho e as sobras são limpos; as configurações da chapa retornam aos valores iniciais.

Se quiser guardar alterações do projeto atual, clique em **Cancelar** e salve primeiro. Os arquivos já salvos não são apagados ao iniciar outro projeto.

Para sair, feche a janela pelo **X**. Salve antes de fechar.

## Giro das peças e posição da chapa

A opção **Permitir giro 90°** autoriza o otimizador a girar aquela peça, respeitando as restrições dos veios.

Na versão 1.1.2, a chapa é desenhada com o comprimento na horizontal e a largura na vertical. Ainda não existe um botão para girar a visualização da chapa inteira.

## Como interpretar o resultado

O programa testa diferentes estratégias de distribuição, mas não garante encontrar o melhor arranjo matematicamente possível.

A quantidade de chapas cadastrada é uma previsão: se forem necessárias mais chapas para acomodar todas as peças, o programa calcula essa necessidade e exibe um aviso.

Confira as medidas, os veios, a espessura do corte e a sequência de execução antes de cortar o material.

## Atualização e backup

Para atualizar, baixe a versão desejada, extraia e execute novamente:

```bash
bash instalar.sh
```

O instalador guarda uma cópia da instalação anterior e do lançador em uma pasta de backup e informa o caminho no terminal.

Por padrão:

- Aplicativo: `~/.local/share/plano-corte-gerson27/`
- Backups: `~/.local/share/plano-corte-gerson27-backups/`

Se `XDG_DATA_HOME` estiver configurado, essas pastas ficam dentro desse diretório. Os projetos JSON salvos pelo usuário não são apagados pelo instalador.

## Arquivos do projeto

| Arquivo | Função |
| --- | --- |
| `plano_corte.py` | Interface, projetos, visualização e exportação PDF. |
| `otimizador.py` | Algoritmo de distribuição e cálculo das sobras. |
| `instalar.sh` | Instalação para o usuário e criação do atalho. |
| `icone.png` | Ícone G27. |
| `LEIA-ME.txt` | Notas da versão. |

## Melhorias da versão 1.1.2

- Início com projeto vazio, sem carregar as quatro peças do exemplo antigo.
- Botão **Novo** com confirmação e limpeza do plano anterior.
- Ícone G27 no cabeçalho e integração do ícone com o lançador GTK/Wayland.
- Layout ajustado para 1366×768, mantendo o botão de otimização fora da área de rolagem.

## Como contribuir

Contribuições são bem-vindas! Consulte o [guia de contribuição](CONTRIBUTING.md) para preparar o ambiente, testar alterações e enviar uma pull request. As propostas serão revisadas antes de entrar na versão oficial.

## Sugestões e problemas

Use a aba [Issues](https://github.com/gersongarros/plano-de-corte-gerson27/issues) para relatar problemas ou sugerir melhorias. Informe a versão do aplicativo, o sistema utilizado e os passos para reproduzir o problema.

Projeto mantido por [gersongarros](https://github.com/gersongarros).
