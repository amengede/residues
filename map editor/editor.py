from config import *
import widgets
import model
    
class Editor(QMainWindow):
    """
        The App.
    """


    def __init__(self):
        """
            Create the main layout, set everything up
            and make a new model.
        """

        super().__init__()
        self.setWindowTitle("Map Maker")
        self._reset_state()
        self._build_layout()
        self._build_and_connect_widgets()
        self._create_menu()
        self._new()
    
    def _create_menu(self) -> None:
        """
            Construct the file menu for the editor.
        """

        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")

        new_button = QAction("New", self)
        new_button.triggered.connect(self._new)
        file_menu.addAction(new_button)

        save_button = QAction("Save", self)
        save_button.triggered.connect(self._save)
        file_menu.addAction(save_button)

        load_button = QAction("Load", self)
        load_button.triggered.connect(self._load)
        file_menu.addAction(load_button)
    
    def _reset_state(self) -> None:
        """
            Reset any editor state, independent of model state.
        """

        self.current_brush = OBJECT_TYPE_BLOCK
        self._object_descriptors = \
            model.load_object_descriptors(
                "../levels/object_descriptions.txt")
        self.objects: dict[int, list[model.GameObject]] = {}
        self.selected_object = None
        self._mouse_mode = MOUSE_MODE_NEW

    def _build_layout(self) -> None:
        """
            Build the layout for the program.
        """

        layout = QVBoxLayout()
        
        middle_frame = QHBoxLayout()

        self._tools_frame = QVBoxLayout()
        self._content_panel = widgets.MainView(self)
        self._detail_frame = QVBoxLayout()

        middle_frame.addLayout(self._tools_frame)
        middle_frame.addWidget(
            self._content_panel, 
            alignment=Qt.AlignmentFlag.AlignTop)
        middle_frame.addLayout(self._detail_frame)

        layout.addLayout(middle_frame)
        widget = QWidget()
        widget.setLayout(layout)
        self.setCentralWidget(widget)
    
    def _build_and_connect_widgets(self) -> None:
        """
            Build the widgets for the program.
            Also, connect their actions to appropriate callbacks.
        """

        self._build_tool_widgets()
        self._build_detail_widgets()
    
    def _build_tool_widgets(self) -> None:

        mouse_options = QComboBox()
        mouse_options.addItems(["select", "edit", "new"])
        mouse_options.setCurrentIndex(self._mouse_mode)
        mouse_options.currentIndexChanged.connect(lambda i: self._set_mouse_mode(i))

        self._tools_frame.addWidget(mouse_options, alignment=Qt.AlignmentFlag.AlignTop)
    
    def _brush_type_changed(self, new_brush: int):
        self.current_brush = new_brush

    def _build_detail_widgets(self) -> None:

        while self._detail_frame.count() != 0:
            child = self._detail_frame.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._brush_view = widgets.BrushView(
            object_descriptors = self._object_descriptors,
            callback = self._brush_type_changed,
            current_brush = self.current_brush)
        self._detail_frame.addWidget(self._brush_view)

        self._detail_frame.insertStretch(-1, 1)
    
    def _new(self) -> None:
        """
            Make a new model.
        """

        self._reset_state()
        self._content_panel.repaint()
    
    def _save(self) -> None:

        filename = QFileDialog.getSaveFileName(self)
        if len(filename[0]) <= 0:
            return
        
        filename = filename[0]

        with open(filename, "w") as file:
            for objects in self.objects.values():
                for obj in objects:
                    obj.save(file)
    
    def _load(self) -> None:

        filename = QFileDialog.getOpenFileName(self)

        if len(filename[0]) <= 0:
            return

        self._reset_state()
        
        filename = filename[0]
        self.objects = model.load_game_objects(
            filename, self._object_descriptors)
        
        self._content_panel.repaint()
    
    def _set_mouse_mode(self, mode: int) -> None:
        """
            Set the editor's mouse mode to the given mode.
        """

        self._mouse_mode = mode

    def click(self, pos: QPoint, event: QMouseEvent) -> None:

        #apply grid snap
        world_pos = self._content_panel.screen_to_world(pos)
        world_pos_snapped = self._content_panel.get_world_pos_snapped(world_pos)

        object_under_click = self.object_at_pos(world_pos)

        if event.button() == Qt.MouseButton.RightButton:
            self.right_click(object_under_click)
        else:
            if self._mouse_mode == MOUSE_MODE_NEW:
                self.left_click_new(
                    object_under_click, world_pos_snapped)
            elif self._mouse_mode == MOUSE_MODE_EDIT:
                self.left_click_edit(
                    object_under_click, world_pos_snapped)
            else:
                self.left_click_select(
                    object_under_click, world_pos_snapped)
        
        self.hierarchy_click()     
        self._content_panel.repaint()

    def object_at_pos(
            self, world_pos: QPointF) -> model.GameObject | None:
        
        if self.current_brush not in self.objects:
            return None
        
        for obj in self.objects[self.current_brush]:
        
            rect = obj.rect
            x = rect.x()
            y = rect.y()
            size = rect.size()
            w = size.width()
            h = size.height()
        
            if world_pos.x() > x and world_pos.x() < x + w\
                and world_pos.y() > y and world_pos.y() < y + h:
                
                return obj
        
        return None
    
    def left_click_new(
            self, object_under_click: model.GameObject, 
            world_pos_snapped: QPointF) -> None:

        x = world_pos_snapped.x()
        y = world_pos_snapped.y()

        if not object_under_click is None:
            return
        
        if self.current_brush not in self.objects:
            self.objects[self.current_brush] = []
        
        if self.selected_object is not None:
            self.selected_object.selected = False

        descriptor = self._object_descriptors[self.current_brush]
        self.selected_object = model.GameObject(
            x, y, self.current_brush, descriptor,
            self.objects[OBJECT_TYPE_BLOCK])
        self.selected_object.selected = True
        self.objects[self.current_brush].append(self.selected_object)
    
    def left_click_edit(
            self, object_under_click: model.GameObject, 
            world_pos_snapped: QPointF) -> None:

        x = world_pos_snapped.x()
        y = world_pos_snapped.y()

        if self.selected_object is None:
            return
        
        rect = self.selected_object.rect
        rect.setX(x)
        rect.setY(y)
    
    def left_click_select(
            self, object_under_click: model.GameObject, 
            world_pos_snapped: QPointF) -> None:

        if not self.selected_object is None:
            self.selected_object.selected = False
        
        self.selected_object = object_under_click
        if self.selected_object:
            self.selected_object.selected = True
    
    def right_click(
            self, object_under_click: model.GameObject) -> None:

        #delete
        if (object_under_click is not None 
            and self.current_brush in self.objects
            and object_under_click in self.objects[self.current_brush]):
            self.objects[self.current_brush].remove(object_under_click)
        #deselect
        if self.selected_object is not None:
            self.selected_object.selected = False
        self.selected_object = None
    
    def hierarchy_click(self):

        while self._detail_frame.count() != 0:
            child = self._detail_frame.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self._brush_view = widgets.BrushView(
            object_descriptors = self._object_descriptors,
            callback = self._brush_type_changed,
            current_brush = self.current_brush)
        self._detail_frame.addWidget(self._brush_view)

        self._detail_frame.insertStretch(-1, 1)

if __name__ == "__main__":

    app = QApplication(sys.argv)

    window = Editor()
    window.show()

    app.exec()