import threading
from flask import Flask, render_template, request, make_response
from readtxt import RQ

# Variables necesarias para la comunicación
en_espera = True
jugadores = {}

# Funciones para la carga del cuestionario
rq = RQ()
rq.read_questions()
# print(rq.title, rq.preguntas)


# Funciones del profesor/maestro/director de juego
host_player = Flask(__name__)


@host_player.route("/")
def index():
    # Creamos texto con la lista de jugadores
    lista_usuarios = ''
    for usuario in jugadores.values():
        lista_usuarios = lista_usuarios + ' ' + usuario['apodo']

    data = {
        'web': 'CloneHoot',
        'bienvenida': '¡Saludos!',
        'usuarios': lista_usuarios,
    }
    return make_response(render_template('index.html', data=data))


@host_player.route("/test", methods=['GET', 'POST'])
def test():
    global en_espera
    en_espera = False
    lista_usuarios = ''
    titulo = rq.title

    # TODO Consigo que muestre la primera, pero no que pase a la siguiente
    for ii in rq.preguntas.keys():
        for usuario in jugadores.values():
            if usuario['total'] == ii:
                lista_usuarios = lista_usuarios + ' ' + usuario['apodo']
        # Los datos de las preguntas para presentarlos en cada pantalla
        enunciado = rq.preguntas[ii]['enunciado']
        respuestas = rq.preguntas[ii]['respuestas']
        # Los datos para pasarlo a la plantilla
        data = {
            'web': 'CloneHoot - Quiz',
            'titulo': titulo,
            'preguntas': enunciado,
            'respuestas': respuestas,
            'usuarios': lista_usuarios,
        }
        # TODO Intentos de conseguir que se actualice
        if request.method == 'POST':
            if request.form['next']:
                ii += 1
        return render_template('test.html', data=data)


# Funciones del jugador
player_side = Flask(__name__)


@player_side.route("/respuesta", methods=['GET', 'POST'])
def respuesta():
    # obtener nombre del jugador
    usuario = request.cookies.get('apodo')
    # obtener el jugador
    jugador = jugadores[usuario]

    titulo = rq.title
    # TODO Consigo que muestre la primera, pero no que pase a la siguiente
    for ii in rq.preguntas.keys():
        enunciado = rq.preguntas[ii]['enunciado']
        correcta = rq.preguntas[ii]['correcta']

        # si respuesta correcta sumar punto
        if request.method == 'POST':
            if request.form['submit_button'] == str(correcta):
                jugador['puntuaciones'] += 1
                # print(jugador)
            # TODO Una idea para llevar la contabilidad de preguntas superadas, funciona
            jugador['total'] += 1
            return nextq()

        # TODO enviar a pagina siguiente
        data = {
            'web': 'CloneHoot - Quiz',
            'titulo': titulo,
            'preguntas': enunciado,
        }
        return render_template('respuesta.html', data=data)


# La plantilla para la espera a la siguiente pregunta
@player_side.route("/next")
def nextq():
    data = {
        'web': 'CloneHoot - Quiz',
    }
    return render_template('next.html', data=data)


@player_side.route("/")
def index():
    data = {
        'web': 'CloneHoot',
        'bienvenida': '¡Saludos, Jugadores!',
    }
    return render_template('player.html', data=data)


@player_side.route("/registrar", methods=['POST', 'GET'])
def registrar():
    if request.method == 'POST':
        user = request.form['apodo']

    nuevo_usuario = {'apodo': user, 'puntuaciones': 0, 'total': 0}
    jugadores[user] = nuevo_usuario
    bienvenido = f'Hola {user}, enseguida empezamos'
    data = {
        'web': 'CloneHoot',
        'bienvenida': bienvenido,
    }
    resp = make_response(render_template('espera.html', data=data))
    resp.set_cookie('apodo', user)

    return resp


@player_side.route('/espera')
def espera():
    if en_espera is True:
        redirigida = 'espera'
    else:
        redirigida = 'respuesta'
    usuario = request.cookies.get('apodo')
    bienvenido = f'Hola {usuario}, esperando a más jugadores'
    data = {
        'web': 'CloneHoot',
        'bienvenida': bienvenido,
        'refrescar': f'3; URL={redirigida}'
    }
    return render_template('espera2.html', data=data)


'''def pagina_no_encontrada(error):
    return render_template('404.html'), 404'''


def arranca1():
    host_player.run(port=5000)


def arranca2():
    player_side.run(port=5001)


if __name__ == '__main__':
    thread1 = threading.Thread(target=arranca1)
    thread2 = threading.Thread(target=arranca2)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
