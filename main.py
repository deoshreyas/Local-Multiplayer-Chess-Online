from flask import Flask, render_template, request, redirect, url_for, session  
from flask_socketio import SocketIO, join_room, leave_room, send
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

@app.route("/", methods=["POST", "GET"])
def index():
    session.clear()

    if request.method=="POST":
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)
        if join:
            if not code:
                return render_template("index.html", error="Please enter a code!")
        
        room = code 

        if create:
            room = GenerateCode(5)
            rooms[room] = {"fen": "start", "members": 0}
        elif code not in rooms:
            return render_template("index.html", error="Invalid code!")
        
        session["room"] = room
        
        return redirect(url_for("home"))
    return render_template("index.html")

@app.route("/game/")
def home():
    room = session.get("room")
    if room is None or room not in rooms:
        return redirect(url_for("index"))
    if rooms[room]["members"]>=2:
        return redirect(url_for("index"))
    return render_template("board.html", room=room, fen=rooms[room]["fen"])

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    if not room:
        return
    if room not in rooms:
        leave_room(room)
        return 
    if rooms[room]["members"]>=2: # Only 2 players allowed
        leave_room(room)
        return 
    join_room(room)
    rooms[room]["members"] += 1

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"]<=0:
            del rooms[room] 

@socketio.on("move")
def move(data):
    room = session.get("room")
    if room not in rooms:
        return 
    content = {
        "tag": "game",
        "fen": data["fen"]
    }
    send(content, to=room)
    rooms[room]["fen"] = data["fen"]

if __name__ == "__main__":
    socketio.run(app, debug=True)