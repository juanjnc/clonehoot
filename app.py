from datetime import datetime
from threading import Thread
from flask import Flask, make_response, render_template, request, send_from_directory, url_for
from flask_socketio import SocketIO
from readtests import RT

# Initialize applications
rt = RT()  # Initialize RT class for handling questions
host_app = Flask(__name__)
socketio_host = SocketIO(host_app)

player_app = Flask(__name__)
socketio_player = SocketIO(player_app)

# Game state
waiting_game = True
players = {}
start_time = 0
max_question_time = 15
current_question_index = 0
pending_questions = list(rt.questions.keys())


# Host routes
@host_app.route("/", methods=["GET", "POST"])
def host_index():
    """Main page for the host."""
    global start_time
    player_list = ", ".join(player["nickname"] for player in players.values())
    if request.method == "POST" and request.form.get('submit_button') == 'Start Game':
        start_time = datetime.now().timestamp()
        return test_page()

    data = {"web": "CloneHoot", "welcome_message": "Welcome!", "players": player_list}
    return render_template("index.html", data=data)


@host_app.route("/test", methods=["GET", "POST"])
def test_page():
    """Update test page during the quiz."""
    global start_time, current_question_index, pending_questions, waiting_game
    
    waiting_game = False

    if not pending_questions:
        return final_page()

    question_id = pending_questions[0]
    current_question_index = question_id
    question_data = rt.questions[question_id]

    time_remaining = max_question_time - int(datetime.now().timestamp() - start_time)
    player_list = ", ".join(player["nickname"] for player in players.values() if player["total"] == current_question_index)

    if time_remaining <= 0:
        start_time = datetime.now().timestamp()
        pending_questions.pop(0)

    template_data = {
        "web": "CloneHoot - Quiz",
        "topic": rt.topic,
        "question": question_data["TITLE"],
        "answers": question_data["answers"],
        "players": player_list,
        "time_remaining": time_remaining
    }

    if question_data["TITLE"].endswith(".png"):
        return render_template("test_img.html", data=template_data, image=url_for("download_file", name=question_data["TITLE"]))
    return render_template("test.html", data=template_data)


@host_app.route("/<path:name>")
def download_file(name):
    """Serves image files for questions."""
    return send_from_directory("./tests", name, as_attachment=True)


@host_app.route("/fin", methods=["GET", "POST"])
def final_page():
    """Displays the final results."""
    winner = calculate_winner()
    data = {
        "web": "CloneHoot - Quiz",
        "winner": winner["name"],
        "score": winner["score"],
        "leaderboard": winner["leaderboard"],
    }
    return render_template("fin.html", data=data)


# Player routes
@player_app.route("/")
def player_index():
    """Landing page for players."""
    data = {
        "web": "CloneHoot",
        "welcome_message": "Welcome Players!",
    }
    return render_template("player.html", data=data)


@player_app.route("/register", methods=["POST", "GET"])
def register_player():
    """Handles player registration."""
    global players
    if request.method == "POST":
        nickname = request.form["name"]
        if nickname in players or any(c in nickname for c in ",-;") or not nickname or len(nickname) > 15:
            return render_template("player_taken.html", data={"web": "CloneHoot"})

        players[nickname] = {"nickname": nickname, "score": 0, "total": -1}
        welcome_message = f"Hello {nickname}, we'll start right away"
        response = make_response(render_template("waiting.html", data={"web": "CloneHoot", "welcome_message": welcome_message}))
        response.set_cookie("name", nickname)
        return response
    return render_template("register.html")


@player_app.route("/waiting")
def waiting_page():
    """Waiting page for players until the game starts."""
    global waiting_game
    nickname = request.cookies.get("name")
    message = f"Hello {nickname}, waiting for more players"
    data = {"web": "CloneHoot", "welcome_message": message, "refresh": "1; URL=answer" if not waiting_game else "1; URL=waiting"}
    return render_template("waiting2.html", data=data)


@player_app.route("/answer", methods=["GET", "POST"])
def submit_answer():
    """Handles player responses to questions."""
    global pending_questions
    nickname = request.cookies.get("name")
    player = players[nickname]
    topic = rt.topic
    question_id = pending_questions[0]
    correct_answer = rt.questions[question_id]["correct"]
    if request.method == "POST":
        player["total"] += 1
        if request.form["submit_button"] == correct_answer:
            player["score"] += 1
        return next_question()
    data = {
        "web": "CloneHoot - Quiz",
        "topic": topic,
    }
    return render_template("answer.html", data=data)


@player_app.route("/next", methods=["GET", "POST"])
def next_question():
    """Prepares the next question or ends the game if no more questions."""
    if not pending_questions:
        return final_page()

    question_id = pending_questions[0]
    nickname = request.cookies.get("name")
    player = players[nickname]
    correct_answer = rt.questions[question_id]["correct"]
    if player["total"] == current_question_index:
        return submit_answer()

    data = {"web": "CloneHoot - Quiz", "correct_answer": correct_answer}
    return render_template("next.html", data=data)


def start_host():
    """Starts the host side of the application."""
    socketio_host.run(app=host_app, host='0.0.0.0', port=5000)


def start_player():
    """Starts the player side of the application."""
    socketio_player.run(app=player_app, host='0.0.0.0', port=5001)


def calculate_winner():
    """Calculates and returns the winner of the quiz."""
    leaderboard = sorted(
        ((nickname, attrs['score']) for nickname, attrs in players.items()), 
        key=lambda x: x[1],
        reverse=True
    )
    winner_name, max_score = leaderboard[0]
    return {
        "name": winner_name,
        "score": max_score,
        "leaderboard": [f"{nick} => {score}" for nick, score in leaderboard]
    }


if __name__ == "__main__":
    host_thread = Thread(target=start_host, daemon=True)
    player_thread = Thread(target=start_player, daemon=True)
    host_thread.start()
    player_thread.start()
    host_thread.join()
    player_thread.join()