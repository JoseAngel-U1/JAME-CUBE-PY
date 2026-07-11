<div align="center">

# 📖 Historia del Proyecto

> **El origen de JAME Cube y la evolución entre la versión Python y la versión Web.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge\&logo=python\&logoColor=white)
![PySide6](https://img.shields.io/badge/PySide6-6.5+-41CD52?style=for-the-badge\&logo=qt\&logoColor=white)
![Cube](https://img.shields.io/badge/Cubes-2x2%20%7C%203x3%20%7C%204x4-blue?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

</div>

---

# 🚀 Origen

Este proyecto nació originalmente como una aplicación de escritorio desarrollada en **Python**.

Su objetivo era crear un **simulador del Cubo de Rubik**, capaz de representar visualmente el estado del cubo, aplicar movimientos siguiendo la notación **WCA** y servir como base para mi cronómetro de speedcubing.

> ⚠️ Por motivos personales, esta primera versión nunca fue publicada en GitHub.

---

# 🌐 Evolución

Tiempo después decidí llevar parte de ese trabajo a la web y publiqué:

## 🔗 JAME-CUBE – Rubik's Cube Simulator

**Repositorio:**

https://github.com/JoseAngel-U1/JAME-CUBE-Rubik-s-Cube-Simulator

La versión web nació tomando como base el proyecto original en Python, pero enfocándose únicamente en el cubo **3x3**.

---

# 💻 Este repositorio

Este repositorio corresponde al proyecto original desarrollado en **Python**, el cual ahora publico con una versión mucho más completa y actualizada.

## ✨ Soporte actual

|  Cubo  |    Estado    |
| :----: | :----------: |
| 🟢 2x2 | ✅ Compatible |
| 🟢 3x3 | ✅ Compatible |
| 🟢 4x4 | ✅ Compatible |

---

## ⚡ Principales mejoras

* 🧩 Simulación completa del estado del cubo.
* 🔄 Motor de movimientos reutilizable.
* 📐 Soporte para movimientos estándar y **Wide Moves**.
* ✅ Validación completa de secuencias.
* 🎨 Renderizado mediante **PySide6**.
* 🏗️ Arquitectura modular y escalable.
* ⏱️ Base preparada para integrarse con **Timer JAME**.

---

# 🗂️ Estructura del Proyecto

```text
JAME-CUBE-PY/
├── main.py                # Punto de entrada
├── core/                  # Lógica pura, sin Qt
│   ├── constants.py       # Tamaños permitidos, colores
│   ├── cube_model.py      # Rotaciones, adyacencias, apply_basic_move
│   └── move_parser.py     # Parseo y validación de secuencias (scrambles)
└── ui/                    # Componentes gráficos (Qt)
    ├── cube_widget.py      # Renderizado del cubo
    └── main_window.py      # Ventana principal y controles
```

> La separación entre `core/` y `ui/` permite testear la lógica del cubo sin depender de PySide6, y facilita agregar un solver o generador de scrambles a futuro sin tocar la interfaz.

---

# 🔀 Relación entre ambos proyectos

| 🌐 Versión Web                      | 🖥️ Versión Python                       |
| ----------------------------------- | ---------------------------------------- |
| Enfocada únicamente en **3x3**.     | Proyecto original.                       |
| Implementación simplificada.        | Arquitectura más avanzada.               |
| Publicada primero.                  | Desarrollada primero, publicada después. |
| Ideal para usar desde el navegador. | Implementación principal del proyecto.   |
| Solo un tipo de cubo.               | Soporte para **2x2, 3x3 y 4x4**.         |

---

# 📈 Línea del tiempo

```text
🖥️ Desarrollo original en Python
              │
              │ (Nunca publicado)
              ▼
🌐 Versión Web (3x3)
              │
              ▼
🚀 Publicación del proyecto original
        Python + PySide6
      (2x2 • 3x3 • 4x4)
```
---

# 🛠️ Requisitos e Instalación

```bash
git clone https://github.com/JoseAngel-U1/JAME-CUBE-PY.git
cd JAME-CUBE-PY
pip install PySide6
```

---

# ▶️ Cómo ejecutar

```bash
python main.py
```

---

<div align="center">

### ❤️ Ambos repositorios forman parte de la evolución del mismo proyecto.

**La versión web nació inspirada en esta implementación de Python, mientras que este repositorio continúa siendo la implementación principal donde se desarrollan las nuevas funcionalidades.**

</div>
