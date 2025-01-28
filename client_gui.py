import pygame
import argparse
import socket
import xmlrpc.client as rpc
import time
import sys
import random
from threading import Thread

class ClienteJogoGUI:
    def __init__(self, servidor_ip, servidor_porta):
        pygame.font.init()
        self.server = rpc.ServerProxy(f"http://{servidor_ip}:{servidor_porta}/")
        self.player_id = random.randint(1000, 9999)
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

    def desenhar_menu(self):
        self.screen.fill(self.PRETO)
        
        # Título
        titulo = self.font_grande.render("RPG Battle Arena", True, self.BRANCO)
        titulo_rect = titulo.get_rect(center=(self.WIDTH//2, 100))
        self.screen.blit(titulo, titulo_rect)
        
        # Botões
        for texto, rect in self.botoes_menu.items():
            pygame.draw.rect(self.screen, self.CINZA, rect)
            texto_surface = self.font_media.render(texto.replace("_", " ").title(), True, self.BRANCO)
            texto_rect = texto_surface.get_rect(center=rect.center)
            self.screen.blit(texto_surface, texto_rect)

    def desenhar_lobby(self):
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

    def desenhar_jogo(self):
        self.screen.fill(self.PRETO)
        
        # Placar
        placar = self.font_grande.render(f"{self.placar_jogador} x {self.placar_oponente}", True, self.BRANCO)
        placar_rect = placar.get_rect(center=(self.WIDTH//2, 50))
        self.screen.blit(placar, placar_rect)
        
        # Rodada atual
        rodada = self.font_media.render(f"Rodada {self.rodada_atual}", True, self.BRANCO)
        rodada_rect = rodada.get_rect(center=(self.WIDTH//2, 100))
        self.screen.blit(rodada, rodada_rect)
        
        # IDs dos jogadores
        jogador_texto = self.font_pequena.render(f"Você: {self.player_id}", True, self.VERDE)
        jogador_rect = jogador_texto.get_rect(center=(self.WIDTH//4, 20))
        self.screen.blit(jogador_texto, jogador_rect)
        
        result, opponent_id = self.server.get_opponent_id(self.player_id, self.match_id)
        oponente_texto = self.font_pequena.render(f"Oponente: {opponent_id}", True, self.BRANCO)
        oponente_rect = oponente_texto.get_rect(center=(3 * self.WIDTH//4, 20))
        self.screen.blit(oponente_texto, oponente_rect)
        
        # Mensagem
        if self.mensagem:
            msg = self.font_media.render(self.mensagem, True, self.BRANCO)
            msg_rect = msg.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
            self.screen.blit(msg, msg_rect)
        
        # Indicação de turno
        try:
            current_turn = self.server.get_current_turn(self.match_id)
            turno_texto = "Sua vez" if current_turn == self.player_id else "Vez do oponente"
            turno_surface = self.font_media.render(turno_texto, True, self.VERDE if turno_texto == "Sua vez" else self.BRANCO)
            turno_rect = turno_surface.get_rect(center=(self.WIDTH//2, self.HEIGHT//2 + 50))
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
        try:
            success, message = self.server.add_to_waiting_list(self.player_id)
            self.mensagem = message
            if success:
                self.estado = "lobby"
        except Exception as e:
            self.mensagem = f"Erro ao conectar ao servidor: {e}"
            
    def remove_new_game(self):
        try:
            success, message = self.server.remove_waiting_list(self.player_id)
            self.mensagem = message
            if success:
                self.estado = "menu"
        except Exception as e:
            self.mensagem = f"Erro ao conectar ao servidor: {e}"

    def verificar_fim_jogo(self):
        if self.placar_jogador >= (self.max_rodadas // 2 + 1):
            self.mensagem = "Você venceu o jogo!"
            self.estado = "menu"
            return True
        elif self.placar_oponente >= (self.max_rodadas // 2 + 1):
            self.mensagem = "Você perdeu o jogo!"
            self.estado = "menu"
            return True
        return False

    def executar(self):
        # Inicializa o Pygame
        pygame.init()
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("[DEBUG] Saindo do jogo...")
                    self.remove_new_game()
                    pygame.quit()
                    print("[DEBUG] Jogo finalizado.")
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.estado == "menu":
                        for acao, rect in self.botoes_menu.items():
                            if rect.collidepoint(mouse_pos):
                                if acao == "new_game":
                                    print("[DEBUG] Procurando nova partida...")
                                    self.estado = "lobby"
                                    self.handle_new_game()
                                elif acao == "quit":
                                    print("[DEBUG] Saindo do jogo...")
                                    self.remove_new_game()
                                    pygame.quit()
                                    print("[DEBUG] Jogo finalizado.")
                                    sys.exit()
                                    print("[DEBUG] Sistema encerrado.")
                    
                    elif self.estado == "jogando":
                        for opcao, rect in self.botoes_jogo.items():
                            if rect.collidepoint(mouse_pos):
                                self.escolha_atual = opcao
                                try:
                                    sucesso, mensagem = self.server.make_move(
                                        self.player_id, self.match_id, opcao)
                                    self.mensagem = mensagem
                                    
                                    if sucesso:
                                        if "Você venceu" in mensagem:
                                            self.placar_jogador += 1
                                            self.rodada_atual += 1
                                        elif "Você perdeu" in mensagem:
                                            self.placar_oponente += 1
                                            self.rodada_atual += 1
                                        elif "Empate" in mensagem:
                                            self.rodada_atual += 1
                                        
                                        if not self.verificar_fim_jogo():
                                            self.escolha_atual = None
                                    else:
                                        print(f"[ERROR] Erro ao fazer jogada: {mensagem}")
                                        self.mensagem = mensagem     
                                except Exception as e:
                                    print(f"[ERROR] Erro ao fazer jogada: {e}")
                                    self.mensagem = "Erro ao fazer jogada"
            
            # Verifica se uma partida foi encontrada
            if self.estado == "lobby":
                print("[DEBUG] Verificando partida...")
                sucesso, match_id = self.server.find_match(self.player_id)
                if sucesso:
                    if isinstance(match_id, int):
                        print(f"[DEBUG] Partida encontrada: {match_id}")
                        self.match_id = match_id
                        self.estado = "jogando"
                        self.mensagem = ""
                    else:
                        print(f"[DEBUG] {match_id}")
                else:
                    print("[DEBUG] Partida não encontrada")
                    self.tempo_espera += 1
                    if self.tempo_espera >= 5000:
                        self.mensagem = "Nenhuma partida encontrada"
                        self.tempo_espera = 0
                        self.estado = "menu"
                
            # Atualiza a tela
            if self.estado == "menu":
                self.desenhar_menu()
            elif self.estado == "lobby":
                self.desenhar_lobby()
            elif self.estado == "jogando":
                self.desenhar_jogo()
            
            pygame.display.flip()
            clock.tick(60)

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
    server = rpc.ServerProxy(server_url)
    
    try:
        # Testar conexão com o servidor
        print("[DEBUG] Testando conexão com o servidor...")
        response = server.system.listMethods()
        print("[DEBUG] Conexão estabelecida com sucesso")
        print(f"[DEBUG] Métodos disponíveis: {response}")
    except Exception as e:
        print(f"[DEBUG] Erro ao conectar ao servidor: {e}")
    
    print("[DEBUG] Iniciando interface gráfica...")
    
    # Inicia o cliente com interface gráfica
    cliente = ClienteJogoGUI(args.ip, args.porta)
    
    # Registrar o jogador no servidor
    print("[DEBUG] Registrando jogador no servidor...")
    sucesso, mensagem = server.register_player(cliente.player_id, porta)
    print(f"[DEBUG] {mensagem}")
    
    cliente.executar() 