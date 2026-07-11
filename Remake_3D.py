from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QComboBox,
    QGraphicsScene, QGraphicsView, QGraphicsRectItem,
    QMessageBox
)
from PySide6.QtGui import QBrush, QPen, QColor, QPainter
from PySide6.QtCore import Qt, QRectF, QTimer
import sys, re, copy

#TODO: Tamanos de cubo permitidos, y a partir de que tamano se habilitan los wide moves
TAMANOS_PERMITIDOS = (2, 3, 4)
TAMANO_MINIMO_WIDE = 4  #* Rw/Uw/etc. solo tienen sentido real desde 4x4 en adelante

#TODO: Colores para las caras del cubo
COLORS = {
    'U': QColor("white"),   # Up
    'D': QColor("yellow"),  # Down
    'F': QColor("green"),   # Front
    'B': QColor("blue"),    # Back
    'L': QColor("orange"),  # Left
    'R': QColor("red")      # Right
}


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
*/
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
        t_norm = t.replace("'", "'").replace("'", "'")
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


#TODO: Valida la secuencia COMPLETA antes de tocar el cubo.
#? Devuelve (es_valida, moves, rechazados). Si hay al menos un token
#? rechazado, es_valida = False y no debe aplicarse ningun movimiento.
def validate_sequence(seq, n):
    moves, rechazados = parse_sequence(seq, n)
    es_valida = len(rechazados) == 0 and len(moves) > 0
    return es_valida, moves, rechazados


#!  WIDGET DEL CUBO
class RubikCubeWidget(QGraphicsView):
    def __init__(self, state, n):
        super().__init__()
        self.state = state
        self.n = n
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-color: #222; border-radius: 10px;")
        self.draw_cube()

    #TODO: Separacion visual entre stickers de una misma cara,
    #TODO: y separacion (mayor) entre caras distintas.
    STICKER_GAP = 2
    FACE_GAP = 4
 
    def draw_cube(self):
        self.scene.clear()
        n = self.n
        size = 120 // n if n <= 6 else 15  #* achicar el sticker si el cubo es grande
        #* "block" = ancho/alto de una cara completa + el gap que la separa de la siguiente
        block = n * size + self.FACE_GAP
        positions = {
            'U': (block, 0),
            'L': (0, block),
            'F': (block, block),
            'R': (2 * block, block),
            'B': (3 * block, block),
            'D': (block, 2 * block)
        }
        for face, (x, y) in positions.items():
            self.draw_face(face, x, y, size)
 
    def draw_face(self, face, top_left_x, top_left_y, size):
        n = self.n
        gap = self.STICKER_GAP
        for i in range(n):
            for j in range(n):
                color = COLORS[self.state[face][i * n + j]]
                rect = QRectF(
                    top_left_x + j * size + gap / 2,
                    top_left_y + i * size + gap / 2,
                    size - gap,
                    size - gap
                )
                square = QGraphicsRectItem(rect)
                square.setBrush(QBrush(color))
                square.setPen(QPen(Qt.black, 1))
                self.scene.addItem(square)


#! APLICACIÓN PRINCIPAL:
class RubikCubeApp(QWidget):
    def __init__(self, n=3):
        super().__init__()
        self.n = n
        self.setWindowTitle("Cubo de Rubik Interactivo")
        self.setGeometry(350, 200, 610, 550)
        self.setStyleSheet("""
            QWidget { background-color: #1e1e1e; color: white; font-family: 'Segoe UI'; }
            QLineEdit { background-color: #333; color: white; border: 1px solid #555; border-radius: 6px; padding: 6px; }
            QPushButton { background-color: #0078d7; color: white; border: none; border-radius: 6px; padding: 8px 12px; }
            QPushButton:hover { background-color: #005a9e; }
            QComboBox { background-color: #333; color: white; border: 1px solid #555; border-radius: 6px; padding: 6px; }
        """)

        self.cube = create_initial_cube(self.n)
        self.moves_applied = 0

        #* Layouts
        layout = QVBoxLayout(self)

        label = QLabel("Simulador de Cubo de Rubik")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
        layout.addWidget(label)

        #* Selector de tamano de cubo
        selector_layout = QHBoxLayout()
        selector_label = QLabel("Tamaño del cubo:")
        self.size_selector = QComboBox()
        for tam in TAMANOS_PERMITIDOS:
            self.size_selector.addItem(f"{tam}x{tam}", tam)
        self.size_selector.setCurrentIndex(TAMANOS_PERMITIDOS.index(self.n))
        selector_layout.addWidget(selector_label)
        selector_layout.addWidget(self.size_selector)
        selector_layout.addStretch()
        layout.addLayout(selector_layout)

        self.cube_widget = RubikCubeWidget(self.cube, self.n)
        layout.addWidget(self.cube_widget)

        #* Entrada de movimientos
        entry_layout = QHBoxLayout()
        self.entry = QLineEdit()
        self.apply_btn = QPushButton("Aplicar")
        self.reset_btn = QPushButton("Reiniciar")
        entry_layout.addWidget(self.entry)
        entry_layout.addWidget(self.apply_btn)
        entry_layout.addWidget(self.reset_btn)
        layout.addLayout(entry_layout)

        self.meta_label = QLabel()
        self.meta_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.meta_label)

        #TODO: Conexiones
        self.apply_btn.clicked.connect(self.apply_moves)
        self.reset_btn.clicked.connect(self.reset_cube)
        self.entry.returnPressed.connect(self.apply_moves)
        self.size_selector.currentIndexChanged.connect(self.change_size)

        self._actualizar_placeholder()
        self._actualizar_status("Estado: resuelto · movimientos aplicados: 0")

    #TODO: FUNCIONES DE CONTROL:
    def _wide_permitido(self):
        return self.n >= TAMANO_MINIMO_WIDE

    def _actualizar_placeholder(self):
        if self._wide_permitido():
            self.entry.setPlaceholderText("Ejemplo: Rw U R' Uw'  (w = movimiento wide, 2 capas)")
        else:
            self.entry.setPlaceholderText("Ejemplo: R U R' U'  (wide 'w' no disponible en este tamaño)")

    def _actualizar_status(self, texto):
        self.meta_label.setText(texto)

    def change_size(self):
        nuevo_n = self.size_selector.currentData()
        self.n = nuevo_n
        self.cube = create_initial_cube(self.n)
        self.cube_widget.n = self.n
        self.cube_widget.state = self.cube
        self.cube_widget.draw_cube()
        self.moves_applied = 0
        self._actualizar_placeholder()
        estado_wide = "habilitados" if self._wide_permitido() else "bloqueados (solo desde 4x4)"
        self._actualizar_status(
            f"Cubo {self.n}x{self.n} · movimientos wide {estado_wide} · movimientos aplicados: 0"
        )

    def reset_cube(self):
        self.cube = create_initial_cube(self.n)
        self.cube_widget.state = self.cube
        self.cube_widget.draw_cube()
        self.moves_applied = 0
        self._actualizar_status(f"Estado: resuelto ({self.n}x{self.n}) · movimientos aplicados: 0")

    #TODO: Muestra una alerta modal cuando la secuencia no es aplicable
    #TODO: en su totalidad para el cubo seleccionado.
    def _alertar_scramble_invalido(self, rechazados):
        #* Un motivo especifico por cada token, en vez de un unico
        #* mensaje generico para toda la secuencia.
        motivos = [clasificar_token_invalido(t, self.n) for t in rechazados]
        detalle = "\n".join(f"• {m}" for m in motivos)

        QMessageBox.warning(
            self,
            "Scramble inválido",
            f"La secuencia contiene movimientos no válidos para el cubo {self.n}x{self.n}:\n\n"
            f"{detalle}\n\nNo se aplicó ningún movimiento."
        )

    def apply_moves(self):
        seq = self.entry.text().strip()
        if not seq: return

        #* Se valida TODA la secuencia antes de tocar el cubo.
        #* Si hay un solo token invalido, no se aplica nada y se avisa.
        es_valida, moves, rechazados = validate_sequence(seq, self.n)

        if not es_valida:
            self._alertar_scramble_invalido(rechazados if rechazados else [seq])
            self._actualizar_status(
                f"⚠️ Scramble rechazado · movimientos aplicados: {self.moves_applied}"
            )
            return

        self.animate_moves(moves)
        self.entry.clear()

    def animate_moves(self, moves):
        """#? Aplica los movimientos uno a uno con una animación leve."""
        self.moves_list = moves
        self.move_index = 0

        def step():
            if self.move_index >= len(self.moves_list):
                return
            move, times, wide = self.moves_list[self.move_index]
            self.cube = apply_basic_move(self.cube, move, self.n, times, wide)
            self.cube_widget.state = self.cube
            self.cube_widget.draw_cube()
            self.moves_applied += 1
            self._actualizar_status(f"Cubo {self.n}x{self.n} · movimientos aplicados: {self.moves_applied}")
            self.move_index += 1
            if self.move_index < len(self.moves_list):
                QTimer.singleShot(150, step)

        step()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RubikCubeApp(n=3)
    window.show()
    sys.exit(app.exec())