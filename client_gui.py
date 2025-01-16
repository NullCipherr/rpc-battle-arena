import pygame
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
        
        # Estados do jogo
        self.estado = "menu"  # menu, lobby, jogando, resultado
        self.tempo_espera = 0
        self.mensagem = ""
        
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
        
        # Desenha as opções
        opcoes = ["pedra", "papel", "tesoura"]
        for i, opcao in enumerate(opcoes):
            rect = pygame.Rect(150 + i*200, self.HEIGHT//2 - 25, 150, 50)
            cor = self.VERDE if self.escolha_atual == opcao else self.CINZA
            pygame.draw.rect(self.screen, cor, rect)
            texto = self.font_media.render(opcao.title(), True, self.BRANCO)
            texto_rect = texto.get_rect(center=rect.center)
            self.screen.blit(texto, texto_rect)
        
        # Mensagem
        if self.mensagem:
            msg = self.font_media.render(self.mensagem, True, self.BRANCO)
            msg_rect = msg.get_rect(center=(self.WIDTH//2, 100))
            self.screen.blit(msg, msg_rect)

    def procurar_partida(self):
        try:
            sucesso, self.match_id = self.servidor.find_match(self.player_id)
            if sucesso:
                self.estado = "jogando"
                self.mensagem = "Partida encontrada! Faça sua jogada."
        except:
            self.estado = "menu"
            self.mensagem = "Erro ao conectar ao servidor"

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
                        opcoes = ["pedra", "papel", "tesoura"]
                        for i, opcao in enumerate(opcoes):
                            rect = pygame.Rect(150 + i*200, self.HEIGHT//2 - 25, 150, 50)
                            if rect.collidepoint(mouse_pos):
                                self.escolha_atual = opcao
                                try:
                                    sucesso, mensagem = self.servidor.make_move(
                                        self.player_id, self.match_id, opcao)
                                    self.mensagem = mensagem
                                    if "venceu" in mensagem or "Empate" in mensagem:
                                        self.estado = "menu"
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
    # Configuração inicial
    servidor_ip = input("Digite o IP do servidor (padrão: localhost): ") or "localhost"
    servidor_porta = input("Digite a porta do servidor: ")
    
    # Inicia o cliente com interface gráfica
    cliente = ClienteJogoGUI(servidor_ip, servidor_porta)
    cliente.executar()

if __name__ == "__main__":
    main() 