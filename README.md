## Arquitetura

1. **Frontend (Interface Web):** HTML5, CSS (Bootstrap 4) e python Flask Jinja2.
2. **Backend (Gerente SNMP):** pysnmp
3. **Banco de Dados**: PostgreSQL

## Ambiente
No sistema operacional Linux Mint 22.1 x86_64
```bash

python3 -m venv venv
source ./venv/bin/activate

pip install flask
pip install pysnmp
pip install psycopg2-binary
pip install netifaces
pip install crontab

flask --app server.py run --host="10.90.90.90" --port=5000

sudo apt install postgresql

# Instalar a chave pública do repositório:
curl -fsS https://www.pgadmin.org/static/packages_pgadmin_org.pub | sudo gpg --dearmor -o /etc/apt/keyrings/packages-pgadmin-org.gpg

# Criar arquivo de configuração de repositório para o Linux Mint 22.1:
sudo sh -c 'echo "deb [signed-by=/etc/apt/keyrings/packages-pgadmin-org.gpg] https://ftp.postgresql.org/pub/pgadmin/pgadmin4/apt/noble pgadmin4 main" > /etc/apt/sources.list.d/pgadmin4.list && apt update'

sudo apt install pgadmin4

```
## Árvore de pastas
```text
tf_ogmr/
├── templates/
|   └── index.html                # Página principal do gerente (professor)
|   └── login.html                # Página inicial de login
|   └── nao_autorizado.html       # Página de computador não autorizado ao sistema
├── main.py                       # Back-end para manipulação SNMP
├── server.py                     # Aplicação servidora da página web via Flask
├── README.md                     # Especificação do projeto
└── createOGMR.sql                # Script de criação de banco de dados (PostgreSQL)
```
