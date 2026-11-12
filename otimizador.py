"""Otimizador de cortes guilhotina 2D, sem dependências gráficas.
Medidas em mm. Cortes sempre atravessam um retângulo livre.
"""
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class Retangulo:
    x: float
    y: float
    w: float
    h: float

@dataclass
class PecaColocada(Retangulo):
    nome: str
    indice: int
    girada: bool

@dataclass
class Folha:
    pecas: list
    sobras: list


def validar(projeto):
    chapa = projeto['chapa']
    for k in ('comprimento', 'largura'):
        if not 0 < float(chapa[k]) <= 100000:
            raise ValueError(f'Dimensão da chapa inválida: {k}.')
    if not 0 <= float(projeto['serra']) <= 50:
        raise ValueError('A espessura do corte deve estar entre 0 e 50 mm.')
    if not projeto['pecas']:
        raise ValueError('Adicione pelo menos uma peça.')
    qtd = 0
    for i, p in enumerate(projeto['pecas'], 1):
        if not str(p['nome']).strip():
            raise ValueError(f'Informe o nome da peça {i}.')
        if not 0 < float(p['comprimento']) <= 100000 or not 0 < float(p['largura']) <= 100000:
            raise ValueError(f'Medidas inválidas para a peça {i}.')
        if not 1 <= int(p['quantidade']) <= 2000:
            raise ValueError(f'Quantidade inválida para a peça {i}.')
        qtd += int(p['quantidade'])
    if qtd > 3000:
        raise ValueError('Máximo de 3.000 peças por projeto.')


def orientacoes(p, veio_chapa):
    """Veio em eixo X ou Y, peça em relação ao seu comprimento (X) / largura (Y)."""
    veio_peca = p.get('veio', 'livre')
    opcoes = []
    for girada in (False, True):
        if girada and (not p.get('girar', True)):
            continue
        eixo = veio_peca
        if girada:
            eixo = {'comprimento': 'largura', 'largura': 'comprimento'}.get(eixo, eixo)
        if veio_chapa != 'livre' and eixo != 'livre' and eixo != veio_chapa:
            continue
        w, h = float(p['comprimento']), float(p['largura'])
        if girada:
            w, h = h, w
        if girada and w == h:
            continue
        opcoes.append((w, h, girada))
    return opcoes


def dividir(r, w, h, kerf, modo):
    """Partição guilhotina: cortes de ponta a ponta do retângulo atual."""
    direita = max(0.0, r.w - w - kerf)
    baixo = max(0.0, r.h - h - kerf)
    saida = []
    if modo == 'vertical':
        if direita > 1e-7:
            saida.append(Retangulo(r.x + w + kerf, r.y, direita, r.h))
        if baixo > 1e-7:
            saida.append(Retangulo(r.x, r.y + h + kerf, w, baixo))
    else:
        if baixo > 1e-7:
            saida.append(Retangulo(r.x, r.y + h + kerf, r.w, baixo))
        if direita > 1e-7:
            saida.append(Retangulo(r.x + w + kerf, r.y, direita, h))
    return saida


def executar_estrategia(projeto, ordem, metodo):
    chapa = projeto['chapa']
    W, H, kerf = float(chapa['comprimento']), float(chapa['largura']), float(projeto['serra'])
    folhas = []
    pendentes = list(ordem)
    while pendentes:
        livres = [Retangulo(0, 0, W, H)]
        colocadas = []
        proximas = []
        for indice, p in pendentes:
            candidatos = []
            for j, r in enumerate(livres):
                for w, h, girada in orientacoes(p, chapa.get('veio', 'livre')):
                    if w <= r.w + 1e-7 and h <= r.h + 1e-7:
                        sobra = r.w*r.h - w*h
                        metricas = {
                            'area': (sobra, min(r.w-w, r.h-h)),
                            'lado': (min(r.w-w, r.h-h), sobra),
                            'longo': (max(r.w-w, r.h-h), sobra),
                        }
                        candidatos.append((metricas[metodo[0]], j, w, h, girada))
            if not candidatos:
                proximas.append((indice, p))
                continue
            _, j, w, h, girada = min(candidatos, key=lambda c: c[0])
            r = livres.pop(j)
            if metodo[1] == 'auto':
                modo = 'vertical' if (r.w-w)*r.h > (r.h-h)*r.w else 'horizontal'
            else:
                modo = metodo[1]
            livres.extend(dividir(r, w, h, kerf, modo))
            colocadas.append(PecaColocada(r.x, r.y, w, h, p['nome'], indice, girada))
        if not colocadas:
            raise ValueError('Uma ou mais peças não cabem na chapa, considerando o sentido dos veios e a rotação permitida. Verifique as dimensões.')
        folhas.append(Folha(colocadas, livres))
        pendentes = proximas
    return folhas


def otimizar(projeto):
    validar(projeto)
    chapa = projeto['chapa']
    expandidas = []
    for idx, p in enumerate(projeto['pecas']):
        if not any(w <= chapa['comprimento'] and h <= chapa['largura'] for w, h, _ in orientacoes(p, chapa.get('veio', 'livre'))):
            raise ValueError(f'A peça "{p["nome"]}" não cabe na chapa com as regras de veios/rotação definidas.')
        expandidas.extend((idx + 1, p) for _ in range(int(p['quantidade'])))
    classificacoes = [
        lambda item: float(item[1]['comprimento'])*float(item[1]['largura']),
        lambda item: max(float(item[1]['comprimento']),float(item[1]['largura'])),
        lambda item: min(float(item[1]['comprimento']),float(item[1]['largura'])),
        lambda item: float(item[1]['comprimento']),
        lambda item: float(item[1]['largura']),
    ]
    estrategias = [('area', 'auto'), ('area', 'vertical'), ('area', 'horizontal'),
                   ('lado', 'auto'), ('lado', 'vertical'), ('lado', 'horizontal'),
                   ('longo', 'auto')]
    melhor = None
    melhor_nota = None
    for chave in classificacoes:
        ordem = sorted(expandidas, key=chave, reverse=True)
        for metodo in estrategias:
            folhas = executar_estrategia(projeto, ordem, metodo)
            # Menos chapas; menos área fragmentada e menos retalhos pequenos.
            ultima = folhas[-1]
            area_livre = sum(r.w*r.h for r in ultima.sobras)
            maior = max((r.w*r.h for r in ultima.sobras), default=0)
            nota = (len(folhas), -maior, -area_livre, sum(len(f.sobras) for f in folhas))
            if melhor_nota is None or nota < melhor_nota:
                melhor_nota, melhor = nota, folhas
    area_chapa = float(chapa['comprimento'])*float(chapa['largura'])
    area_pecas = sum(float(p['comprimento'])*float(p['largura'])*int(p['quantidade']) for p in projeto['pecas'])
    return {
        'folhas': melhor,
        'quantidade_folhas': len(melhor),
        'quantidade_pecas': len(expandidas),
        'area_pecas': area_pecas,
        'area_total': area_chapa * len(melhor),
        'aproveitamento': area_pecas/(area_chapa*len(melhor))*100,
        'area_sobras': sum(r.w*r.h for f in melhor for r in f.sobras),
    }
