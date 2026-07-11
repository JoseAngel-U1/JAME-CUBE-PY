""" #! Modelo del cubo: estado inicial, rotaciones de caras y aplicación de movimientos.

    * No depende de Qt / UI: es lógica pura, facil de testear por separado.
"""

import copy


#TODO: Estado inicial del cubo (resuelto), generalizado a n*n stickers por cara
def create_initial_cube(n):
    faces = ('U', 'D', 'F', 'B', 'L', 'R')
    return {face: [face] * (n * n) for face in faces}


#TODO: UTILS: Rotar una cara (array de n*n)
def _rotate_cw(face, n):
    out = [None] * (n * n)
    for r in range(n):
        for c in range(n):
            out[c * n + (n - 1 - r)] = face[r * n + c]
    return out


def _rotate_ccw(face, n):
    out = [None] * (n * n)
    for r in range(n):
        for c in range(n):
            out[(n - 1 - c) * n + r] = face[r * n + c]
    return out


def _rotate_180(face, n):
    out = [None] * (n * n)
    for r in range(n):
        for c in range(n):
            out[(n - 1 - r) * n + (n - 1 - c)] = face[r * n + c]
    return out


def rotate_face(face, n, k):
    """#* k=0 identidad, 1=CW, 2=180, 3=CCW."""
    k = k % 4
    match k:
        case 0: return list(face)
        case 1: return _rotate_cw(face, n)
        case 2: return _rotate_180(face, n)
        case 3: return _rotate_ccw(face, n)


#TODO: MAPEOS DE ADYACENCIAS, generalizado para cualquier n y profundidad
#TODO: (depth=0 -> capa externa; depth=1 -> capa siguiente hacia adentro,
#TODO: necesaria solo para wide moves en cubos de 4x4 o mas)
def adj_nxn_depth(n, depth):
    def fila_sup():
        return [depth * n + c for c in range(n)]

    def fila_inf():
        return [(n - 1 - depth) * n + c for c in range(n)]

    return {
        "U": [
            ["F", fila_sup()], ["R", fila_sup()], ["B", fila_sup()], ["L", fila_sup()],
        ],
        "D": [
            ["F", fila_inf()], ["L", fila_inf()], ["B", fila_inf()], ["R", fila_inf()],
        ],
        "F": [
            ["U", [(n - 1 - depth) * n + c for c in range(n)]],
            ["R", [r * n + depth for r in range(n)]],
            ["D", [depth * n + (n - 1 - c) for c in range(n)]],
            ["L", [(n - 1 - r) * n + (n - 1 - depth) for r in range(n)]],
        ],
        "B": [
            ["U", [depth * n + (n - 1 - c) for c in range(n)]],
            ["L", [r * n + depth for r in range(n)]],
            ["D", [(n - 1 - depth) * n + c for c in range(n)]],
            ["R", [(n - 1 - r) * n + (n - 1 - depth) for r in range(n)]],
        ],
        "R": [
            ["U", [(n - 1 - r) * n + (n - 1 - depth) for r in range(n)]],
            ["B", [r * n + depth for r in range(n)]],
            ["D", [(n - 1 - r) * n + (n - 1 - depth) for r in range(n)]],
            ["F", [(n - 1 - r) * n + (n - 1 - depth) for r in range(n)]],
        ],
        "L": [
            ["U", [r * n + depth for r in range(n)]],
            ["F", [r * n + depth for r in range(n)]],
            ["D", [r * n + depth for r in range(n)]],
            ["B", [(n - 1 - r) * n + (n - 1 - depth) for r in range(n)]],
        ],
    }


#TODO: Aplica un movimiento (capa externa, o "wide" = 2 capas externas):
"""
    * Aplica un movimiento simple (pBase = 'R' 'U' ...). times = 1 (CW),
    * 2 (180°) o 3 (CCW) -> usando 3 como equivalente a -1 (una CW menos).
    * wide=True -> ademas de la capa externa, arrastra la capa inmediatamente
    * siguiente hacia adentro (equivalente a Rw, Uw, etc. en notacion WCA).
"""
def apply_basic_move(cube, move, n, times=1, wide=False):
    times = ((times % 4) + 4) % 4
    if times == 0: return cube

    c = copy.deepcopy(cube)
    c[move] = rotate_face(c[move], n, times)

    profundidades = range(2) if wide else range(1)
    for depth in profundidades:
        adj = adj_nxn_depth(n, depth)
        strips = [[c[face][i] for i in idxs] for face, idxs in adj[move]]

        if move in ('U', 'D'):
            for _ in range(times):
                first = strips.pop(0)
                strips.append(first)
        else:
            for _ in range(times):
                last = strips.pop()
                strips.insert(0, last)

        for (face, idxs), strip in zip(adj[move], strips):
            for pos, val in zip(idxs, strip):
                c[face][pos] = val

    return c
