class RQ:
    def __init__(self):
        # Necesitamos un índice para listar las preguntas como diccionarios, también ayuda a iterar
        self.index = 1  # El índice empieza en 1 para seguir la numeración de las preguntas
        self.title = None
        self.preguntas = {self.index: {}}

    def read_questions(self):
        # Es más fácil declarando las llaves y el valor ya, ahorra forzar tipos luego
        pregunta = {'enunciado': '', 'respuestas': [], 'correcta': 0}

        with open('questions.txt', encoding="utf8") as questions:
            questions = questions.readlines()

        self.title = questions[0]
        question = questions[1:]

        # Actualiza los valores, las respuestas al ser lista van distinto
        for line in question:
            if line.startswith('*'):
                pregunta['enunciado'] = line[1:].strip("\n")
            elif line.startswith('-'):
                pregunta['respuestas'].append(line[1:].strip("\n"))
            elif line.startswith('+'):
                # Verifica que correcta es 0, si no error porque ya hay una
                if pregunta['correcta'] == 0:
                    pregunta['respuestas'].append(line[1:].strip("\n"))
                else:
                    raise "Only one correct answer"
                
                pregunta['correcta'] = len(pregunta['respuestas'])
            elif line.startswith('='):
                # Antes de añadir, verificar que la información es válida
                if pregunta['enunciado'] != '':
                    print('ok')
                if pregunta['respuestas'] != []:
                    print('ok')
                if pregunta['correcta'] != 0:
                    print('ok')
                else:
                    raise 'Check the format of the test' 
                # Añade, cambia el índice para la pregunta y limpia
                self.preguntas[self.index] = pregunta
                self.index += 1
                pregunta = {'enunciado': '', 'respuestas': [], 'correcta': 0}
