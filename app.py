import threading
from flask import Flask, render_template, request, make_response, send_from_directory, url_for
from readtests import RT
from datetime import datetime
from flask_socketio import SocketIO

# Variables necesarias para la comunicación entre los dos procesos
rt = RT()
en_espera = True
jugadores = {}
start_time = 0
question_time = 15
contador = 0
pendientes = list(rt.questions.keys())

# Funciones del profesor/maestro/director de juego
host_player = Flask(__name__)
socketio_host = SocketIO(host_player)

@host_player.route("/", methods=['GET', 'POST'])
def index():
    # Página principal del host
    global start_time

    # Creamos texto con la lista de jugadores
    lista_usuarios = ''

    for usuario in jugadores.values():
        lista_usuarios = lista_usuarios + (usuario['apodo']+ ', ')

    if request.method == 'POST':
        start_time = datetime.now().timestamp()

        if request.form['submit_button'] == 'start':
            return test()

    data = {
        'web': 'CloneHoot',
        'bienvenida': '¡Saludos!',
        'usuarios': lista_usuarios[:-2],
    }

    return make_response(render_template('index.html', data=data))


@host_player.route("/test", methods=['GET', 'POST'])
def test():
    # Página del test, se va actualizando
    # Cambios globales
    global en_espera
    global start_time
    global contador
    global pendientes

    en_espera = False
    lista_usuarios = ''
    topic = rt.topic

    # fin del juego si la lista está vacia
    if len(pendientes) == 0:
        return fin()

    # Lleva el número de preguntas y un contador para sincronizar a los jugadores
    num_preg = pendientes[0]
    contador = pendientes[0]
    # Los datos de las preguntas para presentarlos en cada pantalla
    enunciado = rt.questions[num_preg]['TITLE']
    respuestas = rt.questions[num_preg]['answers']
    # Devuelve ell tiempo restante de la pregunta
    time_remaining = (question_time - int(datetime.now().timestamp() - start_time))
    # debería mostrar lista de jugadores por responder o ya respondidos
    for usuario in jugadores.values():
        if usuario['total'] == contador:
            lista_usuarios = lista_usuarios + (usuario['apodo']+ ', ')
    # 15 segundos para responder
    if datetime.now().timestamp() - start_time >= question_time:
        start_time = datetime.now().timestamp()
        pendientes.pop(0)

    if enunciado.endswith('.png'):
        data = {
            'web': 'CloneHoot - Quiz',
            'topic': topic,
            'preguntas': enunciado,
            'respuestas': respuestas,
            'usuarios': lista_usuarios[:-2],
            'tiempo': time_remaining,
        }

        return render_template('test_img.html', data=data, image=url_for('download_file', name=enunciado))

    # Los datos para pasarlo a la plantilla
    data = {
        'web': 'CloneHoot - Quiz',
        'topic': topic,
        'preguntas': enunciado,
        'respuestas': respuestas,
        'usuarios': lista_usuarios,
        'tiempo': time_remaining,
    }

    return render_template('test.html', data=data)


@host_player.route('/<path:name>')
def download_file(name):
    return send_from_directory('./tests', name, as_attachment=True)


@host_player.route("/fin", methods=['GET', 'POST'])
def fin():
    # Página del final de partida
    data = {
        'web': 'CloneHoot - Quiz',
        'ganador': ganador()[0],
        'puntuacion': ganador()[1],
        'lista': ganador()[2],
    }

    return render_template('fin.html', data=data)


# Funciones del jugador
player_side = Flask(__name__)
socketio_player = SocketIO(player_side)

@player_side.route("/")
def index():
    # Página principal del jugador
    data = {
        'web': 'CloneHoot',
        'bienvenida': '¡Saludos, Jugadores!',
    }

    return render_template('player.html', data=data)


@player_side.route("/registrar", methods=['POST', 'GET'])
def registrar():
    global jugadores
    # Primera página de espera para el jugador
    if request.method == 'POST':
        user = request.form['apodo']

    # Comprueba si el user existe
    if user in jugadores:
        data = {
            'web': 'CloneHoot',
        }
        return render_template('player_taken.html', data=data)

    # Comprueba si el user tiene caracteres prohibidos
    for item in ',-;':
        if item in user:
            data = {
                'web': 'CloneHoot',
            }
            return render_template('player_taken.html', data=data)
    
    if user == '' or user == ' ':
        data = {
            'web': 'CloneHoot',
        }
        return render_template('player_taken.html', data=data)

    # Se crea una cookie con el usuario dado
    nuevo_usuario = {'apodo': user, 'puntuaciones': 0, 'total': -1}
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
    # Primera página de espera para el jugador
    # Cuando el host da la orden se redirije a la partida
    if en_espera is True:
        redirigida = 'espera'
    else:
        redirigida = 'respuesta'
    usuario = request.cookies.get('apodo')
    bienvenido = f'Hola {usuario}, esperando a más jugadores'

    data = {
        'web': 'CloneHoot',
        'bienvenida': bienvenido,
        'refrescar': f'1; URL={redirigida}'
    }

    return render_template('espera2.html', data=data)


@player_side.route("/respuesta", methods=['GET', 'POST'])
def respuesta():
    global pendientes

    # obtener nombre del jugador
    usuario = request.cookies.get('apodo')
    # obtener el jugador
    jugador = jugadores[usuario]

    # Obtener las respuestas
    topic = rt.topic
    num_preg = pendientes[0]
    correcta = rt.questions[num_preg]['correct']

    if request.method == 'POST':
        # Añade 1 al contador de preguntas realizadas
        jugador['total'] += 1
    
        # si respuesta correcta sumar punto
        if request.form['submit_button'] == str(correcta):
            jugador['puntuaciones'] += 1
        return nextq()
    
    data = {
        'web': 'CloneHoot - Quiz',
        'topic': topic,
    }

    return render_template('respuesta.html', data=data)


@player_side.route("/next", methods=['GET', 'POST'])
def nextq():
    # La plantilla para la espera a la siguiente pregunta
    global contador
    global pendientes
    
    if len(pendientes) == 0:
        # fin del juego
        data = {
            'web': 'CloneHoot - Quiz',
            'ganador': ganador()[0],
            'puntuacion': ganador()[1],
            'lista': ganador()[2],
        }
        return render_template('fin.html', data=data)
    
    num_preg = pendientes[0]
    usuario = request.cookies.get('apodo')
    jugador = jugadores[usuario]
    correcta = rt.questions[num_preg]['correct']
    
    if jugador['total'] == contador:
        return respuesta()

    data = {
        'web': 'CloneHoot - Quiz',
        'correcta': correcta
    }

    return render_template('next.html', data=data)


def start_host():
    socketio_host.run(app=host_player, port=5000)


def start_player():  # TODO host="0.0.0.0" will make the page accessable
    socketio_player.run(app=player_side, host="0.0.0.0", port=5001)


def ganador():
    # Busca al ganador de la partida
    maxima = -1
    nombre = ''
    lista = []

    for jugador, valores in jugadores.items():
        lista.append(f"{jugador} => {valores['puntuaciones']}")

        if valores['puntuaciones'] > maxima:
            maxima = valores['puntuaciones']
            nombre = jugador
    lista.sort()

    return [nombre, maxima, lista]


if __name__ == '__main__':
    thread1 = threading.Thread(target=start_host)
    thread2 = threading.Thread(target=start_player)

    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
