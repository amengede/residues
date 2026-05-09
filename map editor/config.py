import PyQt6
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, 
    QHBoxLayout, QLabel, QGridLayout, QPushButton,
    QFileDialog, QFrame, QLineEdit, QComboBox
)
from PyQt6.QtGui import (
    QAction, QPainter, QColor, QFont, QIcon, 
    QPixmap, QPalette, QMouseEvent, QPaintEvent, 
    QCursor, QMatrix4x4, QVector4D, QTransform,
    QPaintEngine, QPolygon
)
from PyQt6.QtCore import (
    QSize, QPointF, QRect, QPoint, Qt, QRectF,
    QTimer
)

import sys

import json
import math

MOUSE_MODE_SELECT = 0
MOUSE_MODE_EDIT = 1
MOUSE_MODE_NEW = 2

MAIN_PANEL_WIDTH = 640
MAIN_PANEL_HEIGHT = 480

OBJECT_TYPE_COUNT = 7
OBJECT_TYPE_NPC_OVERWORLD_DOWN = 0
OBJECT_TYPE_OVERWORLD_BUILDING = 1
OBJECT_TYPE_OVERWORLD_GRASS = 2
OBJECT_TYPE_OVERWORLD_PATH = 3
OBJECT_TYPE_OVERWORLD_PUZZLE = 4
OBJECT_TYPE_OVERWORLD_TREE = 5
OBJECT_TYPE_PC_OVERWORLD_DOWN = 6

code_lookup = {
    "npc": OBJECT_TYPE_NPC_OVERWORLD_DOWN,
    "building": OBJECT_TYPE_OVERWORLD_BUILDING,
    "grass": OBJECT_TYPE_OVERWORLD_GRASS,
    "path": OBJECT_TYPE_OVERWORLD_PATH,
    "puzzle": OBJECT_TYPE_OVERWORLD_PUZZLE,
    "tree": OBJECT_TYPE_OVERWORLD_TREE,
    "pc": OBJECT_TYPE_PC_OVERWORLD_DOWN
}

CAMERA_MOVE_LEFT = 0
CAMERA_MOVE_RIGHT = 1
CAMERA_MOVE_UP = 2
CAMERA_MOVE_DOWN = 3