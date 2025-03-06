# A Queijada Real de Sintra

Um jogo de combate multiplayer baseado na lendária Queijada Real de Sintra, onde os melhores guerreiros lutam pelo direito de saborear este tesouro culinário!

## Narrativa

A lendária Queijada real de Sintra, passada de geração em geração e confecionada somente 1 vez por ano pelos melhores cozinheiros da família real, é pela primeira vez revelada ao público e todos querem ser os primeiros a dar uma dentada neste tesouro culinário. Mas há um problema... só o guerreiro mais forte pode comê-la!

Os maiores lutadores da região juntaram-se para o torneio definitivo! Agora, só há uma regra: duelo até ao último suspiro (ou até o rei ficar aborrecido e expulsar todos do palácio).

## Classes

- **O Pasteleiro Lutador** - Usa tabuleiros e rolos da massa como armas. Forte em combate corpo a corpo.
- **O Hipnotizador do Açúcar** - Atira açúcar em pó nos olhos dos inimigos para cegá-los temporariamente.
- **O Ladrão de Doces** - Rouba buffs dos adversários com ataques rápidos.

## Níveis

1. Pastelaria - Onde tudo começa, entre balcões e bandejas
2. Estação - Lute nas plataformas enquanto o trem passa
3. Floresta - Desafie seus inimigos em troncos e galhos
4. Montanha - Tenha cuidado com as plataformas traiçoeiras
5. Palácio - A batalha final pelo direito de comer a queijada!

## Setup

1. Instale Python 3.x
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## Iniciando o Jogo

1. Inicie o servidor:
```bash
python server.py
```

2. Inicie o(s) cliente(s):
```bash
python client.py
```

## Controles

- Setas direcionais: Mover para esquerda/direita
- Espaço: Pular
- E: Atacar/Usar habilidade especial
- SHIFT: Esquivar
- C: Escalar plataformas

## Recursos Especiais

- Buffs como "Glacê Indestrutível" (invencibilidade) e "Mordida Certeira" (dano aumentado)
- A queijada aparece no meio de cada round - o primeiro a pegá-la vence!
- Se houver empate por muito tempo, um pombo pode roubar a queijada e todos perdem
- Easter Egg: Os Três Mosqueteiros podem aparecer e conceder poder a todos os jogadores

## Objetivo

Ser o primeiro a comer a queijada real de Sintra, provando que você é o guerreiro mais forte do reino! 