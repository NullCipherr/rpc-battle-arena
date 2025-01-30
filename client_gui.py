# Alunos
# Andrei Roberto da Costa
# Daniel Aparecido da Cunha Braz
# Henrique Rosa de Araujo 

import pygame
import argparse
import socket
import xmlrpc.client as rpc
import time
import sys
import random
from threading import Thread

class ClienteJogoGUI:
    """" Classe que representa o cliente do jogo com interface gráfica """
    def __init__(self, servidor_ip, servidor_porta):
        # Inicializa o cliente
        pygame.font.init() # Inicializa as fontes do Pygame
        self.server = rpc.ServerProxy(f"http://{servidor_ip}:{servidor_porta}/") # Conecta ao servidor
        self.player_id = random.randint(1000, 9999) # ID do jogador
        
        # Configurações da tela
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("RPS Battle Arena")
        
        # Fontes
        self.font_grande = pygame.font.SysFont('arial', 64)
        self.font_media = pygame.font.SysFont('arial', 32)
        self.font_pequena = pygame.font.SysFont('arial', 24)
        
        # Cores
        self.BRANCO = (255, 255, 255)
        self.PRETO = (0, 0, 0)
        self.CINZA = (128, 128, 128)
        self.VERMELHO = (255, 0, 0)
        self.VERDE = (0, 255, 0)
        self.AZUL = (0, 0, 255)
        
        # Estados do jogo
        self.estado = "menu"  # menu, lobby, jogando, resultado
        self.tempo_espera = 0
        self.mensagem = ""
        
        # Atualização do placar
        self.needs_score_update = False
        
        # Placar
        self.placar_jogador = 0
        self.placar_oponente = 0
        self.rodada_atual = 1
        self.max_rodadas = 5
        
        print(f"[DEBUG] ID do Jogador: {self.player_id}")
        self.match_id = None
        print(f"[DEBUG] ID da Partida: {self.match_id}")
        self.escolha_atual = None
        print(f"[DEBUG] Escolha Atual: {self.escolha_atual}")
        
        # Botões do menu
        self.botoes_menu = {
            "new_game": pygame.Rect(self.WIDTH//2 - 100, 200, 200, 50),
            "credits": pygame.Rect(self.WIDTH//2 - 100, 300, 200, 50),
            "quit": pygame.Rect(self.WIDTH//2 - 100, 400, 200, 50)
        }
        
        # Botões do jogo
        self.botoes_jogo = {
            "pedra": pygame.Rect(100, self.HEIGHT - 100, 150, 50),
            "papel": pygame.Rect(325, self.HEIGHT - 100, 150, 50),
            "tesoura": pygame.Rect(550, self.HEIGHT - 100, 150, 50)
        }
        # Botões da tela de resultado
        self.botoes_resultado = {
            "nova_partida": pygame.Rect(self.WIDTH // 2 - 100, self.HEIGHT // 2 + 50, 200, 50),
            "voltar_menu": pygame.Rect(self.WIDTH // 2 - 100, self.HEIGHT // 2 + 120, 200, 50)
        }
        
        
    def desenhar_resultado(self):
        """Desenha a tela de resultado do jogo."""
        self.screen.fill(self.PRETO)
        
        # Título do resultado
        titulo = self.font_grande.render("Fim do Jogo", True, self.BRANCO)
        titulo_rect = titulo.get_rect(center=(self.WIDTH // 2, 100))
        self.screen.blit(titulo, titulo_rect)
        
        # Mensagem de resultado
        resultado = self.font_media.render(self.mensagem, True, self.BRANCO)
        resultado_rect = resultado.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 - 50))
        self.screen.blit(resultado, resultado_rect)
        
        # Botão para nova partida
        pygame.draw.rect(self.screen, self.VERDE, self.botoes_resultado["nova_partida"])
        nova_partida_texto = self.font_media.render("Nova Partida", True, self.BRANCO)
        nova_partida_texto_rect = nova_partida_texto.get_rect(center=self.botoes_resultado["nova_partida"].center)
        self.screen.blit(nova_partida_texto, nova_partida_texto_rect)
        
        # Botão para voltar ao menu
        pygame.draw.rect(self.screen, self.VERMELHO, self.botoes_resultado["voltar_menu"])
        voltar_menu_texto = self.font_media.render("Voltar ao Menu", True, self.BRANCO)
        voltar_menu_texto_rect = voltar_menu_texto.get_rect(center=self.botoes_resultado["voltar_menu"].center)
        self.screen.blit(voltar_menu_texto, voltar_menu_texto_rect)

    def desenhar_menu(self):
        """ Desenha a tela do menu """
        self.screen.fill(self.PRETO)
        
        # Título
        titulo = self.font_grande.render("RPS Battle Arena", True, self.BRANCO)
        titulo_rect = titulo.get_rect(center=(self.WIDTH//2, 100))
        self.screen.blit(titulo, titulo_rect)
        
        # Botões
        for texto, rect in self.botoes_menu.items():
            pygame.draw.rect(self.screen, self.CINZA, rect)
            texto_surface = self.font_media.render(texto.replace("_", " ").title(), True, self.BRANCO)
            texto_rect = texto_surface.get_rect(center=rect.center)
            self.screen.blit(texto_surface, texto_rect)

    def desenhar_lobby(self):
        """ Desenha a tela de lobby """
        self.screen.fill(self.PRETO)
        
        # Mensagem de procurando partida
        texto = self.font_grande.render("Procurando Partida", True, self.BRANCO)
        texto_rect = texto.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 - 50))
        self.screen.blit(texto, texto_rect)
        
        # Contador
        pontos = "." * (int(time.time() * 2) % 4)
        contador = self.font_media.render(f"Aguardando{pontos}", True, self.BRANCO)
        contador_rect = contador.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
        
        self.screen.blit(contador, contador_rect)
    
    def desenhar_credits(self):
        """ Desenha a tela de créditos """
        self.screen.fill(self.PRETO)
        
        # Título
        titulo = self.font_grande.render("Créditos", True, self.BRANCO)
        titulo_rect = titulo.get_rect(center=(self.WIDTH//2, 100))
        self.screen.blit(titulo, titulo_rect)
        
        # Informações da disciplina
        info_disciplina = self.font_media.render("Desenvolvido para a disciplina de Sistemas Distribuídos", True, self.BRANCO)
        info_rect = info_disciplina.get_rect(center=(self.WIDTH//2, 180))
        self.screen.blit(info_disciplina, info_rect)
        
        uni = self.font_media.render("Universidade Estadual de Maringá", True, self.BRANCO)
        uni_rect = uni.get_rect(center=(self.WIDTH//2, 220))
        self.screen.blit(uni, uni_rect)
        
        # Equipe
        equipe = self.font_media.render("Equipe:", True, self.BRANCO)
        equipe_rect = equipe.get_rect(center=(self.WIDTH//2, 300))
        self.screen.blit(equipe, equipe_rect)
        
        # Lista de integrantes
        integrantes = [
            "Andrei Roberto da Costa",
            "Daniel Aparecido da Cunha Braz",
            "Henrique Rosa de Araujo"
        ]
        
        y_pos = 350
        for integrante in integrantes:
            nome = self.font_media.render(integrante, True, self.BRANCO)
            nome_rect = nome.get_rect(center=(self.WIDTH//2, y_pos))
            self.screen.blit(nome, nome_rect)
            y_pos += 40
        
        # Botão voltar (estilo menu)
        self.voltar_button = pygame.Rect(self.WIDTH//2 - 100, self.HEIGHT - 100, 200, 50)
        pygame.draw.rect(self.screen, self.CINZA, self.voltar_button)
        voltar = self.font_media.render("Voltar", True, self.BRANCO)
        voltar_rect = voltar.get_rect(center=self.voltar_button.center)
        self.screen.blit(voltar, voltar_rect)

    def desenhar_jogo(self):
        """ Desenha a tela de jogo """
        self.screen.fill(self.PRETO)
        
        # Placar
        placar = self.font_grande.render(f"{self.placar_jogador} x {self.placar_oponente}", True, self.BRANCO)
        placar_rect = placar.get_rect(center=(self.WIDTH // 2, 50))
        self.screen.blit(placar, placar_rect)

        # Rodada atual
        rodada = self.font_media.render(f"Rodada {self.rodada_atual}", True, self.BRANCO)
        rodada_rect = rodada.get_rect(center=(self.WIDTH // 2, 100))
        self.screen.blit(rodada, rodada_rect)

        # IDs dos jogadores
        jogador_texto = self.font_pequena.render(f"Você: {self.player_id}", True, self.VERDE)
        jogador_rect = jogador_texto.get_rect(center=(self.WIDTH // 4, 20))
        self.screen.blit(jogador_texto, jogador_rect)
        
        try:
            result, opponent_id = self.server.get_opponent_id(self.player_id, self.match_id)
            oponente_texto = self.font_pequena.render(f"Oponente: {opponent_id}", True, self.BRANCO)
            oponente_rect = oponente_texto.get_rect(center=(3 * self.WIDTH // 4, 20))
            self.screen.blit(oponente_texto, oponente_rect)
        except Exception as e:
            print(f"[ERROR] Erro ao obter ID do oponente: {e}")

        # Mensagem
        if self.mensagem:
            msg = self.font_media.render(self.mensagem, True, self.BRANCO)
            msg_rect = msg.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            self.screen.blit(msg, msg_rect)

        # Indicação de turno
        try:
            current_turn = self.server.get_current_turn(self.match_id)
            turno_texto = "Sua vez" if current_turn == self.player_id else "Vez do oponente"
            
            if turno_texto == "Sua vez" and self.mensagem == "Não é o seu turno":
                self.mensagem = ""
            elif turno_texto == "Sua vez" and self.mensagem == "Aguardando a jogada do oponente...":
                self.mensagem = ""
            
            if current_turn == self.player_id and self.needs_score_update:
                # self.mensagem = ""
                self.sinc_placar() # Sincroniza o placar com o servidor
                self.needs_score_update = False
            elif current_turn != self.player_id:
                self.needs_score_update = True
            
            turno_surface = self.font_media.render(turno_texto, True, self.VERDE if turno_texto == "Sua vez" else self.BRANCO)
            turno_rect = turno_surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2 + 50))
            self.screen.blit(turno_surface, turno_rect)
        except Exception as e:
            print(f"[ERROR] Erro ao obter o turno atual: {e}")

        # Botões de jogada
        for opcao, rect in self.botoes_jogo.items():
            cor = self.VERDE if self.escolha_atual == opcao else self.AZUL
            pygame.draw.rect(self.screen, cor, rect)
            texto = self.font_media.render(opcao.title(), True, self.BRANCO)
            texto_rect = texto.get_rect(center=rect.center)
            self.screen.blit(texto, texto_rect)
        
    def handle_new_game(self):
        """ Adiciona o jogador à lista de espera de novas partidas """
        try:
            # Reseta os dados da partida anterior (se houver)
            self.resetar_partida()
            
            success, message = self.server.add_to_waiting_list(self.player_id)
            self.mensagem = message
            if success:
                self.estado = "lobby"
                print(f"[DEBUG] Novo jogo iniciado. Estado atual: {self.estado}")
            else:
                print(f"[ERROR] Erro ao adicionar à lista de espera: {message}")
        except Exception as e:
            self.mensagem = f"Erro ao conectar ao servidor: {e}"
            print(f"[DEBUG] Exceção em handle_new_game: {e}")
            
    def remove_new_game(self):
        """ Remove o jogador da lista de espera de novas partidas """
        try:
            success, message = self.server.remove_waiting_list(self.player_id)
            self.mensagem = message
            if success:
                self.estado = "menu"
        except Exception as e:
            self.mensagem = f"Erro ao conectar ao servidor: {e}"
            
    def resetar_partida(self):
        """ Reseta os dados da partida anterior """
        self.placar_jogador = 0 # Reseta o placar
        self.placar_oponente = 0 # Reseta o placar
        self.rodada_atual = 1 # Reseta a rodada atual
        self.match_id = None # Reseta o ID da partida
        self.escolha_atual = None # Reseta a escolha do jogador
        self.mensagem = ""  # Limpa a mensagem de resultado
        self.estado = "menu"  # Garante que o estado seja resetado
        print("[DEBUG] Dados da partida resetados com sucesso")
            
    def remove_match(self):
        """ Remove o jogador da partida atual """
        try:
            success, message = self.server.remove_match(self.player_id, self.match_id)
            self.mensagem = message
            if success:
                print("[DEBUG] Partida {self.match_id} removida com sucesso")
                self.estado = "menu"
        except Exception as e:
            self.mensagem = f"Erro ao conectar ao servidor: {e}"

    def verificar_fim_jogo(self):
        """ Verifica se o jogo terminou """
        if self.placar_jogador >= (self.max_rodadas // 2 + 1):
            self.mensagem = "Você venceu a partida, Parabéns!"
            self.estado = "resultado"
            return True
        elif self.placar_oponente >= (self.max_rodadas // 2 + 1):
            self.mensagem = "Você perdeu o jogo, Lamento!"
            self.estado = "resultado"
            return True
        return False
    
    def verificar_estado_partida(self):
        """Verifica o estado da partida (placar, rodada atual, fim do jogo)."""
        try:
            # Sincroniza o placar
            # self.sinc_placar()
            
            # Verifica se o jogo terminou
            if self.match_id is not None:
                game_over, winner = self.server.check_game_over(self.match_id)
                if game_over:
                    self.mensagem = f"Fim do jogo! {winner} venceu a partida!"
                    self.estado = "resultado"
                    print(f"[DEBUG] Fim do jogo detectado. Estado atual: {self.estado}")
                    return True
            else:
                print("[DEBUG] Partida não encontrada. Ignorando verificação de estado.")
        except Exception as e:
            print(f"[ERROR] Erro ao verificar estado da partida: {e}")
        return False

    def executar(self):
        """ Executa o loop principal do jogo """
        pygame.init()
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.sair_do_jogo()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.tratar_click(pygame.mouse.get_pos())
            
            # Verifica se uma partida foi encontrada
            if self.estado == "lobby":
                self.verificar_partida()
            
            # Verifica o estado da partida (placar, rodada atual, fim do jogo)
            if self.estado == "jogando":
                self.verificar_estado_partida()
                
            # Atualiza a tela
            self.atualizar_tela()
            pygame.display.flip()
            clock.tick(60)

    def sair_do_jogo(self):
        print("[DEBUG] Saindo do jogo...")
        self.remove_new_game()
        pygame.quit()
        print("[DEBUG] Jogo finalizado.")
        sys.exit()
    
    def tratar_click(self, mouse_pos):
        """ Trata os cliques do mouse de acordo com o estado atual """
        print(f"[DEBUG] Estado atual antes do clique: {self.estado}")
        
        if self.estado == "menu":
            for acao, rect in self.botoes_menu.items():
                if rect.collidepoint(mouse_pos):
                    if acao == "new_game":
                        print("[DEBUG] Procurando nova partida...")
                        self.estado = "lobby"  # Define o estado como "lobby"
                        self.handle_new_game()
                    elif acao == "credits":
                        self.estado = "credits"
                    elif acao == "quit":
                        self.sair_do_jogo()
        elif self.estado == "jogando":
            self.fazer_jogada(mouse_pos)
        elif self.estado == "credits" and self.voltar_button.collidepoint(mouse_pos):
            self.estado = "menu"
        elif self.estado == "resultado":
            if self.botoes_resultado["nova_partida"].collidepoint(mouse_pos):
                print("[DEBUG] Iniciando nova partida a partir da tela de resultado.")
                self.estado = "lobby"  # Define o estado como "lobby"
                self.handle_new_game()
            elif self.botoes_resultado["voltar_menu"].collidepoint(mouse_pos):
                print("[DEBUG] Voltando ao menu a partir da tela de resultado.")
                self.estado = "menu" # Define o estado como "menu"
                self.remove_match()
                self.resetar_partida()
        
        print(f"[DEBUG] Estado atual após o clique: {self.estado}")
    
    def fazer_jogada(self, mouse_pos):
        if self.match_id is None:
            print("[DEBUG] Nenhuma partida encontrada ainda.")
            return
        
        for opcao, rect in self.botoes_jogo.items():
            if rect.collidepoint(mouse_pos):
                self.escolha_atual = opcao
                print(f"[DEBUG] Enviando jogada - player_id: {self.player_id}, match_id: {self.match_id}, escolha: {opcao}")
                try:
                    print(f"[DEBUG] Fazendo jogada: player_id={self.player_id}, match_id={self.match_id}, escolha={opcao}")
                    sucesso, message = self.server.make_move(self.player_id, self.match_id, opcao)
                    print(f"[DEBUG] Resposta do servidor: sucesso={sucesso}, message={message}")
                    if sucesso:
                        self.atualizar_jogo(message) # Atualiza o jogo
                        print(f"[DEBUG] Jogada feita com sucesso: sucesso={sucesso}, message={message}")
                    else:
                        self.mensagem = message
                        print(f"[ERROR] Erro ao fazer jogada: {message}")
                except Exception as e:
                    print(f"[ERROR] Exceção ao fazer jogada: {e}")
                    self.mensagem = "Erro ao fazer jogada. Tente novamente."
    
    def atualizar_jogo(self, message):
        try:
            # Verifica o resultado da rodada
            if "venceu a rodada" in message:
                # Determina quem venceu a rodada
                if str(self.player_id) in message:
                    print(f"[DEBUG] Você venceu a rodada!")
                    self.placar_jogador += 1  # Incrementa o placar do jogador local
                else:
                    print(f"[DEBUG] Você perdeu a rodada!")
                    self.placar_oponente += 1  # Incrementa o placar do oponente local
            elif message == "Empate na rodada!":
                print(f"[DEBUG] Empate na rodada!")
            
            # Sincroniza o placar e a rodada com o servidor
            self.sinc_placar()
            self.sinc_rodada()
            
            # Verifica se o jogo terminou
            if self.verificar_fim_jogo():
                self.estado = "resultado"
                print(f"[DEBUG] Fim do jogo! Placar final: {self.placar_jogador} x {self.placar_oponente}")
        except Exception as e:
            print(f"[ERROR] Erro ao atualizar o jogo: {e}")
            self.mensagem = "Erro ao atualizar o jogo. Tente novamente."
    
    def sinc_message(self):
        # Sincroniza a mensagem com o servidor
        success, message = self.server.get_message(self.player_id, self.match_id)
        if success:
            self.mensagem = message
        else:
            print(f"[ERROR] Erro ao sincronizar a mensagem: {message}")
    
    def sinc_placar(self):
        """ Sincroniza o placar com o servidor """
        try:
            success, scores = self.server.get_score(self.match_id)
            if success:
                # Verifica se o match_id é o mesmo da partida atual
                if self.match_id is not None:
                    self.placar_jogador = scores.get(str(self.player_id), 0)
                    opponent_id = self.server.get_opponent_id(self.player_id, self.match_id)[1]
                    self.placar_oponente = scores.get(str(opponent_id), 0)
                    print(f"[DEBUG] Placar sincronizado: {scores}")
                    self.sinc_rodada()
                    print(f"[DEBUG] Rodada sincronizada: {self.rodada_atual}")
                    self.sinc_message()
                    print(f"[DEBUG] Mensagem sincronizada: {self.mensagem}")
                else:
                    print("[DEBUG] Partida não encontrada. Ignorando sincronização do placar.")
            else:
                print(f"[ERROR] Erro ao sincronizar o placar: {scores}")
        except Exception as e:
            print(f"[ERROR] Erro ao sincronizar o placar: {e}")
        
    def sinc_rodada(self):
        # Sincroniza a rodada atual com o servidor
        success, round_number = self.server.get_round(self.match_id)
        if success:
            self.rodada_atual = round_number
        else:
            print(f"[ERROR] Erro ao sincronizar a rodada: {round_number}")
    
    def verificar_partida(self):
        print("[DEBUG] Procurando partida...")
        try:
            sucesso, match_id = self.server.find_match(self.player_id)
            if sucesso:
                self.match_id = int(match_id)
                self.estado = "jogando"
                self.server.remove_waiting_list(self.player_id)
                self.mensagem = ""
                print(f"[DEBUG] Partida encontrada: {match_id}, Estado atual: {self.estado}")
            else:
                print(f"[DEBUG] Nenhuma partida encontrada. Estado atual: {self.estado}")
        except Exception as e:
            print(f"[ERROR] Erro ao encontrar partida: {e}")
    
    def atualizar_tela(self):
        """ Atualiza a tela com base no estado atual do jogo """
        # print(f"[DEBUG] Atualizando tela. Estado atual: {self.estado}")
        
        if self.estado == "menu":
            self.desenhar_menu()
        elif self.estado == "lobby":
            self.desenhar_lobby()
        elif self.estado == "credits":
            self.desenhar_credits()
        elif self.estado == "jogando":
            self.desenhar_jogo()
        elif self.estado == "resultado":
            self.desenhar_resultado()
        else:
            print(f"[DEBUG] Estado inválido: {self.estado}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='localhost', help='IP do servidor')
    parser.add_argument('--porta', type=int, default=8080, help='Porta do servidor')
    args = parser.parse_args()
    
    # Configuração inicial
    ip = args.ip
    porta = args.porta
    
    print("[DEBUG] Iniciando cliente...")
    print(f"[DEBUG] Conectando ao servidor: {ip}:{porta}")
    server_url = f"http://{ip}:{porta}/"
    server = rpc.ServerProxy(server_url, allow_none=True)
    
    # Inicia o cliente com interface gráfica
    cliente = ClienteJogoGUI(args.ip, args.porta)
    
    try:
        # Testar conexão com o servidor
        print("[DEBUG] Testando conexão com o servidor...")
        response = server.system.listMethods()
        print("[DEBUG] Conexão estabelecida com sucesso")
        print(f"[DEBUG] Métodos disponíveis: {response}")
    except Exception as e:
        print(f"[DEBUG] Erro ao conectar ao servidor: {e}")
    
    # Registrar o jogador no servidor
    try:
        sucesso, mensagem = cliente.server.register_player(cliente.player_id, porta)
        print(f"[DEBUG] {mensagem}")
    except Exception as e:
        print(f"[ERROR] Erro ao registrar jogador: {e}")
    
    cliente.executar() 