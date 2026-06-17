from flask import *

from main import *
import asyncio
import psycopg2

app = Flask(__name__)

@app.route("/")
def login(noAuth = False):
	
	return render_template('login.html', noAuth=noAuth)

connection = psycopg2.connect(
	dbname="gerente",
	user="postgres",
	password="root",
	host="localhost",
	port=5432)
cursor = connection.cursor()

import netifaces

def get_mac_for_ip(ip):
    for interface in netifaces.interfaces():
        addrs = netifaces.ifaddresses(interface)
        try:
            # Check if the interface has the target IP
            if_ips = addrs[netifaces.AF_INET][0]['addr']
            if if_ips == ip:
                # Return the MAC address for that interface
                return addrs[netifaces.AF_LINK][0]['addr']
        except (KeyError, IndexError):
            continue
    return None

# Example usage: Get MAC for your current local IP
import socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print(f"MAC for {local_ip}: {mac}")   


def verif_mac(client_ip):
	mac = get_mac_for_ip(client_ip)
	query = 'SELECT * FROM salas WHERE gerente=%s'
	cursor.execute(query, (mac,))
	row = cursor.fetchone()
	
	return (row, mac)
@app.route("/logando", methods = ['POST'])
def logando():
	
	client_ip = request.remote_addr
	row, mac = verif_mac(client_ip)

	if row is None:
		print(f'Máquina não autorizada tentando acessar gerência.')
		print(f'MAC: {mac}')
		print(f'IP: {client_ip}')
		return redirect(url_for('nao_autorizado'))

	user = request.form.get('user')
	passw = request.form.get('passw')
	query2 = 'SELECT * FROM professores'
	cursor.execute(query2)
	while(True):
		one = cursor.fetchone()
		if(one is None):
			break;
		else:
			if(one[1] == user and one[2] == passw):
				query3 = 'SELECT * FROM portas WHERE idSala=%s'
				cursor.execute(query3, (row[0],))
				# fazer a lista de portas para recuperar para fazer a lista interna do logado
				# ports = []
				# while True:

				return redirect(url_for('logado'))

	return redirect(url_for('login', noAuth = True))

		

@app.route("/nao_autorizado")
def nao_autorizado():
	return render_template('nao_autorizado.html')

@app.route("/logado")
def logado():
	# ports = asyncio.run(inter())
	# for p in ports:
	# 	print(
	#         f"{p['ifindex']:3d} "
	#         f"{p['name']:30s} "
	#         f"admin={p['admin']:5s} "
	#     	f"oper={p['oper']}"
	#     )
	

	ports = asyncio.run(inter())
	return render_template('index.html', ports = ports)