import os
import sys

def main():
    print("=== Iniciando Servidor do Battle Arena ===")
    
    # Verifica se o arquivo do servidor existe
    if not os.path.exists("server.py"):
        print("Erro: Arquivo server.py não encontrado!")
        sys.exit(1)
    
    try:
        # Executa o servidor
        os.system("python3 server.py")
    except Exception as e:
        print(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 