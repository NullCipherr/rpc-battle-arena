from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random
import os

class GameServer:
    def __init__(self):
        self.players = {}  # Armazena informações dos jogadores
        self.matches = {}  # Armazena partidas em andamento
        self.choices = {}  # Armazena as escolhas dos jogadores
        self.scores = {}   # Armazena o placar das partidas
        self.max_rounds = 5  # Número máximo de rodadas
        
    def register_player(self, player_id, port):
        """Registra um novo jogador se o ID não estiver em uso"""
        if player_id in self.players:
            return False, "ID de jogador já existe"
        self.players[player_id] = {"port": port, "in_game": False}
        return True, f"Jogador {player_id} registrado com sucesso"
    
    def find_match(self, player_id):
        """Encontra ou cria uma partida para um jogador"""
        if player_id not in self.players:
            return False, "Jogador não registrado"
            
        # Verifica se o jogador já está em uma partida
        for match_id, players in self.matches.items():
            if player_id in players:
                return True, match_id
                
        # Procura por partidas disponíveis
        for match_id, players in self.matches.items():
            if len(players) == 1:
                self.matches[match_id].append(player_id)
                # Inicializa o placar para a partida
                if match_id not in self.scores:
                    self.scores[match_id] = {
                        players[0]: 0,  # Jogador 1
                        player_id: 0     # Jogador 2
                    }
                return True, match_id
                
        # Cria nova partida se não houver disponível
        match_id = len(self.matches)
        self.matches[match_id] = [player_id]
        self.scores[match_id] = {player_id: 0}
        return True, match_id
    
    def make_move(self, player_id, match_id, choice):
        """Processa a jogada de um jogador"""
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        if player_id not in self.matches[match_id]:
            return False, "Jogador não está nesta partida"
        if choice not in ["pedra", "papel", "tesoura"]:
            return False, "Escolha inválida"
            
        self.choices[player_id] = choice
        
        # Verifica se ambos os jogadores fizeram suas escolhas
        match_players = self.matches[match_id]
        if len(match_players) == 2 and all(p in self.choices for p in match_players):
            return self.resolve_match(match_id)
        
        return True, "Jogada registrada, aguardando oponente"
    
    def resolve_match(self, match_id):
        """Determina o vencedor da rodada e atualiza o placar"""
        players = self.matches[match_id]
        choice1 = self.choices[players[0]]
        choice2 = self.choices[players[1]]
        
        combinacoes_vencedoras = {
            "pedra": "tesoura",
            "papel": "pedra",
            "tesoura": "papel"
        }
        
        # Determina o vencedor da rodada
        if choice1 == choice2:
            resultado = "Empate!"
        elif combinacoes_vencedoras[choice1] == choice2:
            resultado = f"Jogador {players[0]} venceu a rodada!"
            self.scores[match_id][players[0]] += 1
        else:
            resultado = f"Jogador {players[1]} venceu a rodada!"
            self.scores[match_id][players[1]] += 1
            
        # Verifica se alguém ganhou o jogo
        for player, score in self.scores[match_id].items():
            if score >= (self.max_rounds // 2 + 1):
                resultado = f"Jogador {player} venceu o jogo!"
                # Limpa os dados da partida
                del self.scores[match_id]
                del self.matches[match_id]
                for p in players:
                    if p in self.choices:
                        del self.choices[p]
                return True, resultado
        
        # Limpa apenas as escolhas para a próxima rodada
        for player in players:
            if player in self.choices:
                del self.choices[player]
        
        return True, resultado

    def get_match_status(self, player_id, match_id):
        """Retorna o status atual da partida"""
        if match_id not in self.matches or match_id not in self.scores:
            return False, "Partida não encontrada"
        
        return True, {
            "scores": self.scores[match_id],
            "current_round": sum(self.scores[match_id].values()) + 1,
            "max_rounds": self.max_rounds
        }

def main():
    # Se estiver em modo debug, usa a porta da variável de ambiente
    if 'PORTA' in os.environ:
        porta = int(os.environ['PORTA'])
    else:
        porta = int(input("Digite a porta do servidor: "))
    
    # Cria o servidor
    servidor = SimpleXMLRPCServer(("localhost", porta), 
                               requestHandler=SimpleXMLRPCRequestHandler,
                               allow_none=True)
    
    # Registra a instância do jogo
    jogo = GameServer()
    servidor.register_instance(jogo)
    
    print(f"Servidor rodando na porta {porta}...")
    servidor.serve_forever()

if __name__ == "__main__":
    main()
