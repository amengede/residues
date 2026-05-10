from support import *
import math
import random

#region constants
EVENT_TYPE_ATTACK = 5
EVENT_TYPE_DIE = 6
EVENT_TYPE_HURT = 7
EVENT_TYPE_LOW_HEALTH = 8
EVENT_TYPE_START_TURN = 9
EVENT_TYPE_MACHINE_TICK = 10
EVENT_TYPE_GUI_NAVIGATE = 11
EVENT_TYPE_ICE_SPELL = 12
EVENT_TYPE_FIRE_SPELL = 13
EVENT_TYPE_LIGHTNING_SPELL = 14
EVENT_TYPE_STEP_PATH = 15
EVENT_TYPE_STEP_DIRT = 16
EVENT_TYPE_MACHINE_RESET = 17
EVENT_TYPE_DIALOGUE_TICK = 18

GAME_PHASE_LOGO = 0
GAME_PHASE_MENU = 1
GAME_PHASE_OVERWORLD = 2
GAME_PHASE_BATTLE = 3
GAME_PHASE_CONSOLE = 4
#endregion
#region setup
pg.init()
audio_system = AudioPlayer()
screen = pg.display.set_mode(SCREEN_SIZE)
clock = pg.time.Clock()
#endregion
#region Logo Phase
class LogoModel(Model):
    FPS_25 = 25.0 / 60.0
    FRAME_PAUSE = 120

    def __init__(self):
        super().__init__()
        self._gfx_objects: list[int] = []
        self._make_objects()
        self.timeout = None
    
    def _make_objects(self):

        self._gfx_objects.append(OBJECT_TYPE_LOGO)

        self._logo = AnimatedEntity(
            x = SCREEN_WIDTH // 2,
            y = SCREEN_HEIGHT // 2,
            width = SCREEN_WIDTH,
            height = SCREEN_HEIGHT,
            object_type = OBJECT_TYPE_LOGO,
            animation_type = ANIMATION_TYPE_IDLE)
        
        self._logo.add_observer(self._event_queue)
    
    def get_gfx_objects(self) -> list[int]:
        return self._gfx_objects

    def get_logo(self) -> AnimatedEntity:
        return self._logo
    
    def update(self) -> int:

        if self.timeout is None:
            self._logo.update(self.FPS_25)

        for event in self.get_events():
            if event.event_type == EVENT_TYPE_ANIMATION_END:
                self._logo.set_frame(-1)
                self.timeout = Timer(duration=self.FRAME_PAUSE)
        self.clear_events()

        if self.timeout is None:
            return GAME_PHASE_NO_CHANGE
        
        self.timeout.update()
        
        return (GAME_PHASE_MENU 
                if self.timeout.is_ellapsed() 
                else GAME_PHASE_NO_CHANGE)

class LogoView(View):

    def load_gfx_objects(self,
        gfx_objects: list[int]) -> None:

        for object_type in gfx_objects:
            self.load_gfx(object_type)
    
    def draw(self, logo: AnimatedEntity) -> None:

        self._draw_animated_entity(logo)
        self._finish_drawing()

class LogoController(Controller):

    def __init__(self, clock: Clock, screen: Surface):
        super().__init__(clock)
        self._model = LogoModel()
        self._view = LogoView(screen)
        self._view.load_gfx_objects(
            self._model.get_gfx_objects())
        self._load_music()
        self._skip = False
    
    def _load_music(self) -> None:
        audio_system.load_track("music",
                                "music/menu.wav")
        audio_system.start_music("music")
    
    def _draw(self) -> None:
        self._view.draw(self._model.get_logo())

    def _update_world(self):
        
        if self._skip:
            return GAME_PHASE_MENU
        
        return self._model.update()

    def _key_pressed(self, key):
        self._skip = True
#endregion
#region Menu Phase
class MenuModel(Model):

    def __init__(self):
        super().__init__()
        self._gfx_objects: list[int] = []
        self._objects: dict[int, list[Entity]] = {}
        self._make_objects()

    def _make_objects(self) -> None:

        self._gfx_objects.append(OBJECT_TYPE_TITLE_SCREEN)
        background = Entity(
            x = 878, y = SCREEN_HEIGHT - 25,
            width = 1755, height = 1080,
            object_type = OBJECT_TYPE_TITLE_SCREEN)
        self._objects[OBJECT_TYPE_TITLE_SCREEN] = [background]

        self._gfx_objects.append(OBJECT_TYPE_LABEL_RESIDUES)
        title = Entity(
            x = 100, y = 50,
            width = 100, height = 50,
            object_type = OBJECT_TYPE_LABEL_RESIDUES)
        self._objects[OBJECT_TYPE_LABEL_RESIDUES] = [title]

        self._gfx_objects.append(OBJECT_TYPE_LABEL_START)
        new_button = Button(
            x = 350, y = 450,
            width = 100, height = 50,
            text = "New Game")
        new_button.add_observer(self._event_queue)
        new_button.add_observer(audio_system.get_events())
        self.add_observer(new_button.get_events())
        self._objects[OBJECT_TYPE_LABEL_START] = [new_button]

        self._gfx_objects.append(OBJECT_TYPE_LABEL_QUIT)
        quit_button = Button(
            x = 500, y = 450,
            width = 100, height = 50,
            text = "Quit")
        quit_button.add_observer(self._event_queue)
        quit_button.add_observer(audio_system.get_events())
        self.add_observer(quit_button.get_events())
        self._objects[OBJECT_TYPE_LABEL_QUIT] = [quit_button]
    
    def get_gfx_objects(self) -> dict[int, list[Entity]]:
        return self._gfx_objects
    
    def get_objects(self) -> dict[int, list[Entity]]:
        return self._objects

    def update(self, mouse_x: int, mouse_y: int) -> int:

        button: Button = self._objects[OBJECT_TYPE_LABEL_START][0]
        button.update(mouse_x, mouse_y)

        button = self._objects[OBJECT_TYPE_LABEL_QUIT][0]
        button.update(mouse_x, mouse_y)

        for event in self.get_events():
            if event.event_type == EVENT_TYPE_MOUSE_CLICK:
                button: Button = event.instance
                if not button.is_active():
                    continue
                if button._text == "New Game":
                    audio_system.stop_music()
                    return GAME_PHASE_OVERWORLD
                if button._text == "Quit":
                    audio_system.stop_music()
                    return GAME_PHASE_EXIT
        self.clear_events()

        return GAME_PHASE_NO_CHANGE
    
    def handle_click(self) -> None:
        self.publish(Message(event_type=EVENT_TYPE_MOUSE_CLICK,
                             object_type=OBJECT_TYPE_MODEL,
                             instance = self))

class MenuView(View):

    def __init__(self, screen: Surface):
        super().__init__(screen)
    
    def load_gfx_objects(self, gfx_objects: list[int]) -> None:
        
        for object_type in gfx_objects:
            self.load_gfx(object_type)
    
    def draw_button(self, button: Button, object_type: int) -> None:

        if button.is_active():
            shifted_rect = button.get_draw_rect_data()
            shifted_rect[0] -= 10
            shifted_rect[1] -= 10
            pg.draw.rect(self._screen, (0,0,0), shifted_rect)
            self._draw_entity_coloured(button, -10, -10)
        
        self._draw_entity_image_overloaded(button, object_type)
   
    def draw(self, objects: dict[int, list[Entity]]) -> None:

        self._draw_entity_image(objects[OBJECT_TYPE_TITLE_SCREEN][0])
        self._draw_entity_image(objects[OBJECT_TYPE_LABEL_RESIDUES][0])
        self.draw_button(objects[OBJECT_TYPE_LABEL_START][0],
                         OBJECT_TYPE_LABEL_START)
        self.draw_button(objects[OBJECT_TYPE_LABEL_QUIT][0],
                         OBJECT_TYPE_LABEL_QUIT)
        self._finish_drawing()

class MenuController(Controller):
    def __init__(self, clock: Clock, screen: Surface):
        super().__init__(clock)
        self._model = MenuModel()
        self._view = MenuView(screen)
        self._view.load_gfx_objects(self._model.get_gfx_objects())
        self._load_sfx()
    
    def _load_sfx(self) -> None:
        audio_system.load_sfx(
            object_type = OBJECT_TYPE_BUTTON,
            event_type = EVENT_TYPE_MOUSE_ENTER,
            filename = "sfx/click_1.wav")
        
        audio_system.load_sfx(
            object_type = OBJECT_TYPE_BUTTON,
            event_type = EVENT_TYPE_MOUSE_LEAVE,
            filename = "sfx/click_2.wav")
        
        audio_system.load_sfx(
            object_type = OBJECT_TYPE_BUTTON,
            event_type = EVENT_TYPE_MOUSE_CLICK,
            filename = "sfx/click_3.wav")
    
    def _draw(self) -> None:
        self._view.draw(self._model.get_objects())
    
    def _update_world(self) -> int:

        audio_system.update()
        
        return self._model.update(
            mouse_x = self._mouse_pos[0],
            mouse_y = self._mouse_pos[1])
    
    def _mouse_clicked(self):
        self._model.handle_click()

#endregion
#region Overworld
class Camera(Rectangle):

    def __init__(self):
        super().__init__(
            x = SCREEN_WIDTH / 2, y = SCREEN_HEIGHT / 2,
            width = SCREEN_WIDTH, height = SCREEN_HEIGHT)
        self._target = None
    
    def set_target(self, target: Entity) -> None:
        self._target = target
    
    def update(self) -> None:
        if self._target is None:
            return
        
        other_x = self._target.get_x()
        other_y = self._target.get_y()
        dx = other_x - self._x
        dy = other_y - self._y
        follow_speed = 0.05
        self._x += follow_speed * dx
        self._y += follow_speed * dy

class Player(Entity, Observable):

    FOOTSTEP_SIZE = 32

    def __init__(self, x: int, y: int):
        w = 0.25 * 212
        h = 0.25 * 268
        Entity.__init__(self, x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_PC_OVERWORLD_DOWN)
        Observable.__init__(self)
        self.x_scale = 1.0

        self._x_since_last_step = x
        self._y_since_last_step = y
        self._on_path = False
        self._on_grass = False
        self._is_blocking = True
        self._speed = 4
    
    def update(self, object_groups: dict[int, EntityGroup]) -> None:

        paths: EntityGroup = object_groups[OBJECT_TYPE_OVERWORLD_PATH]
        self._on_grass = paths.overlaps(self)

        grasses: EntityGroup = object_groups[OBJECT_TYPE_OVERWORLD_GRASS]
        self._on_grass = grasses.overlaps(self)
    
    def is_on_grass(self) -> bool:
        return self._on_grass
    
    def is_blocking(self) -> bool:
        return self._is_blocking
    
    def step(self) -> None:
        dx = self._x - self._x_since_last_step
        dy = self._y - self._y_since_last_step

        dist = math.sqrt(dx ** 2 + dy ** 2)
        if dist < self.FOOTSTEP_SIZE:
            return
        
        self._x_since_last_step = self._x
        self._y_since_last_step = self._y

        event_type = (EVENT_TYPE_STEP_PATH 
                      if self._on_path 
                      else EVENT_TYPE_STEP_DIRT)
        
        self.publish(Message(
            event_type, OBJECT_TYPE_PC_OVERWORLD_DOWN, self))
    
    def move_left(self,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self.x_scale = -1
        self._object_type = OBJECT_TYPE_PC_OVERWORLD_LEFT_RIGHT
        
        self._x -= self._speed
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_PC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self._x += self._speed
            return
        
        self.step()
    
    def move_right(self,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self.x_scale = 1
        self._object_type = OBJECT_TYPE_PC_OVERWORLD_LEFT_RIGHT
        
        self._x += self._speed
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_PC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self._x -= self._speed
            return
        
        self.step()
    
    def move_up(self,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self._object_type = OBJECT_TYPE_PC_OVERWORLD_UP
        
        self._y -= self._speed
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_PC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self._y += self._speed
            return
        
        self.step()
    
    def move_down(self,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self._object_type = OBJECT_TYPE_PC_OVERWORLD_DOWN
        
        self._y += self._speed
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_PC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self._y -= self._speed
            return
        
        self.step()

class NPC(Entity):
    LABELS = ["npc_a", "npc_b"]
    NPC_COUNT = 0

    def __init__(self, x: int, y: int):
        w = 0.25 * 192
        h = 0.25 * 320
        super().__init__(x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_NPC_OVERWORLD_DOWN)
        self.x_scale = 1.0

        self._is_blocking = True

        self.choose_direction()
        self._speed = 4
        self._label = NPC.LABELS[NPC.NPC_COUNT % len(NPC.LABELS)]
        NPC.NPC_COUNT += 1
    
    def get_label(self) -> str:
        return self._label
    
    def speak(self) -> str:
        with open(f"dialogue/{self._label}.txt", "r") as file:
            lines = file.readlines()
            return random.choice(lines)
    
    def choose_direction(self) -> None:

        self._timer = Timer(random.randint(60, 240))
        self._direction = random.randint(0, 3)
    
    def update(self, object_groups: dict[int, EntityGroup]) -> None:

        self._timer.update()

        if self._timer.is_ellapsed():
            self.choose_direction()
        
        if self._direction == 0:
            self.move_left(self._speed, object_groups)
        elif self._direction == 1:
            self.move_right(self._speed, object_groups)
        elif self._direction == 2:
            self.move_up(self._speed, object_groups)
        elif self._direction == 3:
            self.move_down(self._speed, object_groups)
    
    def is_blocking(self) -> bool:
        return self._is_blocking
    
    def move_left(self,
                  amount: float,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self.x_scale = -1
        self._object_type = OBJECT_TYPE_NPC_OVERWORLD_LEFT_RIGHT
        
        self._x -= amount
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_NPC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self.choose_direction()
            self._x += amount
            return
    
    def move_right(self,
                  amount: float,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self.x_scale = 1
        self._object_type = OBJECT_TYPE_NPC_OVERWORLD_LEFT_RIGHT
        
        self._x += amount
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_NPC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self.choose_direction()
            self._x -= amount
            return
    
    def move_up(self,
                  amount: float,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self._object_type = OBJECT_TYPE_NPC_OVERWORLD_UP
        
        self._y -= amount
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_NPC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self._y += amount
            return
    
    def move_down(self,
                  amount: float,
                  object_groups: dict[int, EntityGroup]) -> None:
        
        self._object_type = OBJECT_TYPE_NPC_OVERWORLD_DOWN
        
        self._y += amount
        can_move = True
        for object_type, object_group in object_groups.items():
            if object_type == OBJECT_TYPE_NPC_OVERWORLD_DOWN:
                continue

            for overlapping in object_group.get_overlapping(self):
                if overlapping.is_blocking():
                    can_move = False
            
            if not can_move:
                break
        
        if not can_move:
            self._y -= amount
            return

class Building(Entity):

    def __init__(self, x: int, y: int):
        w = 0.5 * 260
        h = 0.5 * 330
        super().__init__(x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_OVERWORLD_BUILDING)
        self.object_type = OBJECT_TYPE_OVERWORLD_BUILDING

        self._is_blocking = True
    
    def is_blocking(self) -> bool:
        return self._is_blocking

class Grass(Entity):

    def __init__(self, x: int, y: int):
        w = 0.125 * 301
        h = 0.125 * 341
        super().__init__(x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_OVERWORLD_GRASS)

        self._is_blocking = False
    
    def is_blocking(self) -> bool:
        return self._is_blocking
    
class Path(Entity):

    def __init__(self, x: int, y: int):
        w = 0.25 * 253
        h = 0.25 * 314
        super().__init__(x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_OVERWORLD_PATH)

        self._is_blocking = False
    
    def is_blocking(self) -> bool:
        return self._is_blocking

class Puzzle(Entity):

    def __init__(self, x: int, y: int):
        w = 0.25 * 426
        h = 0.25 * 436
        super().__init__(x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_OVERWORLD_PUZZLE)

        self._is_blocking = True
    
    def is_blocking(self) -> bool:
        return self._is_blocking

class Tree(Entity):

    def __init__(self, x: int, y: int):
        w = 0.25 * 315
        h = 0.25 * 267
        super().__init__(x = x + 0.5 * w, y = y + 0.5 * h,
                         width = w, height = h,
                         object_type = OBJECT_TYPE_OVERWORLD_TREE)

        self._is_blocking = True
    
    def is_blocking(self) -> bool:
        return self._is_blocking

class OverworldModel(Model):

    fresh = True

    def __init__(self):
        super().__init__()
        self._gfx_objects: list[int] = []
        audio_system.load_track("overworld", "music/overworld.wav")
        audio_system.start_music("overworld")
        if OverworldModel.fresh:
            self.load("levels/level_1.txt")
            self.fresh = False
        else:
            self.load("levels/temp.txt")
        
        self._dialogue_line = ""
        self._dialogue_buffer = ""
        self._speaking_npc = None
        self._timer = None
        self.add_observer(audio_system.get_events())
        self.should_compute = False
    
    def get_dialogue_buffer(self) -> str:
        return self._dialogue_buffer

    def get_speaking_npc(self) -> str:
        return self._speaking_npc
    
    def load(self, filename: str) -> None:
        self._gfx_objects.clear()
        self._object_groups: dict[int, EntityGroup] = {
            OBJECT_TYPE_NPC_OVERWORLD_DOWN: EntityGroup(),
            OBJECT_TYPE_OVERWORLD_BUILDING: EntityGroup(),
            OBJECT_TYPE_OVERWORLD_GRASS: EntityGroup(),
            OBJECT_TYPE_OVERWORLD_PATH: EntityGroup(),
            OBJECT_TYPE_OVERWORLD_PUZZLE: EntityGroup(),
            OBJECT_TYPE_OVERWORLD_TREE: EntityGroup(),
        }
        self._player = None

        self._declare_gfx(OBJECT_TYPE_NPC_A_PORTRAIT)
        self._declare_gfx(OBJECT_TYPE_NPC_B_PORTRAIT)
        
        with open(filename, "r") as file:
            while line := file.readline():
                line = line.replace("\n", "")
                words = line.split()

                if words[0] == "tree":
                    self._declare_gfx(OBJECT_TYPE_OVERWORLD_TREE)
                    self._make_tree(words)
                if words[0] == "building":
                    self._declare_gfx(OBJECT_TYPE_OVERWORLD_BUILDING)
                    self._make_building(words)
                if words[0] == "grass":
                    self._declare_gfx(OBJECT_TYPE_OVERWORLD_GRASS)
                    self._make_grass(words)
                if words[0] == "path":
                    self._declare_gfx(OBJECT_TYPE_OVERWORLD_PATH)
                    self._make_path(words)
                if words[0] == "puzzle":
                    self._declare_gfx(OBJECT_TYPE_OVERWORLD_PUZZLE)
                    self._make_puzzle(words)
                if words[0] == "npc":
                    self._declare_gfx(OBJECT_TYPE_NPC_OVERWORLD_DOWN)
                    self._declare_gfx(OBJECT_TYPE_NPC_OVERWORLD_LEFT_RIGHT)
                    self._declare_gfx(OBJECT_TYPE_NPC_OVERWORLD_UP)
                    self._make_npc(words)
                if words[0] == "pc":
                    self._declare_gfx(OBJECT_TYPE_PC_OVERWORLD_DOWN)
                    self._declare_gfx(OBJECT_TYPE_PC_OVERWORLD_LEFT_RIGHT)
                    self._declare_gfx(OBJECT_TYPE_PC_OVERWORLD_UP)
                    self._make_pc(words)
        
        for group in self._object_groups.values():
            group.rebuild()

        self._camera = Camera()
        self._camera.set_target(self._player)
        self._declare_gfx(OBJECT_TYPE_BLANK_PAGE)
        self._background = Entity(
            SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2,
            639 * 8, 191 * 8, 
            OBJECT_TYPE_BLANK_PAGE)
    
    def _declare_gfx(self, object_type: int) -> None:
        if object_type not in self._gfx_objects:
            self._gfx_objects.append(object_type)
    
    def get_gfx_objects(self) -> list[int]:
        return self._gfx_objects

    def save(self, filename: str) -> None:
        
        with open(filename, "w") as file:
            file.write(self._save_pc())

            for tree in self._object_groups[OBJECT_TYPE_OVERWORLD_TREE]\
                .get_members():
                
                file.write(self._save_tree(tree))
            
            for building in self._object_groups[OBJECT_TYPE_OVERWORLD_BUILDING]\
                .get_members():
                
                file.write(self._save_building(building))
            
            for grass in self._object_groups[OBJECT_TYPE_OVERWORLD_GRASS]\
                .get_members():
                
                file.write(self._save_grass(grass))

            for path in self._object_groups[OBJECT_TYPE_OVERWORLD_PATH]\
                .get_members():
                
                file.write(self._save_path(path))
            
            for puzzle in self._object_groups[OBJECT_TYPE_OVERWORLD_PUZZLE]\
                .get_members():
                
                file.write(self._save_puzzle(puzzle))
            
            for npc in self._object_groups[OBJECT_TYPE_NPC_OVERWORLD_DOWN]\
                .get_members():
                
                file.write(self._save_npc(npc))
    
    def _make_tree(self, words: list[str]) -> None:
        self._object_groups[OBJECT_TYPE_OVERWORLD_TREE].add(
            Tree(float(words[1]), float(words[2]))
        )
    
    def _save_tree(self, tree: Tree) -> str:
        rect = tree.get_draw_rect_data()
        return f"tree {rect[0]} {rect[1]}\n"
    
    def _make_building(self, words: list[str]) -> None:
        self._object_groups[OBJECT_TYPE_OVERWORLD_BUILDING].add(
            Building(float(words[1]), float(words[2]))
        )
    
    def _save_building(self, building: Building) -> str:
        rect = building.get_draw_rect_data()
        return f"building {rect[0]} {rect[1]}\n"
    
    def _make_grass(self, words: list[str]) -> None:
        self._object_groups[OBJECT_TYPE_OVERWORLD_GRASS].add(
            Grass(float(words[1]), float(words[2]))
        )
    
    def _save_grass(self, tree: Tree) -> str:
        rect = tree.get_draw_rect_data()
        return f"grass {rect[0]} {rect[1]}\n"

    def _make_path(self, words: list[str]) -> None:
        self._object_groups[OBJECT_TYPE_OVERWORLD_PATH].add(
            Path(float(words[1]), float(words[2]))
        )
    
    def _save_path(self, path: Path) -> str:
        rect = path.get_draw_rect_data()
        return f"path {rect[0]} {rect[1]}\n"
    
    def _make_puzzle(self, words: list[str]) -> None:
        self._object_groups[OBJECT_TYPE_OVERWORLD_PUZZLE].add(
            Puzzle(float(words[1]), float(words[2]))
        )
    
    def _save_puzzle(self, puzzle: Puzzle) -> str:
        rect = puzzle.get_draw_rect_data()
        return f"puzzle {rect[0]} {rect[1]}\n"

    def _make_npc(self, words: list[str]) -> None:
        self._object_groups[OBJECT_TYPE_NPC_OVERWORLD_DOWN].add(
            NPC(float(words[1]), float(words[2]))
        )
    
    def _save_npc(self, npc: NPC) -> list[str]:
        rect = npc.get_draw_rect_data()
        return f"npc {rect[0]} {rect[1]}\n"
    
    def _make_pc(self, words: list[str]) -> None:
        self._player = Player(float(words[1]), float(words[2]))
        self._player.add_observer(audio_system.get_events())
        self._player.add_observer(self.get_events())
    
    def _save_pc(self) -> list[str]:
        rect = self._player.get_draw_rect_data()
        return f"pc {rect[0]} {rect[1]}\n"

    def get_covered_object_groups(self) -> dict[int, EntityGroup]:
        return {
            OBJECT_TYPE_OVERWORLD_PATH: 
                self._object_groups[OBJECT_TYPE_OVERWORLD_PATH],
            OBJECT_TYPE_OVERWORLD_GRASS: 
                self._object_groups[OBJECT_TYPE_OVERWORLD_GRASS],
        }
    
    def get_covering_object_groups(self) -> dict[int, EntityGroup]:
        return {
            OBJECT_TYPE_NPC_OVERWORLD_DOWN: 
                self._object_groups[OBJECT_TYPE_NPC_OVERWORLD_DOWN],
            OBJECT_TYPE_OVERWORLD_TREE: 
                self._object_groups[OBJECT_TYPE_OVERWORLD_TREE],
            OBJECT_TYPE_OVERWORLD_PUZZLE: 
                self._object_groups[OBJECT_TYPE_OVERWORLD_PUZZLE],
            OBJECT_TYPE_OVERWORLD_BUILDING: 
                self._object_groups[OBJECT_TYPE_OVERWORLD_BUILDING],
        }
    
    def get_player(self) -> Player:
        return self._player
    
    def get_camera(self) -> Camera:
        return self._camera
    
    def get_background(self) -> Entity:
        return self._background

    def generate_encounter(self) -> None:
        
        monster_count = random.randint(1, 4)
        monster_distribution = (0,0,0,0,1,1,2)

        with open("levels/encounter.txt", "w") as file:
            for _ in range(monster_count):
                choice = random.choice(monster_distribution)
                if choice == 0:
                    file.write(self.make_demon())
                elif choice == 1:
                    file.write(self.make_ghost_archer())
                elif choice == 2:
                    file.write(self.make_mage())
    
    def make_demon(self) -> str:
        
        health = random.randint(8, 15)
        damage = random.randint(10, 18)
        return f"demon {health}/{health} {damage}\n"

    def make_ghost_archer(self) -> str:
        
        health = random.randint(20, 25)
        damage = random.randint(12, 20)
        return f"ghost_archer {health}/{health} {damage}\n"

    def make_mage(self) -> str:
        
        health = random.randint(10, 25)
        damage = random.randint(10, 20)
        return f"mage {health}/{health} {damage}\n"

    def update(self) -> int:

        if self.should_compute:
            return GAME_PHASE_CONSOLE

        for event in self.get_events():
            if (event.event_type in (EVENT_TYPE_STEP_DIRT,
                                     EVENT_TYPE_STEP_PATH)):
                if self._player.is_on_grass():
                    if (random.randint(1, 10)) > 9:
                        OverworldModel.fresh = False
                        self.save("levels/temp.txt")
                        self.generate_encounter()
                        audio_system.stop_music()
                        return GAME_PHASE_BATTLE
        self.clear_events()

        self._camera.update()

        self._player.update(self._object_groups)

        npcs = self._object_groups[OBJECT_TYPE_NPC_OVERWORLD_DOWN]
        for npc in npcs.get_members():
            npc.update(self._object_groups)
        npcs.rebuild()

        if len(self._dialogue_buffer) < len(self._dialogue_line):
            if self._timer is None:
                self._timer = Timer(4)
            elif self._timer.is_ellapsed():
                cursor = len(self._dialogue_buffer)
                self._dialogue_buffer += self._dialogue_line[cursor]
                self.publish(Message(EVENT_TYPE_DIALOGUE_TICK,
                                     OBJECT_TYPE_MODEL, self))
                self._timer = None
        elif len(self._dialogue_buffer) != 0:
            if self._timer is None:
                self._timer = Timer(180)
            elif self._timer.is_ellapsed():
                self._dialogue_buffer = ""
                self._dialogue_line = ""
                self._speaking_npc = None
                self._timer = None
        
        if self._timer is not None:
            self._timer.update()

        return GAME_PHASE_NO_CHANGE
        
    def handle_keys(self, keys: dict[int, bool]) -> None:

        if keys[pg.K_LEFT]:
            self._player.move_left(self._object_groups)
        if keys[pg.K_RIGHT]:
            self._player.move_right(self._object_groups)
        if keys[pg.K_UP]:
            self._player.move_up(self._object_groups)
        if keys[pg.K_DOWN]:
            self._player.move_down(self._object_groups)
    
    def key_pressed(self, key: int) -> None:

        if key == pg.K_SPACE:
            dx = 0
            dy = 0
            object_type = self._player.get_object_type()
            if object_type == OBJECT_TYPE_PC_OVERWORLD_DOWN:
                dy = 32
            elif object_type == OBJECT_TYPE_PC_OVERWORLD_UP:
                dy = -32
            elif self._player.x_scale > 0:
                dx = 32
            else:
                dx = -32
            
            shifted_rect = Rectangle(self._player.get_x() + dx,
                                     self._player.get_y() + dy,
                                     2 * self._player.get_half_width(),
                                     2 * self._player.get_half_height())

            overlapping = self._object_groups[
                OBJECT_TYPE_NPC_OVERWORLD_DOWN].get_overlapping(shifted_rect)
            
            if len(overlapping) > 0:
                self._dialogue_buffer = ""
                npc: NPC = overlapping[0]
                self._dialogue_line = npc.speak()
                self._speaking_npc = npc
            
            overlapping = self._object_groups[
                OBJECT_TYPE_OVERWORLD_PUZZLE].get_overlapping(shifted_rect)
            
            if len(overlapping) > 0:
                self.save("levels/temp.txt")
                self.should_compute = True

class OverworldView(View):

    def __init__(self, screen: Surface):
        super().__init__(screen)
    
    def load_gfx_objects(self, gfx_objects: list[int]) -> None:
        for object_type in gfx_objects:
            self.load_gfx(object_type)
    
    def draw(self, covered_object_groups: dict[int, EntityGroup],
             covering_object_groups: dict[int, EntityGroup],
             camera: Camera, background: Entity,
             player: Player,
             speaking_npc: NPC,
             dialogue_buffer: str) -> None:
        
        cam_x = camera.get_x() - SCREEN_WIDTH / 2
        cam_y = camera.get_y() - SCREEN_HEIGHT / 2
        self._draw_entity_image(background, cam_x, cam_y)

        covering_grass = []
        visible_set = []
        for object_type, object_group in covered_object_groups.items():
            if object_type == OBJECT_TYPE_OVERWORLD_GRASS:
                grasses = object_group.get_overlapping(camera)
                for grass in grasses:
                    if grass.get_y() > player.get_y():
                        covering_grass.append(grass)
                    else:
                        self._draw_entity_image(grass, cam_x, cam_y)
            else:
                visible_set.extend(object_group.get_overlapping(camera))
        for entity in visible_set:
            self._draw_entity_image(entity, cam_x, cam_y)
        
        should_flip = True if player.x_scale < 0 else False
        self._draw_entity_image(player, cam_x, cam_y, should_flip)

        for grass in covering_grass:
            self._draw_entity_image(grass, cam_x, cam_y)
        
        visible_set = []
        for object_type, object_group in covering_object_groups.items():
            visible_set.extend(object_group.get_overlapping(camera))
        for entity in visible_set:
            self._draw_entity_image(entity, cam_x, cam_y)
        
        if speaking_npc is not None:
            rect = [200, 430, 700, 150]
            pg.draw.rect(self._screen, (196, 196, 196), rect)
            pg.draw.rect(self._screen, (0, 0, 0), rect, 4)

            self._draw_text(dialogue_buffer, 300, 450, (0,0,0))
            
            object_type = (OBJECT_TYPE_NPC_A_PORTRAIT 
                           if speaking_npc.get_label() == "npc_a" 
                           else OBJECT_TYPE_NPC_B_PORTRAIT)
            if object_type not in self._images:
                return
        
            image = self._images[object_type]
            dst_rect = (150, 400)
            self._screen.blit(image, dst_rect)
        
        self._finish_drawing()

class OverworldController(Controller):

    def __init__(self, clock: Clock, screen: Surface):
        super().__init__(clock)
        self._load_sfx()
        self._model = OverworldModel()
        self._view = OverworldView(screen)
        self._view.load_gfx_objects(self._model.get_gfx_objects())
    
    def _load_sfx(self) -> None:
        audio_system.clear_all()
        audio_system.load_sfx(
            OBJECT_TYPE_PC_OVERWORLD_DOWN, 
            EVENT_TYPE_STEP_PATH, "sfx/step_1.wav", 4.0)
        audio_system.load_sfx(
            OBJECT_TYPE_PC_OVERWORLD_DOWN, 
            EVENT_TYPE_STEP_PATH, "sfx/step_2.wav", 4.0)
        audio_system.load_sfx(
            OBJECT_TYPE_PC_OVERWORLD_DOWN, 
            EVENT_TYPE_STEP_PATH, "sfx/step_3.wav", 4.0)
        audio_system.load_sfx(
            OBJECT_TYPE_PC_OVERWORLD_DOWN, 
            EVENT_TYPE_STEP_PATH, "sfx/step_4.wav", 4.0)
        
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL,
            EVENT_TYPE_DIALOGUE_TICK,
            "sfx/click_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL,
            EVENT_TYPE_DIALOGUE_TICK,
            "sfx/click_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL,
            EVENT_TYPE_DIALOGUE_TICK,
            "sfx/click_3.wav")
    
    def _draw(self) -> None:
        self._view.draw(
            self._model.get_covered_object_groups(), 
            self._model.get_covering_object_groups(), 
            self._model.get_camera(), 
            self._model.get_background(), 
            self._model.get_player(),
            self._model.get_speaking_npc(),
            self._model.get_dialogue_buffer())
    
    def _update_world(self) -> int:
        audio_system.update()

        return self._model.update()
    
    def _handle_held_keys(self):
        self._model.handle_keys(self._keys)
    
    def _key_pressed(self, key):
        self._model.key_pressed(key)
#endregion
#region Battle
class Actor(Observable):

    def __init__(self, name: str, health: int,
                 max_health: int, damage: int,
                 display: int, x, y):
        super().__init__()
        self._name = name
        self._health = health
        self._max_health = max_health
        self._damage = damage
        self._friendly = False
        self._display = display
        self._base_type = display
        self._dx = 0
        self.x = x
        self.y = y
        self.add_observer(audio_system.get_events())
    
    def get_display(self) -> int:
        return self._display
    
    def get_dx(self) -> float:
        return self._dx
    
    def set_dx(self, dx: float) -> None:
        self._dx = dx

    def get_name(self) -> str:
        return self._name
    
    def get_health(self) -> int:
        return self._health
    
    def get_max_health(self) -> int:
        return self._max_health
    
    def get_damage(self) -> int:
        return self._damage
    
    def hurt(self):
        pass

    def kill(self):
        pass

    def perform_attack(self):
        pass

    def start_turn(self):
        pass
    
    def take_damage(self, amount: int) -> None:
        self._health = max(0, self._health - amount)
        if self._health > 0:
            self.hurt()
        else:
            self.kill()
    
    def is_friendly(self) -> bool:
        return self._friendly
    
    def is_alive(self) -> bool:
        return self._health > 0
    
    def get_moves(self) -> list[str]:
        pass
    
    def get_base_type(self) -> int:
        return self._base_type

class Ada(Actor):

    def __init__(self, health: int, max_health: int, damage: int):
        super().__init__("Ada Lovelace", health,
                         max_health, damage, OBJECT_TYPE_ADA_IDLE, 650, 0)
        self._friendly = True
        if self._health < 15:
            self._display = OBJECT_TYPE_ADA_LOW_HEALTH
    
    def hurt(self):
        
        self._display = OBJECT_TYPE_ADA_HURT
        self.publish(Message(EVENT_TYPE_HURT,
                             OBJECT_TYPE_ADA_IDLE, self))

    def kill(self):
        self._display = OBJECT_TYPE_ADA_DEAD
        self.publish(Message(EVENT_TYPE_DIE,
                             OBJECT_TYPE_ADA_IDLE, self))

    def perform_attack(self):
        self._display = OBJECT_TYPE_ADA_ATTACK
        self.publish(Message(EVENT_TYPE_ATTACK,
                             OBJECT_TYPE_ADA_IDLE, self))

    def start_turn(self):
        
        if self._health < 15:
            self._display = OBJECT_TYPE_ADA_LOW_HEALTH
            self.publish(Message(EVENT_TYPE_LOW_HEALTH,
                                 OBJECT_TYPE_ADA_IDLE, self))
        else:
            self._display = OBJECT_TYPE_ADA_IDLE
            self.publish(Message(EVENT_TYPE_START_TURN,
                                 OBJECT_TYPE_ADA_IDLE, self))
    
    def get_moves(self) -> list[str]:
        return ["Ice Spell", "Lightning Spell", "Fire Spell"]

class Babbage(Actor):

    def __init__(self, health: int, max_health: int, damage: int):
        super().__init__("Charles Babbage", health, max_health,
                         damage, OBJECT_TYPE_BABBAGE_IDLE, 700, 100)
        self._friendly = True
        if self._health < 15:
            self._display = OBJECT_TYPE_BABBAGE_LOW_HEALTH
    
    def get_moves(self) -> list[str]:
        return ["Bash"]
    
    def hurt(self):
        
        self._display = OBJECT_TYPE_BABBAGE_HURT
        self.publish(Message(EVENT_TYPE_HURT,
                             OBJECT_TYPE_BABBAGE_IDLE, self))

    def kill(self):
        self._display = OBJECT_TYPE_BABBAGE_DEAD
        self.publish(Message(EVENT_TYPE_DIE,
                             OBJECT_TYPE_BABBAGE_IDLE, self))

    def perform_attack(self):
        self._display = OBJECT_TYPE_BABBAGE_ATTACK
        self.publish(Message(EVENT_TYPE_ATTACK,
                             OBJECT_TYPE_BABBAGE_IDLE, self))

    def start_turn(self):
        
        if self._health < 15:
            self._display = OBJECT_TYPE_BABBAGE_LOW_HEALTH
            self.publish(Message(EVENT_TYPE_LOW_HEALTH,
                                 OBJECT_TYPE_BABBAGE_IDLE, self))
        else:
            self._display = OBJECT_TYPE_BABBAGE_IDLE
            self.publish(Message(EVENT_TYPE_START_TURN,
                                 OBJECT_TYPE_BABBAGE_IDLE, self))

class Alice(Actor):

    def __init__(self, health: int, max_health: int, damage: int):
        super().__init__("Alice Liddell", health, max_health,
                         damage, OBJECT_TYPE_ALICE_IDLE, 650, 300)
        self._friendly = True
        if self._health < 15:
            self._display = OBJECT_TYPE_ALICE_LOW_HEALTH
    
    def get_moves(self) -> list[str]:
        return ["Slingshot"]
    
    def hurt(self):
        self._display = OBJECT_TYPE_ALICE_HURT
        self.publish(Message(EVENT_TYPE_HURT,
                             OBJECT_TYPE_ALICE_IDLE, self))

    def kill(self):
        self._display = OBJECT_TYPE_ALICE_DEAD
        self.publish(Message(EVENT_TYPE_DIE,
                             OBJECT_TYPE_ADA_IDLE, self))

    def perform_attack(self):
        self._display = OBJECT_TYPE_ALICE_ATTACK
        self.publish(Message(EVENT_TYPE_ATTACK,
                             OBJECT_TYPE_ALICE_IDLE, self))

    def start_turn(self):
        
        if self._health < 15:
            self._display = OBJECT_TYPE_ALICE_LOW_HEALTH
            self.publish(Message(EVENT_TYPE_LOW_HEALTH,
                                 OBJECT_TYPE_ALICE_IDLE, self))
        else:
            self._display = OBJECT_TYPE_ALICE_IDLE
            self.publish(Message(EVENT_TYPE_START_TURN,
                                 OBJECT_TYPE_ALICE_IDLE, self))

class Demon(Actor):

    def __init__(self, health: int, max_health: int, damage: int, i: int):
        super().__init__("Demon", health, max_health,
                         damage, OBJECT_TYPE_DEMON_IDLE, 100, 150 * i)
    
    def get_moves(self) -> list[str]:
        return ["Stabby Stabby"]
    
    def hurt(self):
        self._display = OBJECT_TYPE_DEMON_HURT
        self.publish(Message(EVENT_TYPE_HURT,
                             OBJECT_TYPE_DEMON_IDLE, self))

    def kill(self):
        self._display = OBJECT_TYPE_DEMON_DEAD
        self.publish(Message(EVENT_TYPE_DIE,
                             OBJECT_TYPE_DEMON_IDLE, self))

    def perform_attack(self):
        self._display = OBJECT_TYPE_DEMON_ATTACK
        self.publish(Message(EVENT_TYPE_ATTACK,
                             OBJECT_TYPE_DEMON_IDLE, self))
    
    def start_turn(self):
        self._display = OBJECT_TYPE_DEMON_IDLE

class GhostArcher(Actor):

    def __init__(self, health: int, max_health: int, damage: int, i: int):
        super().__init__("Ghost Archer", health, max_health, damage,
                         OBJECT_TYPE_GHOST_ARCHER_IDLE, 100, 150 * i)
    
    def get_moves(self) -> list[str]:
        return ["Shoot"]
    
    def hurt(self):
        self._display = OBJECT_TYPE_GHOST_ARCHER_HURT
        self.publish(Message(EVENT_TYPE_HURT,
                             OBJECT_TYPE_GHOST_ARCHER_IDLE, self))

    def kill(self):
        self._display = OBJECT_TYPE_GHOST_ARCHER_DEAD
        self.publish(Message(EVENT_TYPE_DIE,
                             OBJECT_TYPE_GHOST_ARCHER_IDLE, self))

    def perform_attack(self):
        self._display = OBJECT_TYPE_GHOST_ARCHER_ATTACK
        self.publish(Message(EVENT_TYPE_ATTACK,
                             OBJECT_TYPE_GHOST_ARCHER_IDLE, self))

    def start_turn(self):
        self._display = OBJECT_TYPE_GHOST_ARCHER_IDLE

class Mage(Actor):

    def __init__(self, health: int, max_health: int, damage: int, i: int):
        super().__init__("Mage", health, max_health,
                         damage, OBJECT_TYPE_MAGE_IDLE, 100, 150 * i)
        self._friendly = False
    
    def get_moves(self) -> list[str]:
        return ["Lightning Spell", "Ice Spell", "Fire Spell"]

    def hurt(self):
        self._display = OBJECT_TYPE_MAGE_HURT
        self.publish(Message(EVENT_TYPE_HURT,
                             OBJECT_TYPE_MAGE_IDLE, self))

    def kill(self):
        self._display = OBJECT_TYPE_MAGE_DEAD
        self.publish(Message(EVENT_TYPE_DIE,
                             OBJECT_TYPE_MAGE_IDLE, self))

    def perform_attack(self):
        self._display = OBJECT_TYPE_MAGE_ATTACK
        self.publish(Message(EVENT_TYPE_ATTACK,
                             OBJECT_TYPE_MAGE_IDLE, self))

    def start_turn(self):
        self._display = OBJECT_TYPE_MAGE_IDLE

class Encounter:

    def __init__(self):
        self._actors = []
        self._pending_actors = []
        self._current_actor_index = -1
        self._friendly_count = 0
        self._unfriendly_count = 0
    
    def add_actor(self, actor: Actor):
        if actor.is_friendly():
            self._friendly_count += 1
        else:
            self._unfriendly_count += 1
        
        self._actors.append(actor)
        self._pending_actors.append(actor)
    
    def register_death(self, actor: Actor):
        if actor.is_friendly():
            self._friendly_count -= 1
        else:
            self._unfriendly_count -= 1
    
    def choose_actor(self) -> Actor:

        for actor in self._pending_actors:
            if not actor.is_alive():
                self._pending_actors.remove(actor)
        
        if len(self._pending_actors) == 0:
            self.reshuffle()
        
        if len(self._pending_actors) == 0:
            return None
        
        actor = random.choice(self._pending_actors)
        self._pending_actors.remove(actor)
        self._current_actor_index = self._actors.index(actor)
        return actor
    
    def reshuffle(self) -> None:
        for actor in self._actors:
            if actor.is_alive():
                self._pending_actors.append(actor)

    def over(self) -> bool:
        return (self._friendly_count == 0
                or self._unfriendly_count == 0)
    
    def won(self) -> bool:
        return (self._unfriendly_count == 0
                and self._friendly_count > 0)
    
    def get_next_target(self, friendly: bool) -> Actor:
        for i in range(len(self._actors)):
            self._current_actor_index += 1
            target = self._actors[(self._current_actor_index) 
                                  % len(self._actors)]
            if (not target.is_alive()
                or target.is_friendly() != friendly):
                continue
            return target
        
    def get_previous_target(self, friendly: bool):
        for i in range(len(self._actors)):
            self._current_actor_index -= 1
            target = self._actors[(self._current_actor_index) 
                                  % len(self._actors)]
            if (not target.is_alive()
                or target.is_friendly() != friendly):
                continue
            return target
    
    def get_actors(self) -> list[Actor]:
        return self._actors

    def get_counts(self) -> tuple[int]:
        return (self._unfriendly_count, self._friendly_count)

class BattleModel(Model):

    STATE_TURN_START = 0
    STATE_SELECT_MOVE = 1
    STATE_SELECT_TARGET = 2
    STATE_ATTACK = 3
    STATE_TARGET_DAMAGED = 4
    STATE_CHOOSE_ACTOR = 5
    STATE_NO_CHANGE = 6
    
    STANDARD_DELAY = 60
    FPS_25 = 25 / 60

    def __init__(self):
        super().__init__()
        self.monster_count = 0
        self._gfx_objects: list[int] = []
        audio_system.load_track("combat", "music/combat.wav")
        audio_system.start_music("combat")
        self.load()
        self.current_actor = self._encounter.choose_actor()
        self.current_target: Actor = None
        self.current_move: str = ""
        self._target_x = 0
        self._timer = None
        self.buttons = []

        self.states = {
            self.STATE_TURN_START: {
                "enter": self.enter_turn_start,
                "update": self.update_turn_start,
                "exit": self.exit_turn_start,
            },
            self.STATE_SELECT_MOVE: {
                "enter": self.enter_select_move,
                "update": self.update_select_move,
                "exit": self.exit_select_move,
            },
            self.STATE_SELECT_TARGET: {
                "enter": self.enter_select_target,
                "update": self.update_select_target,
                "exit": self.exit_select_target,
            },
            self.STATE_ATTACK: {
                "enter": self.enter_attack,
                "update": self.update_attack,
                "exit": self.exit_attack,
            },
            self.STATE_TARGET_DAMAGED: {
                "enter": self.enter_target_damaged,
                "update": self.update_target_damaged,
                "exit": self.exit_target_damaged,
            },
            self.STATE_CHOOSE_ACTOR: {
                "enter": self.enter_choose_actor,
                "update": self.update_choose_actor,
                "exit": self.exit_choose_actor,
            },
        }
        self.state = self.STATE_CHOOSE_ACTOR
        self.states[self.state]["enter"]()

        self.animated_entities = []
        self.entities = []
        self.buttons = []
        self._encounter_over = False
        self.add_observer(audio_system.get_events())
    
    def load(self) -> None:
        #self._gfx_objects.clear()
        self._encounter = Encounter()
        self._declare_gfx(OBJECT_TYPE_LIGHTNING_BOLT)
        self._declare_gfx(OBJECT_TYPE_ICE_SPELL)
        self._declare_gfx(OBJECT_TYPE_FIRE_SPELL)
        self._declare_gfx(OBJECT_TYPE_BLANK_PAGE)
        self._background = Entity(
            0, 0,
            639 * 8, 191 * 8, 
            OBJECT_TYPE_BLANK_PAGE)
        
        with open("levels/party.txt", "r") as file:
            while line := file.readline():
                line = line.replace("\n", "")
                words = line.split()

                if words[0] == "ada":
                    self._declare_gfx(OBJECT_TYPE_ADA_ATTACK)
                    self._declare_gfx(OBJECT_TYPE_ADA_DEAD)
                    self._declare_gfx(OBJECT_TYPE_ADA_HURT)
                    self._declare_gfx(OBJECT_TYPE_ADA_IDLE)
                    self._declare_gfx(OBJECT_TYPE_ADA_LOW_HEALTH)
                    self._make_actor(words, Ada)
                if words[0] == "babbage":
                    self._declare_gfx(OBJECT_TYPE_BABBAGE_ATTACK)
                    self._declare_gfx(OBJECT_TYPE_BABBAGE_DEAD)
                    self._declare_gfx(OBJECT_TYPE_BABBAGE_HURT)
                    self._declare_gfx(OBJECT_TYPE_BABBAGE_IDLE)
                    self._declare_gfx(OBJECT_TYPE_BABBAGE_LOW_HEALTH)
                    self._make_actor(words, Babbage)
                if words[0] == "alice":
                    self._declare_gfx(OBJECT_TYPE_ALICE_ATTACK)
                    self._declare_gfx(OBJECT_TYPE_ALICE_DEAD)
                    self._declare_gfx(OBJECT_TYPE_ALICE_HURT)
                    self._declare_gfx(OBJECT_TYPE_ALICE_IDLE)
                    self._declare_gfx(OBJECT_TYPE_ALICE_LOW_HEALTH)
                    self._make_actor(words, Alice)
        
        with open("levels/encounter.txt", "r") as file:
            while line := file.readline():
                line = line.replace("\n", "")
                words = line.split()

                if words[0] == "demon":
                    self._declare_gfx(OBJECT_TYPE_DEMON_ATTACK)
                    self._declare_gfx(OBJECT_TYPE_DEMON_DEAD)
                    self._declare_gfx(OBJECT_TYPE_DEMON_HURT)
                    self._declare_gfx(OBJECT_TYPE_DEMON_IDLE)
                    self._make_actor(words, Demon)
                if words[0] == "ghost_archer":
                    self._declare_gfx(OBJECT_TYPE_GHOST_ARCHER_ATTACK)
                    self._declare_gfx(OBJECT_TYPE_GHOST_ARCHER_DEAD)
                    self._declare_gfx(OBJECT_TYPE_GHOST_ARCHER_HURT)
                    self._declare_gfx(OBJECT_TYPE_GHOST_ARCHER_IDLE)
                    self._make_actor(words, GhostArcher)
                if words[0] == "mage":
                    self._declare_gfx(OBJECT_TYPE_MAGE_ATTACK)
                    self._declare_gfx(OBJECT_TYPE_MAGE_DEAD)
                    self._declare_gfx(OBJECT_TYPE_MAGE_HURT)
                    self._declare_gfx(OBJECT_TYPE_MAGE_IDLE)
                    self._make_actor(words, Mage)
    
    def _declare_gfx(self, object_type: int) -> None:
        if object_type not in self._gfx_objects:
            self._gfx_objects.append(object_type)
    
    def get_gfx_objects(self) -> list[int]:
        return self._gfx_objects

    def save(self) -> None:
        
        with open("levels/party.txt", "w") as file:
            for actor in self._encounter.get_actors():
                if not actor.is_friendly():
                    continue
                file.write(self._save_actor(actor))
    
    def _make_actor(self, words: list[str], _class) -> None:

        health, _, max_health = words[1].partition("/")
        health = int(health)
        max_health = int(max_health)
        damage = int(words[2])
        if words[0] in ("demon", "ghost_archer", "mage"):
            actor: Actor = _class(health, max_health, damage, self.monster_count)
            self.monster_count += 1
        else:
            actor: Actor = _class(health, max_health, damage)
        self._encounter.add_actor(actor)
    
    def _save_actor(self, actor: Actor) -> str:
        formal_name = actor.get_name()
        name = ""
        if formal_name == "Ada Lovelace":
            name = "ada"
        elif formal_name == "Charles Babbage":
            name = "babbage"
        elif formal_name == "Alice Liddell":
            name = "alice"
        
        health = actor.get_health()
        max_health = actor.get_max_health()
        damage = actor.get_damage()

        return f"{name} {health}/{max_health} {damage}\n"
    
    def enter_turn_start(self) -> None:
        
        self.current_actor.start_turn()
        self._timer = Timer(self.STANDARD_DELAY)

        if self.current_actor.is_friendly():
            self._target_x = -100
        else:
            self._target_x = 100

    def update_turn_start(self) -> int:
        
        self._timer.update()
        if (self._timer.is_ellapsed()):
            return self.STATE_SELECT_MOVE

        dx = self.current_actor.get_dx()
        if self.current_actor.is_friendly():
            dx = max(self._target_x, dx - 1)
        else:
            dx = max(self._target_x, dx + 1)
        self.current_actor.set_dx(dx)
        return self.STATE_NO_CHANGE
    
    def exit_turn_start(self) -> None:
        pass

    def enter_select_move(self) -> None:
        
        if self.current_actor.is_friendly():
            moves = self.current_actor.get_moves()
            self.buttons: list[Button] = []
            for i,move in enumerate(moves):
                button = Button(450, 400 + 50 * i, 200, 50, text = move)
                button.add_observer(self._event_queue)
                button.add_observer(audio_system.get_events())
                self.add_observer(button.get_events())
                self.buttons.append(button)
    
    def update_select_move(self) -> int:
        
        if not self.current_actor.is_friendly():
            #randomly choose a move!
            moves = self.current_actor.get_moves()
            self.current_move = random.choice(moves)
            return self.STATE_SELECT_TARGET
        
        # if the character is friendly, then we must wait for the user
        # to click a button.
        for button in self.buttons:
            button.update(self.mouse_x, self.mouse_y)
        return self.STATE_NO_CHANGE
    
    def exit_select_move(self) -> None:
        self.buttons.clear()
    
    def enter_select_target(self) -> None:

        self.current_target = self._encounter.get_next_target(
            not self.current_actor.is_friendly())
        
    def update_select_target(self) -> int:

        if not self.current_actor.is_friendly():
            #randomly choose a target
            for i in range(random.randint(0, 3)):
                self.current_target = self._encounter.get_next_target(True)
            return self.STATE_ATTACK
        
        # if the character is friendly, then we must wait for the user
        # to select a target
        return self.STATE_NO_CHANGE
    
    def exit_select_target(self) -> None:
        pass

    def enter_attack(self) -> None:
        self.current_actor.perform_attack()
        self._timer = Timer(self.STANDARD_DELAY)
    
    def update_attack(self) -> int:
        self._timer.update()
        if self._timer.is_ellapsed():
            return self.STATE_TARGET_DAMAGED
        return self.STATE_NO_CHANGE
    
    def exit_attack(self) -> None:
        pass

    def enter_target_damaged(self) -> None:
        damage = self.current_actor.get_damage() + random.randint(1, 5)
        self.current_target.take_damage(damage)
        if self.current_move == "Ice Spell":
            self.animated_entities.append(AnimatedEntity(self.current_target.x, 
                                                    self.current_actor.y, 0, 0, 
                                                    OBJECT_TYPE_ICE_SPELL, 
                                                    ANIMATION_TYPE_IDLE))
            self.publish(Message(EVENT_TYPE_ATTACK, OBJECT_TYPE_ICE_SPELL, self))
        elif self.current_move == "Fire Spell":
            self.animated_entities.append(AnimatedEntity(self.current_target.x, 
                                                    self.current_actor.y, 0, 0, 
                                                    OBJECT_TYPE_FIRE_SPELL, 
                                                    ANIMATION_TYPE_IDLE))
        elif self.current_move == "Lightning Spell":
            self.entities.append(Entity(self.current_target.x, 
                                        self.current_actor.y, 0, 0, 
                                                    OBJECT_TYPE_LIGHTNING_BOLT))
        if not self.current_target.is_alive():
            self._encounter.register_death(self.current_target)
        self.current_target = None
        self._timer = Timer(2 * self.STANDARD_DELAY)
    
    def update_target_damaged(self) -> int:
        self._timer.update()
        if self._timer.is_ellapsed():
            return self.STATE_CHOOSE_ACTOR
        return self.STATE_NO_CHANGE
    
    def exit_target_damaged(self) -> None:
        self.entities.clear()
        self.animated_entities.clear()
        self.current_actor.set_dx(0)

        if self._encounter.over():
            self._encounter_over = True
    
    def enter_choose_actor(self) -> None:
        self.current_actor = self._encounter.choose_actor()
    
    def update_choose_actor(self) -> int:
        return self.STATE_TURN_START
    
    def exit_choose_actor(self) -> None:
        pass

    def get_actors(self) -> list[Actor]:
        
        return self._encounter.get_actors()
    
    def get_current_target(self) -> Actor | None:
        return self.current_target
    
    def get_entities(self) -> list[Entity]:
        return self.entities
    
    def get_animated_entities(self) -> list[AnimatedEntity]:
        return self.animated_entities
    
    def get_background(self) -> Entity:
        return self._background

    def update(self, mouse_x, mouse_y) -> int:

        for effect in self.animated_entities:
            effect.update(1.0)

        self.clear_events()

        self.mouse_x = mouse_x
        self.mouse_y = mouse_y

        next_state = self.states[self.state]["update"]()
        if next_state == self.STATE_NO_CHANGE:
            return GAME_PHASE_NO_CHANGE

        self.states[self.state]["exit"]()
        self.state = next_state
        self.states[self.state]["enter"]()

        if self._encounter_over:
            if self._encounter.won():
                self.save()
            return GAME_PHASE_OVERWORLD
        else:
            return GAME_PHASE_NO_CHANGE
    
    def key_pressed(self, key: int) -> None:

        if self.state == self.STATE_SELECT_TARGET:
            if key in (pg.K_LEFT, pg.K_UP):
                self.current_target = self._encounter.get_previous_target(False)
                self.publish(Message(event_type=EVENT_TYPE_MOUSE_CLICK,
                                object_type=OBJECT_TYPE_MODEL,
                                instance = self))
            if key in (pg.K_RIGHT, pg.K_DOWN):
                self.current_target = self._encounter.get_next_target(False)
                self.publish(Message(event_type=EVENT_TYPE_MOUSE_CLICK,
                                object_type=OBJECT_TYPE_MODEL,
                                instance = self))
            
            if key in (pg.K_SPACE, pg.K_RETURN):
                self.states[self.state]["exit"]()
                self.state = self.STATE_ATTACK
                self.states[self.state]["enter"]()
                self.publish(Message(event_type=EVENT_TYPE_MOUSE_CLICK,
                                object_type=OBJECT_TYPE_MODEL,
                                instance = self))
            
            if key == pg.K_ESCAPE:
                self.states[self.state]["exit"]()
                self.state = self.STATE_SELECT_MOVE
                self.states[self.state]["enter"]()
                self.current_target = None
                self.publish(Message(event_type=EVENT_TYPE_MOUSE_CLICK,
                                object_type=OBJECT_TYPE_MODEL,
                                instance = self))
    
    def handle_click(self, mouse_x: int, mouse_y: int) -> None:
        if self.state == self.STATE_SELECT_MOVE:
            for button in self.buttons:
                if button.contains(mouse_x, mouse_y):
                    self.current_move = button._text
                    self.states[self.state]["exit"]()
                    self.state = self.STATE_SELECT_TARGET
                    self.states[self.state]["enter"]()
                self.publish(Message(event_type=EVENT_TYPE_MOUSE_CLICK,
                                object_type=OBJECT_TYPE_MODEL,
                                instance = self))

class BattleView(View):

    def __init__(self, screen: Surface):
        super().__init__(screen)
        self._inactive_button_colour = (128, 128, 128)
        self._active_button_colour = (255, 96, 128)
        self._load_image(OBJECT_TYPE_ARROW)
    
    def load_gfx_objects(self, gfx_objects: list[int]) -> None:
        for object_type in gfx_objects:
            self.load_gfx(object_type)
    
    def draw_button(self, button: Button):

        colour = self._active_button_colour if button.is_active()\
            else self._inactive_button_colour
        rect = button.get_draw_rect_data()
        pg.draw.rect(self._screen, colour, rect)
        self._draw_text(button._text, rect[0] + 16, button._y - 16, (0,0,0))
    
    def draw(self, background: Entity, actors: list[Actor],
             buttons: list[Button], current_target: Actor,
             lightning_bolts: list[Entity],
             vfx: list[AnimatedEntity], current_actor: Actor) -> None:
        
        self._draw_entity_image(background)

        for actor in actors:
            object_type = actor.get_display()
            if object_type not in self._images:
                return
        
            image = self._images[object_type]
            dst_rect = (actor.x + actor._dx, actor.y)
            self._screen.blit(image, dst_rect)

            health_percentage = actor.get_health() / actor.get_max_health()

            rect = [dst_rect[0], dst_rect[1], 100 * health_percentage, 10]
            pg.draw.rect(self._screen, (226, 0, 0), rect)
            rect = [dst_rect[0], dst_rect[1], 100, 10]
            pg.draw.rect(self._screen, (0, 0, 0), rect, 4)
        
        rect = [325, 375, 275, 175]
        pg.draw.rect(self._screen, (0, 0, 0), rect, 4)
        if current_actor is not None:
            self._draw_text(current_actor.get_name(), 325, 345, (0,0,0))
        
        for button in buttons:
            self.draw_button(button)
        
        if current_target is not None:
            image = self._images[OBJECT_TYPE_ARROW]
            dst_rect = (current_target.x, current_target.y)
            self._screen.blit(image, dst_rect)
        
        for bolt in lightning_bolts:
            self._draw_entity_image(bolt, cam_y = -20)
        
        for effect in vfx:
            self._draw_animated_entity(effect, cam_x = 200, cam_y = -50)

        
        self._finish_drawing()

class BattleController(Controller):

    def __init__(self, clock: Clock, screen: Surface):
        super().__init__(clock)
        self._load_sfx()
        self._model = BattleModel()
        self._view = BattleView(screen)
        self._view.load_gfx_objects(self._model.get_gfx_objects())
    
    def _load_sfx(self) -> None:
        audio_system.clear_all()

        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/ada_attack_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/ada_attack_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/ada_attack_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_DIE, "sfx/ada_die_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_DIE, "sfx/ada_die_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_DIE, "sfx/ada_die_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_HURT, "sfx/ada_hurt_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_HURT, "sfx/ada_hurt_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_HURT, "sfx/ada_hurt_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_LOW_HEALTH, "sfx/ada_low_health.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_LOW_HEALTH, "sfx/ada_low_health_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_LOW_HEALTH, "sfx/ada_low_health_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ADA_IDLE, 
            EVENT_TYPE_START_TURN, "sfx/ada_start_turn.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/alice_attack_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/alice_attack_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/alice_attack_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_DIE, "sfx/alice_die_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_DIE, "sfx/alice_die_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_DIE, "sfx/alice_die_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_HURT, "sfx/ada_hurt_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_HURT, "sfx/ada_hurt_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_HURT, "sfx/ada_hurt_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_LOW_HEALTH, "sfx/ada_low_health.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_START_TURN, "sfx/alice_start_turn_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_ALICE_IDLE, 
            EVENT_TYPE_START_TURN, "sfx/alice_start_turn_2.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/babbage_attack_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/babbage_attack_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/babbage_attack_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_DIE, "sfx/babbage_die_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_DIE, "sfx/babbage_die_2.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/babbage_hurt_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/babbage_hurt_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/babbage_hurt_3.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/babbage_hurt_4.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_LOW_HEALTH, "sfx/babbage_low_health.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_BABBAGE_IDLE, 
            EVENT_TYPE_START_TURN, "sfx/babbage_start_turn.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/demon_attack_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/demon_attack_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/demon_attack_3.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/demon_attack_4.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/demon_attack_5.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_DIE, "sfx/demon_die_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_DIE, "sfx/demon_die_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_DIE, "sfx/demon_die_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_HURT, "sfx/demon_hurt_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_HURT, "sfx/demon_hurt_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_DEMON_IDLE, 
            EVENT_TYPE_HURT, "sfx/demon_hurt_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_GHOST_ARCHER_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/ghost_archer_attack_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_GHOST_ARCHER_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/ghost_archer_attack_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_GHOST_ARCHER_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/ghost_archer_attack_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_GHOST_ARCHER_IDLE, 
            EVENT_TYPE_DIE, "sfx/ghost_archer_die_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_GHOST_ARCHER_IDLE, 
            EVENT_TYPE_DIE, "sfx/ghost_archer_die_2.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_GHOST_ARCHER_IDLE, 
            EVENT_TYPE_HURT, "sfx/ghost_archer_hurt.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/mage_attack_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/mage_attack_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_ATTACK, "sfx/mage_attack_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_DIE, "sfx/mage_die_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_DIE, "sfx/mage_die_2.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/mage_hurt_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/mage_hurt_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MAGE_IDLE, 
            EVENT_TYPE_HURT, "sfx/mage_hurt_3.wav")
        
        audio_system.load_sfx(
            object_type = OBJECT_TYPE_BUTTON,
            event_type = EVENT_TYPE_MOUSE_ENTER,
            filename = "sfx/click_1.wav")
        
        audio_system.load_sfx(
            object_type = OBJECT_TYPE_BUTTON,
            event_type = EVENT_TYPE_MOUSE_LEAVE,
            filename = "sfx/click_2.wav")
        
        audio_system.load_sfx(
            object_type = OBJECT_TYPE_BUTTON,
            event_type = EVENT_TYPE_MOUSE_CLICK,
            filename = "sfx/click_3.wav")
        
        audio_system.load_sfx(
            object_type=OBJECT_TYPE_ICE_SPELL,
            event_type = EVENT_TYPE_ATTACK,
            filename = "sfx/ice_spell.wav")
    
    def _draw(self) -> None:
        self._view.draw(
            self._model.get_background(),
            self._model.get_actors(),
            self._model.buttons,
            self._model.current_target,
            self._model.get_entities(),
            self._model.get_animated_entities(),
            self._model.current_actor)
    
    def _update_world(self) -> int:
        audio_system.update()

        return self._model.update(self._mouse_pos[0], self._mouse_pos[1])
    
    def _key_pressed(self, key):
        self._model.key_pressed(key)
    
    def _mouse_clicked(self):
        self._model.handle_click(self._mouse_pos[0], self._mouse_pos[1])
#endregion
#region Console
class ConsoleModel(Model):

    MAX_LINE_LENGTH = 25
    MAX_LINE_COUNT = 10

    def __init__(self):
        super().__init__()
        self._gfx_objects: list[int] = []
        audio_system.load_track("hacking", "music/hacking.wav")
        audio_system.start_music("hacking")
        
        self._top_line = ";; x = y + 1"
        self._buffer: list[str] = ["" for _ in range(ConsoleModel.MAX_LINE_COUNT)]
        self.add_observer(audio_system.get_events())

        self.cursor_pos = 0
        self.cursor_line = 0

        self._declare_gfx(OBJECT_TYPE_CONSOLE)
        self._declare_gfx(OBJECT_TYPE_GEAR)
        self.should_exit = False

        self.timer = None

        self.memory = [0 for _ in range(10)]
        self.stack = [0 for _ in range(10)]
        self.stack_pointer = 0
        self.instruction_counter = 0

        #TODO: Make buttons
    
    def get_top_line(self) -> str:
        return self._top_line
    
    def get_buffer(self) -> list[str]:
        buffer = self._buffer.copy()
        buffer[self.cursor_line] = (
            buffer[self.cursor_line][:self.cursor_pos] 
            + "|" 
            + buffer[self.cursor_line][self.cursor_pos:])
        return buffer
        
    def _declare_gfx(self, object_type: int) -> None:
        if object_type not in self._gfx_objects:
            self._gfx_objects.append(object_type)
    
    def get_gfx_objects(self) -> list[int]:
        return self._gfx_objects

    def get_memory(self) -> list[int]:
        return self.memory
    
    def get_stack_pointer(self) -> int:
        return self.stack_pointer
    
    def get_stack(self) -> list[int]:
        return self.stack
    
    def get_instruction_counter(self) -> int:
        return self.instruction_counter
    
    def update(self) -> int:

        if self.should_exit:
            return GAME_PHASE_OVERWORLD
        
        if self.timer is not None:
            self.timer.update()
            if self.timer.is_ellapsed():
                if self.instruction_counter < len(self._buffer):
                    self.run_line(self.instruction_counter)
                    self.instruction_counter += 1
                    self.timer = Timer(60)
                else:
                    self.timer = None
                    self.instruction_counter = 0
                    self.publish(Message(EVENT_TYPE_MACHINE_RESET,
                                         OBJECT_TYPE_MODEL, self))

        #TODO: update buttons
        pass

        return GAME_PHASE_NO_CHANGE
    
    def run_line(self, line_number: int):

        self.publish(Message(EVENT_TYPE_MACHINE_TICK,
                             OBJECT_TYPE_MODEL, self))
        
        line = self._buffer[line_number].strip()
        words = line.split(" ")

        if words[0] == "push":
            self.execute_push_op(words)
        if words[0] == "pop":
            self.execute_pop_op(words)
        if words[0] == "add":
            self.execute_add_op()
        if words[0] == "sub":
            self.execute_sub_op()
        if words[0] == "mul":
            self.execute_mul_op()
        if words[0] == "load":
            self.execute_load_op()
        if words[0] == "store":
            self.execute_store_op()
    
    def execute_push_op(self, words: list[int]) -> None:
        if self.stack_pointer == 10:
            return
        
        self.stack[self.stack_pointer] = int(words[1])
        self.stack_pointer += 1
    
    def execute_pop_op(self, words: list[int]) -> None:
        if self.stack_pointer == 0:
            return
        
        self.stack_pointer -= 1
    
    def execute_add_op(self) -> None:
        if self.stack_pointer < 2:
            return
        
        operand_a = self.stack[self.stack_pointer - 1]
        operand_b = self.stack[self.stack_pointer - 2]
        self.stack_pointer -= 1
        self.stack[self.stack_pointer - 1] = operand_a + operand_b
    
    def execute_sub_op(self) -> None:
        if self.stack_pointer < 2:
            return
        
        operand_a = self.stack[self.stack_pointer - 1]
        operand_b = self.stack[self.stack_pointer - 2]
        self.stack_pointer -= 1
        self.stack[self.stack_pointer - 1] = operand_a - operand_b
    
    def execute_mul_op(self) -> None:
        if self.stack_pointer < 2:
            return
        
        operand_a = self.stack[self.stack_pointer - 1]
        operand_b = self.stack[self.stack_pointer - 2]
        self.stack_pointer -= 1
        self.stack[self.stack_pointer - 1] = operand_a * operand_b
    
    def execute_load_op(self) -> None:
        if self.stack_pointer < 1:
            return
        
        address = self.stack[self.stack_pointer - 1]
        self.stack[self.stack_pointer - 1] = self.memory[address]
    
    def execute_store_op(self) -> None:
        if self.stack_pointer < 2:
            return
        
        value = self.stack[self.stack_pointer - 2]
        address = self.stack[self.stack_pointer - 1]
        self.memory[address] = value
        self.stack_pointer -= 2
    
    def key_pressed(self, key: int) -> None:

        if key == pg.K_RETURN:
            self.publish(Message(EVENT_TYPE_MACHINE_RESET,
                                OBJECT_TYPE_MODEL, self))
        else:
            self.publish(Message(EVENT_TYPE_MACHINE_TICK,
                                OBJECT_TYPE_MODEL, self))
        
        if key == pg.K_ESCAPE:
            self.should_exit = True
            return

        if key == pg.K_LEFT:
            self.cursor_pos -= 1
            if self.cursor_pos < 0:
                if self.cursor_line > 0:
                    self.cursor_line -= 1
                    self.cursor_pos = len(self._buffer[self.cursor_line])
                else:
                    self.cursor_line = len(self._buffer) - 1
                    self.cursor_pos = len(self._buffer[self.cursor_line])
            return
        
        if key == pg.K_RIGHT:
            self.cursor_pos += 1
            if self.cursor_pos > ConsoleModel.MAX_LINE_LENGTH:
                if self.cursor_line < ConsoleModel.MAX_LINE_COUNT:
                    self.cursor_line += 1
                    self.cursor_pos = 0
                else:
                    self.cursor_pos = 0
                    self.cursor_line = 0
            return
        
        if key == pg.K_UP:
            self.cursor_line = (self.cursor_line - 1) % len(self._buffer)
            self.cursor_pos = min(self.cursor_pos, len(self._buffer[self.cursor_line]))
            return
        
        if key == pg.K_DOWN:
            self.cursor_line = (self.cursor_line + 1) % len(self._buffer)
            self.cursor_pos = min(self.cursor_pos, len(self._buffer[self.cursor_line]))
            return

        if key == pg.K_RETURN:
            self.cursor_line += 1
            self.cursor_pos = 0
            return
        
        if key == pg.K_BACKSPACE:
            if self.cursor_pos > 0:
                self._buffer[self.cursor_line] = (
                    self._buffer[self.cursor_line][:self.cursor_pos - 1] 
                    + self._buffer[self.cursor_line][self.cursor_pos:])
                self.cursor_pos -= 1
            elif (self.cursor_line) > 0:
                self.cursor_line -= 1
                self.cursor_pos = len(self.cursor_line) - 1
                self._buffer[self.cursor_line] = \
                    self._buffer[self.cursor_line][:self.cursor_pos] 
        
        else:
            if len(self._buffer) == 0 or (len(self._buffer[self.cursor_line])
                   < ConsoleModel.MAX_LINE_LENGTH):
                self._buffer[self.cursor_line] += chr(key)
                self.cursor_pos += 1

    def handle_click(self):
        self.timer = Timer(60)

class ConsoleView(View, Observable):

    def __init__(self, screen: Surface):
        View.__init__(self, screen)
        Observable.__init__(self)
        self.gear_angle = 0
    
    def load_gfx_objects(self, gfx_objects: list[int]) -> None:
        for object_type in gfx_objects:
            self.load_gfx(object_type)
    
    def update(self):
        for event in self._event_queue:
            if event.event_type in (EVENT_TYPE_MACHINE_TICK,
                                    EVENT_TYPE_MACHINE_RESET):
                self.gear_angle -= 10
                self.gear_angle = self.gear_angle % 360
        self._event_queue.clear()

    def draw(self, top_line: str,
             buffer: list[str],
             memory: list[int],
             stack: list[int],
             stack_pointer: int,
             instruction_counter: int) -> None:

        self._screen.fill((196, 196, 196))

        object_type = OBJECT_TYPE_CONSOLE
        
        if object_type not in self._images:
            return
        
        image = self._images[object_type]
        dst_rect = (75, -10)
        self._screen.blit(image, dst_rect)

        self._draw_text(top_line, 200, 75, (0, 32, 0))
        for i, line in enumerate(buffer):
            color = (128, 32, 0) if i == instruction_counter else (0, 32, 0)
            self._draw_text(line, 200, 75 + 25 * (i + 1), color)

        for i, value in enumerate(memory):
            self._draw_text(str(value), 150 + 40 * i, 475, (0, 32, 0))
        
        for i, value in enumerate(stack):
            color = (128, 32, 0) if i == stack_pointer else (0, 32, 0)
            self._draw_text(str(value), 700, 35 + 35 * i, color)

        object_type = OBJECT_TYPE_GEAR
        
        if object_type not in self._images:
            return
        
        image = self._images[object_type]
        dst_rect = (50, 50)
        new_image = pg.transform.rotate(image, self.gear_angle)
        new_rect = new_image.get_rect(center = (50,50))
        self._screen.blit(new_image, new_rect)

        image = self._images[object_type]
        dst_rect = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50)
        new_image = pg.transform.rotate(image, -self.gear_angle)
        new_rect = new_image.get_rect(center = (SCREEN_WIDTH - 50, SCREEN_HEIGHT - 50))
        self._screen.blit(new_image, new_rect)
        
        self._finish_drawing()

class ConsoleController(Controller):

    def __init__(self, clock: Clock, screen: Surface):
        super().__init__(clock)
        self._load_sfx()
        self._model = ConsoleModel()
        self._view = ConsoleView(screen)
        self._view.load_gfx_objects(self._model.get_gfx_objects())
        self._model.add_observer(self._view.get_events())
    
    def _load_sfx(self) -> None:
        audio_system.clear_all()
        
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL,
            EVENT_TYPE_MACHINE_TICK,
            "sfx/click_1.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL,
            EVENT_TYPE_MACHINE_TICK,
            "sfx/click_2.wav")
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL,
            EVENT_TYPE_MACHINE_TICK,
            "sfx/click_3.wav")
        
        audio_system.load_sfx(
            OBJECT_TYPE_MODEL, 
            EVENT_TYPE_MACHINE_RESET, 
            "sfx/windup.wav")
    
    def _draw(self) -> None:
        self._view.draw(self._model.get_top_line(),
                        self._model.get_buffer(),
                        self._model.get_memory(),
                        self._model.get_stack(),
                        self._model.get_stack_pointer(),
                        self._model.get_instruction_counter())
    
    def _update_world(self) -> int:
        audio_system.update()
        self._view.update()

        return self._model.update()
    
    def _key_pressed(self, key):
        self._model.key_pressed(key)
    
    def _mouse_clicked(self):
        return self._model.handle_click()
#endregion
def main():
    next_phase = GAME_PHASE_LOGO
    while next_phase != GAME_PHASE_EXIT:
        if next_phase == GAME_PHASE_LOGO:
            controller = LogoController(clock, screen)
        elif next_phase == GAME_PHASE_MENU:
            controller = MenuController(clock, screen)
        elif next_phase == GAME_PHASE_OVERWORLD:
            controller = OverworldController(clock, screen)
        elif next_phase == GAME_PHASE_BATTLE:
            controller = BattleController(clock, screen)
        elif next_phase == GAME_PHASE_CONSOLE:
            controller = ConsoleController(clock, screen)
        next_phase = controller.run()
main()