# Cores e formatação
BOLD := $(shell tput bold)
RED := $(shell tput setaf 1)
GREEN := $(shell tput setaf 2)
YELLOW := $(shell tput setaf 3)
BLUE := $(shell tput setaf 4)
MAGENTA := $(shell tput setaf 5)
CYAN := $(shell tput setaf 6)
WHITE := $(shell tput setaf 7)
RESET := $(shell tput sgr0)

# Variáveis
PYTHON = python3
TEST = pytest
SERVER = server.py
CLIENT = client_gui.py
PORT = 5000
LOG_DIR = logs
DATE := $(shell date +%Y%m%d_%H%M%S)

# Portas de teste
TEST_SERVER_PORT = 5000
TEST_CLIENT_PORT = 5001
TEST_CLIENT2_PORT = 5002

# Lista de comandos e suas descrições
COMMANDS = \
	"server - Iniciar servidor" \
	"client1 - Iniciar cliente 1" \
	"client2 - Iniciar cliente 2" \
	"integration-test - Executar teste integrado" \
	"debug-server - Debugar servidor" \
	"check-port - Verificar porta" \
	"clean - Limpar arquivos" \
	"show-logs - Mostrar logs" \
	"kill-all - Encerrar processos"

EXAMPLES = \
	"make PORT=5001 server - Porta específica " \
	"make debug-server - Modo debug" \
	"make check-port PORT=5000 - Verifica porta"

# Função para exibir a tabela de comandos
define print_table
	@for cmd in $(COMMANDS); do \
		name=$$(echo $$cmd | cut -d'-' -f1 | xargs); \
		desc=$$(echo $$cmd | cut -d'-' -f2- | xargs); \
        name_len=$$(echo $$name | wc -c); \
        padding=$$((25-$$name_len)); \
		printf "$(BOLD)$(BLUE)║ %-25s %-38s ║\n" "$$name" "$$desc"; \
	done
endef

# Função para exibir a tabela de exemplos
define print_examples
	@for ex in $(EXAMPLES); do \
		cmd=$$(echo $$ex | cut -d'-' -f1); \
		desc=$$(echo $$ex | cut -d'-' -f2-); \
		printf "$(BOLD)$(BLUE)║ %-25s %-38s ║\n" "$$cmd" "$$desc"; \
	done
endef

# Funções de impressão
define print_status
	@echo "$(BOLD)$(BLUE)╔══════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(BLUE)║$(RESET)  ⚠️ $(BOLD)$(CYAN)[STATUS]$(RESET)$(2)$(1)$(RESET)"
	@echo "$(BOLD)$(BLUE)╚══════════════════════════════════════════════════════════╝$(RESET)"
endef

define print_error
	@echo "$(BOLD)$(RED)╔══════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(RED)║$(RESET) ⚠️  $(BOLD)$(RED)[ERRO]$(RESET) $(1)"
	@echo "$(BOLD)$(RED)╚══════════════════════════════════════════════════════════╝$(RESET)"
endef

define print_success
	@echo "$(BOLD)$(GREEN)╔══════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(GREEN)║$(RESET) ✅ $(BOLD)$(GREEN)[SUCESSO]$(RESET) $(1)"
	@echo "$(BOLD)$(GREEN)╚══════════════════════════════════════════════════════════╝$(RESET)"
endef

# Criar diretórios necessários
$(LOG_DIR):
	@mkdir -p $(LOG_DIR)
	$(call print_success,"Diretório de logs criado")
	$(call print_status,"Logs serão salvos em: $(LOG_DIR)"," 📁 ")
	$(call print_status,"Utilize make help para ajuda."," 📚 ")

# Teste do jogo
test-game:
	$(call print_status, "Iniciando ambiente de teste."," 🧪 ")
	@mkdir -p $(LOG_DIR)
	@echo "Iniciando servidor na porta $(TEST_SERVER_PORT)"
	@PORTA=$(TEST_SERVER_PORT) python3 server.py > $(LOG_DIR)/server_test_$(DATE).log 2>&1 & echo $$! > $(LOG_DIR)/server.pid
	@sleep 2
	@echo "Iniciando cliente 1 na porta $(TEST_CLIENT_PORT)"
	@$(PYTHON) client_gui.py --ip localhost --porta $(TEST_SERVER_PORT) & echo $$! > $(LOG_DIR)/client1.pid
	@echo "Iniciando cliente 2 na porta $(TEST_CLIENT2_PORT)"
	@$(PYTHON) client_gui.py --ip localhost --porta $(TEST_SERVER_PORT) & echo $$! > $(LOG_DIR)/client2.pid
	$(call print_success, "Teste iniciado com sucesso.")
	@echo "Para encerrar todos os processos utilize: make kill-all"

# Iniciar servidor com logs
server: check-port $(LOG_DIR)
	$(call print_status,"Iniciando servidor na porta $(PORT)...","🚀 ")
	@echo "$(CYAN)➜ Salvando logs em: $(LOG_DIR)/server_$(DATE).log$(RESET)"
	@echo $(PORT) | $(PYTHON) $(SERVER) 2>&1 | tee $(LOG_DIR)/server_$(DATE).log

# Iniciar clientes com logs
client1: $(LOG_DIR)
	$(call print_status,"Iniciando cliente 1...","👤 ")
	@echo "$(CYAN)➜ Salvando logs em: $(LOG_DIR)/client1_$(DATE).log$(RESET)"
	@$(PYTHON) $(CLIENT) 2>&1 | tee $(LOG_DIR)/client1_$(DATE).log

client2: $(LOG_DIR)
	$(call print_status,"Iniciando cliente 2...","👥 ")
	@echo "$(CYAN)➜ Salvando logs em: $(LOG_DIR)/client2_$(DATE).log$(RESET)"
	@$(PYTHON) $(CLIENT) 2>&1 | tee $(LOG_DIR)/client2_$(DATE).log

# Teste de integração com servidor e 2 clientes
integration-test: check-port $(LOG_DIR)
	$(call print_status,"Iniciando teste de integração na porta $(PORT)...","🔄 ")
	@echo "$(CYAN)➜ Log do servidor: $(LOG_DIR)/server_test_$(DATE).log$(RESET)"
	@echo "$(CYAN)➜ Log do cliente 1: $(LOG_DIR)/client1_test_$(DATE).log$(RESET)"
	@echo "$(CYAN)➜ Log do cliente 2: $(LOG_DIR)/client2_test_$(DATE).log$(RESET)"
	@(echo $(PORT) | $(PYTHON) $(SERVER) 2>&1 | tee $(LOG_DIR)/server_test_$(DATE).log) & \
	server_pid=$$! && \
	sleep 2 && \
	($(PYTHON) $(CLIENT) 2>&1 | tee $(LOG_DIR)/client1_test_$(DATE).log) & \
	($(PYTHON) $(CLIENT) 2>&1 | tee $(LOG_DIR)/client2_test_$(DATE).log) & \
	wait

# Iniciar servidor em modo debug
debug-server:
	$(call print_status,"Iniciando servidor em modo debug na porta $(PORT)...","🐛 ")
	@echo "$(YELLOW)➜ Comandos de debug:$(RESET)"
	@echo "  $(MAGENTA)n$(RESET) - próxima linha"
	@echo "  $(MAGENTA)c$(RESET) - continuar execução"
	@echo "  $(MAGENTA)l$(RESET) - mostrar localização atual"
	@echo "  $(MAGENTA)p variável$(RESET) - imprimir variável"
	@echo "  $(MAGENTA)q$(RESET) - sair"
	@echo "$(YELLOW)➜ A porta $(PORT) será usada automaticamente$(RESET)"
	@PORTA=$(PORT) $(PYTHON) -m pdb $(SERVER)

# Verificar disponibilidade da porta
check-port:
	@if [ -z "$(PORT)" ]; then \
		$(call print_error,"Porta não especificada!"); \
		exit 1; \
    fi
	$(call print_status,"Verificando se a porta $(PORT) está disponível...","🔍 ")
	@if nc -z localhost $(PORT) 2>/dev/null; then \
		$(call print_error,"Porta $(PORT) já está em uso!"); \
		exit 1; \
	else \
		$(call print_success,"Porta $(PORT) está disponível"); \
	fi

# Limpar arquivos gerados e logs
clean:
	$(call print_status," Limpando arquivos gerados e logs...")
	@rm -f *.pyc
	@rm -rf __pycache__
	@rm -rf $(LOG_DIR)
	$(call print_success,"Limpeza concluída")

# Mostrar logs
show-logs:
	$(call print_status,"Logs disponíveis:","📋 ")
	@if [ -d "$(LOG_DIR)" ]; then \
		echo "$(CYAN)"; \
		ls -l --color=auto $(LOG_DIR); \
		echo "$(RESET)"; \
	else \
		$(call print_error,"Diretório de logs não encontrado"); \
	fi

# Matar todos os processos Python (parada de emergência)
kill-all:
	$(call print_status,"Encerrando todos os processos Python..."," ⚡ ")
	@if [ -f "$(LOG_DIR)/server.pid" ]; then kill $$(cat $(LOG_DIR)/server.pid) 2>/dev/null || true; fi
	@if [ -f "$(LOG_DIR)/client1.pid" ]; then kill $$(cat $(LOG_DIR)/client1.pid) 2>/dev/null || true; fi
	@if [ -f "$(LOG_DIR)/client2.pid" ]; then kill $$(cat $(LOG_DIR)/client2.pid) 2>/dev/null || true; fi
	@rm -f $(LOG_DIR)/*.pid
	$(call print_success,"Todos os processos foram encerrados")

# Ajuda
help:
	@echo "$(BOLD)$(BLUE)╔══════════════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(BLUE)║$(RESET) $(BLUE) $(BOLD)                  🚀 Comandos Disponíveis $(RESET)$(BOLD)$(BLUE)                      ║$(RESET)"
	@echo "$(BOLD)$(BLUE)╠══════════════════════════════════════════════════════════════════╣$(RESET)"
	$(call print_table)
	@echo "$(BOLD)$(BLUE)╠══════════════════════════════════════════════════════════════════╣$(RESET)"
	@echo "$(BOLD)$(BLUE)║$(RESET) $(BOLD)📝 Exemplos de Uso:$(RESET)                           $(BOLD)$(BLUE)                   ║$(RESET)"
	@echo "$(BOLD)$(BLUE)╠══════════════════════════════════════════════════════════════════╣$(RESET)"
	$(call print_examples)
	@echo "$(BOLD)$(BLUE)╚══════════════════════════════════════════════════════════════════╝$(RESET)"

# Declarar alvos phony
.PHONY: test server client1 client2 integration-test clean check-port debug-server help kill-all show-logs