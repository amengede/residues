from support import *

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

        #TODO: Title

        #TODO: New Game Button

        #TODO: Quit Button
    
    def get_gfx_objects(self) -> dict[int, list[Entity]]:
        return self._gfx_objects
    
    def get_objects(self) -> dict[int, list[Entity]]:
        return self._objects

class MenuView(View):

    def __init__(self, screen: Surface):
        super().__init__(screen)
    
    def load_gfx_objects(self, gfx_objects: list[int]) -> None:
        
        for object_type in gfx_objects:
            self.load_gfx(object_type)
        
    def draw(self, objects: dict[int, list[Entity]]) -> None:

        self._draw_entity_image(objects[OBJECT_TYPE_TITLE_SCREEN][0])

        self._finish_drawing()

class MenuController(Controller):
    def __init__(self, clock: Clock, screen: Surface):
        super().__init__(clock)
        self._model = MenuModel()
        self._view = MenuView(screen)
        self._view.load_gfx_objects(self._model.get_gfx_objects())
    
    def _draw(self) -> None:
        self._view.draw(self._model.get_objects())
    
    def _update_world(self) -> int:
        
        return GAME_PHASE_NO_CHANGE

#endregion
def main():
    next_phase = GAME_PHASE_LOGO
    while next_phase != GAME_PHASE_EXIT:
        if next_phase == GAME_PHASE_LOGO:
            controller = LogoController(clock, screen)
        elif next_phase == GAME_PHASE_MENU:
            controller = MenuController(clock, screen)
        next_phase = controller.run()

main()