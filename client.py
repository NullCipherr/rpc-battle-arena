import xmlrpc.client
import time

class ClienteJogo:
    def __init__(self, servidor_ip, servidor_porta):
        # Conecta ao servidor
        self.servidor = xmlrpc.client.ServerProxy(f'http://{servidor_ip}:{servidor_porta}')
        self.player_id = None
        self.match_id = None

    def registrar_jogador(self):
        """Registra o jogador no servidor"""
        while True:
            self.player_id = input("Digite seu ID de jogador: ")
            sucesso, mensagem = self.servidor.register_player(self.player_id, 0)
            if sucesso:
                print(mensagem)
                break
            print(f"Erro: {mensagem}")

    def fazer_jogada(self):
        """Processa uma jogada do jogador"""
        while True:
            escolha = input("Faça sua jogada (pedra/papel/tesoura): ").lower()
            if escolha in ["pedra", "papel", "tesoura"]:
                return escolha
            print("Jogada inválida! Escolha pedra, papel ou tesoura.")

    def jogar(self):
        """Loop principal do jogo"""
        print("Procurando uma partida...")
        sucesso, self.match_id = self.servidor.find_match(self.player_id)
        
        if not sucesso:
            print(f"Erro ao procurar partida: {self.match_id}")
            return

        print(f"Partida encontrada! ID da partida: {self.match_id}")
        
        while True:
            # Faz a jogada
            escolha = self.fazer_jogada()
            sucesso, mensagem = self.servidor.make_move(self.player_id, self.match_id, escolha)
            
            print(mensagem)
            
            # Se a partida terminou (resultado foi determinado)
            if "venceu" in mensagem or "Empate" in mensagem:
                break
            
            # Se ainda está aguardando o outro jogador
            print("Aguardando jogada do oponente...")
            time.sleep(1)  # Espera 1 segundo antes de verificar novamente

def main():
    # Configuração inicial
    print("=== Cliente do Jogo Pedra, Papel e Tesoura ===")
    servidor_ip = input("Digite o IP do servidor (padrão: localhost): ") or "localhost"
    servidor_porta = input("Digite a porta do servidor: ")

    # Cria e inicia o cliente
    try:
        cliente = ClienteJogo(servidor_ip, servidor_porta)
        cliente.registrar_jogador()
        
        # Loop principal do jogo
        while True:
            cliente.jogar()
            
            # Pergunta se quer jogar novamente
            jogar_novamente = input("Deseja jogar novamente? (s/n): ").lower()
            if jogar_novamente != 's':
                break
                
    except Exception as e:
        print(f"Erro de conexão: {e}")
        print("Verifique se o servidor está rodando e se o IP e porta estão corretos.")

if __name__ == "__main__":
    main()
