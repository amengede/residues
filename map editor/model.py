from config import *

class ObjectDescriptor:
    """
        Describes a general object
    """

    def __init__(
            self, name: str, scale: float,
            image_filename: str, sits_on_ground: bool):

        self._name = name
        self._scale = scale
        self._sits_on_ground = sits_on_ground
        image = QPixmap(image_filename)
        transform = QTransform.fromScale(scale, scale)
        self._image = image.transformed(transform)
    
    def get_size(self) -> QSize:

        return self._image.size()

class GameObject:


    def __init__(
            self, x: float, y: float, _type: int, 
            _descriptor: ObjectDescriptor, 
            _ground_blocks: list["GameObject"]):

        size = _descriptor.get_size()
        self.rect = QRectF(x, y, float(size.width()), float(size.height()))
        self._type = _type
        self.selected = False

        if _descriptor._sits_on_ground:
            self.place_on_ground(_ground_blocks)
        
        self._descriptor = _descriptor
    
    def place_on_ground(self, _ground_blocks: list["GameObject"]) -> None:

        for block in _ground_blocks:
            if self.overlaps(block):
                x = self.rect.x()
                y = block.rect.y() - self.rect.height()
                w = self.rect.width()
                h = self.rect.height()
                self.rect = QRectF(x, y, w, h)
                #self.rect.setY(block.rect.y() - self.rect.height())
                return
    
    def overlaps(self, other: "GameObject") -> bool:

        this_left = self.rect.x()
        other_right = other.rect.x() + other.rect.width()
        if this_left > other_right:
            return False
        
        this_right = self.rect.x() + self.rect.width()
        other_left = other.rect.x()
        if this_right < other_left:
            return False
        
        this_top = self.rect.y()
        other_bottom = other.rect.y() + other.rect.height()
        if this_top > other_bottom:
            return False
        
        this_bottom = self.rect.y() + self.rect.height()
        other_top = other.rect.y()
        if this_bottom < other_top:
            return False
        
        return True
    
    def save(self, file) -> None:

        file.write(f"{self._descriptor._name} {self.rect.x()} {self.rect.y()}\n")

def load_game_objects(
        filename: str, 
        object_descriptors: dict[int, ObjectDescriptor]) -> dict[int, list[GameObject]]:

    objects = {}

    with open(filename, "r") as file:
        while line := file.readline():

            line = line.replace("\n", "")
            words = line.split(" ")

            if len(words) < 3:
                continue

            name = words[0]
            if name not in code_lookup:
                continue

            code = code_lookup[name]
            if code not in object_descriptors:
                continue
            x = float(words[1])
            y = float(words[2])
            descriptor = object_descriptors[code]

            if code not in objects:
                objects[code] = []
            
            objects[code].append(GameObject(x, y, code, descriptor, []))
    
    return objects

def load_object_descriptors(filename: str) -> dict[int, ObjectDescriptor]:
    
    descriptors = {}

    with open(filename, "r") as file:
        while line := file.readline():

            line = line.replace("\n", "")
            words = line.split(" ")

            if len(words) < 3:
                continue

            name = words[0]
            if name not in code_lookup:
                continue

            code = code_lookup[name]
            scale = float(words[1])
            filepath = words[2]
            sits_on_ground = False

            descriptors[code] = ObjectDescriptor(
                name, scale, filepath, sits_on_ground)
        
    return descriptors
