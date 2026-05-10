#---- Real Engine ------------------------------------------------------------#
#region imports
import pygame as pg
import random
#endregion
#region constants
EVENT_TYPE_ANIMATION_END = 0
EVENT_TYPE_MOUSE_CLICK = 1
EVENT_TYPE_MOUSE_ENTER = 2
EVENT_TYPE_MOUSE_LEAVE = 3
OBJECT_TYPE_BUTTON = 0
OBJECT_TYPE_MODEL = 1
OBJECT_TYPE_COUNT = 2
GAME_PHASE_EXIT = -2
GAME_PHASE_NO_CHANGE = -1
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 540
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
#endregion
from image_assets import *
#region Events
class Message:
    """
        A message represents that an event has occurred.
    """

    def __init__(self, event_type: int, object_type: int, instance: any):
        """
            Initialize a new message.

            Parameters:
                event_type: code indicating the type of event which occurred.
                object_type: code indicating the type of object which triggered this event.
                instance: instance of the object which triggered this event.
        """

        self.event_type = event_type
        self.object_type = object_type
        self.instance = instance

EventQueue = list[Message]

class Observable:
    """
        An oberverable object can publish events. Observable objects can also observe
        events which have occurred (provided they are observing the objects which make them)
    """

    def __init__(self):
        """ Initialize a new observable object. """
        self._observers: list[EventQueue] = []
        self._event_queue: EventQueue = []
    
    def publish(self, event: Message) -> None:
        """
            Publish the given event to all observers.

            Parameters:
                event: Message to publish
        """

        for event_queue in self._observers:
            event_queue.append(event)
    
    def add_observer(self, event_queue: EventQueue) -> None:
        """
            Add the given event queue to this object's set of observers.

            Parameters:
                event_queue: observer to add.
        """
        
        self._observers.append(event_queue)
    
    def get_events(self) -> EventQueue:
        """
            Return the list of events which have occurred.
        """

        return self._event_queue
    
    def clear_events(self) -> None:
        """
            Clear the list of events, indicating they have all
            been either handled or ignored.
        """

        self._event_queue.clear()
#endregion
#region Timers
class Timer:
    """Counts down a number of frames."""

    def __init__(self, duration: int):
        self._duration = duration
    
    def update(self) -> None:
        self._duration = max(0, self._duration - 1)
    
    def is_ellapsed(self) -> bool:
        return self._duration == 0
#endregion
#region Audio
SFX = pg.mixer.Sound
class AudioPlayer(Observable):
    """
        Basic Audio system. Can play music tracks on loop and one-off sound effects.
    """

    def __init__(self):
        """
            Initialize the Audio Player. There should only be one Audio Player
            for the lifetime of the program, otherwise bad things *may* happen.
        """
        super().__init__()
        pg.mixer.init()
        pg.mixer.set_num_channels(32)
        self._current_music: SFX | None = None
        self._sfx: dict[int, dict[int, list[SFX]]] = {}
        self._tracks: dict[str, SFX] = {}
        
    def load_sfx(self, object_type: int,
                 event_type: int,
                 filename: str, gain: float = 1.0) -> None:
        """
            Load a sound effect. Sound effects are associated with a specific
            object and event.

            Parameters:
                object_type: object to associate this sound effect with.
                event_type: event to associate ths sound effect with.
                filename: name of file to load, must be wav, 16 bit signed, 44100 Hz
        """
        
        if not object_type in self._sfx:
            self._sfx[object_type] = {}
        sound_board = self._sfx[object_type]
        sound = pg.mixer.Sound(filename)
        sound.set_volume(gain)
        if event_type not in sound_board:
            sound_board[event_type] = []
        sound_board[event_type].append(sound)
    
    def clear_all(self) -> None:
        """
            Unload all sfx and music
        """

        for soundboard in self._sfx.values():
            for sounds in soundboard.values():
                for sound in sounds:
                    sound.stop()
                sounds.clear()

    def unload_sfx(self, object_type: int, event_type: int) -> None:
        """
            Unload the sound for the given object and event.
        """

        if object_type not in self._sfx:
            return
        
        sound_board = self._sfx[object_type]
        if event_type not in sound_board:
            return
        sound = sound_board[event_type]
        sound.stop()
        sound_board.pop(event_type)

    def load_track(self, track_name: str, filename: str) -> None:
        """
            Load a music track. Tracks are associated with a name.

            Parameters:
                track_name: name of the track.
                filename: name of file to load, must be wav, 16 bit signed, 44100 Hz
        """

        track = pg.mixer.Sound(filename)
        track.set_volume(0.75)
        self._tracks[track_name] = track

    def unload_track(self, track_name: str) -> None:
        """
            Unload the track with the given name.
        """
        
        if track_name not in self._tracks:
            return
        
        track = self._tracks[track_name]
        track.stop()
        self._tracks.pop(track_name)

    def update(self) -> None:
        """
            Check for any events which would trigger sfx to play
        """
        
        for event in self.get_events():
            if event.object_type not in self._sfx:
                continue
            sound_board = self._sfx[event.object_type]
            if event.event_type not in sound_board:
                continue
            if len(sound_board[event.event_type]) == 0:
                continue
            sound = random.choice(sound_board[event.event_type])
            sound.play()
        self.clear_events()

    def start_music(self, track_name: str) -> None:
        """
            Try to play the given track name (on loop)
        """
        
        if track_name not in self._tracks:
            print(f"Unknown track: {track_name}")
            return
        
        if not self._current_music is None:
            self._current_music.stop()
        
        self._current_music = self._tracks[track_name]
        self._current_music.play(-1)

    def stop_music(self) -> None:
        """
            Try to stop the currently playing music
        """

        if self._current_music is None:
            return
        
        self._current_music.stop()
        self._current_music = None
#endregion
#region Model
class Rectangle:
    """
        A general rectangle.
    """

    def __init__(self, x: int, y: int, width: int, height: int):
        """
            Initialize a new Rectangle

            Parameters:
                x: x coordinate of rectangle's centre
                y: y coordinate of rectangle's centre
                width: width of rectangle
                height: height of rectangle
        """

        self._x = x
        self._y = y
        self._half_width = width / 2
        self._half_height = height / 2
    
    def get_x(self) -> int:
        """
            Returns the rectangle's center x coordinate.
        """
        return self._x

    def get_y(self) -> int:
        """
            Returns the rectangle's center y coordinate.
        """
        return self._y
    
    def get_half_width(self) -> int:
        """
            Returns the Rectangle's half-width
        """
        return self._half_width

    def get_half_height(self) -> int:
        """
            Returns the Rectangle's half-height
        """
        return self._half_height

    def move_by(self, dx: int, dy: int) -> None:
        """
            Move the Rectangle by the given amount.

            Parameters:
                dx: x component of movement
                dy: y component of movement
        """

        self._x += dx
        self._y += dy
    
    def move_to(self, x: int, y: int) -> None:
        """
            Move the Rectangle to the given position.

            Parameters:
                x: new x coordinate for centre
                y: new y coordinate for centre
        """

        self._x = x
        self._y = y

    def overlaps(self, other: "Rectangle") -> bool:
        """
            Returns whether this Rectangle overlaps with the other one.
        """

        this_left = self._x - self._half_width
        other_right = other._x + other._half_width
        if this_left > other_right:
            return False
        
        this_right = self._x + self._half_width
        other_left = other._x - other._half_width
        if this_right < other_left:
            return False
        
        this_top = self._y - self._half_height
        other_bottom = other._y + other._half_height
        if this_top > other_bottom:
            return False
        
        this_bottom = self._y + self._half_height
        other_top = other._y - other._half_height
        if this_bottom < other_top:
            return False
        
        return True

    def contains(self, x: int, y: int) -> bool:
        """
            Returns whether this Rectangle contains the given point.
        """

        left = self._x - self._half_width
        right = self._x + self._half_width
        top = self._y - self._half_height
        bottom = self._y + self._half_height

        return (x < right and x > left and y > top and y < bottom)

class Entity(Rectangle):
    """
        A visible object in the game world.
    """

    def __init__(self, x: int, y: int, width: int, height: int, object_type: int):
        """
            Initialize a new entity.

            Parameters:
                x,y: coordinates of Entity's centre
                width, height: total size of Entity, in pixels
                object_type: code representing type of game object
        """

        super().__init__(x, y, width, height)
        self._object_type = object_type
    
    def get_object_type(self) -> int:
        """
            Return's this Entity's object type.
        """

        return self._object_type
    
    def get_draw_rect_data(self) -> list[int]:
        """
            Returns a bundle of data used to draw a rect around this entity.
        """

        return [self._x - self._half_width, self._y - self._half_height,
                2 * self._half_width, 2 * self._half_height]

class AnimatedEntity(Entity, Observable):
    """
        Represents an animated game object.
    """

    def __init__(self, x: int, y: int, width: int, height: int,
                 object_type: int, animation_type: int):
        """
            Initialize a new animated entity.

            Parameters:
                x,y: coordinates of Entity's centre
                width, height: total size of Entity, in pixels
                object_type: code representing type of game object
                animation: Animation to apply to the object
        """

        Entity.__init__(self, x, y, width, height, object_type)
        Observable.__init__(self)
        self._state = animation_type
        self._frame_number = 0.0
        self._spritesheets = ANIMATION_DESCRIPTORS[object_type]
        spritesheet = self._spritesheets[animation_type]
        self._frame_count = spritesheet["image_count"]
        self._mirror = False
    
    def set_frame(self, frame_number: int):
        self._frame_number = frame_number % self._frame_count
    
    def get_state(self) -> int:
        """
            Returns the current state
        """

        return self._state
    
    def set_state(self, animation_type: int) -> None:
        """
            Sets the entity's animation.

            Parameters:
                animation: new animation to apply
        """

        self._state = animation_type
        self._frame_number = 0.0
        spritesheet = self._spritesheets[animation_type]
        self._frame_count = spritesheet["image_count"]
    
    def should_mirror(self) -> bool:
        return self._mirror

    def set_mirror(self, mirror: bool) -> None:
        self._mirror = mirror
    
    def update(self, rate: float) -> None:
        """
            progress the animation by the given amount.

            Parameters:
                rate: animation speed, supports decimals
        """

        self._frame_number += rate
        if self._frame_number >= self._frame_count:
            event = Message(EVENT_TYPE_ANIMATION_END, self._object_type, self)
            self.publish(event)
            self._frame_number -= self._frame_count
    
    def get_frame_number(self) -> int:
        """
            Returns object's current frame number as a whole number.
        """

        return int(self._frame_number)

class Button(Entity, Observable):
    """
        Represents a button.
    """

    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        """
            Initialize a new button.

            Parameters:
                x,y: coordinates of button's centre
                width, height: total size of button, in pixels
                text: label for the button
        """

        Entity.__init__(self, x, y, width, height,
                        object_type = OBJECT_TYPE_BUTTON)
        Observable.__init__(self)
        self._text = text
        self._active = False
    
    def is_active(self) -> bool:
        """
            Returns whether the button is active
        """

        return self._active

    def update(self, mouse_x: int, mouse_y: int) -> None:
        """
            update the button

            Parameters:
                mouse_x: current x coordinate of mouse
                mouse_y: current y coordinate of mouse
        """

        now_active = self.contains(mouse_x, mouse_y)
        if (now_active ^ self._active):
            event_type = EVENT_TYPE_MOUSE_ENTER if self._active else EVENT_TYPE_MOUSE_LEAVE
            event = Message(event_type, OBJECT_TYPE_BUTTON, self)
            self.publish(event)
            self._active = now_active

        if self._active:
            for event in self.get_events():
                if event.event_type != EVENT_TYPE_MOUSE_CLICK:
                    continue
                event = Message(EVENT_TYPE_MOUSE_CLICK, OBJECT_TYPE_BUTTON, self)
                self.publish(event)
                break
        self.clear_events()

class BVHNode(Rectangle):
    """
        Bounding Box which can hold Rectangles.
    """

    def __init__(self):
        """Initialize a new bounding box"""
        super().__init__(x = 0, y = 0, width=-1e30, height=-1e30)
        self._children: list[Rectangle] = []
        self._external = True
    
    def add(self, other: Rectangle) -> None:
        """
            Add a rectangle to this node, growing so the other rectangle fits
            tightly inside.
        """

        left = min(self._x - self._half_width, other._x - other._half_width)
        right = max(self._x + self._half_width, other._x + other._half_width)
        top = min(self._y - self._half_height, other._y - other._half_height)
        bottom = max(self._y + self._half_height, other._y + other._half_height)

        self._x = (left + right) / 2
        self._y = (top + bottom) / 2
        self._half_width = (right - left) / 2
        self._half_height = (bottom - top) / 2

        self._children.append(other)
    
    def split(self, allocator: "EntityGroup") -> None:
        """
            Attempt to split the node into children.
        """

        if len(self._children) < 2:
            self._external = True
            return
        
        if self._half_width > self._half_height:
            self._horizontal_split(allocator)
        else:
            self._vertical_split(allocator)
    
    def _horizontal_split(self, allocator: "EntityGroup") -> None:
        """
            Split this node horizontally.
        """

        # buckets
        left_children = []
        right_children = []

        # throw children into buckets
        for child in self._children:
            if child._x < self._x:
                left_children.append(child)
            else:
                right_children.append(child)
        
        # did they all go into one bucket?
        if len(left_children) == 0 or len(right_children) == 0:
            self._external = True
            return
        
        # we can actually split
        left_node = allocator.allocate_node()
        for child in left_children:
            left_node.add(child)
        left_node.split(allocator)
        right_node = allocator.allocate_node()
        for child in right_children:
            right_node.add(child)
        right_node.split(allocator)

        self._external = False
        self._children = [left_node, right_node]
    
    def _vertical_split(self, allocator: "EntityGroup") -> None:
        """
            Split this node vertically.
        """

        # buckets
        top_children = []
        bottom_children = []

        # throw children into buckets
        for child in self._children:
            if child._y < self._y:
                top_children.append(child)
            else:
                bottom_children.append(child)
        
        # did they all go into one bucket?
        if len(top_children) == 0 or len(bottom_children) == 0:
            self._external = True
            return
        
        # we can actually split
        top_node = allocator.allocate_node()
        for child in top_children:
            top_node.add(child)
        top_node.split(allocator)
        bottom_node = allocator.allocate_node()
        for child in bottom_children:
            bottom_node.add(child)
        bottom_node.split(allocator)

        self._external = False
        self._children = [top_node, bottom_node]

    def is_external(self) -> bool:
        """
            Returns whether this node is external.
        """

        return self._external

    def get_children(self) -> list[Rectangle]:
        """
            Returns the node's children.
        """

        return self._children

class EntityGroup:
    """
        A group of Entities, collision checks within this group should be quite fast.
    """

    def __init__(self):
        """
            Initialize a new Entity Group.
        """

        self._rectangles: list[Rectangle] = []
        self._nodes: tuple[BVHNode] = None
        self._used_nodes = 0
        self._rectangle_count = 0
        self._root_node = BVHNode()
        self._dirty = False
    
    def allocate_node(self) -> BVHNode:
        """
            Allocate a new node from the group's store.
        """

        if self._used_nodes == len(self._nodes):
            return BVHNode()

        self._used_nodes += 1
        return self._nodes[self._used_nodes - 1]
    
    def add(self, rectangle: Rectangle) -> None:
        """
            Add a new rectangle. Group must be rebuilt before this takes effect.

            Parameters:
                rectangle: Rectangle to add.
        """

        if self._rectangle_count < len(self._rectangles):
            self._rectangles[self._rectangle_count] = rectangle
        else:
            self._rectangles.append(rectangle)
        self._rectangle_count += 1
        self._dirty = True
    
    def remove(self, index: int) -> None:
        """
            Remove the rectangle at the given index.
            Group must be rebuilt before this takes effect.

            Parameters:
                index: index of Rectangle to remove.
        """

        self._rectangle_count -= 1
        self._rectangles[index] = self._rectangles[self._rectangle_count]
        self._dirty = True
    
    def update(self):
        if not self._dirty:
            return
        
        self.rebuild()
        self._dirty = False
    
    def rebuild(self) -> None:
        """
            Rebuild the BVH.
        """

        if self._rectangle_count == 0:
            return
        
        self._nodes = tuple(BVHNode() for _ in range(2 * self._rectangle_count - 1))
        self._used_nodes = 0
        self._root_node = self.allocate_node()
        for i in range(self._rectangle_count):
            self._root_node.add(self._rectangles[i])
        self._root_node.split(self)
    
    def get_members(self) -> list[Rectangle]:
        """
            Returns all the active members of the group.
        """

        return self._rectangles[:self._rectangle_count]

    def overlaps(self, other: Rectangle) -> bool:
        """
            Returns whether any member of this group overlaps with the given rectangle.
        """

        if self._rectangle_count == 0:
            return False

        nodes: list[BVHNode] = [self._root_node]

        while len(nodes) > 0:
            
            node = nodes.pop(0)

            if not node.overlaps(other):
                continue
            
            if node.is_external():
                children: list[Rectangle] = node.get_children()
                for child in children:
                    if child.overlaps(other):
                        return True
            else:
                children: list[BVHNode] = node.get_children()
                for child in children:
                    if child.overlaps(other):
                        nodes.append(child)
        return False

    def get_overlapping(self, other: Rectangle) -> list[Rectangle]:
        """
            Returns all of the rectangles overlapping with the given one.
        """

        if self._rectangle_count == 0:
            return []

        nodes: list[BVHNode] = [self._root_node]
        overlapping: list[Rectangle] = []

        while len(nodes) > 0:
            
            node = nodes.pop(0)

            if not node.overlaps(other):
                continue
            
            if node.is_external():
                children: list[Rectangle] = node.get_children()
                for child in children:
                    if child.overlaps(other):
                        overlapping.append(child)
            else:
                children: list[BVHNode] = node.get_children()
                for child in children:
                    if child.overlaps(other):
                        nodes.append(child)
        return overlapping

    def get_internal_overlaps(self) -> list[tuple[Rectangle]]:
        """
            Returns all of the hit records, pairs of members within this group which overlap
            with one another.

            Records are double-counted, so for every (rect_1, rect_2) pair, (rect_2, rect_1) will
            also be recorded.
        """

        if self._rectangle_count == 0:
            return []

        nodes: list[BVHNode] = [self._root_node]
        overlapping: list[tuple[Rectangle]] = []

        while len(nodes) > 0:
            
            node = nodes.pop(0)

            children = node.get_children()
            child_count = len(children)

            if child_count < 2:
                continue
            
            if node.is_external():
                for child_a in children:
                    for child_b in children:
                        if child_a is child_b:
                            continue
                        if child_a.overlaps(child_b):
                            overlapping.append((child_a, child_b))
            else:
                for child in children:
                    nodes.append(child)
        return overlapping

class Model(Observable):
    """
        Abstract class representing some sort of Model class.
    """

    pass
#endregion
#region View
Surface = pg.Surface
Font = pg.font.Font
Colour = tuple[int]
class View:
    """
        A general class for drawing things.
    """

    def __init__(self, screen: Surface):
        """
            Initialize a new view.

            Parameters:
                screen: Surface to draw to
        """
        self._screen = screen
        self._font = pg.font.Font(None, 32)
        self._animations: dict[int, dict[int, list[Surface]]] = {}
        self._images: dict[int, Surface] = {}
        self._colours: dict[int, Colour] = {}
    
    def load_colour(self, object_type: int, colour: tuple[int]) -> None:
        """
            Add a colour and associate it with a given object type.

            Parameters:
                object_type: type of object this colour is meant for
                colour: colour to load
        """
        self._colours[object_type] = colour
    
    def unload_colour(self, object_type: int) -> None:
        """
            Forget about the colour for the given object type.

            Parameters:
                object_type: type of object to forget about
        """
        if object_type not in self._colours:
            return
        self._colours.pop(object_type)
    
    def load_gfx(self, object_type: int) -> None:

        if object_type in IMAGE_DESCRIPTORS:
            self._load_image(object_type)
        elif object_type in ANIMATION_DESCRIPTORS:
            self._load_animation(object_type)

    def _load_image(self, object_type: int) -> None:
        """
            Load an image and associate it with a given object type.

            Parameters:
                object_type: type of object to load image for
        """
        descriptor = IMAGE_DESCRIPTORS[object_type]
        filename = descriptor["filename"]
        scale = descriptor["scale"]
        image = pg.image.load(filename).convert_alpha()
        image = pg.transform.scale_by(image, scale)
        if "flip" in descriptor:
            image = pg.transform.flip(image, True, False)
        if "angle" in descriptor:
            image = pg.transform.rotate(image, descriptor["angle"])
        self._images[object_type] = image
    
    def _unload_image(self, object_type: int) -> None:
        """
            Unload the image for the given object type

            Parameters:
                object_type: type of object to unload image for.
        """
        if object_type not in self._images:
            return
        self._images.pop(object_type)
    
    def _load_animation(self, object_type: int) -> None:
        """
            Load an animation and associate it with a given object type.

            Parameters:
                object_type: type of object to load animations for
                object_name: name of object
                animation: description of animation being loaded
                scale: scale factor to apply (default is 1.0)
        """

        if object_type not in self._animations:
            self._animations[object_type] = {}
        spritesheet = self._animations[object_type]

        spritesheet_descriptors = ANIMATION_DESCRIPTORS[object_type]
        for animation_type, descriptor in spritesheet_descriptors.items():
            images = []
            base_filename = descriptor["filename"]
            image_count = descriptor["image_count"]
            base_frame_number = descriptor["base_frame"]
            scale = descriptor["scale"]
            for i in range(image_count):
                filename = base_filename + f"{str(i + base_frame_number).zfill(3)}.png"
                image = pg.image.load(filename).convert_alpha()
                image = pg.transform.scale_by(image, scale)
                if base_frame_number == 1:
                    image.set_colorkey((0,0,0))
                images.append(image)
            spritesheet[animation_type] = images
    
    def _unload_animation(self, object_type: int, animation_type: int) -> None:
        """
            Unload a given animation for the given object type.

            Parameters:
                object_type: type of object to forget about.
                animation: description of animation being unloaded.
        """
        if object_type not in self._animations:
            return
        spritesheet = self._animations[object_type]
        if animation_type not in spritesheet:
            return
        
        spritesheet.pop(animation_type)
        if len(spritesheet) == 0:
            self._animations.pop(object_type)
    
    def _clear_screen(self, colour: Colour) -> None:
        """
            Flush the screen out with the given colour.
        """
        self._screen.fill(colour)
    
    def _draw_text(self, text: str, x: int, y: int, colour: tuple[int]) -> None:
        """
            Draw text on the screen.

            Parameters:
                text: text to draw
                x: x coordinate of top-left corner
                y: y coordinate of top-left corner
                colour: colour for text
        """
        antialias = False
        rendered_text = self._font.render(text, antialias, colour)
        self._screen.blit(source = rendered_text, dest = (x,y))

    def _draw_entity_coloured(
            self, entity: Entity, 
            cam_x: int = 0, cam_y: int = 0) -> None:
        """
            Draw an entity as a coloured rectangle.

            Paramateters:
                entity: Entity to draw
                cam_x: x coordinate to subtract from entity's position (default is no change)
                cam_y: y coordinate to subtract from entity's position (default is no change)
        """

        object_type = entity.get_object_type()
        if object_type not in self._colours:
            return
        
        colour = self._colours[object_type]
        dst_rect = entity.get_draw_rect_data()
        dst_rect[0] -= cam_x
        dst_rect[1] -= cam_y
        pg.draw.rect(self._screen, colour, dst_rect)
    
    def _draw_entity_image(
            self, entity: Entity,
            cam_x: int = 0, cam_y: int = 0,
            should_flip: bool = False) -> None:
        """
            Draw an entity with an image.

            Paramateters:
                entity: Entity to draw
                cam_x: x coordinate to subtract from entity's position (default is no change)
                cam_y: y coordinate to subtract from entity's position (default is no change)
        """

        object_type = entity.get_object_type()
        if object_type not in self._images:
            return
        
        image = self._images[object_type]
        if should_flip:
            image = pg.transform.flip(image, True, False)
        dst_rect = entity.get_draw_rect_data()
        dst_rect[0] -= cam_x
        dst_rect[1] -= cam_y
        self._screen.blit(image, dst_rect)
    
    def _draw_entity_image_overloaded(
            self, entity: Entity, object_type: int,
            cam_x: int = 0, cam_y: int = 0) -> None:
        """
            Draw an entity with an image.

            Paramateters:
                entity: Entity to draw
                cam_x: x coordinate to subtract from entity's position (default is no change)
                cam_y: y coordinate to subtract from entity's position (default is no change)
        """

        if object_type not in self._images:
            return
        
        image = self._images[object_type]
        dst_rect = entity.get_draw_rect_data()
        dst_rect[0] -= cam_x
        dst_rect[1] -= cam_y
        self._screen.blit(image, dst_rect)
    
    def _draw_animated_entity(
            self, entity: AnimatedEntity,
            cam_x: int = 0, cam_y: int = 0) -> None:
        """
            Draw an animated entity.

            Paramateters:
                entity: Entity to draw
                cam_x: x coordinate to subtract from entity's position (default is no change)
                cam_y: y coordinate to subtract from entity's position (default is no change)
        """
        
        object_type = entity.get_object_type()
        if object_type not in self._animations:
            print("Unknown object!")
            return
        
        spritesheet = self._animations[object_type]
        animation_type = entity.get_state()
        
        if animation_type not in spritesheet:
            print("Unknown animation type!")
            return
        
        sprite = spritesheet[animation_type]
        
        frame_number = entity.get_frame_number()
        if frame_number > len(sprite):
            return
        
        image = pg.transform.flip(sprite[frame_number], entity.should_mirror(), False)
        dst_rect = entity.get_draw_rect_data()
        dst_rect[0] -= cam_x
        dst_rect[1] -= cam_y
        self._screen.blit(image, dst_rect)

    def _finish_drawing(self) -> None:
        """
            Update the screen after drawing.
        """
        
        pg.display.update()
#endregion
#region Controller
Clock = pg.time.Clock
class Controller:
    """
        Coordinates messages between systems, top-level manager.
    """
    
    def __init__(self, clock: Clock):
        """
            Initialize a new Controller.

            Parameters:
                clock: Clock object used to control framerate.
        """
        self._clock = clock
        self._keys = {}
        self._mouse_pos = (0,0)
    
    def _update_world(self) -> None:
        pass

    def _draw(self) -> int:
        pass
    
    def _key_pressed(self, key: int) -> None:
        pass
    
    def _key_released(self, key: int) -> None:
        pass
    
    def _mouse_clicked(self) -> None:
        pass
    
    def _handle_held_keys(self) -> None:
        pass
    
    def _handle_events(self) -> bool:
        
        self._keys = pg.key.get_pressed()
        self._mouse_pos = pg.mouse.get_pos()

        self._handle_held_keys()
        
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return False
            if event.type == pg.MOUSEBUTTONDOWN:
                self._mouse_clicked()
                continue
            if event.type == pg.KEYDOWN:
                self._key_pressed(event.key)
                continue
            if event.type == pg.KEYUP:
                self._key_released(event.key)
                continue
        
        return True

    def run(self) -> int:

        running = True
        while running:
            
            running = self._handle_events()
            if not running:
                return GAME_PHASE_EXIT

            next_phase = self._update_world()
            if next_phase != GAME_PHASE_NO_CHANGE:
                return next_phase

            self._draw()

            self._clock.tick(60)
#endregion
#-----------------------------------------------------------------------------#