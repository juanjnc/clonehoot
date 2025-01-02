from datetime import datetime
from flask import Flask, make_response, render_template, request, send_from_directory, url_for, redirect
from flask_socketio import SocketIO
from readtests import RT

# Initialize application
rt = RT()  # Initialize RT class for handling questions
app = Flask(__name__)
socketio = SocketIO(app)

# Game state
waiting_game = True
players = {}
start_time = 0
max_question_time = 15
current_question_index = 0
pending_questions = list(rt.questions.keys())


# Host routes
@app.route("/", methods=["GET", "POST"])
def host_index():
    """Main page for the host."""
    global start_time
    player_list = ", ".join(player["nickname"] for player in players.values())
    if request.method == "POST" and request.form.get("submit_button") == "Start Game":
        start_time = datetime.now().timestamp()
        return test_page()

    data = {"web": "CloneHoot", "welcome_message": "Welcome!", "players": player_list}
    return render_template("index.html", data=data)


@app.route("/test", methods=["GET", "POST"])
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
    player_list = ", ".join(
        player["nickname"] for player in players.values() if player["total"] == current_question_index
    )

    if time_remaining <= 0:
        start_time = datetime.now().timestamp()
        pending_questions.pop(0)

    template_data = {
        "web": "CloneHoot - Quiz",
        "topic": rt.topic,
        "question": question_data["TITLE"],
        "answers": question_data["answers"],
        "players": player_list,
        "time_remaining": time_remaining,
        "image": url_for("download_file", apodo=question_data["TITLE"]) if question_data["TITLE"].endswith(".png") else None
    }

    return render_template("test.html", data=template_data)


@app.route("/<path:apodo>")
def download_file(apodo):
    """Serves image files for questions."""
    return send_from_directory("./tests", apodo, as_attachment=True)


@app.route("/fin", methods=["GET", "POST"])
def final_page():
    """Displays the final results."""
    winner = calculate_winner()
    data = {
        "web": "CloneHoot - Quiz",
        "winner": winner["apodo"],
        "score": winner["score"],
        "leaderboard": winner["leaderboard"],
    }
    return render_template("fin.html", data=data)


# Player routes
@app.route("/player/")
def player_index():
    """Landing page for players."""
    data = {
        "web": "CloneHoot",
        "welcome_message": "Welcome Players!",
    }
    return render_template("player.html", data=data)


@app.route("/player/register", methods=["POST", "GET"])
def register_player():
    """Handles player registration."""
    global players
    if request.method == "POST":
        nickname = request.form["apodo"]
        if nickname in players or any(c in nickname for c in ",-;") or not nickname or len(nickname) > 15:
            return render_template(
                "player_taken.html",
                data={"web": "CloneHoot", "welcome_message": "Username already taken or invalid name"},
            )

        players[nickname] = {"nickname": nickname, "score": 0, "total": -1}
        welcome_message = f"Hello {nickname}, we'll start right away"
        response = make_response(redirect(url_for("player_waiting")))
        response.set_cookie("apodo", nickname)
        return response
    return render_template("register.html", data={"web": "CloneHoot", "welcome_message": "Welcome Players!"})


@app.route("/player/waiting")
def player_waiting():
    """Waiting page for players until the game starts."""
    if not waiting_game:
        return redirect(url_for("submit_answer"))
    data = {"web": "CloneHoot", "refresh": 5, "welcome_message": "Welcome to the Waiting Room"}  # Example refresh rate
    return render_template("waiting.html", data=data)


@app.route("/player/waiting2")
def player_waiting2():
    return redirect(url_for("player_waiting"))


@app.route("/player/answer", methods=["GET", "POST"])
def submit_answer():
    """Handles player responses to questions."""
    global pending_questions
    nickname = request.cookies.get("apodo")
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


@app.route("/player/next", methods=["GET", "POST"])
def next_question():
    """Prepares the next question or ends the game if no more questions."""
    if not pending_questions:
        return final_page()

    question_id = pending_questions[0]
    nickname = request.cookies.get("apodo")
    player = players[nickname]
    correct_answer = rt.questions[question_id]["correct"]
    if player["total"] == current_question_index:
        return submit_answer()

    data = {"web": "CloneHoot - Quiz", "correct_answer": correct_answer}
    return render_template("next.html", data=data)


def calculate_winner():
    """Calculates and returns the winner of the quiz."""
    leaderboard = sorted(
        ((nickname, attrs["score"]) for nickname, attrs in players.items()), key=lambda x: x[1], reverse=True
    )
    winner_name, max_score = leaderboard[0]
    return {
        "apodo": winner_name,
        "score": max_score,
        "leaderboard": [f"{nick} => {score}" for nick, score in leaderboard],
    }


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
