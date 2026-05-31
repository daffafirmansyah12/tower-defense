"""
main.py - Tower Defense Entry Point
==========================================
Flow layar:
  MainMenu → DifficultySelectMenu → Game (PLAYING)
           ↕ ESC                     ↕ ESC
         PauseMenu ←──────────────────┘
           ↓ Main Menu
         MainMenu
           ↓ Settings
         SettingsMenu
           ↓ Game Over
         GameOverScreen → Retry / MainMenu
"""

import pygame
import time
from config import *
from game import Game
from ui import (
    MainMenu, DifficultySelectMenu, PauseMenu,
    SettingsMenu, GameOverScreen, InGameHUD, Fonts
)

# Mapping string difficulty → Enum
DIFF_MAP = {
    'EASY':   Difficulty.EASY,
    'NORMAL': Difficulty.NORMAL,
    'HARD':   Difficulty.HARD,
}


# ──────────────────────────────────────────────────────
#  Adapter: hubungkan Game lama ke InGameHUD baru
# ──────────────────────────────────────────────────────

def build_hud_state(game: Game) -> dict:
    """Ambil semua data dari Game untuk dikirim ke InGameHUD."""
    from game import IceTower, FireTower, LightningTower, LaserTower, TargetMode

    tower_names = {
        IceTower: 'Ice', FireTower: 'Fire',
        LightningTower: 'Lightning', LaserTower: 'Laser',
    }
    mode_names = {
        TargetMode.FIRST: 'FIRST', TargetMode.LAST: 'LAST',
        TargetMode.STRONGEST: 'STRONGEST', TargetMode.CLOSEST: 'CLOSEST',
    }

    sel_info = None
    if game.selected_tower:
        t = game.selected_tower
        sel_info = {
            'type':       tower_names.get(type(t), 'Tower'),
            'level':      t.level,
            'damage':     t.damage,
            'mode':       mode_names.get(t.target_mode, '?'),
            'sell_value': t.get_sell_value(),
        }

    return {
        'score':               game.score,
        'money':               game.money,
        'base_health':         game.base_health,
        'wave':                game.wave_manager.wave_number,
        'tower_count':         len(game.towers),
        'difficulty':          game.difficulty_config['difficulty_name'],
        'gap_timer':           game.gap_timer if game.game_state == GameState.WAVE_GAP else 0,
        'gap_duration':        game.gap_duration,
        'turbo_mode':          game.turbo_mode,
        'is_paused':           game.is_paused,
        'selected_tower_info': sel_info,
    }


def build_gameover_stats(game: Game, playtime: float) -> dict:
    return {
        'score':          game.score,
        'wave':           game.wave_manager.wave_number,
        'playtime':       playtime,
        'enemies_killed': getattr(game, 'enemies_killed', 0),
        'money_earned':   getattr(game, 'total_money_earned', 0),
        'difficulty':     game.difficulty_config['difficulty_name'],
        'towers_placed':  getattr(game, 'towers_placed', len(game.towers)),
    }


# ──────────────────────────────────────────────────────
#  GAME RUNNER — integrasikan UI baru ke game loop
# ──────────────────────────────────────────────────────

class GameRunner:
    """
    Menggantikan game.run() yang lama. Mengelola semua screen
    dan menginjeksikan HUD baru ke dalam loop game.
    """

    def __init__(self, difficulty: Difficulty, settings: dict):
        self.game      = Game(difficulty)
        self.hud       = InGameHUD()
        self.settings  = settings
        self.pause_menu = PauseMenu()
        self.result    = None   # 'main_menu' | 'retry' | 'quit'
        self._start_time = time.time()
        self._paused_time = 0.0
        self._pause_start = None

    def _get_playtime(self):
        total = time.time() - self._start_time - self._paused_time
        return total

    def run(self):
        from game import IceTower, FireTower, LightningTower, LaserTower

        game = self.game
        game.start_first_wave()

        settings_screen = None

        while True:
            clock.tick(60)

            # ── Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.result = 'quit'
                    return

                # Pause toggle via ESC
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    if not game.is_paused:
                        game.is_paused = True
                        self._pause_start = time.time()
                    else:
                        game.is_paused = False
                        if self._pause_start:
                            self._paused_time += time.time() - self._pause_start
                            self._pause_start = None

                # Jika settings overlay aktif
                if settings_screen:
                    settings_screen.handle_event(event)
                    if settings_screen.choice in ('back', 'apply'):
                        if settings_screen.choice == 'apply':
                            self.settings.update(settings_screen.settings)
                        settings_screen = None
                    continue

                # Pause menu event
                if game.is_paused:
                    self.pause_menu.handle_event(event)
                    ch = self.pause_menu.choice
                    if ch == 'resume':
                        game.is_paused = False
                        if self._pause_start:
                            self._paused_time += time.time() - self._pause_start
                            self._pause_start = None
                        self.pause_menu.choice = None
                    elif ch == 'settings':
                        settings_screen = SettingsMenu(dict(self.settings))
                        self.pause_menu.choice = None
                    elif ch == 'main_menu':
                        self.result = 'main_menu'
                        return
                    elif ch == 'leaderboard':
                        # TODO: tampilkan leaderboard overlay
                        self.pause_menu.choice = None
                    continue

                # Game controls (keyboard)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.toggle_pause()
                    if event.key == pygame.K_z:
                        game.toggle_turbo()
                    if event.key == pygame.K_1:
                        game.place_tower("ice")
                    if event.key == pygame.K_2:
                        game.place_tower("fire")
                    if event.key == pygame.K_3:
                        game.place_tower("lightning")
                    if event.key == pygame.K_4:
                        game.place_tower("laser")
                    if event.key == pygame.K_u:
                        game.upgrade_tower()
                    if event.key == pygame.K_t:
                        game.change_target_mode()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mx, my = pygame.mouse.get_pos()
                    if event.button == 1:
                        game.select_tower(mx, my)
                    elif event.button == 3:
                        game.sell_tower(mx, my)

            # ── Update
            if settings_screen:
                settings_screen.update()
            elif game.is_paused:
                self.pause_menu.update()
            else:
                game.update()

            self.hud.update(game.base_health, game.money)

            # ── Draw
            game.draw_map()

            for tower in game.towers:
                tower.draw(screen)
            for enemy in game.enemies:
                enemy.draw(screen)
            for bullet in game.bullets:
                bullet.draw(screen)
            for special in game.special_bullets:
                special.draw(screen)

            # HUD baru menggantikan draw_ui lama
            hud_data = build_hud_state(game)
            wave_info = game.wave_manager.get_wave_info()
            self.hud.draw_top_bar(screen, hud_data)
            self.hud.draw_bottom_bar(screen, hud_data, wave_info)

            # Wave complete banner
            if game.game_state == GameState.WAVE_GAP:
                time_left = (game.gap_duration - game.gap_timer) / 60.0
                self.hud.draw_wave_complete_banner(
                    screen,
                    game.wave_manager.wave_number,
                    game.wave_bonus,
                    time_left
                )

            # Sell/Mode feedback
            if game.sell_feedback_timer > 0:
                self.hud.draw_sell_feedback(
                    screen, game.sell_feedback_text,
                    game.sell_feedback_timer / 60.0
                )
            if game.mode_change_feedback_timer > 0:
                self.hud.draw_mode_change_feedback(
                    screen, game.mode_change_text,
                    game.mode_change_feedback_timer / 60.0
                )

            # Pause menu overlay
            if game.is_paused and not settings_screen:
                self.pause_menu.draw(screen)

            # Settings overlay
            if settings_screen:
                settings_screen.draw(screen)

            pygame.display.update()

            # ── Game over check
            if game.game_state == GameState.GAME_OVER:
                self.result = 'game_over'
                self._stats = build_gameover_stats(game, self._get_playtime())
                return


# ──────────────────────────────────────────────────────
#  MAIN APPLICATION LOOP
# ──────────────────────────────────────────────────────

def main():
    Fonts.init()

    current_screen = 'main_menu'
    settings = {
        'vol_master': 80, 'vol_sfx': 70, 'vol_music': 60,
        'graphics': 1, 'difficulty': 1,
        'fullscreen': False, 'show_fps': False,
    }
    last_difficulty = Difficulty.NORMAL
    last_stats = None

    main_menu       = MainMenu()
    diff_menu       = None
    settings_screen = None
    gameover_screen = None

    while True:
        clock.tick(60)

        # ── EVENT HANDLING per screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

            if current_screen == 'main_menu':
                main_menu.handle_event(event)

            elif current_screen == 'difficulty_select' and diff_menu:
                diff_menu.handle_event(event)

            elif current_screen == 'settings' and settings_screen:
                settings_screen.handle_event(event)

            elif current_screen == 'game_over' and gameover_screen:
                gameover_screen.handle_event(event)

        # ── UPDATE + TRANSITION

        if current_screen == 'main_menu':
            main_menu.update()
            ch = main_menu.choice
            if ch == 'new_game':
                diff_menu = DifficultySelectMenu()
                current_screen = 'difficulty_select'
                main_menu.choice = None
            elif ch == 'settings':
                settings_screen = SettingsMenu(dict(settings))
                current_screen = 'settings'
                main_menu.choice = None
            elif ch == 'quit':
                pygame.quit()
                return
            elif ch in ('load_game', 'leaderboard'):
                # TODO: hubungkan ke API nanti
                main_menu.choice = None

        elif current_screen == 'difficulty_select' and diff_menu:
            diff_menu.update()
            ch = diff_menu.choice
            if ch == 'back':
                current_screen = 'main_menu'
                diff_menu.choice = None
            elif ch in DIFF_MAP:
                last_difficulty = DIFF_MAP[ch]
                # Mulai game
                runner = GameRunner(last_difficulty, settings)
                runner.run()

                if runner.result == 'quit':
                    pygame.quit()
                    return
                elif runner.result == 'main_menu':
                    current_screen = 'main_menu'
                    main_menu = MainMenu()
                elif runner.result == 'game_over':
                    last_stats = runner._stats
                    gameover_screen = GameOverScreen(last_stats)
                    current_screen = 'game_over'

                diff_menu.choice = None

        elif current_screen == 'settings' and settings_screen:
            settings_screen.update()
            ch = settings_screen.choice
            if ch == 'apply':
                settings.update(settings_screen.settings)
                current_screen = 'main_menu'
                settings_screen.choice = None
            elif ch == 'back':
                current_screen = 'main_menu'
                settings_screen.choice = None

        elif current_screen == 'game_over' and gameover_screen:
            gameover_screen.update()
            ch = gameover_screen.choice
            if ch == 'retry':
                runner = GameRunner(last_difficulty, settings)
                runner.run()

                if runner.result == 'quit':
                    pygame.quit()
                    return
                elif runner.result == 'main_menu':
                    current_screen = 'main_menu'
                    main_menu = MainMenu()
                elif runner.result == 'game_over':
                    last_stats = runner._stats
                    gameover_screen = GameOverScreen(last_stats)

                gameover_screen.choice = None
            elif ch == 'main_menu':
                current_screen = 'main_menu'
                main_menu = MainMenu()
                gameover_screen.choice = None

        # ── DRAW
        if current_screen == 'main_menu':
            main_menu.draw(screen)
        elif current_screen == 'difficulty_select' and diff_menu:
            diff_menu.draw(screen)
        elif current_screen == 'settings' and settings_screen:
            settings_screen.draw(screen)
        elif current_screen == 'game_over' and gameover_screen:
            gameover_screen.draw(screen)

        pygame.display.update()


if __name__ == '__main__':
    main()
