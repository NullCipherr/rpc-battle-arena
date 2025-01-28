import xmlrpc.server as rpc
import socket
import sys
import random
import os
import signal
import argparse

class GameServer:
    def __init__(self):
        self.players = {}  # Armazena informações dos jogadores
        self.matches = {}  # Armazena partidas em andamento
        self.choices = {}  # Armazena as escolhas dos jogadores
        self.scores = {}   # Armazena o placar das partidas
        self.max_rounds = 5  # Número máximo de rodadas
        self.waiting_list = []  # Lista de espera para partidas
        self.current_turn = {}  # Armazena o jogador atual de cada partida
        
    def register_player(self, player_id, port):
        """Registra um novo jogador se o ID não estiver em uso"""
        if player_id in self.players:
            return False, "ID de jogador já existe"
        self.players[player_id] = {"port": port, "in_game": False}
        return True, f"Jogador {player_id} registrado com sucesso"
    
    def remove_waiting_list(self, player_id):
        print(f"[DEBUG] Removendo jogador {player_id} da lista de espera...")
        if player_id in self.waiting_list:
            self.waiting_list.remove(player_id)
            return True, f"Jogador {player_id} removido da lista de espera"
        return False, f"Jogador {player_id} não está na lista de espera"

    def add_to_waiting_list(self, player_id):
        """Adiciona um jogador à lista de espera"""
        print(f"[DEBUG] Adicionando jogador {player_id} à lista de espera...")
        self.waiting_list.append(player_id)
        print(f"[DEBUG] Jogador {player_id} adicionado à lista de espera")
        self.players[player_id] = {"in_game": False}
        print(f"[DEBUG] Jogadores na lista de espera: {len(self.waiting_list)}")
        return True, "Aguardando mais jogadores"
    
    def update_players(self, match_id):
        """Envia atualizações para ambos os jogadores"""
        match_players = self.matches[match_id]
        current_turn = self.current_turn[match_id]
        for player in match_players:
            port = self.players[player]["port"]
            message = f"Atualização: É a vez do jogador {current_turn}"
            self.send_message(player, port, message)
            print(f"[DEBUG] Enviando atualização para jogador {player} na porta {port}")
            print(f"[DEBUG] É a vez do jogador {current_turn}")
    
    def send_message(self, player_id, port, message):
        """Envia uma mensagem para o jogador via socket"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.connect(('localhost', port))
                sock.sendall(message.encode('utf-8'))
                print(f"[DEBUG] Mensagem enviada para jogador {player_id} na porta {port}")
        except ConnectionRefusedError:
            print(f"[ERROR] Não foi possível conectar ao jogador {player_id} na porta {port}")
    
    def find_match(self, player_id):
        """Encontra ou cria uma partida para um jogador"""
        if player_id not in self.players:
            return False, "Jogador não registrado"
            
        # Verifica se o jogador já está em uma partida
        for match_id, players in self.matches.items():
            if player_id in players:
                return True, match_id
                
        # Verifica se há jogadores na lista de espera
        if len(self.waiting_list) >= 2:
            print("[DEBUG] Dois jogadores na lista de espera")
            player1 = self.waiting_list.pop(0)
            player2 = self.waiting_list.pop(0)
            match_id = len(self.matches) + 1
            self.matches[match_id] = [player1, player2]
            self.scores[match_id] = {player1: 0, player2: 0}
            self.players[player1]["in_game"] = True
            self.players[player2]["in_game"] = True
            self.current_turn[match_id] = player1  # Inicializa o turno com o primeiro jogador
            print(f"[DEBUG] Partida criada: {match_id} com jogadores {player1} e {player2}")
            return True, match_id
        else:
            print("[DEBUG] Menos de dois jogadores na lista de espera")
            return False, "Aguardando mais jogadores"
    
    def make_move(self, player_id, match_id, choice):
        """Processa a jogada de um jogador"""
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        if player_id not in self.matches[match_id]:
            return False, "Jogador não está nesta partida"
        if choice not in ["pedra", "papel", "tesoura"]:
            return False, "Escolha inválida"
        
        # Verifica se é o turno do jogador
        if self.current_turn[match_id] != player_id:
            return False, "Não é o seu turno"
        else:
            print(f"[DEBUG] Jogador {player_id} escolheu {choice}")
        
        # Registra a escolha do jogador
        self.choices[player_id] = choice
        print(f"[DEBUG] Escolhas registradas: {self.choices}")
        
        # Alterna o turno para o próximo jogador
        self.next_turn(match_id)
        
        # Verifica se ambos os jogadores fizeram suas escolhas
        match_players = self.matches[match_id]
        if len(match_players) == 2 and all(p in self.choices for p in match_players):
            print(f"[DEBUG] Ambos os jogadores fizeram suas escolhas")
            return self.resolve_match(match_id)
        return True, "Jogada registrada, aguardando oponente"
    
    def next_turn(self, match_id):
        """Alterna o turno para o próximo jogador"""
        match_players = self.matches[match_id]
        current_player = self.current_turn[match_id]
        next_player = match_players[1] if match_players[0] == current_player else match_players[0]
        self.current_turn[match_id] = next_player
        
    def get_opponent_id(self, player_id, match_id):
        """Retorna o ID do oponente de um jogador"""
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        if player_id not in self.matches[match_id]:
            return False, "Jogador não está nesta partida"
        match_players = self.matches[match_id]
        return True, [p for p in match_players if p != player_id][0]
        
    def get_current_turn(self, match_id):
        """Retorna o jogador atual de uma partida"""
        if match_id in self.current_turn:
            return self.current_turn[match_id]
        return None
    
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
        
        # Lógica para determinar o vencedor da rodada
        if choice1 == choice2:
            resultado = "Empate na rodada!"
        elif (choice1 == "pedra" and choice2 == "tesoura") or \
            (choice1 == "tesoura" and choice2 == "papel") or \
            (choice1 == "papel" and choice2 == "pedra"):
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
        
        # Alterna a vez para o próximo jogador
        self.current_turn[match_id] = players[1] if self.current_turn[match_id] == players[0] else players[0]

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

def check_port(ip, port):
    """Verifica se a porta está disponível"""
    print(f"[DEBUG] Verificando disponibilidade da porta {port}...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        print(f"[DEBUG] Tentando ligar a porta {port}...")
        sock.bind((ip, port))
        sock.close()
        print(f"[DEBUG] Porta {port} disponível")
        return True
    except OSError:
        print(f"[DEBUG] Porta {port} em uso")
        return False

if __name__ == "__main__":
    # Configurar argumentos de linha de comando
    parser = argparse.ArgumentParser(description='Servidor RPS Battle Arena')
    parser.add_argument('--ip', default='localhost', help='IP do servidor')
    parser.add_argument('--porta', type=int, default=5000, help='Porta do servidor')
    args = parser.parse_args()    
    
    ip = args.ip
    porta = args.porta

    print("[DEBUG] Iniciando servidor RPS Battle Arena...")
    print(f"[SETTINGS] IP: {ip}")
    print(f"[SETTINGS] Porta: {porta}")
    print(f"[SETTINGS] PID do servidor: {os.getpid()}")

    # Iniciar servidor
    print(f"[DEBUG] Iniciando servidor em {ip}:{porta}")
    servidor = rpc.SimpleXMLRPCServer((ip, porta))
    servidor.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    servidor.register_instance(GameServer())
    servidor.register_function(check_port)
    servidor.register_function(servidor.system_listMethods, 'system.listMethods')
    print("[DEBUG] Servidor iniciado com sucesso")
    servidor.serve_forever()