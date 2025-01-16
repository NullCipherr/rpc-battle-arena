from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler
import random

class GameServer:
    def __init__(self):
        self.players = {}  # Armazena informações dos jogadores
        self.matches = {}  # Armazena partidas em andamento
        self.choices = {}  # Armazena as escolhas dos jogadores
        
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
                return True, match_id
                
        # Cria nova partida se não houver disponível
        match_id = len(self.matches)
        self.matches[match_id] = [player_id]
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
        """Determina o vencedor da partida"""
        players = self.matches[match_id]
        choice1 = self.choices[players[0]]
        choice2 = self.choices[players[1]]
        
        combinacoes_vencedoras = {
            "pedra": "tesoura",
            "papel": "pedra",
            "tesoura": "papel"
        }
        
        if choice1 == choice2:
            resultado = "Empate!"
        elif combinacoes_vencedoras[choice1] == choice2:
            resultado = f"Jogador {players[0]} venceu!"
        else:
            resultado = f"Jogador {players[1]} venceu!"
            
        # Limpa os dados da partida
        for player in players:
            del self.choices[player]
        del self.matches[match_id]
        
        return True, resultado

def main():
    # Cria o servidor
    porta = int(input("Digite a porta do servidor: "))
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
