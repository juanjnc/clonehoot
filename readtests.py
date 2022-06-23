from tkinter.messagebox import QUESTION
import yaml  # PyYAML
from tkinter import Tk
from tkinter.filedialog import askopenfilename


class RT:
    def __init__(self):
        self.title = None
        self.questions = {0: {'TITLE': 'You have 15 seconds to answer',
                              'answers': ['This show the options in the test',
                                          'Only one is correct, search the matching button',
                                          'Press now any button to continue',
                                          'Have fun!'],
                              'correct': 0}}
        self.read_questions()

    # Abre el archivo y carga los datos
    def open_test(self, route):
        with open(route, encoding="utf8") as file:
                test = yaml.safe_load(file)

        self.title = test['TOPIC']
        self.questions.update(test['TEST'])

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
