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

You must change the content of *questions.txt* following this pattern:

    TOPIC OF THE TEST
    
    *QUESTION TITLE
    -WRONG ANSWER
    +CORRECT ANSWER
    -WRONG ANSWER
    -WRONG ANSWER
    = END OF QUESTION
    
    REPEAT QUESTION FORMAT


 - There must always be 3 wrong answers (marked with "-") and 1 correct answer (marked with "+")
 - You may change the position of the correct answer in the list
 - You may have any number of questions, must have at least 1
