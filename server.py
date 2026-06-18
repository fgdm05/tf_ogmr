from flask import *

from main import *
import asyncio
import psycopg2
import netifaces
from crontab import CronTab
from datetime import datetime		
import os
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route("/")
def login(noAuth = False):
	if(noAuth):
		session.permanent = False
	return render_template('login.html', noAuth=noAuth)

connection = psycopg2.connect(
	dbname="gerente",
	user="postgres",
	password="root",
	host="localhost",
	port=5432)
cursor = connection.cursor()



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
	session.permanent = True
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
				
				#session['ports'] = interfaces
				session['idSala'] = row[0]
				return redirect(url_for('logado'))

	return redirect(url_for('login', noAuth = True))


gateway = "10.204.132.51"
@app.route("/acao", methods=['POST'])
def acao():
	acao = request.form.get('acao')
	port = request.form.get('port')
	
	if(acao == "2"):
		print('acao2')
		inicio = datetime.strptime(request.form.get('inicio'), '%Y-%m-%dT%H:%M')
		fim = datetime.strptime(request.form.get('fim'), '%Y-%m-%dT%H:%M')
		print(inicio)
		print(fim)
		if(fim < inicio):
			print('Data de fim não pode ser antes da data de início')
			return redirect(url_for('logado'))
		
		# (crontab -l 2>/dev/null; echo "30 16 18 6 * /home/trivia/tf2/tf_ogmr/venv/bin/python /home/trivia/tf2/tf_ogmr/cron.py 2 10.90.90.90 2") | crontab -
		py = "/home/trivia/tf2/tf_ogmr/venv/bin/python"
		print(py)
		cron2 = "/home/trivia/tf2/tf_ogmr/cron.py"
		portaa = port
		print(portaa)
		tempo = f"{inicio.minute} {inicio.hour} {inicio.day} {inicio.month} *"
		comando = f'(crontab -l 2>/dev/null; echo "{tempo} {py} {cron2} {portaa} 10.90.90.90 2") | crontab -'
		A = f'(crontab -l 2>/dev/null; echo "30 16 18 6 * /home/trivia/tf2/tf_ogmr/venv/bin/python /home/trivia/tf2/tf_ogmr/cron.py 2 10.90.90.90 2") | crontab -'
		print(comando)
		print(A)
		os.system(comando)
		tempo2 = f"{fim.minute} {fim.hour} {fim.day} {fim.month}"
		comando2 = f'(crontab -l 2>/dev/null; echo "{tempo2} {py} {cron2} {int(portaa)} 10.90.90.90 1") | crontab -'
		os.system(comando2)



	elif(acao == "1"):
		asyncio.run(set_port(int(port), 1))
		time.sleep(1.5)

	return redirect(url_for('logado', refresh=time.time()))


@app.route("/nao_autorizado")
def nao_autorizado():
	return render_template('nao_autorizado.html')

def get_tabela(idSala):
	query3 = 'SELECT * FROM portas WHERE idSala=%s'
	cursor.execute(query3, (idSala,))
	ports = [x[0] for x in cursor.fetchall()]
	return ports

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
	# query3 = 'SELECT * FROM portas WHERE idSala=%s'
	# cursor.execute(query3, (session.get('idSala'),))
	# # fazer a lista de portas para recuperar para fazer a lista interna do logado
	# # ports = []
	# # while True:
	# ports = [x[0] for x in cursor.fetchall()]
	# print('ports')
	# print(ports)
	# interfaces = asyncio.run(inter(ports))
	portss = get_tabela(session.get('idSala'))
	interfaces = asyncio.run(inter(portss))
	#ports = asyncio.run(inter(list(range(1,24))))
	#ports = session.get('ports')
	return render_template('index.html', ports = interfaces)


async def descobrirMinhaPorta(mac_alvo):
	mac_dec = ".".join(str(int(x, 16)) for x in mac_alvo.split(":"))
	oid_mac_table = "1.3.6.1.2.1.17.4.3.1.2"
	bridge_port = await run(OID=f"{oid_mac_table}.{mac_dec}", gateway=gateway, community='public')
	print('bridge')
	print(bridge_port)

    

	return porta


@app.route("/bloquearTodas", methods=["POST"])
def bloquearTodas():
	ports = get_tabela(session.get('idSala'))
	print(f'IP {request.remote_addr}')
	mac = get_mac_for_ip(request.remote_addr)
	print(mac)
	port = asyncio.run(descobrirMinhaPorta(mac))
	return redirect(url_for("logado"))


@app.route("/liberarTodas", methods=["POST"])
def liberarTodas():

	return redirect(url_for("logado"))
