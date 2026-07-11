""" #! Parseo y validación de secuencias de movimientos (scrambles).

    * Tampoco depende de Qt: recibe texto plano y devuelve estructuras
    * de datos + mensajes de error listos para mostrar en la UI.
"""

import re

from .constants import TAMANO_MINIMO_WIDE


#TODO: Parsea la secuencia de movimientos, validando cuales estan permitidos
#TODO: para el tamano de cubo actual (bloquea 'w' si n < TAMANO_MINIMO_WIDE).
#? Devuelve (moves_validos, tokens_rechazados) para poder avisarle al usuario.
def parse_sequence(seq, n):
    if not seq.strip(): return [], []
    tokens = seq.strip().split()
    moves = []
    rechazados = []
    permitir_wide = n >= TAMANO_MINIMO_WIDE

    for t in tokens:
        #? Normalizar comillas (`'` o `'`) a ASCII ' si vienen de copias
        t_norm = t.replace("’", "'").replace("‘", "'")
        m = re.match(r"^([UDLRFB])([wW]?)(['2]?)$", t_norm)
        if not m:
            rechazados.append(t)
            continue

        base, w, mod = m.groups()
        wide = bool(w)

        if wide and not permitir_wide:
            rechazados.append(t)
            continue

        if mod == "2": times = 2
        elif mod == "'": times = 3
        else: times = 1
        moves.append((base, times, wide))

    return moves, rechazados


#TODO: Valida la secuencia COMPLETA antes de tocar el cubo.
#? Devuelve (es_valida, moves, rechazados). Si hay al menos un token
#? rechazado, es_valida = False y no debe aplicarse ningun movimiento.
def validate_sequence(seq, n):
    moves, rechazados = parse_sequence(seq, n)
    es_valida = len(rechazados) == 0 and len(moves) > 0
    return es_valida, moves, rechazados


#TODO: Clasifica POR QUE un token puntual fue rechazado, para poder
#TODO: mostrarle al usuario un motivo especifico (letra invalida,
#TODO: minuscula, wide no disponible, modificador raro, etc.)
#TODO: en vez de un mensaje generico para toda la secuencia.
def clasificar_token_invalido(t, n):
    t_norm = t.replace("’", "'").replace("‘", "'")

    if not t_norm:
        return f"«{t}»: token vacío"

    primera = t_norm[0]
    if primera.upper() not in "UDLRFB":
        return f"«{t}»: '{primera}' no es una cara válida (usar U D L R F B)"

    if primera.islower():
        return f"«{t}»: la cara debe ir en mayúscula ('{primera.upper()}' en vez de '{primera}')"

    resto = t_norm[1:]
    wide = False
    idx = 0
    if idx < len(resto) and resto[idx] in "wW":
        wide = True
        idx += 1

    if wide and n < TAMANO_MINIMO_WIDE:
        return (f"«{t}»: movimiento wide no disponible en cubo {n}x{n} "
                f"(solo desde {TAMANO_MINIMO_WIDE}x{TAMANO_MINIMO_WIDE})")

    modificador = resto[idx:]
    if modificador not in ("", "'", "2"):
        return (f"«{t}»: modificador inválido ('{modificador}'). "
                f"Los únicos válidos son: sin nada (giro simple), ' (giro antihorario) o 2 (180°)")

    return f"«{t}»: notación inválida (ej: R, U', F2, Rw, Rw')"
