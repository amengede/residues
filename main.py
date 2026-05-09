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

GAME_PHASE_LOGO = 0
GAME_PHASE_MENU = 1
GAME_PHASE_OVERWORLD = 2
GAME_PHASE_BATTLE = 3
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
        else:
            self.load("levels/temp.txt")
    
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
        return f"demon {health} {damage}\n"

    def make_ghost_archer(self) -> str:
        
        health = random.randint(20, 25)
        damage = random.randint(12, 20)
        return f"ghost_archer {health} {damage}\n"

    def make_mage(self) -> str:
        
        health = random.randint(10, 25)
        damage = random.randint(10, 20)
        return f"mage {health} {damage}\n"

    def update(self) -> int:

        for event in self.get_events():
            if (event.event_type in (EVENT_TYPE_STEP_DIRT,
                                     EVENT_TYPE_STEP_PATH)):
                if self._player.is_on_grass():
                    if (random.randint(1, 10)) > 9:
                        OverworldModel.fresh = False
                        self.save("levels/temp.txt")
                        self.generate_encounter()
                        return GAME_PHASE_BATTLE
        self.clear_events()

        self._camera.update()

        self._player.update(self._object_groups)

        npcs = self._object_groups[OBJECT_TYPE_NPC_OVERWORLD_DOWN]
        for npc in npcs.get_members():
            npc.update(self._object_groups)
        npcs.rebuild()

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
            #TODO: interact with things!
            pass

class OverworldView(View):

    def __init__(self, screen: Surface):
        super().__init__(screen)
    
    def load_gfx_objects(self, gfx_objects: list[int]) -> None:
        for object_type in gfx_objects:
            self.load_gfx(object_type)
    
    def draw(self, covered_object_groups: dict[int, EntityGroup],
             covering_object_groups: dict[int, EntityGroup],
             camera: Camera, background: Entity,
             player: Player) -> None:
        
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
        
        self._draw_entity_image(player, cam_x, cam_y)

        for grass in covering_grass:
            self._draw_entity_image(grass, cam_x, cam_y)
        
        visible_set = []
        for object_type, object_group in covering_object_groups.items():
            visible_set.extend(object_group.get_overlapping(camera))
        for entity in visible_set:
            self._draw_entity_image(entity, cam_x, cam_y)
        
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
    
    def _draw(self) -> None:
        self._view.draw(
            self._model.get_covered_object_groups(), 
            self._model.get_covering_object_groups(), 
            self._model.get_camera(), 
            self._model.get_background(), 
            self._model.get_player())
    
    def _update_world(self) -> int:
        audio_system.update()

        return self._model.update()
    
    def _handle_held_keys(self):
        self._model.handle_keys(self._keys)
    
    def _key_pressed(self, key):
        self._model.key_pressed(key)
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
        next_phase = controller.run()

main()