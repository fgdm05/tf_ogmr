from flask import Flask, render_template

from main import *
import asyncio
app = Flask(__name__)

@app.route("/")
def hello_world():
	# ports = asyncio.run(inter())
	# for p in ports:
	# 	print(
    #         f"{p['ifindex']:3d} "
    #         f"{p['name']:30s} "
    #         f"admin={p['admin']:5s} "
    #     	f"oper={p['oper']}"
    #     )
	return render_template('index.html', a = 1)