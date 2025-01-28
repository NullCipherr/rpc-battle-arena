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
            print(f"[DEBUG] Jogador {player_id} removido da lista de espera")
            print(f"[DEBUG] Jogadores na lista de espera: {len(self.waiting_list)}")
            return True, f"Jogador {player_id} removido da lista de espera"
        return False, f"Jogador {player_id} não está na lista de espera"

    def add_to_waiting_list(self, player_id):
        """Adiciona um jogador à lista de espera e inicia o jogo quando houver um par"""
        print(f"[DEBUG] Adicionando jogador {player_id} à lista de espera...")
        self.waiting_list.append(player_id)
        print(f"[DEBUG] Jogador {player_id} adicionado à lista de espera")
        self.players[player_id] = {"in_game": False}
        print(f"[DEBUG] Jogadores na lista de espera: {len(self.waiting_list)}")
        if len(self.waiting_list) == 2:
            print("[DEBUG] Dois jogadores na lista de espera")
            print("[DEBUG] Iniciando partida...")
            player1 = self.waiting_list.pop(0)
            player2 = self.waiting_list.pop(0)
            match_id = len(self.matches)
            self.matches[match_id] = [player1, player2]
            self.scores[match_id] = {player1: 0, player2: 0}
            self.players[player1]["in_game"] = True
            self.players[player2]["in_game"] = True
            return True, f"Partida iniciada entre {player1} e {player2}"
        return True, "Aguardando mais jogadores"
    
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

def cleanup_socket(ip, port):
    """Força liberação da porta"""
    import subprocess
    print(f"[DEBUG] Forçando liberação da porta {port}...")
    try:
        subprocess.run(['fuser', '-k', f'{port}/tcp'], stderr=subprocess.DEVNULL)
        print(f"[DEBUG] Porta {port} liberada")
        return True
    except:
        print(f"[DEBUG] Erro ao liberar porta {port}")
        return False

def signal_handler(signum, frame):
    """Handler para shutdown gracioso"""
    print("\nEncerrando servidor...")
    sys.exit(0)

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
    servidor.register_function(cleanup_socket)
    servidor.register_function(servidor.system_listMethods, 'system.listMethods')
    print("[DEBUG] Servidor iniciado com sucesso")
    servidor.serve_forever()