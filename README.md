## Arquitetura

1. **Frontend (Interface Web):** HTML5, CSS (Bootstrap 4) e python Flask Jinja2.
2. **Backend (Gerente SNMP):** pysnmp
3. **Banco de Dados**: PostgreSQL

## Ambiente
```bash
python3 -m venv venv
source ./venv/bin/activate

pip install flask
pip install pysnmp
```
## Árvore de pastas
```text
tf_ogmr/
├── templates/
|   └── index.html                # Página principal do gerente (professor)
├── snmp/
    └── gerente.py                # Back-end para manipulação SNMP
├── server.py                     # Aplicação servidora da página web via Flask
├── README.md                     # Especificação do projeto
└── script.sql                    # Script de criação de banco de dados (PostgreSQL)
```
