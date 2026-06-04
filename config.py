import pygame
from enum import Enum

pygame.init()

# ── Resolusi virtual (desain asli game) ──────────────────────────────
VIRTUAL_W = 1000
VIRTUAL_H = 600

# ── Resolusi layar nyata (fullscreen monitor) ────────────────────────
_info = pygame.display.Info()
SCREEN_W = _info.current_w
SCREEN_H = _info.current_h

# ── Hitung skala & offset untuk letterbox / stretch ─────────────────
# Gunakan stretch penuh (ikuti komentar user: "stretch ke fullscreen")
SCALE_X = SCREEN_W / VIRTUAL_W
SCALE_Y = SCREEN_H / VIRTUAL_H

# ── WIDTH / HEIGHT yang dipakai di seluruh game = ukuran VIRTUAL ─────
# Semua kode game (koordinat, drawing, collision) tetap pakai ini.
WIDTH  = VIRTUAL_W
HEIGHT = VIRTUAL_H

# ── Surface nyata (window) dan virtual surface ───────────────────────
_real_screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.display.set_caption("Tower Defense")

# Virtual surface: semua render ke sini dulu, lalu di-scale ke real_screen
screen = pygame.Surface((VIRTUAL_W, VIRTUAL_H))

clock = pygame.time.Clock()


# ── Helper: flip virtual → real ──────────────────────────────────────
def flip_to_screen():
    """Blit virtual surface (scale penuh) ke layar nyata, lalu flip."""
    scaled = pygame.transform.scale(screen, (SCREEN_W, SCREEN_H))
    _real_screen.blit(scaled, (0, 0))
    pygame.display.flip()


# ── Helper: konversi mouse pos dari koordinat layar nyata → virtual ──
def to_virtual_pos(real_pos):
    """Ubah koordinat mouse (real) ke koordinat virtual game."""
    rx, ry = real_pos
    vx = int(rx / SCALE_X)
    vy = int(ry / SCALE_Y)
    return (vx, vy)


# ─────────────────────────────────────────────────────────────────────
#  WARNA
# ─────────────────────────────────────────────────────────────────────
WHITE       = (255, 255, 255)
BLACK       = (20, 20, 20)
GREEN       = (0, 255, 100)
RED         = (255, 60, 60)
BLUE        = (0, 150, 255)
YELLOW      = (255, 255, 0)
PURPLE      = (180, 0, 255)
CYAN        = (0, 255, 255)
ORANGE      = (255, 165, 0)
LIME        = (50, 205, 50)
DARK_ORANGE = (255, 140, 0)
MAGENTA     = (255, 0, 255)
LIGHT_CYAN  = (100, 200, 255)
PINK        = (255, 192, 203)

font       = pygame.font.SysFont("arial", 28)
small_font = pygame.font.SysFont("arial", 18)
tiny_font  = pygame.font.SysFont("arial", 14)


# ─────────────────────────────────────────────────────────────────────
#  ENUMS & CONFIG CLASSES (tidak berubah)
# ─────────────────────────────────────────────────────────────────────

class GameState(Enum):
    MENU = 0
    DIFFICULTY_SELECT = 1
    PLAYING = 2
    PAUSED = 3
    WAVE_GAP = 4
    GAME_OVER = 5


class WaveState(Enum):
    IDLE = 1
    SPAWNING = 2
    IN_PROGRESS = 3
    COMPLETED = 4


class Difficulty(Enum):
    EASY = 1
    NORMAL = 2
    HARD = 3


class TargetMode(Enum):
    FIRST = 1
    LAST = 2
    STRONGEST = 3
    CLOSEST = 4


class DifficultyConfig:
    @staticmethod
    def get_config(difficulty):
        configs = {
            Difficulty.EASY: {
                'enemy_health_multiplier': 0.7,
                'enemy_speed_multiplier': 0.8,
                'spawn_rate': 40,
                'starting_money': 200,
                'base_health': 20,
                'difficulty_name': 'EASY'
            },
            Difficulty.NORMAL: {
                'enemy_health_multiplier': 1.0,
                'enemy_speed_multiplier': 1.0,
                'spawn_rate': 30,
                'starting_money': 150,
                'base_health': 10,
                'difficulty_name': 'NORMAL'
            },
            Difficulty.HARD: {
                'enemy_health_multiplier': 1.5,
                'enemy_speed_multiplier': 1.2,
                'spawn_rate': 25,
                'starting_money': 100,
                'base_health': 5,
                'difficulty_name': 'HARD'
            }
        }
        return configs.get(difficulty, configs[Difficulty.NORMAL])
