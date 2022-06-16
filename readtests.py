import yaml

class RT:
    def __init__(self):
        self.title = None
        self.preguntas = {}
        self.read_questions()

    def read_questions(self):
        
        with open("test.yaml", encoding="utf8") as file:
            questions = yaml.safe_load(file)
            
        self.title = questions['TOPIC']
        self.preguntas = questions['TEST']