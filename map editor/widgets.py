from PyQt6.QtGui import QMouseEvent
from config import *
import model

class Button(QPushButton):
    """
        A simple button. Accepts a label and can be connected to
        a callback function.
    """

    def __init__(self, label: str, checkable: bool = False):
        """
            Initialize the button.

            Parameters:

                label: The text to display on the button.
                checkable: Whether the button can be held down.
        """

        super().__init__(label)
        self.setCheckable(checkable)

class BrushView(QWidget):
    """
        Shows the currently selected object for the mouse
    """


    def __init__(
            self,
            object_descriptors: dict[int, model.ObjectDescriptor],
            callback,
            current_brush: int):
        """
            Initialize the view.

            Parameters:

                parent: the editor program
        """

        super().__init__()

        self._layout = QHBoxLayout()
        self.setLayout(self._layout)

        self._callback = callback

        label = QLabel("Object:")
        selector = QComboBox()
        self.object_types = [i for i in range(OBJECT_TYPE_COUNT)]
        selector.addItems([object_descriptors[i]._name for i in self.object_types])
        selector.setCurrentIndex(current_brush)

        selector.currentIndexChanged.connect(self.index_changed)
        
        self._layout.addWidget(label)
        self._layout.addWidget(selector)
    
    def index_changed(self, new_index: int) -> None:

        self._callback(self.object_types[new_index])

class MainView(QWidget):
    """
        A view into the main content.
    """
    SNAP_SIZE = 16

    def __init__(self, parent):
        """
            Initialize the view.

            Parameters:

                parent: The main editor program.
        """

        super().__init__()

        self._width = MAIN_PANEL_WIDTH
        self._height = MAIN_PANEL_HEIGHT

        self.setFixedSize(QSize(self._width, self._height))

        self._color = QColor(64, 128, 192)
        self._parent = parent
        self.camera_pos = QPointF(0.0, 0.0)
        icon_size = 32

        self.move_icons = {
            CAMERA_MOVE_LEFT: {
                "dst_rect": QRect(
                    MAIN_PANEL_WIDTH - 3 * icon_size,
                    MAIN_PANEL_HEIGHT - 2 * icon_size,
                    icon_size, icon_size),
                "pixmap": QPixmap("gfx/left-arrow.png", "png"),
                "src_rect": QRect(0, 0, 512, 512)
            },
            CAMERA_MOVE_RIGHT: {
                "dst_rect": QRect(
                    MAIN_PANEL_WIDTH - icon_size, 
                    MAIN_PANEL_HEIGHT - 2 * icon_size, 
                    icon_size, icon_size),
                "pixmap": QPixmap("gfx/right-arrow.png", "png"),
                "src_rect": QRect(0, 0, 512, 512)
            },
            CAMERA_MOVE_UP: {
                "dst_rect": QRect(
                    MAIN_PANEL_WIDTH - 2 * icon_size, 
                    MAIN_PANEL_HEIGHT - 3 * icon_size,
                    icon_size, icon_size),
                "pixmap": QPixmap("gfx/up-arrow.png", "png"),
                "src_rect": QRect(0, 0, 512, 512)
            },
            CAMERA_MOVE_DOWN: {
                "dst_rect": QRect(
                    MAIN_PANEL_WIDTH - 2 * icon_size, 
                    MAIN_PANEL_HEIGHT - icon_size, 
                    icon_size, icon_size),
                "pixmap": QPixmap("gfx/down-arrow.png", "png"),
                "src_rect": QRect(0, 0, 512, 512)
            }
        }

        self.cursor_world_pos = QPointF()
        self.cursor_world_pos_snapped = QPointF()
        self.setMouseTracking(True)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """
            Intercepts a click and
            passes the event along to the parent to handle.
        """

        screen_pos = event.pos()

        self.cursor_world_pos = self.screen_to_world(screen_pos)
        self.cursor_world_pos_snapped = \
            self.get_world_pos_snapped(self.cursor_world_pos)
        
        for movement, icon in self.move_icons.items():
            rect: QRect = icon["dst_rect"]
            if rect.contains(screen_pos):
                self._move_camera(movement)
                self.repaint()
                return

        self._parent.click(screen_pos, event)
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:

        screen_pos = event.pos()
        self.cursor_world_pos = self.screen_to_world(screen_pos)
        self.cursor_world_pos_snapped = \
            self.get_world_pos_snapped(self.cursor_world_pos)
        self.repaint()
    
    def _move_camera(self, movement: int) -> None:

        dx = 0.0
        dy = 0.0

        if movement == CAMERA_MOVE_LEFT:
            dx = -2 * MainView.SNAP_SIZE
        elif movement == CAMERA_MOVE_RIGHT:
            dx = 2 * MainView.SNAP_SIZE
        elif movement == CAMERA_MOVE_UP:
            dy = -2 * MainView.SNAP_SIZE
        elif movement == CAMERA_MOVE_DOWN:
            dy = 2 * MainView.SNAP_SIZE
        
        self.camera_pos.setX(self.camera_pos.x() + dx)
        self.camera_pos.setY(self.camera_pos.y() + dy)

    def _draw_grid(self, painter: QPainter) -> None:

        x = 0
        while x < MAIN_PANEL_WIDTH:
            point_a = QPoint(x, 0)
            point_b = QPoint(x, MAIN_PANEL_HEIGHT)
            painter.drawLine(point_a, point_b)
            x += MainView.SNAP_SIZE
        y = 0
        while y < MAIN_PANEL_HEIGHT:
            point_a = QPoint(0, y)
            point_b = QPoint(MAIN_PANEL_WIDTH, y)
            painter.drawLine(point_a, point_b)
            y += MainView.SNAP_SIZE

    def _draw_object(self, painter: QPainter, obj: model.GameObject) -> None:
        
        rect = obj.rect
        top_left = self.world_to_screen(rect.topLeft())
        bottom_right = self.world_to_screen(rect.bottomRight())
        screen_rect = QRect(top_left, bottom_right)

        if not self.visible(screen_rect):
            return

        image = obj._descriptor._image
        painter.drawPixmap(screen_rect, image)
        hover = self._parent._mouse_mode == MOUSE_MODE_SELECT \
                and obj.rect.contains(self.cursor_world_pos)
        if obj.selected or hover:
            painter.setOpacity(0.5)
            painter.fillRect(screen_rect, QColor("orange"))
            painter.drawRect(screen_rect)
            painter.setOpacity(1.0)

    def _draw_mouse_accents(self, painter: QPainter) -> None:

        new = self._parent._mouse_mode == MOUSE_MODE_NEW
        edit = self._parent._mouse_mode == MOUSE_MODE_EDIT \
            and self._parent.selected_object is not None
        
        if not(new or edit):
            return

        _type = self._parent.current_brush

        x = self.world_to_screen_x(self.cursor_world_pos_snapped.x())
        y = self.world_to_screen_y(self.cursor_world_pos_snapped.y())
        descriptor: model.ObjectDescriptor = self._parent._object_descriptors[_type]
        size = descriptor.get_size()
        w = size.width()
        h = size.height()
        screen_rect = QRect(x, y, w, h)

        if not self.visible(screen_rect):
            return
        
        image = descriptor._image
        painter.setOpacity(0.5)
        painter.drawPixmap(screen_rect, image)
        painter.setOpacity(1.0)

    def paintEvent(self, event: QPaintEvent) -> None:
        """
            Refreshes the view.
        """

        objects: dict[int, list[model.GameObject]] = self._parent.objects
        
        rect = event.rect()
        painter = QPainter(self)
        painter.fillRect(rect, self._color)
        painter.setPen(QColor("black"))

        self._draw_grid(painter)

        for game_objects in objects.values():
            for obj in game_objects:
                self._draw_object(painter, obj)
        
        self._draw_mouse_accents(painter)

        cursor_screen_pos = self.world_to_screen(self.cursor_world_pos)

        for icon in self.move_icons.values():
            if icon["dst_rect"].contains(cursor_screen_pos):
                painter.fillRect(icon["dst_rect"], QColor("white"))
            painter.drawPixmap(icon["dst_rect"], icon["pixmap"], icon["src_rect"])
    
    def screen_to_world_x(self, x: int) -> float:

        return float(x + self.camera_pos.x())
    
    def screen_to_world_y(self, y: int) -> float:

        return float(y + self.camera_pos.y())
    
    def screen_to_world(self, pos: QPoint) -> QPointF:

        return QPointF(
            self.screen_to_world_x(pos.x()),
            self.screen_to_world_y(pos.y()))
    
    def world_to_screen_x(self, x: float) -> int:

        return int(x - self.camera_pos.x())
    
    def world_to_screen_y(self, y: float) -> int:

        return int(y - self.camera_pos.y())
    
    def world_to_screen(self, pos: QPointF) -> QPoint:

        return QPoint(
            self.world_to_screen_x(pos.x()),
            self.world_to_screen_y(pos.y()))

    def get_world_pos_snapped(self, pos: QPoint) -> QPointF:
        return QPointF(
            int(pos.x() / MainView.SNAP_SIZE) * MainView.SNAP_SIZE, 
            int(pos.y() / MainView.SNAP_SIZE) * MainView.SNAP_SIZE)

    def visible(self, rect: QRect) -> bool:

        return rect.x() < MAIN_PANEL_WIDTH \
            and rect.x() + rect.width() > 0 \
            and rect.top() > 0 \
            and rect.bottom() < MAIN_PANEL_HEIGHT