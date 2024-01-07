"""
MIT License

Copyright (c) 2022 hunter87

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""



import os
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import requests as req
from threading import Thread
import datetime
import secrets 
from flask_discord import DiscordOAuth2Session, Unauthorized
import discord as dc
from modules import config, bot

webh = config.cfdata["webh"]

#token = secrets.token_hex(16)
app = Flask("Spruce")
app.static_folder = "static"
app.secret_key = config.spot_secret
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "false"  # !! Only in development environment.

app.config["DISCORD_CLIENT_ID"] = 931202912888164474
app.config["DISCORD_CLIENT_SECRET"] = config.cfdata["csecret"]
app.config["DISCORD_BOT_TOKEN"] =  config.cfdata["TOKEN"]
app.config["DISCORD_REDIRECT_URI"] = "https://sprucebot.tech/callback"
discord = DiscordOAuth2Session(app)

HYPERLINK = '<a href="{}">{}</a>'




def welcome_user(user):
	dm_channel = discord.bot_request("/users/@me/channels","POST",json={"recipient_id": user.id})
	return discord.bot_request(f"/channels/{dm_channel['id']}/messages","POST",json={"content": "You've Successfully Logged In.."})


tokens = []
for i in range(4):
	tokens.append(secrets.token_hex(24))


@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404


@app.route("/", methods=["POST", "GET"])
def index():
	print(request.url)
	return render_template("index.html", msg="dashboard", url="/dashboard")


@app.route("/dashboard/")
def dashboard():
	if not discord.authorized:
		return redirect(url_for("login"))
	try:
		user = discord.fetch_user()
		glds = []
		guilds = discord.fetch_guilds()
		for g in guilds:
			if g.permissions.administrator:
				glds.append(g)
		return render_template("dash.html", avatar=user.avatar_url, leng=len(guilds), title="Spruce Bot -Dashboard", guilds=glds, user=user)
	except Exception as e:
		return "Something Went Wrong", print(e)

@app.route("/<user_id>/guilds/<guild_id>/")
def guild(user_id, guild_id):
	if not discord.authorized:
		return redirect(url_for("login"))
	guild = bot.bot.get_guild(guild_id)
	return jsonify({"guild":guild.name, "guild_id" : guild.id, "owner":guild.owner})
	


@app.route("/login/")
def login():
	return discord.create_session()


@app.route("/login-data/")
def login_with_data():
	return discord.create_session(
	 data=dict(redirect="/me/", coupon="15off", number=15, zero=0, status=False))


@app.route("/invite-bot/")
def invite_bot():
	return discord.create_session(scope=["bot"],permissions=8,guild_id=464488012328468480,disable_guild_select=False)


@app.route("/invite-oauth/")
def invite_oauth():
	return discord.create_session(scope=["bot", "identify"], permissions=8)


@app.route("/callback/")
def callback():
	data = discord.callback()
	redirect_to = data.get("redirect", "/dashboard/")
	#user = discord.fetch_user()
	#welcome_user(user)
	return redirect(redirect_to)


@app.route("/me/")
def me():
	user = discord.fetch_user()
	return f"""
		<html>
		<head>
		<title>{user.name}</title>
		</head>
		<body><img src='{user.avatar_url or user.default_avatar_url}' />
		<p>Is avatar animated: {str(user.is_avatar_animated)}</p>
		<a href={url_for("my_connections")}>Connections</a>
		<br />
		</body>
		</html>
"""


@app.route("/me/guilds/")
def user_guilds():
	glds = []
	guilds = discord.fetch_guilds()
	return "<br />".join([
	 f"[ADMIN] {g.name}" if g.permissions.administrator else g.name
	 for g in guilds
	])


@app.route("/add_to/<int:guild_id>/")
def add_to_guild(guild_id):
	user = discord.fetch_user()
	return user.add_to_guild(guild_id)


@app.route("/me/connections/")
def my_connections():
	user = discord.fetch_user()
	connections = discord.fetch_connections()
	print(type(connections))
	return f"""
<html>
<head>
<title>{user.name}</title>
</head>
<body>
{str([f"{connection.name} - {connection.type}" for connection in connections])}
</body>
</html>

"""


@app.route("/logout/")
def logout():
	discord.revoke()
	return redirect(url_for(".index"))


##### PRIME ########


@app.route("/webhook", methods=['POST'])
def webhook():
	data = json.loads(request.data)
	user = data["user"]
	print(data)
	reminder = False
	if "isWeekend" in data:
		reminder = data["isWeekend"]
	wbd = {
	 "content":
	 f"**<@{user}> Just Voted Spruce | Reminder Enabled : {str(reminder)}**"
	}
	req.post(url=webh, json=wbd)

	return "200"


@app.route("/clnk", methods=['POST'])
def create_code():
	#key = secrets.token_hex(10)
	data = request.form.to_dict()
	print(data)
	key = tokens[-1]
	return redirect(url_for("submit", token=key))


#, filename="sumbit.html"


@app.route("/submit/?key=<token>")
def submit(token):
	rl = request.url.split("key%3D")[-1]
	if tokens[-1] == rl:
		return render_template('payu/confirm.html')
	else:
		return "Link Expired"


@app.route("/success", methods=['POST'])
def success():
	tokens.remove(tokens[0])
	tokens.append(secrets.token_hex(24))
	date = str(datetime.datetime.now())
	date = date.split()[0]
	data = request.form.to_dict()
	data["time"] = date
	server_id = data['server_id']
	vjs = {"content": data}
	req.post(url=webh, json=vjs)
	with open('data.json', 'r') as f:
		frm = json.load(f)
	frm.append(data)

	with open('data.json', 'w') as f:
		json.dump(frm, f, indent=2)
	return render_template("payu/success.html",
	                       server_id=server_id,
	                       date=data["time"])


@app.route("/failed", methods=['POST'])
def failed():
	data = request.form.to_dict()
	#vjs = {"content" : data}
	#print(data)
	#req.post(url=os.environ["payuwbh"], json=vjs)
	return render_template("payu/failed.html", amount=data['amount'])


@app.route("/cancel", methods=['POST'])
def cancel():
	return render_template("cancel.html")


@app.route("/payu", methods=["POST"])
def payu():
	data = str(request.form.to_dict())[0:1987]
	print(data)
	reqs = req.post(url=os.environ['payuwbh'],
	                json={"content": f"<@885193210455011369>\n```\n{data}\n```"})
	return str(reqs)


#################  pages   #################
@app.route("/refund")
def refund():
	return render_template("pages/refund.html", title="Refund Policy")


@app.route("/refund_application")
def refund_app():
	try:
		user = discord.fetch_user()
		#print(dir(user))
		guilds = discord.fetch_guilds()
		if guilds != None:
			return render_template("pages/refund_app.html", guilds=guilds, user=user, title="Refund Application")
	except:
		return "<script>window.location.href='/login'></script>"


@app.route('/prime')
def prime():
	return render_template("prime.html", title="Spruce Prime")


@app.route('/vote')
def vote():
	return "<script>window.location.href='https://top.gg/bot/931202912888164474/vote'</script>"


@app.route('/invite')
def invite():
	return "<script>window.location.href='https://discord.com/oauth2/authorize?client_id=931202912888164474&permissions=8&scope=bot'</script>"


@app.route('/support')
def support():
	return "<script>window.location.href='https://discord.gg/vMnhpAyFZm'</script>"


@app.route("/terms")
def terms():
	return render_template("pages/toc.html", title="Terms And Conditions")


@app.route("/privacy")
def privacy():
	return render_template("pages/privacy.html", title="Privacy Policy")


@app.route("/about")
def about():
	return render_template("pages/about.html", title="About Us - Spruce")


@app.route("/contact")
def contact():
	return render_template("pages/contact.html")


@app.route("/refund_req", methods=["POST"])
def refund_req():
	msgh = os.environ["msgh"]
	data = request.form.to_dict()
	#print(data)
	req.post(
	 url=msgh,
	 json={
	  "content":
	  f"<@{config.owner_id}> Refund```\nEMAIL: {data['email']}\nUSER ID : {data['uid']}\nGUILD_ID : {data['guild']}\nMETHOD : {data['method']}\nINFO : {data['payinfo']}```",
	  "username": data["name"],
	  "avatar_url": data["logo"]
	 })
	return "<h1>Refund Application Request Sent. You'll Get Response Within 24h</h1>"


@app.route("/send", methods=["POST"])
def send():
	msgh = os.environ["msgh"]
	data = request.form.to_dict()
	req.post(
	 url=msgh,
	 json={
	  "content":
	  f"```\nEMAIL: {data['email']}\nSUB : {data['sub']}\nMSG : {data['msg']}\n```",
	  "username": data["name"]
	 })
	return "Sent"

ap = Flask("Health")
@ap.route("/")
def homee():return "Online..!"
def run():ap.run(host='0.0.0.0', port=8080)
def keep_alive():t = Thread(target=run); t.start()

# if __name__ == '__main__':
# 	ap.run(host="0.0.0.0", port=8080)
