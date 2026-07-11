# #! Ventana principal: controles (input, botones, selector de tamaño) + orquestación.

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QComboBox, QMessageBox
)
from PySide6.QtCore import Qt, QTimer

from core.constants import TAMANOS_PERMITIDOS, TAMANO_MINIMO_WIDE
from core.cube_model import create_initial_cube, apply_basic_move
from core.move_parser import validate_sequence, clasificar_token_invalido
from .cube_widget import RubikCubeWidget


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
        #? Aplica los movimientos uno a uno con una animación leve.
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
