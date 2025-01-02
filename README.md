# About CloneHoot

CloneHoot is a WebApp inspired by **kahoot.it**. It is now powered by a single Flask application integrated with **Flask-SocketIO** to enable real-time interactions between the host and players.

## Built using

- **Flask**
- **Flask-SocketIO**
- **PyYAML**

### Installation

To correctly run the program, you need to install the following:

pip install Flask
pip install Flask-SocketIO
pip install PyYAML

For Linux and macOS users, Tkinter needs to be manually installed.

For macOS, you can follow this guide: Install Tkinter on macOS (<https://www.geeksforgeeks.org/how-to-install-tkinter-on-macos/>)

For Linux, you can follow this guide: Install Tkinter on Linux (<https://www.geeksforgeeks.org/how-to-install-tkinter-on-linux/>)

## How to Use

With the updated architecture, only one server runs to handle both host and player interactions.

- The game server runs at `0.0.0.0:5000` and handles both the host interface and player connections.
- Players connect to the server using this `IP:5000\player` address to participate in the quiz.

## Configuration

To configure the questions, modify the contents of `test.yaml` following this pattern:

```yaml
TOPIC: EXAMPLE TITLE
TEST:
  1:
    TITLE: QUESTION TITLE 1
    answers:
      - WRONG ANSWER
      - CORRECT ANSWER
      - WRONG ANSWER
      - WRONG ANSWER
    correct: 2
  2:
    TITLE: PICTURE.PNG
    answers:
      - WRONG ANSWER
      - WRONG ANSWER
      - WRONG ANSWER
      - CORRECT ANSWER
    correct: 4

   REPEAT QUESTION FORMAT
```

- There must always be 3 wrong answers and 1 correct answer
- You must not alter the **TOPIC**, **TEST**, **TITLE**, **answer** and **correct** keywords
- You may change the position of the correct answer in the list
- You may have any number of questions, must have at least 1
- The **TITLE** can be a picture in png format. Place the picture in the same folder and fill the **TITLE** with the name and extension.
