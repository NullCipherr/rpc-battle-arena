import os
import sys

def main():
    print("=== Iniciando Cliente do RPG Battle Arena ===")
    
    # Verifica se o arquivo do cliente existe
    if not os.path.exists("client_gui.py"):
        print("Erro: Arquivo client_gui.py não encontrado!")
        sys.exit(1)
    
    try:
        # Verifica se o Pygame está instalado
        try:
            import pygame
        except ImportError:
            print("Instalando Pygame...")
            os.system("sudo apt install python3-pygame")
        
        # Executa o cliente
        os.system("python3 client_gui.py")
    except Exception as e:
        print(f"Erro ao iniciar o cliente: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 