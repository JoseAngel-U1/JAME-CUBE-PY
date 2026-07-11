# #! Widget que dibuja el estado del cubo (stickers) en una QGraphicsScene.

from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem
from PySide6.QtGui import QBrush, QPen, QPainter
from PySide6.QtCore import Qt, QRectF

from core.constants import COLORS


#!  WIDGET DEL CUBO
class RubikCubeWidget(QGraphicsView):
    #TODO: Separacion visual entre stickers de una misma cara,
    #TODO: y separacion (mayor) entre caras distintas.
    STICKER_GAP = 2
    FACE_GAP = 4

    def __init__(self, state, n):
        super().__init__()
        self.state = state
        self.n = n
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.setRenderHint(QPainter.Antialiasing)
        self.setStyleSheet("background-color: #222; border-radius: 10px;")
        self.draw_cube()

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
