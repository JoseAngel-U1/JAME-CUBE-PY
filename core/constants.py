# #! Constantes compartidas: tamaños de cubo permitidos y colores de caras.

from PySide6.QtGui import QColor

#TODO: Tamanos de cubo permitidos, y a partir de que tamano se habilitan los wide moves
TAMANOS_PERMITIDOS = (2, 3, 4)
TAMANO_MINIMO_WIDE = 4  #* Rw/Uw/etc. solo tienen sentido real desde 4x4 en adelante

#TODO: Colores para las caras del cubo
COLORS = {
    'U': QColor("white"),   #? Up
    'D': QColor("yellow"),  #? Down
    'F': QColor("green"),   #? Front
    'B': QColor("blue"),    #? Back
    'L': QColor("orange"),  #? Left
    'R': QColor("red")      #? Right
}
