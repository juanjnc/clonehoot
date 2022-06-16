# About CloneHoot

CloneHoot is a WebApp inspired by **kahoot.it**.

Built using **Flask**, which you need  in order to run it

# How to use

You must change this

    def  start_player():
	    player_side.run(port=5001)
	    
to this (for example):

    def  start_player():
	    player_side.run(host="0.0.0.0", port=5001)

 - Players run in that IP Address
 - Game Server run in 127.0.0.1:5000

You must change the content of *test.yaml* following this pattern:

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
        TITLE: QUESTION TITLE 2
        answers:
        - WRONG ANSWER
        - WRONG ANSWER
        - WRONG ANSWER
        - CORRECT ANSWER
        correct: 4
    
    REPEAT QUESTION FORMAT


 - There must always be 3 wrong answers and 1 correct answer
 - You must not alter the **TOPIC**, **TEST**, **TITLE**, **answer** and **correct** keywords 
 - You may change the position of the correct answer in the list
 - You may have any number of questions, must have at least 1
