import pygame
import argparse
import socket
import xmlrpc.client
import time
import sys
import random
from threading import Thread

class ClienteJogoGUI:
    def __init__(self, servidor_ip, servidor_porta):
        # Inicializa o Pygame
        pygame.init()
        pygame.font.init()
        
        # Configurações da tela
        self.WIDTH = 800
        self.HEIGHT = 600
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Pedra, Papel e Tesoura - RPG Battle Arena")
        
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
        
        # Conexão com servidor
        self.servidor = xmlrpc.client.ServerProxy(f'http://{servidor_ip}:{servidor_porta}')
        self.player_id = f"player_{random.randint(1000, 9999)}"
        self.match_id = None
        self.escolha_atual = None
        
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
        
        # Mensagem
        if self.mensagem:
            msg = self.font_media.render(self.mensagem, True, self.BRANCO)
            msg_rect = msg.get_rect(center=(self.WIDTH//2, self.HEIGHT//2))
            self.screen.blit(msg, msg_rect)
        
        # Botões de jogada
        for opcao, rect in self.botoes_jogo.items():
            cor = self.VERDE if self.escolha_atual == opcao else self.AZUL
            pygame.draw.rect(self.screen, cor, rect)
            texto = self.font_media.render(opcao.title(), True, self.BRANCO)
            texto_rect = texto.get_rect(center=rect.center)
            self.screen.blit(texto, texto_rect)

    def procurar_partida(self):
        try:
            sucesso, self.match_id = self.servidor.find_match(self.player_id)
            if sucesso:
                self.estado = "jogando"
                self.mensagem = "Partida encontrada! Faça sua jogada."
                self.placar_jogador = 0
                self.placar_oponente = 0
                self.rodada_atual = 1
        except:
            self.estado = "menu"
            self.mensagem = "Erro ao conectar ao servidor"

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
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.estado == "menu":
                        for acao, rect in self.botoes_menu.items():
                            if rect.collidepoint(mouse_pos):
                                if acao == "new_game":
                                    self.estado = "lobby"
                                    Thread(target=self.procurar_partida).start()
                                elif acao == "quit":
                                    pygame.quit()
                                    sys.exit()
                    
                    elif self.estado == "jogando":
                        for opcao, rect in self.botoes_jogo.items():
                            if rect.collidepoint(mouse_pos):
                                self.escolha_atual = opcao
                                try:
                                    sucesso, mensagem = self.servidor.make_move(
                                        self.player_id, self.match_id, opcao)
                                    self.mensagem = mensagem
                                    
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
                                        
                                except:
                                    self.estado = "menu"
                                    self.mensagem = "Erro ao fazer jogada"
            
            # Atualiza a tela
            if self.estado == "menu":
                self.desenhar_menu()
            elif self.estado == "lobby":
                self.desenhar_lobby()
            elif self.estado == "jogando":
                self.desenhar_jogo()
            
            pygame.display.flip()
            clock.tick(60)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ip', default='localhost', help='IP do servidor')
    parser.add_argument('--porta', type=int, default=5000, help='Porta do servidor')
    args = parser.parse_args()
    
    # IP Local automatico para debug
    ip_local = socket.gethostbyname(socket.gethostname())
    print(f"\n[DEBUG] IP Local: {ip_local}")
    print(f"[DEBUG] Conectando ao servidor: {args.ip}:{args.porta}")
    
    # Configuração inicial
    # servidor_ip = input("\nDigite o IP do servidor (padrão: localhost): ") or "localhost"
    # servidor_porta = 5000
    # print("[DEBUG] A porta do servidor é: ", servidor_porta)
    # print("[DEBUG] O IP do servidor é: ", servidor_ip)
    
    # Inicia o cliente com interface gráfica
    cliente = ClienteJogoGUI(args.ip, args.porta)
    cliente.executar()

if __name__ == "__main__":
    main() 