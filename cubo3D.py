import tkinter as tk

# Definir colores para las caras del cubo
colors = {
    'U': 'white',  # Up (Blanco)
    'D': 'yellow', # Down (Amarillo)
    'F': 'green',  # Front (Verde)
    'B': 'blue',   # Back (Azul)
    'L': 'orange', # Left (Naranja)
    'R': 'red'     # Right (Rojo)
}

# Definir estado inicial del cubo (sin mezclar)
initial_state = {
    'U': ['U'] * 9,
    'D': ['D'] * 9,
    'F': ['F'] * 9,
    'B': ['B'] * 9,
    'L': ['L'] * 9,
    'R': ['R'] * 9,
}

# Función para rotar una cara del cubo 90 grados en sentido horario
def rotate_face_clockwise(face):
    return [face[6], face[3], face[0], face[7], face[4], face[1], face[8], face[5], face[2]]

# Función para rotar una cara del cubo 90 grados en sentido antihorario
def rotate_face_counterclockwise(face):
    return [face[2], face[5], face[8], face[1], face[4], face[7], face[0], face[3], face[6]]

# Función para rotar una cara del cubo 180 grados
def rotate_face_180(face):
    return [face[8], face[7], face[6], face[5], face[4], face[3], face[2], face[1], face[0]]

# Definir cómo cada movimiento afecta el estado del cubo
def rotate_cube(state, move):
    new_state = {face: state[face][:] for face in state}
    
    if move.endswith("2"):
        steps = 2
        move = move[0]
    elif move.endswith("'"):
        steps = 3
        move = move[0]
    else:
        steps = 1

    for _ in range(steps):
        temp_state = {face: new_state[face][:] for face in new_state}  # Crear una copia temporal del estado
        if move == 'U':
            temp_state['U'] = rotate_face_clockwise(temp_state['U'])
            temp_state['F'][0:3], temp_state['R'][0:3], temp_state['B'][0:3], temp_state['L'][0:3] = \
                new_state['R'][0:3], new_state['B'][0:3], new_state['L'][0:3], new_state['F'][0:3]
        elif move == 'D':
            temp_state['D'] = rotate_face_clockwise(temp_state['D'])
            temp_state['F'][6:9], temp_state['R'][6:9], temp_state['B'][6:9], temp_state['L'][6:9] = \
                new_state['L'][6:9], new_state['F'][6:9], new_state['R'][6:9], new_state['B'][6:9]
        elif move == 'F':
            temp_state['F'] = rotate_face_clockwise(temp_state['F'])
            temp_state['U'][6:9], temp_state['R'][0:9:3], temp_state['D'][0:3], temp_state['L'][8::-3] = \
                new_state['L'][8::-3], new_state['U'][6:9], new_state['R'][0:9:3], new_state['D'][0:3]
        elif move == 'B':
            temp_state['B'] = rotate_face_clockwise(temp_state['B'])
            temp_state['U'][0:3], temp_state['R'][8::-3], temp_state['D'][6:9], temp_state['L'][0:9:3] = \
                new_state['R'][8::-3], new_state['D'][6:9], new_state['L'][0:9:3], new_state['U'][0:3]
        elif move == 'L':
            temp_state['L'] = rotate_face_clockwise(temp_state['L'])
            temp_state['U'][0:9:3], temp_state['F'][0:9:3], temp_state['D'][0:9:3], temp_state['B'][8::-3] = \
                new_state['B'][8::-3], new_state['U'][0:9:3], new_state['F'][0:9:3], new_state['D'][0:9:3]
        elif move == 'R':
            temp_state['R'] = rotate_face_clockwise(temp_state['R'])
            temp_state['U'][8::-3], temp_state['B'][0:9:3], temp_state['D'][8::-3], temp_state['F'][8::-3] = \
                new_state['F'][8::-3], new_state['U'][8::-3], new_state['B'][0:9:3], new_state['D'][8::-3]
        new_state = temp_state.copy()
    return new_state

# Función para dibujar una cara del cubo
def draw_face(canvas, face, top_left_x, top_left_y):
    size = 30  # Tamaño de cada cuadrado
    for i in range(3):
        for j in range(3):
            color = colors[face[i * 3 + j]]
            x0 = top_left_x + j * size
            y0 = top_left_y + i * size
            x1 = x0 + size
            y1 = y0 + size
            canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="black")

# Función para dibujar todo el cubo
def draw_cube(canvas, state):
    # Coordenadas top-left para cada cara
    positions = {
        'U': (90, 0),
        'L': (0, 90),
        'F': (90, 90),
        'R': (180, 90),
        'B': (270, 90),
        'D': (90, 180)
    }
    
    for face in state:
        x, y = positions[face]
        draw_face(canvas, state[face], x, y)

# Función para aplicar movimientos al cubo y dibujarlo
def apply_moves():
    moves = entry.get().strip().split()
    current_state = initial_state.copy()
    for move in moves:
        current_state = rotate_cube(current_state, move)
    canvas.delete("all")
    draw_cube(canvas, current_state)

# Crear ventana principal
root = tk.Tk()
root.title("Cubo de Rubik")

# Crear canvas para dibujar el cubo
canvas = tk.Canvas(root, width=360, height=270)
canvas.pack()

# Crear entrada de texto para los movimientos
entry = tk.Entry(root, width=50)
entry.pack()

# Botón para aplicar los movimientos
button = tk.Button(root, text="Aplicar movimientos", command=apply_moves)
button.pack()

# Dibujar cubo inicial
draw_cube(canvas, initial_state)

# Ejecutar la aplicación
root.mainloop()
