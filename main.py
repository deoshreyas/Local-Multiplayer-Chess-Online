from flask import Flask, render_template, request, session
from flask_socketio import SocketIO, join_room, leave_room
from random import choices 
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "jkhswjgdgydh"
socketio = SocketIO(app)

rooms = {}

def GenerateCode(length):
    while True:
        code = "".join(choices(ascii_uppercase, k=length))
        if code not in rooms:
            break
    return code

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method=="POST":
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
    return render_template("index.html")

@app.route("/game")
def home():
    return render_template("board.html")

if __name__ == "__main__":
    socketio.run(app)