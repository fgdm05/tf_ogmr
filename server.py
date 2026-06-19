from flask import *

from main import *
import asyncio
import psycopg2
import netifaces
from crontab import CronTab
from datetime import datetime		
import os
import time
from getmac import get_mac_address

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
    return get_mac_address(ip=ip)
    # for interface in netifaces.interfaces():
    #     addrs = netifaces.ifaddresses(interface)
    #     try:
    #         # Check if the interface has the target IP
    #         if_ips = addrs[netifaces.AF_INET][0]['addr']
    #         if if_ips == ip:
    #             # Return the MAC address for that interface
    #             return addrs[netifaces.AF_LINK][0]['addr']
    #     except (KeyError, IndexError):
    #         continue
    # return None

# Example usage: Get MAC for your current local IP
import socket
hostname = socket.gethostname()
local_ip = socket.gethostbyname(hostname)

print(f"MAC for {local_ip}: {mac}")   


def verif_mac(client_ip):
	mac = get_mac_for_ip(client_ip)
	print(f'mac descoberto {mac}')
	query = 'SELECT * FROM salas WHERE gerente=%s'
	cursor.execute(query, (mac,))
	row = cursor.fetchone()
	
	return (row, mac)
@app.route("/logando", methods = ['POST'])
def logando():
	session.permanent = True
	client_ip = request.remote_addr
	row, mac = verif_mac(client_ip)
	print(f"row: {row}")
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


def agendar(inicio, fim, port):
	print('acao2')
	
	print(inicio)
	print(fim)
	
	
	# (crontab -l 2>/dev/null; echo "30 16 18 6 * /home/trivia/tf2/tf_ogmr/venv/bin/python /home/trivia/tf2/tf_ogmr/cron.py 2 10.90.90.90 2") | crontab -
	py = "/home/trivia/tf2/tf_ogmr/venv/bin/python"
	print(py)
	cron2 = "/home/trivia/tf2/tf_ogmr/cron.py"
	portaa = port
	print(portaa)
	tempo = f"{inicio.minute} {inicio.hour} {inicio.day} {inicio.month} *"
	comando = f'(crontab -l 2>/dev/null; echo "{tempo} {py} {cron2} {portaa} 10.90.90.90 2") | crontab -'
	#A = f'(crontab -l 2>/dev/null; echo "30 16 18 6 * /home/trivia/tf2/tf_ogmr/venv/bin/python /home/trivia/tf2/tf_ogmr/cron.py 2 10.90.90.90 2") | crontab -'
	print(comando)
	
	os.system(comando)
	tempo2 = f"{fim.minute} {fim.hour} {fim.day} {fim.month} *"
	comando2 = f'(crontab -l 2>/dev/null; echo "{tempo2} {py} {cron2} {portaa} 10.90.90.90 1") | crontab -'
	os.system(comando2)

gateway = "10.90.90.90"

def formatar_date(data):
	return datetime.strptime(data, '%Y-%m-%dT%H:%M')

@app.route("/acao", methods=['POST'])
def acao():
	acao = request.form.get('acao')
	port = request.form.get('port')
	
	if(acao == "2"):
		inicio = formatar_date(request.form.get('inicio'))
		fim = formatar_date(request.form.get('fim'))
		if(fim < inicio):
			print('Data de fim não pode ser antes da data de início')
			return redirect(url_for('logado'))
		agendar(inicio, fim, port)

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
	ports = [x[0] for x in cursor.fetchall() if x[2]]
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
	porta = await run(OID=f"1.3.6.1.2.1.17.4.3.1.2.{mac_dec}", gateway = gateway)
	print(f"minha porta: {porta}")
	return porta

async def bloquear(ports, minhaPorta):
	corotinas = []
	for p in ports:
		if(minhaPorta != p):
			corotinas.append(await set_port(p,2))
		else:
			print('Não bloqueando a minha porta')
	# results = await asyncio.gather(*corotinas)
	# return results

@app.route("/bloquearTodas", methods=["POST"])
def bloquearTodas():
	ports = get_tabela(session.get('idSala'))
	print(f'IP {request.remote_addr}')
	mac = get_mac_for_ip(request.remote_addr)
	print(mac)
	port = asyncio.run(descobrirMinhaPorta(mac))
	


	#coroutines = [await set_port(p, 2) for p in ports] 
	res = asyncio.run(bloquear(ports, port[0][1]))
	# for p in ports:
	# 	if(port != p):
	# 		asyncio.create_task(set_port(p,2))
	# 		msg += f"{p} "
	# 	else:
	# 		print(f"Não bloqueando a porta {p}")


	return redirect(url_for("logado"))


@app.route("/agendarBloqueio", methods=["POST"])
def agendarBloqueio():
	ports = get_tabela(session.get('idSala'))
	print(f'IP {request.remote_addr}')
	mac = get_mac_for_ip(request.remote_addr)
	print(mac)
	port = asyncio.run(descobrirMinhaPorta(mac))

	inicio = formatar_date(request.form.get('inicio'))
	fim = formatar_date(request.form.get('fim'))
	if(fim < inicio):
		print('Data de fim não pode ser antes da data de início')
		return redirect(url_for('logado'))
		

	for p in ports:
		if(port[0][1] != p):
			agendar(inicio, fim, p)
	
	return redirect(url_for("logado"))


@app.route("/liberarTodas", methods=["POST"])
def liberarTodas():
	ports = get_tabela(session.get('idSala'))
	msg = "Portas "
	for p in ports:
		asyncio.run(set_port(p, 1))
		msg += f"{p} "
	msg += "liberadas!"
	print(msg)
	return redirect(url_for("logado"))
