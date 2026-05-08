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

OBJECT_TYPE_COUNT = 14
OBJECT_TYPE_ALICE = 0
OBJECT_TYPE_ZOMBIE = 1
OBJECT_TYPE_GRIM = 2
OBJECT_TYPE_BLOCK = 3
OBJECT_TYPE_COIN = 4
OBJECT_TYPE_HEALTH = 5
OBJECT_TYPE_SPIKE_UP = 6
OBJECT_TYPE_SPIKE_DOWN = 7
OBJECT_TYPE_SPIKE_LEFT = 8
OBJECT_TYPE_SPIKE_RIGHT = 9
OBJECT_TYPE_WATER = 10
OBJECT_TYPE_MUSHROOM = 11
OBJECT_TYPE_LADDER = 12
OBJECT_TYPE_RESTRICTED = 13

code_lookup = {
    "alice": OBJECT_TYPE_ALICE,
    "zombie": OBJECT_TYPE_ZOMBIE,
    "grim": OBJECT_TYPE_GRIM,
    "block": OBJECT_TYPE_BLOCK,
    "coin": OBJECT_TYPE_COIN,
    "health": OBJECT_TYPE_HEALTH,
    "spike_up": OBJECT_TYPE_SPIKE_UP,
    "spike_down": OBJECT_TYPE_SPIKE_DOWN,
    "spike_left": OBJECT_TYPE_SPIKE_LEFT,
    "spike_right": OBJECT_TYPE_SPIKE_RIGHT,
    "water": OBJECT_TYPE_WATER,
    "mushroom": OBJECT_TYPE_MUSHROOM,
    "ladder": OBJECT_TYPE_LADDER,
    "restricted": OBJECT_TYPE_RESTRICTED
}

CAMERA_MOVE_LEFT = 0
CAMERA_MOVE_RIGHT = 1
CAMERA_MOVE_UP = 2
CAMERA_MOVE_DOWN = 3