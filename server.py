# Alunos
# Andrei Roberto da Costa
# Daniel Aparecido da Cunha Braz
# Henrique Rosa de Araujo 

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
        self.round = 0  # Número da rodada atual.
        self.max_rounds = 5  # Número máximo de rodadas
        self.waiting_list = []  # Lista de espera para partidas
        self.current_turn = {}  # Armazena o jogador atual de cada partida
        
    def register_player(self, player_id, port):
        """
        Registra um novo jogador no sistema, associando seu ID e porta.

        Args:
            player_id (str): O identificador único do jogador.
            port (int): A porta na qual o jogador está escutando.

        Returns:
            tuple: Um booleano indicando sucesso ou falha e uma mensagem explicativa.
                - (True, "Jogador {player_id} registrado com sucesso") se o registro for bem-sucedido.
                - (False, "ID de jogador já existe") se o ID já estiver registrado.

        Observações:
            - O jogador só será registrado se o `player_id` ainda não estiver na lista de jogadores.
        """
        if player_id in self.players:
            return False, "ID de jogador já existe"
        self.players[player_id] = {"port": port, "in_game": False}
        return True, f"Jogador {player_id} registrado com sucesso"
    
    def add_match(self, player1, player2):
        """Adiciona uma partida ao sistema.
        Args:
            player1 (str): ID do primeiro jogador.
            player2 (str): ID do segundo jogador.
        Returns:
            tuple: Um valor booleano indicando sucesso e o ID da partida.
        """
        match_id = len(self.matches) + 1
        self.matches[match_id] = [player1, player2]
        self.scores[match_id] = {player1: 0, player2: 0}
        self.current_turn[match_id] = player1  # Inicializa o turno com o primeiro jogador
        return True, match_id
    
    def add_rounds(self, match_id):
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        if match_id not in self.scores:
            return False, "Placar não encontrado"
        self.round += 1 # Incrementa o número da rodada
        if self.round > self.max_rounds:
            return False, "Número máximo de rodadas atingido"
        return True, f"Rodada {self.round} iniciada"
    
    def remove_waiting_list(self, player_id):
        """
        Remove um jogador da lista de espera.

        Args:
            player_id (str): O identificador único do jogador.

        Returns:
            tuple: Um booleano indicando sucesso ou falha e uma mensagem explicativa.
                - (True, "Jogador {player_id} removido da lista de espera") se a remoção for bem-sucedida.
                - (False, "Jogador {player_id} não está na lista de espera") se o jogador não estiver na lista.

        Observações:
            - A operação não altera o status do jogador na lista geral de jogadores (`self.players`).
        """
        print(f"[DEBUG] Removendo jogador {player_id} da lista de espera...")
        if player_id in self.waiting_list:
            self.waiting_list.remove(player_id)
            if player_id in self.players:
                self.players[player_id]["in_game"] = False
            return True, f"Jogador {player_id} removido da lista de espera"
        return False, f"Jogador {player_id} não está na lista de espera"
    
    def add_score(self, player_id, match_id):
        """" Adiciona um ponto ao jogador vencedor da partida.
        Args:
            player_id (str): ID do jogador vencedor.
            match_id (int): ID da partida.
        Returns:
            tuple: Um valor booleano indicando sucesso e uma mensagem informativa.
        """
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        if player_id not in self.scores[match_id]:
            return False, "Jogador não está nesta partida"
        self.scores[match_id][player_id] += 1
        return True, f"Ponto adicionado ao jogador {player_id}"

    def add_to_waiting_list(self, player_id):
        """
        Adiciona um jogador à lista de espera, preparando-o para ser incluído em uma partida.

        Args:
            player_id (str): O identificador único do jogador.

        Returns:
            tuple: Um booleano indicando sucesso e uma mensagem informativa.
                - (True, "Aguardando mais jogadores") se o jogador for adicionado com sucesso.

        Observações:
            - O jogador será adicionado à lista de espera, e seu status em `self.players` será ajustado para indicar que ele não está em uma partida.
            - É esperado que uma partida seja iniciada assim que o número mínimo de jogadores for atingido.
        """
        print(f"[DEBUG] Adicionando jogador {player_id} à lista de espera...")
        self.waiting_list.append(player_id)
        print(f"[DEBUG] Jogador {player_id} adicionado à lista de espera")
        self.players[player_id] = {"in_game": False}
        print(f"[DEBUG] Jogadores na lista de espera: {len(self.waiting_list)}")
        return True, "Aguardando mais jogadores"
    
    def find_match(self, player_id):
        """Encontra ou cria uma partida para o jogador especificado.
        Args:
            player_id (str): ID do jogador que está buscando uma partida.

        Returns:
            tuple: Um valor booleano indicando sucesso e uma mensagem ou o ID da partida.
                - Se o jogador já estiver registrado em uma partida, retorna o ID da partida.
                - Se não houver jogadores suficientes na lista de espera, retorna uma mensagem de espera.
                - Caso contrário, cria uma nova partida com dois jogadores e retorna o ID da partida.
        """
        if player_id not in self.players:
            return False, "Jogador não registrado"
            
        # Verifica se o jogador já está em uma partida
        for match_id, players in self.matches.items():
            print(f"[DEBUG] Partida {match_id}: {players}")
            if player_id in players:
                print(f"[DEBUG] Jogador {player_id} já está em uma partida")
                return True, match_id
                
        # Verifica se há jogadores na lista de espera
        if len(self.waiting_list) >= 2:
            print("[DEBUG] Dois jogadores na lista de espera")
            player1 = self.waiting_list.pop(0)
            player2 = self.waiting_list.pop(0)
            result, message = self.add_match(player1, player2)
            
            if not result:
                return False, "[DEBUG] Erro ao criar partida"
            else:
                print(f"[DEBUG] Partida com o id {message} criado com sucesso")
            self.players[player1]["in_game"] = True
            self.players[player2]["in_game"] = True
            print(f"[DEBUG] Jogadores na lista de espera: {len(self.waiting_list)}")
            return True, match_id
        else:
            print("[DEBUG] Menos de dois jogadores na lista de espera")
            return False, "Aguardando mais jogadores"
    
    def make_move(self, player_id, match_id, choice):
        """Processa a jogada de um jogador em uma partida.
        Args:
            player_id (str): ID do jogador que está fazendo a jogada.
            match_id (int): ID da partida em que a jogada está sendo feita.
            choice (str): Escolha do jogador ("pedra", "papel" ou "tesoura").

        Returns:
            tuple: Um valor booleano indicando sucesso e uma mensagem de resultado.
                - Se a jogada for registrada com sucesso, retorna uma mensagem de sucesso.
                - Se ambos os jogadores fizerem suas escolhas, resolve a rodada e retorna o resultado.
        """
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
            result, message = self.resolve_match(match_id)
            print(f"[DEBUG] Resultado da rodada: {message}")
            print(f"[DEBUG] Placar atual: {self.scores[match_id]}")
            return result, message
        # Se ainda não houver duas escolhas, retorne uma mensagem de espera
        return True, "Aguardando a jogada do oponente"
    
    def return_score(self, player_id, match_id):
        if player_id is None or match_id is None:
            print("[ERROR] player_id ou match_id é None")
            return (0, 0)
        # Certifique-se de que as chaves são strings
        key = f"{player_id}_{match_id}"
        
        # Verifica se a chave existe no dicionário
        if key in self.scores:
            placar = self.scores[key]
            if isinstance(placar, (tuple, list)) and len(placar) == 2:
                return placar
            else:
                print(f"[WARNING] Valor inválido no dicionário para a chave {key}: {placar}")
                return (0, 0) # Retorna valores padrão (0, 0) se o valor for inválido
        else:
            print(f"[WARNING] Chave não encontrada no dicionário: {key}")
            # Retorna valores padrão (0, 0) se a chave não existir
            return (0, 0)
    
    def next_turn(self, match_id):
        """Alterna o turno para o próximo jogador em uma partida.
        Args:
            match_id (int): ID da partida em que o turno será alternado.
        """
        match_players = self.matches[match_id]
        current_player = self.current_turn[match_id]
        next_player = match_players[1] if match_players[0] == current_player else match_players[0]
        self.current_turn[match_id] = next_player
        
    def remove_match(self, match_id):
        """
        Remove uma partida ativa quando o jogo termina.

        Args:
            match_id (int): ID da partida a ser removida.

        Returns:
            tuple: Um valor booleano indicando sucesso e uma mensagem informativa.
        """
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        
        # Recupera os jogadores da partida
        players = self.matches.pop(match_id)
        
        # Remove informações da partida
        self.scores.pop(match_id, None)
        self.current_turn.pop(match_id, None)
        
        # Atualiza status dos jogadores
        for player in players:
            if player in self.players:
                self.players[player]["in_game"] = False
        
        return True, f"Partida {match_id} removida com sucesso"
        
    def get_opponent_id(self, player_id, match_id):
        """Retorna o ID do oponente de um jogador em uma partida.
        Args:
            player_id (str): ID do jogador que deseja saber o oponente.
            match_id (int): ID da partida em que o jogador está.
        Returns:
            tuple: Um valor booleano indicando sucesso e o ID do oponente.
                - Se o jogador não estiver na partida, retorna uma mensagem de erro.
        """
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        if player_id not in self.matches[match_id]:
            return False, "Jogador não está nesta partida"
        match_players = self.matches[match_id]
        return True, [p for p in match_players if p != player_id][0]
    
    def get_match_status(self, player_id, match_id):
        """Retorna o status atual de uma partida.
        Args:
            player_id (str): ID do jogador que solicita o status.
            match_id (int): ID da partida.

        Returns:
            tuple: Um valor booleano indicando sucesso e o status da partida.
                - O status inclui o placar atual, a rodada atual e o número máximo de rodadas.
        """
        if match_id not in self.matches or match_id not in self.scores:
            return False, "Partida não encontrada"
        
        scores = self.scores[match_id]
        print(f"[DEBUG] Placar da partida {match_id}: {scores}")
        current_round = sum(scores.values()) + 1
        print(f"[DEBUG] Rodada atual: {current_round}")
        max_rounds = self.max_rounds
        print(f"[DEBUG] Número máximo de rodadas: {max_rounds}")
        return scores, current_round, max_rounds
        
    def get_current_turn(self, match_id):
        """Retorna o ID do jogador que está no turno atual.
        Args:
            match_id (int): ID da partida.

        Returns:
            str or None: ID do jogador atual ou None se a partida não estiver registrada.
        """
        if match_id in self.current_turn:
            return self.current_turn[match_id]
        return None
    
    def get_score(self, match_id):
        """Retorna o placar atual de uma partida."""
        if match_id not in self.scores:
            return False, "Partida não encontrada"
        # Converte as chaves do dicionário para strings
        scores = {str(player): score for player, score in self.scores[match_id].items()}
        return True, scores
    
    def resolve_match(self, match_id):
        """Determina o vencedor da rodada e atualiza o placar.
        Args:
            match_id (int): ID da partida.

        Returns:
            tuple: Um valor booleano indicando sucesso e uma mensagem com o resultado da rodada ou do jogo.
                - Se um jogador atingir o número necessário de vitórias, a partida é encerrada e os dados são limpos.
                - Caso contrário, apenas as escolhas são limpas para a próxima rodada.
        """
        if match_id not in self.matches:
            return False, "Partida não encontrada"
        
        players = self.matches[match_id]
        if len(players) != 2:
            return False, "Número insuficiente de jogadores"
        
        player1, player2 = players
        if player1 not in self.choices or player2 not in self.choices:
            return False, "Aguardando as escolhas dos jogadores"
        
        choice1 = self.choices[player1]
        choice2 = self.choices[player2]
        
        combinacoes_vencedoras = {
            ("pedra", "tesoura"): player1,
            ("tesoura", "papel"): player1,
            ("papel", "pedra"): player1,
            ("tesoura", "pedra"): player2,
            ("papel", "tesoura"): player2,
            ("pedra", "papel"): player2,
        }
        
        # Lógica para determinar o vencedor da rodada
        if choice1 == choice2:
            result_msg = f"Empate na rodada!"
        else:
            winner = combinacoes_vencedoras.get((choice1, choice2))
            self.scores[match_id][winner] += 1  # Atualiza o placar no servidor
            result_msg = f"{winner} venceu a rodada!"
        
        # Limpa as escolhas para a próxima rodada
        del self.choices[player1]
        del self.choices[player2]
        
        print(f"O turno atual é de {self.current_turn[match_id]}")
        print(f"[DEBUG] Resultado da rodada: {result_msg}")
        return True, result_msg

    def get_match_status(self, player_id, match_id):
        """Retorna o status atual da partida
        Args:
            player_id (str): ID do jogador que solicita o status
            match_id (int): ID da partida
        Returns:
            tuple: Um valor booleano indicando sucesso e o status da partida
            - O status inclui o placar atual, a rodada atual e o número máximo de rodadas
        """
        if match_id not in self.matches or match_id not in self.scores:
            return False, "Partida não encontrada"
        
        return True, {
            "scores": self.scores[match_id],
            "current_round": sum(self.scores[match_id].values()) + 1,
            "max_rounds": self.max_rounds
        }

if __name__ == "__main__":
    """Função principal para iniciar o servidor RPS Battle Arena."""
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
    servidor.register_function(servidor.system_listMethods, 'system.listMethods')
    print("[DEBUG] Servidor iniciado com sucesso")
    servidor.serve_forever()