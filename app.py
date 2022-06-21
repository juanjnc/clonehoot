import threading
from flask import Flask, render_template, request, make_response
from readtests import RT
from datetime import datetime, timedelta

# Variables necesarias para la comunicación entre los dos procesos
en_espera = True
jugadores = {}
pendientes = [0]
tiempo_inicial = 0
contador = 0


rt = RT()
pendientes = list(rt.questions.keys())

# Funciones del profesor/maestro/director de juego
host_player = Flask(__name__)


@host_player.route("/", methods=['GET', 'POST'])
def index():
    # Página principal del host
    # Esto evita saltar la primera pregunta
    global tiempo_inicial
    
    # Creamos texto con la lista de jugadores
    lista_usuarios = ''
    
    # TODO sincronizar con el inicio del test
    # tiempo_inicial = datetime.now().timestamp()
    
    for usuario in jugadores.values():
        lista_usuarios = lista_usuarios + ' ' + usuario['apodo']
        
    if request.method == 'POST':
        tiempo_inicial = datetime.now().timestamp()
        if request.form['submit_button'] == 'start':
            return test()

    data = {
        'web': 'CloneHoot',
        'bienvenida': '¡Saludos!',
        'usuarios': lista_usuarios,
    }
    return make_response(render_template('index.html', data=data))


@host_player.route("/test", methods=['GET', 'POST'])
def test():
    # Página del test, se va actualizando
    # Cambios globales
    global en_espera
    global tiempo_inicial
    global contador
    global pendientes
    en_espera = False
    lista_usuarios = ''
    titulo = rt.title
    # fin del juego si la lista está vacia
    if len(pendientes) == 0:
        return fin()
    # Lleva el número de preguntas y un contador para sincronizar a los jugadores
    num_preg = pendientes[0]
    contador = pendientes[0]
    # Los datos de las preguntas para presentarlos en cada pantalla
    enunciado = rt.questions[num_preg]['TITLE']
    respuestas = rt.questions[num_preg]['answers']
    
    # TODO debería mostrar lista de jugadores por responder o ya respondidos
    for usuario in jugadores.values():
        if usuario['total'] == contador:
            lista_usuarios = lista_usuarios + ' ' + usuario['apodo']
    
    # 15 segundos para responder
    if datetime.now().timestamp() - tiempo_inicial >= 15:
        tiempo_inicial = datetime.now().timestamp()
        pendientes.pop(0)

    # Los datos para pasarlo a la plantilla
    data = {
        'web': 'CloneHoot - Quiz',
        'titulo': titulo,
        'preguntas': enunciado,
        'respuestas': respuestas,
        'usuarios': lista_usuarios,
        'tiempo': int(datetime.now().timestamp() - tiempo_inicial)
    }
    
    return render_template('test.html', data=data)


@host_player.route("/fin", methods=['GET', 'POST'])
def fin():
    # Página del final de partida
    data = {
        'web': 'CloneHoot - Quiz',
        'ganador': ganador()[0],
        'puntuacion': ganador()[1],
        'lista':ganador()[2],
    }
    return render_template('fin.html', data=data)


# Funciones del jugador
player_side = Flask(__name__)

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
    # Primera página de espera para el jugador
    if request.method == 'POST':
        user = request.form['apodo']
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
    titulo = rt.title
    num_preg = pendientes[0]
    enunciado = rt.questions[num_preg]['TITLE']
    correcta = rt.questions[num_preg]['correct']
    # si respuesta correcta sumar punto
    print('\n')
    print('INFO AL ACTUALIZARSE LA PÁGINA')
    print('La puntuación es de:' + str(jugador['puntuaciones']))
    print('el total de preguntas respondidas es de:' + str(jugador['total']))
    print(f'El valor de pendientes es de {pendientes}')
    print(f'estamos en en la pregunta {pendientes[0]}')
    print('\n')
    if request.method == 'POST':
        # Añade 1 al contador de preguntas realizadas
        jugador['total'] += 1
        print(f'El jugador ha respondido en la pregunta {num_preg} haciendo un total de respondidas de ' + str(jugador['total']))
        print('\n')
        if request.form['submit_button'] == str(correcta):
            jugador['puntuaciones'] += 1
            print(f'El jugador ha obtenido un punto con una puntuacion total de: ' + str(jugador['puntuaciones']))
            print('\n')
            
        return nextq()

    data = {
        'web': 'CloneHoot - Quiz',
        'titulo': titulo,
        'preguntas': enunciado,
    }
    return render_template('respuesta.html', data=data)


@player_side.route("/next", methods=['GET', 'POST'])
def nextq():
    # La plantilla para la espera a la siguiente pregunta
    global contador
    global pendientes
    usuario = request.cookies.get('apodo')
    jugador = jugadores[usuario]
    if len(pendientes) == 0:
        # fin del juego
        data = {
            'web': 'CloneHoot - Quiz',
            'ganador': ganador()[0],
            'puntuacion': ganador()[1],
            'lista':ganador()[2],
        }
        return render_template('fin.html', data=data)
    if jugador['total'] == contador:
        return respuesta()

    data = {
        'web': 'CloneHoot - Quiz',
    }
    return render_template('next.html', data=data)


def start_host():
    host_player.run(port=5000)


def start_player():  # TODO host="0.0.0.0" will make the page accessable
    player_side.run(port=5001)


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

    return [nombre, maxima, lista]


if __name__ == '__main__':
    thread1 = threading.Thread(target=start_host)
    thread2 = threading.Thread(target=start_player)
    
    thread1.start()
    thread2.start()

    thread1.join()
    thread2.join()
