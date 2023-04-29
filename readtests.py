from random import shuffle
from tkinter import Tk
from tkinter.filedialog import askopenfilename

import yaml  # PyYAML


class RT:
    def __init__(self):
        self.topic = None
        self.questions = {0: {'TITLE': f'You have 15 seconds to answer',
                              'answers': ['This show the options in the test',
                                          'Only one is correct, search the matching button',
                                          'If you forgot answer one question, you wil be kicked out due a bug',
                                          'Press now any button to continue. Have Fun'],
                              'correct': 0}}
        self.read_questions()

    # Abre el archivo y carga los datos
    def open_test(self, route):
        with open(route, encoding="utf8") as file:
            test = yaml.safe_load(file)
            
        # Mezcla las preguntas
        order = (list(test['TEST'].values()))
        shuffle(order)
        # Actualiza el nuevo orden con la numeración correcta
        battery = dict()
        for item in order: battery.update({(order.index(item)+1): item})
        
        self.topic = test['TOPIC']
        self.questions.update(battery)


    # Recibe el nombre de archivo y comprueba que se puede abrir
    def read_questions(self):
        root = Tk()
        filetypes = (('yaml files', '*.yaml'), ('yaml files', '*.yml'))
        root.withdraw()

        test = askopenfilename(initialdir="./tests/", filetypes=filetypes)

        try:
            self.open_test(route=test)

        except FileNotFoundError:
            raise FileNotFoundError('File not found, check the directory')
