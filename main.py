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
GAME_PHASE_OVERWORLD = 2
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
def main():
    next_phase = GAME_PHASE_LOGO
    while next_phase != GAME_PHASE_EXIT:
        if next_phase == GAME_PHASE_LOGO:
            controller = LogoController(clock, screen)
        elif next_phase == GAME_PHASE_MENU:
            controller = MenuController(clock, screen)
        next_phase = controller.run()

main()