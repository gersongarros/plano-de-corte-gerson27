#!/usr/bin/env python3
"""Plano de Corte Gerson27 v1.1.2 — GTK4 / Fedora."""
import os
import sys
import json
import math
import html
from pathlib import Path

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, GLib, Gdk, Pango
import cairo

from otimizador import otimizar

APP_ID = 'br.com.gerson27.planodecorte'
BASE = Path(__file__).resolve().parent
GLib.set_prgname(APP_ID)
GLib.set_application_name('Plano de Corte Gerson27')
MATERIAIS = ['MDF', 'Compensado', 'MDP', 'OSB', 'Acrílico', 'Outro']
VEIOS = ['livre', 'comprimento', 'largura']
VEIOS_LABEL = ['Sem restrição', 'No comprimento', 'Na largura']
COLORS = [(0.25, 0.65, 0.84), (0.37, 0.74, 0.54), (0.88, 0.62, 0.35), (0.65, 0.52, 0.83), (0.82, 0.47, 0.58), (0.47, 0.70, 0.69)]


def novo_projeto():
    return {'nome': 'Novo projeto', 'chapa': {'material': 'MDF', 'comprimento': 2750.0, 'largura': 1830.0, 'espessura': 15.0, 'quantidade': 1, 'veio': 'comprimento'},
            'serra': 3.0, 'pecas': []}


def dropdown(items, selecionado=0):
    w = Gtk.DropDown.new_from_strings(items)
    w.set_selected(selecionado)
    w.set_hexpand(True)
    return w


def campo(valor, largura=100):
    e = Gtk.Entry()
    e.set_text(str(valor).rstrip('0').rstrip('.') if isinstance(valor, float) else str(valor))
    e.set_width_chars(7)
    e.set_hexpand(True)
    e.set_size_request(largura, -1)
    e.set_input_purpose(Gtk.InputPurpose.NUMBER)
    return e


def num(widget, nome, inteiro=False):
    try:
        s = widget.get_text().strip().replace(',', '.')
        value = float(s)
        if not math.isfinite(value):
            raise ValueError()
        return int(value) if inteiro and value.is_integer() else (value if not inteiro else (_ for _ in ()).throw(ValueError()))
    except (ValueError, OverflowError):
        raise ValueError(f'Valor inválido em "{nome}". Use um número positivo.')


def rotulo(texto, css=None):
    l = Gtk.Label(label=texto)
    l.set_xalign(0)
    if css:
        l.add_css_class(css)
    return l


def caixa_vertical(espaco=8):
    return Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=espaco)


def caixa_horizontal(espaco=8):
    return Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=espaco)


def linha_campo(pai, titulo, widget):
    item = caixa_vertical(3)
    item.append(rotulo(titulo, 'dim-label'))
    item.append(widget)
    pai.append(item)


def arred(v):
    return f'{v:,.1f}'.replace(',', 'X').replace('.', ',').replace('X', '.') if abs(v-round(v))>1e-5 else f'{round(v):,}'.replace(',', '.')


class Janela(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app, title='Plano de Corte Gerson27 — v1.1.2')
        self.set_icon_name(APP_ID)
        self.set_default_size(1200, 650)
        self.set_size_request(900, 520)
        self.projeto = novo_projeto()
        self.arquivo = None
        self.resultado = None
        self.indice_folha = 0
        self.campos_pecas = []
        self.montar()
        self.iniciar_novo_projeto()

    def css(self):
        provider = Gtk.CssProvider()
        provider.load_from_data(b'''
          .cabecalho { padding: 10px 14px; background: #20313b; }
          .titulo-app { font-weight: 800; font-size: 19px; color: #fafafa; }
          .secao { font-size: 15px; font-weight: bold; margin: 5px 0; }
          .dim-label { font-size: 11px; opacity: .82; }
          .painel { padding: 12px; }
          .bloco { padding: 12px; border-radius: 9px; background: alpha(@theme_fg_color, 0.045); }
          .peca { padding: 8px; margin-bottom: 4px; border-radius: 7px; background: alpha(@theme_fg_color, 0.045); }
          .resumo { font-weight: 600; font-size: 13px; }
          .erro { color: #e87878; }
          .nota { font-size: 11px; opacity: .82; }
        ''')
        Gtk.StyleContext.add_provider_for_display(Gdk.Display.get_default(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def montar(self):
        self.css()
        root = caixa_vertical(0)
        self.set_child(root)
        header = caixa_horizontal(10)
        header.add_css_class('cabecalho')
        ico = Gtk.Image.new_from_file(str(BASE / 'icone.png'))
        ico.set_pixel_size(32)
        header.append(ico)
        titulo = rotulo('Plano de Corte Gerson27', 'titulo-app')
        titulo.set_hexpand(True)
        titulo.set_ellipsize(Pango.EllipsizeMode.END)
        titulo.set_width_chars(12)
        header.append(titulo)
        for texto, fn in [('Novo', self.novo), ('Abrir', self.abrir), ('Salvar', self.salvar), ('Salvar como', self.salvar_como), ('Exportar PDF', self.exportar)]:
            b = Gtk.Button(label=texto)
            b.connect('clicked', fn)
            header.append(b)
        root.append(header)

        split = Gtk.Paned(orientation=Gtk.Orientation.HORIZONTAL)
        split.set_position(430)
        split.set_wide_handle(True)
        split.set_hexpand(True)
        split.set_vexpand(True)
        root.append(split)

        scroll_esq = Gtk.ScrolledWindow()
        scroll_esq.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll_esq.set_size_request(385, 120)
        painel_esq = caixa_vertical(0)
        split.set_start_child(painel_esq)
        split.set_resize_start_child(False)
        split.set_shrink_start_child(False)
        split.set_shrink_end_child(False)
        scroll_esq.set_vexpand(True)
        painel_esq.append(scroll_esq)
        lateral = caixa_vertical(10)
        lateral.add_css_class('painel')
        scroll_esq.set_child(lateral)

        bloco = caixa_vertical(8)
        bloco.add_css_class('bloco')
        bloco.append(rotulo('1  Projeto e chapa', 'secao'))
        self.nome = Gtk.Entry()
        linha_campo(bloco, 'Nome do projeto', self.nome)
        self.material = dropdown(MATERIAIS)
        linha_campo(bloco, 'Material', self.material)
        dims = caixa_horizontal(6)
        self.c = campo(2750)
        self.l = campo(1830)
        linha_campo(dims, 'Comprimento (mm)', self.c)
        linha_campo(dims, 'Largura (mm)', self.l)
        bloco.append(dims)
        dims2 = caixa_horizontal(6)
        self.esp = campo(15)
        self.qch = campo(1)
        self.serra = campo(3)
        linha_campo(dims2, 'Espessura (mm)', self.esp)
        linha_campo(dims2, 'Qtd. chapas', self.qch)
        linha_campo(dims2, 'Corte da serra (mm)', self.serra)
        bloco.append(dims2)
        self.veio_chapa = dropdown(VEIOS_LABEL)
        linha_campo(bloco, 'Sentido dos veios da chapa', self.veio_chapa)
        lateral.append(bloco)

        bloco2 = caixa_vertical(7)
        bloco2.add_css_class('bloco')
        topo = caixa_horizontal(5)
        texto = rotulo('2  Peças para cortar', 'secao')
        texto.set_hexpand(True)
        topo.append(texto)
        btadd = Gtk.Button(label='+ Peça')
        btadd.connect('clicked', lambda *_: self.adicionar_peca())
        topo.append(btadd)
        bloco2.append(topo)
        nota_veio = rotulo('Veio: orientação do desenho da peça; “Livre” permite girar.', 'nota')
        nota_veio.set_wrap(True)
        bloco2.append(nota_veio)
        self.lista_pecas = caixa_vertical(5)
        bloco2.append(self.lista_pecas)
        lateral.append(bloco2)
        botao = Gtk.Button(label='OTIMIZAR PLANO DE CORTE')
        botao.add_css_class('suggested-action')
        botao.set_margin_bottom(8)
        botao.connect('clicked', self.otimizar_callback)
        botao.set_margin_start(12)
        botao.set_margin_end(12)
        botao.set_margin_top(8)
        painel_esq.append(botao)
        self.botao_otimizar = botao
        self.scroll_campos = scroll_esq

        direita = caixa_vertical(8)
        direita.add_css_class('painel')
        split.set_end_child(direita)
        topo_direita = caixa_horizontal(10)
        titulo2 = rotulo('3  Plano de corte e sobras', 'secao')
        titulo2.set_hexpand(True)
        topo_direita.append(titulo2)
        self.folha_anterior = Gtk.Button(label='◀')
        self.folha_anterior.connect('clicked', lambda *_: self.mudar_folha(-1))
        topo_direita.append(self.folha_anterior)
        self.folha_label = rotulo('Chapa 0/0')
        topo_direita.append(self.folha_label)
        self.folha_proxima = Gtk.Button(label='▶')
        self.folha_proxima.connect('clicked', lambda *_: self.mudar_folha(1))
        topo_direita.append(self.folha_proxima)
        direita.append(topo_direita)
        self.desenho = Gtk.DrawingArea()
        self.desenho.set_content_width(320)
        self.desenho.set_content_height(180)
        self.desenho.set_hexpand(True)
        self.desenho.set_vexpand(True)
        self.desenho.set_draw_func(self.desenhar)
        desenho_box = Gtk.Frame()
        desenho_box.set_child(self.desenho)
        desenho_box.set_vexpand(True)
        direita.append(desenho_box)
        self.resumo = rotulo('Informe as peças e clique em Otimizar.', 'resumo')
        self.resumo.set_wrap(True)
        direita.append(self.resumo)
        direita.append(rotulo('Sobras dimensionadas da chapa exibida (mm)', 'secao'))
        sobra_scroll = Gtk.ScrolledWindow()
        sobra_scroll.set_min_content_height(105)
        sobra_scroll.set_max_content_height(150)
        self.sobras = Gtk.TextView()
        self.sobras.set_editable(False)
        self.sobras.set_cursor_visible(False)
        self.sobras.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.sobras.set_left_margin(10)
        self.sobras.set_top_margin(7)
        sobra_scroll.set_child(self.sobras)
        direita.append(sobra_scroll)
        self.status = rotulo('Pronto.', 'nota')
        root.append(self.status)
        self.status.set_ellipsize(Pango.EllipsizeMode.END)
        self.status.set_margin_start(14)
        self.status.set_margin_bottom(6)

    def adicionar_peca(self, dados=None):
        dados = dados or {'nome': f'Peça {len(self.campos_pecas)+1}', 'comprimento': 700, 'largura': 900, 'quantidade': 1, 'veio': 'livre', 'girar': True}
        card = caixa_vertical(6)
        card.add_css_class('peca')
        linha = caixa_horizontal(6)
        nome = Gtk.Entry()
        nome.set_text(str(dados['nome']))
        nome.set_hexpand(True)
        linha.append(nome)
        remover = Gtk.Button(label='✕')
        remover.set_tooltip_text('Remover peça')
        linha.append(remover)
        card.append(linha)
        medidas = caixa_horizontal(5)
        comprimento = campo(dados['comprimento'], 74)
        largura = campo(dados['largura'], 74)
        qtd = campo(dados['quantidade'], 60)
        linha_campo(medidas, 'Comprimento', comprimento)
        linha_campo(medidas, 'Largura', largura)
        linha_campo(medidas, 'Quantidade', qtd)
        card.append(medidas)
        opcoes = caixa_horizontal(8)
        veio = dropdown(VEIOS_LABEL, VEIOS.index(dados.get('veio', 'livre')))
        linha_campo(opcoes, 'Veio da peça', veio)
        girar = Gtk.CheckButton(label='Permitir giro 90°')
        girar.set_active(bool(dados.get('girar', True)))
        opcoes.append(girar)
        card.append(opcoes)
        info = dict(card=card, nome=nome, comprimento=comprimento, largura=largura, quantidade=qtd, veio=veio, girar=girar)
        self.campos_pecas.append(info)
        self.lista_pecas.append(card)
        remover.connect('clicked', lambda *_: self.remover_peca(info))

    def remover_peca(self, info):
        self.lista_pecas.remove(info['card'])
        self.campos_pecas.remove(info)

    def preencher(self, p):
        self.nome.set_text(p.get('nome', 'Meu plano de corte'))
        chapa = p['chapa']
        self.material.set_selected(MATERIAIS.index(chapa.get('material', 'Outro')) if chapa.get('material') in MATERIAIS else 5)
        for widget, chave in ((self.c, 'comprimento'), (self.l, 'largura'), (self.esp, 'espessura'), (self.qch, 'quantidade')):
            widget.set_text(str(chapa.get(chave, 1)))
        self.veio_chapa.set_selected(VEIOS.index(chapa.get('veio', 'livre')))
        self.serra.set_text(str(p.get('serra', 3)))
        for info in list(self.campos_pecas):
            self.remover_peca(info)
        for peca in p.get('pecas', []):
            self.adicionar_peca(peca)

    def coletar(self):
        return {
            'nome': self.nome.get_text().strip() or 'Plano de corte',
            'chapa': {'material': MATERIAIS[self.material.get_selected()],
                      'comprimento': num(self.c, 'comprimento da chapa'),
                      'largura': num(self.l, 'largura da chapa'),
                      'espessura': num(self.esp, 'espessura da chapa'),
                      'quantidade': num(self.qch, 'quantidade de chapas', True),
                      'veio': VEIOS[self.veio_chapa.get_selected()]},
            'serra': num(self.serra, 'espessura do corte'),
            'pecas': [
                {'nome': info['nome'].get_text().strip(),
                 'comprimento': num(info['comprimento'], 'comprimento da peça'),
                 'largura': num(info['largura'], 'largura da peça'),
                 'quantidade': num(info['quantidade'], 'quantidade da peça', True),
                 'veio': VEIOS[info['veio'].get_selected()],
                 'girar': info['girar'].get_active()}
                for info in self.campos_pecas]
        }

    def alerta(self, titulo, descricao):
        dlg = Gtk.MessageDialog(transient_for=self, modal=True,
                                buttons=Gtk.ButtonsType.OK, message_type=Gtk.MessageType.INFO,
                                text=titulo, secondary_text=descricao)
        dlg.connect('response', lambda d, *_: d.destroy())
        dlg.present()

    def otimizar_callback(self, _):
        try:
            p = self.coletar()
            resultado = otimizar(p)
            self.projeto = p
            self.resultado = resultado
            self.indice_folha = 0
            usadas = resultado['quantidade_folhas']
            previstas = p['chapa']['quantidade']
            aviso = f'  •  Atenção: cadastradas {previstas} chapas, mas são necessárias {usadas}.' if usadas > previstas else ''
            self.resumo.set_text(f'{resultado["quantidade_pecas"]} peças  •  {usadas} chapa(s)  •  Aproveitamento: {resultado["aproveitamento"]:.1f}%  •  Área de peças: {resultado["area_pecas"]/1e6:.3f} m²'+aviso)
            self.status.set_text('Otimização guilhotina concluída. Compare as sobras de cada chapa.')
            self.atualizar_folha()
        except Exception as exc:
            self.status.set_text('Erro: ' + str(exc))
            self.alerta('Não foi possível otimizar', str(exc))
        return False

    def mudar_folha(self, direcao):
        if self.resultado:
            self.indice_folha = max(0, min(len(self.resultado['folhas'])-1, self.indice_folha+direcao))
            self.atualizar_folha()

    def atualizar_folha(self):
        if not self.resultado:
            return
        total = len(self.resultado['folhas'])
        self.folha_label.set_text(f'Chapa {self.indice_folha+1}/{total}')
        self.folha_anterior.set_sensitive(self.indice_folha > 0)
        self.folha_proxima.set_sensitive(self.indice_folha < total-1)
        folhas = self.resultado['folhas']
        livres = sorted(folhas[self.indice_folha].sobras, key=lambda r: -r.w*r.h)
        txt = '\n'.join(f'{i}. {arred(r.w)} × {arred(r.h)} mm  —  {r.w*r.h/1e6:.4f} m²' for i, r in enumerate(livres, 1) if r.w >= 1 and r.h >= 1)
        self.sobras.get_buffer().set_text(txt or 'Sem sobras retangulares aproveitáveis.')
        self.desenho.queue_draw()

    def desenhar(self, area, cr, largura, altura):
        cr.set_source_rgb(0.13, 0.16, 0.18)
        cr.paint()
        if not self.resultado:
            return
        self.pintar_plano(cr, largura, altura, self.projeto, self.resultado['folhas'][self.indice_folha])

    @staticmethod
    def pintar_plano(cr, largura, altura, projeto, folha, margem=33, legenda=True):
        W = float(projeto['chapa']['comprimento'])
        H = float(projeto['chapa']['largura'])
        espacox = max(1, largura-2*margem)
        espacoy = max(1, altura-2*margem)
        escala = min(espacox/W, espacoy/H)
        ox = (largura-W*escala)/2
        oy = (altura-H*escala)/2
        cr.set_source_rgb(0.42, 0.37, 0.29)
        cr.rectangle(ox, oy, W*escala, H*escala)
        cr.fill()
        for i, p in enumerate(folha.pecas):
            x, y, w, h = ox+p.x*escala, oy+p.y*escala, p.w*escala, p.h*escala
            r, g, b = COLORS[(p.indice-1)%len(COLORS)]
            cr.set_source_rgb(r,g,b)
            cr.rectangle(x,y,w,h)
            cr.fill_preserve()
            cr.set_source_rgb(0.09,0.13,0.16)
            cr.set_line_width(1.2)
            cr.stroke()
            if w > 58 and h > 31:
                cr.save()
                cr.rectangle(x+2,y+2,w-4,h-4)
                cr.clip()
                cr.set_source_rgb(0.06,0.13,0.18)
                cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                cr.set_font_size(min(12, max(8, w/9)))
                texto = str(p.nome)[:23]
                ext = cr.text_extents(texto)
                cr.move_to(x+(w-ext.width)/2, y+h/2-3)
                cr.show_text(texto)
                cr.set_font_size(min(11,max(8,w/11)))
                dim = f'{arred(p.w)} × {arred(p.h)}'
                ext = cr.text_extents(dim)
                cr.move_to(x+(w-ext.width)/2, y+h/2+12)
                cr.show_text(dim)
                cr.restore()
        for r in folha.sobras:
            x, y, w, h = ox+r.x*escala, oy+r.y*escala, r.w*escala, r.h*escala
            cr.set_source_rgb(.37,.39,.4)
            cr.rectangle(x,y,w,h)
            cr.fill_preserve()
            cr.set_source_rgb(.85,.77,.60)
            cr.set_line_width(1)
            cr.stroke()
            if w > 65 and h > 29:
                cr.save()
                cr.rectangle(x+1,y+1,w-2,h-2)
                cr.clip()
                cr.set_source_rgb(.98,.96,.87)
                cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
                cr.set_font_size(10)
                texto = f'{arred(r.w)} × {arred(r.h)}'
                ext = cr.text_extents(texto)
                cr.move_to(x+(w-ext.width)/2, y+h/2+4)
                cr.show_text(texto)
                cr.restore()
        cr.set_source_rgb(.95,.95,.95)
        cr.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
        cr.set_font_size(12)
        topo = f'{arred(W)} mm'
        ex = cr.text_extents(topo)
        cr.move_to(ox+(W*escala-ex.width)/2, max(15,oy-8))
        cr.show_text(topo)
        cr.save()
        cr.translate(max(12, ox-8), oy+H*escala/2)
        cr.rotate(-math.pi/2)
        ex = cr.text_extents(f'{arred(H)} mm')
        cr.move_to(-ex.width/2,0)
        cr.show_text(f'{arred(H)} mm')
        cr.restore()

    def novo(self, _):
        dlg = Gtk.MessageDialog(
            transient_for=self, modal=True,
            buttons=Gtk.ButtonsType.NONE,
            message_type=Gtk.MessageType.QUESTION,
            text='Iniciar um novo projeto?',
            secondary_text='O projeto atual será retirado da tela. Se ainda precisa salvá-lo, clique em Cancelar e depois em Salvar. Os arquivos já salvos não serão apagados.')
        dlg.add_button('Cancelar', Gtk.ResponseType.CANCEL)
        dlg.add_button('Novo projeto', Gtk.ResponseType.ACCEPT)
        dlg.set_default_response(Gtk.ResponseType.CANCEL)

        def resposta(dialogo, resposta):
            dialogo.destroy()
            if resposta == Gtk.ResponseType.ACCEPT:
                self.iniciar_novo_projeto()

        dlg.connect('response', resposta)
        dlg.present()

    def iniciar_novo_projeto(self):
        projeto = novo_projeto()
        projeto['nome'] = 'Novo projeto'
        projeto['pecas'] = []
        self.arquivo = None
        self.projeto = projeto
        self.preencher(projeto)
        self.resultado = None
        self.indice_folha = 0
        self.folha_label.set_text('Chapa 0/0')
        self.folha_anterior.set_sensitive(False)
        self.folha_proxima.set_sensitive(False)
        self.sobras.get_buffer().set_text('')
        self.resumo.set_text('Adicione as peças e clique em Otimizar plano de corte.')
        self.status.set_text('Novo projeto criado. Defina a chapa e adicione peças com + Peça.')
        self.desenho.queue_draw()
        self.scroll_campos.get_vadjustment().set_value(0)
        self.nome.grab_focus()
        self.nome.select_region(0, -1)

    def selecionar_arquivo(self, titulo, acao, extensao, callback):
        seletor = Gtk.FileChooserNative.new(titulo, self, acao, 'Selecionar' if acao == Gtk.FileChooserAction.OPEN else 'Salvar', 'Cancelar')
        filtro = Gtk.FileFilter()
        filtro.set_name(f'Arquivos {extensao.upper()}')
        filtro.add_pattern('*.'+extensao)
        seletor.add_filter(filtro)
        if acao == Gtk.FileChooserAction.SAVE:
            seletor.set_current_name('plano_corte_gerson27.'+extensao)
        def resposta(dialogo, resposta):
            if resposta == Gtk.ResponseType.ACCEPT:
                caminho = dialogo.get_file().get_path()
                if not caminho.lower().endswith('.'+extensao):
                    caminho += '.'+extensao
                try:
                    callback(caminho)
                except Exception as exc:
                    self.alerta('Erro no arquivo', str(exc))
            dialogo.destroy()
        seletor.connect('response', resposta)
        seletor.show()

    def abrir(self, _):
        def carregar(caminho):
            with open(caminho, 'r', encoding='utf-8') as f:
                p = json.load(f)
            self.preencher(p)
            self.arquivo = caminho
            self.otimizar_callback(None)
            self.status.set_text('Projeto aberto: '+caminho)
        self.selecionar_arquivo('Abrir projeto', Gtk.FileChooserAction.OPEN, 'json', carregar)

    def gravar(self, caminho):
        p = self.coletar()
        with open(caminho, 'w', encoding='utf-8') as f:
            json.dump(p, f, ensure_ascii=False, indent=2)
        self.arquivo = caminho
        self.status.set_text('Projeto salvo: '+caminho)

    def salvar(self, _):
        if self.arquivo:
            try:
                self.gravar(self.arquivo)
            except Exception as exc:
                self.alerta('Erro ao salvar', str(exc))
        else:
            self.salvar_como(None)

    def salvar_como(self, _):
        self.selecionar_arquivo('Salvar projeto', Gtk.FileChooserAction.SAVE, 'json', self.gravar)

    def exportar(self, _):
        if not self.resultado:
            self.alerta('Sem plano de corte', 'Clique em Otimizar antes de exportar.')
            return
        self.selecionar_arquivo('Exportar PDF', Gtk.FileChooserAction.SAVE, 'pdf', self.gravar_pdf)

    def gravar_pdf(self, caminho):
        # A4 paisagem, medidas em pontos PDF; uma página por chapa.
        p = self.coletar()
        resultado = otimizar(p)
        doc = cairo.PDFSurface(caminho, 842, 595)
        ctx = cairo.Context(doc)
        for index, folha in enumerate(resultado['folhas']):
            ctx.set_source_rgb(1,1,1)
            ctx.paint()
            ctx.set_source_rgb(.13,.20,.24)
            ctx.select_font_face('Sans', cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            ctx.set_font_size(18)
            ctx.move_to(35, 36)
            ctx.show_text('Plano de Corte Gerson27')
            ctx.set_font_size(11)
            ctx.move_to(35, 57)
            ctx.show_text(f'{p["nome"]} - {p["chapa"]["material"]} - Chapa {index+1}/{len(resultado["folhas"])}')
            ctx.set_source_rgb(.12,.12,.12)
            ctx.set_font_size(10)
            ctx.move_to(35, 77)
            ctx.show_text(f'Chapa: {arred(p["chapa"]["comprimento"])} x {arred(p["chapa"]["largura"])} mm | Corte: {arred(p["serra"])} mm | Aproveitamento: {resultado["aproveitamento"]:.1f}%')
            ctx.save()
            ctx.rectangle(25,88,792,345)
            ctx.clip()
            ctx.translate(25,88)
            self.pintar_plano(ctx, 792, 345, p, folha)
            ctx.restore()
            ctx.set_source_rgb(.12,.12,.12)
            ctx.set_font_size(11)
            ctx.move_to(35,452)
            ctx.show_text('Pecas nesta chapa:')
            ctx.set_font_size(9)
            pecas = [f'{peca.nome}: {arred(peca.w)} x {arred(peca.h)} mm' for peca in folha.pecas]
            ctx.move_to(35,470)
            ctx.show_text(' | '.join(pecas)[:125])
            ctx.set_font_size(11)
            ctx.move_to(35,497)
            ctx.show_text('Sobras retangulares (mm):')
            ctx.set_font_size(10)
            sobras = sorted(folha.sobras, key=lambda r: -r.w*r.h)
            texto = '   |   '.join(f'{arred(r.w)} x {arred(r.h)}' for r in sobras if r.w>=1 and r.h>=1)
            for i, trecho in enumerate([texto[n:n+105] for n in range(0,len(texto),105)][:3]):
                ctx.move_to(35,515+i*16)
                ctx.show_text(trecho)
            ctx.set_font_size(9)
            ctx.move_to(35,578)
            ctx.show_text('Cortes guilhotina - conferir medidas, sentido dos veios e seguranca antes de cortar.')
            ctx.show_page()
        doc.finish()
        self.status.set_text('PDF exportado: '+caminho)
        self.alerta('PDF gerado', f'Arquivo salvo em:\n{caminho}')


class Aplicativo(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self):
        janela = self.props.active_window
        if janela is None:
            janela = Janela(self)
        janela.present()


if __name__ == '__main__':
    raise SystemExit(Aplicativo().run(sys.argv))
