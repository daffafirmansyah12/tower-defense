"""
sprites.py - Tower Defense Sprite System
================================================

Sistem sprite terpusat dengan graceful fallback ke primitif pygame.
Tidak mengubah logika game.py — hanya mengganti bagian draw().

STRUKTUR FOLDER ASSET:
  assets/
  └── images/
      ├── towers/
      │   ├── ice_tower.png         (60x60, transparan) - menara es biru
      │   ├── ice_tower_l2.png      (60x60) - level 2 upgrade
      │   ├── ice_tower_l3.png      (60x60) - level 3+
      │   ├── fire_tower.png        (60x60) - menara api merah/oranye
      │   ├── fire_tower_l2.png     (60x60)
      │   ├── fire_tower_l3.png     (60x60)
      │   ├── lightning_tower.png   (60x60) - menara petir kuning/cyan
      │   ├── lightning_tower_l2.png
      │   ├── lightning_tower_l3.png
      │   ├── laser_tower.png       (60x60) - menara laser magenta
      │   ├── laser_tower_l2.png
      │   └── laser_tower_l3.png
      │
      ├── enemies/
      │   ├── enemy_fast.png        (40x40) - musuh cepat merah, bentuk ramping
      │   ├── enemy_tank.png        (55x55) - musuh tank ungu, besar & berat
      │   ├── enemy_slow.png        (50x50) - musuh lambat oranye, gemuk
      │   ├── enemy_flying.png      (35x35) - musuh terbang hijau, sayap
      │   ├── enemy_boss.png        (70x70) - boss oranye gelap, besar & detail
      │   ├── enemy_shield.png      (45x45) - musuh biru dengan perisai
      │   ├── enemy_healer.png      (42x42) - musuh pink, tanda plus/heal
      │   ├── enemy_split.png       (45x45) - musuh oranye, tanda split
      │   └── enemy_split_child.png (25x25) - anak split lebih kecil
      │
      └── bullets/
          ├── bullet_ice.png        (12x12) - proyektil es biru
          ├── bullet_fire.png       (12x12) - proyektil api merah
          └── bullet_laser.png      (12x12) - proyektil laser magenta

CATATAN:
- Semua sprite PNG dengan alpha (transparan background)
- Jika file tidak ada → fallback ke primitif pygame otomatis
- Ukuran sprite akan di-scale sesuai ukuran object di game
- Rekomendasi: gunakan sprite pixel art 64x64 lalu di-scale
"""

import pygame
import os

# ─────────────────────────────────────────────
#  SPRITE CACHE & LOADER
# ─────────────────────────────────────────────

_sprite_cache: dict = {}


def _load(path: str, size: tuple | None = None) -> pygame.Surface | None:
    """Load sprite dengan cache. Return None jika tidak ada (fallback ke primitif)."""
    key = (path, size)
    if key in _sprite_cache:
        return _sprite_cache[key]

    if not os.path.exists(path):
        _sprite_cache[key] = None
        return None

    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.smoothscale(img, size)
        _sprite_cache[key] = img
        return img
    except Exception:
        _sprite_cache[key] = None
        return None


def _tower_sprite_path(tower_type: str, level: int) -> str:
    """Pilih path sprite tower berdasarkan type dan level."""
    if level >= 3:
        suffix = '_l3'
    elif level == 2:
        suffix = '_l2'
    else:
        suffix = ''
    return f'assets/images/{tower_type}_tower{suffix}.png'


# ─────────────────────────────────────────────
#  TOWER DRAW FUNCTIONS
# ─────────────────────────────────────────────

def _draw_tower_base(screen: pygame.Surface, tower, color: tuple, size: int = 50):
    """
    Fallback: gambar tower dengan primitif pygame.
    Dibuat lebih menarik dari versi asli.
    """
    x, y = tower._x, tower._y

    # Shadow
    shadow_surf = pygame.Surface((size + 6, size + 6), pygame.SRCALPHA)
    pygame.draw.circle(shadow_surf, (0, 0, 0, 80), (size // 2 + 3, size // 2 + 6), size // 2)
    screen.blit(shadow_surf, (x - size // 2 - 3, y - size // 2 - 3))

    # Base platform (hexagonal-ish)
    base_color = tuple(max(0, c - 60) for c in color[:3])
    pygame.draw.circle(screen, base_color, (x, y), size // 2 + 4)

    # Main body
    pygame.draw.circle(screen, color, (x, y), size // 2)

    # Inner highlight
    highlight = tuple(min(255, c + 80) for c in color[:3])
    pygame.draw.circle(screen, highlight, (x - size // 8, y - size // 8), size // 6)

    # Border
    pygame.draw.circle(screen, (255, 255, 255), (x, y), size // 2, 2)


def _draw_tower_common(screen: pygame.Surface, tower, sprite_surface):
    """Gambar sprite tower beserta range ring, selection, level badge, dan mode indicator."""
    x, y = tower._x, tower._y
    size = sprite_surface.get_width() if sprite_surface else 50

    # ── Range circle
    range_surf = pygame.Surface((tower._range * 2, tower._range * 2), pygame.SRCALPHA)
    pygame.draw.circle(range_surf, (255, 255, 255, 35),
                       (tower._range, tower._range), tower._range)
    pygame.draw.circle(range_surf, (200, 220, 255, 70),
                       (tower._range, tower._range), tower._range, 1)
    screen.blit(range_surf, (x - tower._range, y - tower._range))

    # ── Selection ring
    if tower._is_selected:
        sel_surf = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        t = pygame.time.get_ticks() / 300
        pulse = int(180 + 75 * abs(__import__('math').sin(t)))
        pygame.draw.circle(sel_surf, (255, 220, 0, pulse),
                           (size // 2 + 10, size // 2 + 10),
                           size // 2 + 8, 3)
        screen.blit(sel_surf, (x - size // 2 - 10, y - size // 2 - 10))

    # ── Sprite or fallback
    if sprite_surface:
        screen.blit(sprite_surface, (x - size // 2, y - size // 2))
    # (fallback sudah digambar sebelum memanggil fungsi ini jika sprite=None)

    # ── Level badge (pojok kiri bawah)
    badge_size = 16
    badge_x = x + size // 2 - badge_size - 2
    badge_y = y - size // 2 + 2
    badge_surf = pygame.Surface((badge_size, badge_size), pygame.SRCALPHA)
    pygame.draw.rect(badge_surf, (0, 0, 0, 180), badge_surf.get_rect(), border_radius=4)
    screen.blit(badge_surf, (badge_x, badge_y))
    lv_font = pygame.font.SysFont('arial', 11, bold=True)
    lv_text = lv_font.render(str(tower._level), True, (255, 220, 80))
    screen.blit(lv_text, (badge_x + badge_size // 2 - lv_text.get_width() // 2,
                           badge_y + badge_size // 2 - lv_text.get_height() // 2))

    # ── Target mode indicator (pojok kanan bawah)
    from config import TargetMode
    mode_symbols = {
        TargetMode.FIRST:    ('F', (80, 255, 80)),
        TargetMode.LAST:     ('L', (255, 120, 80)),
        TargetMode.STRONGEST:('S', (255, 80, 200)),
        TargetMode.CLOSEST:  ('C', (80, 200, 255)),
    }
    sym, sym_color = mode_symbols.get(tower._target_mode, ('?', (200, 200, 200)))
    m_font = pygame.font.SysFont('arial', 11, bold=True)
    m_text = m_font.render(sym, True, sym_color)
    m_badge = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.rect(m_badge, (0, 0, 0, 180), m_badge.get_rect(), border_radius=3)
    screen.blit(m_badge, (x - size // 2 + 2, y - size // 2 + 2))
    screen.blit(m_text, (x - size // 2 + 2 + 7 - m_text.get_width() // 2,
                          y - size // 2 + 2 + 7 - m_text.get_height() // 2))


def draw_ice_tower(screen: pygame.Surface, tower):
    size = 50
    sprite = _load(_tower_sprite_path('ice', tower._level), (size, size))
    if not sprite:
        _draw_tower_base(screen, tower, (0, 150, 255), size)
    _draw_tower_common(screen, tower, sprite)


def draw_fire_tower(screen: pygame.Surface, tower):
    size = 50
    sprite = _load(_tower_sprite_path('fire', tower._level), (size, size))
    if not sprite:
        _draw_tower_base(screen, tower, (255, 60, 60), size)
    _draw_tower_common(screen, tower, sprite)


def draw_lightning_tower(screen: pygame.Surface, tower):
    size = 50
    sprite = _load(_tower_sprite_path('lightning', tower._level), (size, size))
    if not sprite:
        _draw_tower_base(screen, tower, (100, 200, 255), size)
    _draw_tower_common(screen, tower, sprite)


def draw_laser_tower(screen: pygame.Surface, tower):
    size = 50
    sprite = _load(_tower_sprite_path('laser', tower._level), (size, size))
    if not sprite:
        _draw_tower_base(screen, tower, (255, 0, 255), size)
    _draw_tower_common(screen, tower, sprite)


# ─────────────────────────────────────────────
#  ENEMY DRAW HELPERS
# ─────────────────────────────────────────────

def _draw_health_bar(screen: pygame.Surface, enemy, y_offset: int = -12):
    """Health bar di atas enemy."""
    bar_w = enemy._size
    bar_h = 5
    bx = int(enemy._x)
    by = int(enemy._y) + y_offset

    # Background
    pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, bar_h), border_radius=2)

    # Fill
    hp_ratio = max(0, enemy._health / enemy._max_health)
    fill_color = (
        int(255 * (1 - hp_ratio)),
        int(220 * hp_ratio),
        0
    )
    if hp_ratio > 0:
        pygame.draw.rect(screen, fill_color,
                         (bx, by, int(bar_w * hp_ratio), bar_h), border_radius=2)

    # Border
    pygame.draw.rect(screen, (180, 180, 180), (bx, by, bar_w, bar_h), 1, border_radius=2)


def _draw_slow_overlay(screen: pygame.Surface, enemy):
    """Overlay biru transparan saat enemy kena slow."""
    if not enemy._is_slowed:
        return
    overlay = pygame.Surface((enemy._size, enemy._size), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (100, 180, 255, 80), overlay.get_rect(), border_radius=8)
    pygame.draw.rect(overlay, (150, 200, 255, 180), overlay.get_rect(), 2, border_radius=8)
    screen.blit(overlay, (int(enemy._x), int(enemy._y)))


def _draw_enemy_sprite(screen, enemy, sprite_path: str, fallback_color: tuple,
                       border_color: tuple | None = None, label: str | None = None,
                       y_offset: float = 0):
    """Helper umum: gambar sprite atau fallback rect, lalu health bar & slow overlay."""
    size = enemy._size
    ex = int(enemy._x)
    ey = int(enemy._y + y_offset)

    sprite = _load(sprite_path, (size, size))

    if sprite:
        screen.blit(sprite, (ex, ey))
    else:
        # Fallback primitif yang lebih menarik
        # Shadow
        sh = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(sh, (0, 0, 0, 60), sh.get_rect(), border_radius=10)
        screen.blit(sh, (ex + 3, ey + 3))
        # Body
        pygame.draw.rect(screen, fallback_color, (ex, ey, size, size), border_radius=10)
        # Shine
        shine = pygame.Surface((size // 2, size // 3), pygame.SRCALPHA)
        pygame.draw.ellipse(shine, (255, 255, 255, 50), shine.get_rect())
        screen.blit(shine, (ex + size // 4, ey + 4))
        # Border
        bc = border_color or tuple(min(255, c + 80) for c in fallback_color[:3])
        pygame.draw.rect(screen, bc, (ex, ey, size, size), 2, border_radius=10)
        # Label
        if label:
            lf = pygame.font.SysFont('arial', 11, bold=True)
            lt = lf.render(label, True, (255, 255, 255))
            screen.blit(lt, (ex + size // 2 - lt.get_width() // 2,
                              ey + size - 14))

    _draw_slow_overlay(screen, enemy)
    _draw_health_bar(screen, enemy, y_offset=int(y_offset) - 10)


# ─────────────────────────────────────────────
#  ENEMY DRAW FUNCTIONS
# ─────────────────────────────────────────────

def draw_fast_enemy(screen: pygame.Surface, enemy):
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_fast.png',
                       (255, 60, 60), (255, 150, 150))


def draw_tank_enemy(screen: pygame.Surface, enemy):
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_tank.png',
                       (180, 0, 255), (220, 100, 255))


def draw_slow_enemy(screen: pygame.Surface, enemy):
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_slow.png',
                       (255, 165, 0), (255, 210, 100))


def draw_flying_enemy(screen: pygame.Surface, enemy):
    """Flying enemy punya hover offset."""
    y_off = getattr(enemy, '_hover_offset', 0)
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_flying.png',
                       (50, 205, 50), (150, 255, 100),
                       y_offset=y_off)


def draw_boss_enemy(screen: pygame.Surface, enemy):
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_boss.png',
                       (255, 140, 0), (255, 220, 0), label='BOSS')

    # Boss: tampilkan HP% di atas bar
    ex, ey = int(enemy._x), int(enemy._y)
    hp_pct = int(enemy._health / enemy._max_health * 100)
    f = pygame.font.SysFont('arial', 10)
    t = f.render(f'{hp_pct}%', True, (255, 255, 255))
    screen.blit(t, (ex + enemy._size - t.get_width() - 2, ey - 22))


def draw_shield_enemy(screen: pygame.Surface, enemy):
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_shield.png',
                       (0, 150, 255), (100, 220, 255))

    # Shield ring overlay (jika shield masih ada)
    if enemy._shield_hp > 0:
        ex = int(enemy._x) + enemy._size // 2
        ey = int(enemy._y) + enemy._size // 2
        t = pygame.time.get_ticks() / 500
        import math
        pulse_r = enemy._size // 2 + 5 + int(3 * math.sin(t))
        ring_surf = pygame.Surface((pulse_r * 2 + 4, pulse_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (0, 220, 255, 160),
                           (pulse_r + 2, pulse_r + 2), pulse_r, 3)
        screen.blit(ring_surf, (ex - pulse_r - 2, ey - pulse_r - 2))

        # Shield HP label
        f = pygame.font.SysFont('arial', 10, bold=True)
        t_surf = f.render(f'S{enemy._shield_hp}', True, (0, 230, 255))
        screen.blit(t_surf, (int(enemy._x) + 3, int(enemy._y) + enemy._size - 14))


def draw_healer_enemy(screen: pygame.Surface, enemy):
    _draw_enemy_sprite(screen, enemy,
                       'assets/images/enemy_healer.png',
                       (255, 192, 203), (255, 150, 180))

    # Heal radius ring
    ex = int(enemy._x) + enemy._size // 2
    ey = int(enemy._y) + enemy._size // 2
    hr = enemy._heal_radius
    ring = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
    pygame.draw.circle(ring, (255, 100, 150, 30), (hr, hr), hr)
    pygame.draw.circle(ring, (255, 100, 150, 80), (hr, hr), hr, 1)
    screen.blit(ring, (ex - hr, ey - hr))

    # Label
    f = pygame.font.SysFont('arial', 10, bold=True)
    t = f.render('HEAL', True, (255, 192, 203))
    screen.blit(t, (int(enemy._x) + 3, int(enemy._y) + enemy._size - 14))


def draw_split_enemy(screen: pygame.Surface, enemy):
    path = ('assets/images/enemy_split_child.png'
            if enemy._is_child else 'assets/images/enemy_split.png')
    color = (255, 165, 0)
    border = (255, 210, 100)
    label = None if enemy._is_child else 'SPLIT'
    _draw_enemy_sprite(screen, enemy, path, color, border, label)


# ─────────────────────────────────────────────
#  BULLET DRAW FUNCTIONS
# ─────────────────────────────────────────────

def draw_bullet_ice(screen: pygame.Surface, bullet):
    sprite = _load('assets/images/bullet_ice.png', (12, 12))
    if sprite:
        screen.blit(sprite, (int(bullet._x) - 6, int(bullet._y) - 6))
    else:
        # Fallback: bola es biru dengan glow
        glow = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (100, 180, 255, 80), (10, 10), 9)
        screen.blit(glow, (int(bullet._x) - 10, int(bullet._y) - 10))
        pygame.draw.circle(screen, (0, 200, 255), (int(bullet._x), int(bullet._y)), 5)
        pygame.draw.circle(screen, (200, 240, 255), (int(bullet._x) - 1, int(bullet._y) - 1), 2)


def draw_bullet_fire(screen: pygame.Surface, bullet):
    sprite = _load('assets/images/bullet_fire.png', (12, 12))
    if sprite:
        screen.blit(sprite, (int(bullet._x) - 6, int(bullet._y) - 6))
    else:
        glow = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 100, 0, 80), (10, 10), 9)
        screen.blit(glow, (int(bullet._x) - 10, int(bullet._y) - 10))
        pygame.draw.circle(screen, (255, 80, 0), (int(bullet._x), int(bullet._y)), 5)
        pygame.draw.circle(screen, (255, 220, 100), (int(bullet._x) - 1, int(bullet._y) - 1), 2)


def draw_bullet_laser(screen: pygame.Surface, bullet):
    sprite = _load('assets/images/bullet_laser.png', (12, 12))
    if sprite:
        screen.blit(sprite, (int(bullet._x) - 6, int(bullet._y) - 6))
    else:
        glow = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(glow, (255, 0, 255, 80), (10, 10), 9)
        screen.blit(glow, (int(bullet._x) - 10, int(bullet._y) - 10))
        pygame.draw.circle(screen, (255, 0, 200), (int(bullet._x), int(bullet._y)), 5)
        pygame.draw.circle(screen, (255, 180, 255), (int(bullet._x) - 1, int(bullet._y) - 1), 2)


def draw_bullet_default(screen: pygame.Surface, bullet):
    """Fallback untuk bullet biasa (misal dari IceTower/FireTower jika tidak dispesifikasi)."""
    glow = pygame.Surface((16, 16), pygame.SRCALPHA)
    pygame.draw.circle(glow, (255, 255, 100, 80), (8, 8), 7)
    screen.blit(glow, (int(bullet._x) - 8, int(bullet._y) - 8))
    pygame.draw.circle(screen, (255, 230, 0), (int(bullet._x), int(bullet._y)), 5)
