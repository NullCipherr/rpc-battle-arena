# RPS Battle Arena

Sistema distribuído de jogo Pedra, Papel e Tesoura multiplayer com interface gráfica.

## Recursos

- Jogabilidade multiplayer em tempo real
- Interface gráfica com Pygame
- Arquitetura cliente-servidor usando XML-RPC
- Sistema de matchmaking
- Partidas em melhor de 5 rodadas
- Mecânica baseada em turnos
- Placar em tempo real
- Indicadores de status dos jogadores

## Requisitos

- Python 3.x
- Pygame
- Bibliotecas xmlrpc

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/rps-battle-arena.git
cd rps-battle-arena

# Instale as dependências
pip install pygame
```

## Como Usar

### Iniciar o Servidor

```bash
make server
```

### Iniciar o Cliente

```bash
make client
```

## Outros Comandos:

### Matar todos os processos

```bash
make killall
```

### Limpar Logs

```bash
make clean
```

### Ajuda

```bash
make help
```

## Como Jogar

- Use o mouse para interagir com os botões do jogo
- No menu principal:
  - Nova Partida: Inicia busca por um oponente
  - Créditos: Mostra informações dos desenvolvedores
  - Sair: Fecha o jogo
- Durante a partida:
  - Clique nos botões Pedra, Papel ou Tesoura para fazer sua jogada
  - Aguarde seu turno quando for a vez do oponente
  - O primeiro jogador a vencer 3 rodadas ganha a partida

## Estrutura do Projeto

```bash
rps-battle-arena/
├── server.py        # Servidor do jogo
├── client_gui.py    # Interface gráfica do cliente
├── Makefile        # Comandos de execução
└── logs/           # Arquivos de log

```
