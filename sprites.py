"""
sprites.py - Tower Defense Sprite System (Pure Pygame Visual)
=============================================================
Semua visual digambar pure pygame — tidak perlu file PNG sama sekali.
Tetap support PNG jika tersedia di assets/images/ (auto fallback).
"""

import pygame
import math
import os

# ─────────────────────────────────────────────
#  SPRITE CACHE & LOADER
# ─────────────────────────────────────────────

_sprite_cache: dict = {}


def _load(path: str, size: tuple | None = None) -> pygame.Surface | None:
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
    suffix = '_l3' if level >= 3 else '_l2' if level == 2 else ''
    return f'assets/images/{tower_type}_tower{suffix}.png'


def _load_tower_sprite(tower_type: str, level: int, size: int) -> 'pygame.Surface | None':
    """Load tower sprite sesuai level. Fallback otomatis ke level lebih rendah."""
    path = _tower_sprite_path(tower_type, level)
    sprite = _load(path, (size, size))
    if sprite is None and level >= 3:
        sprite = _load(_tower_sprite_path(tower_type, 2), (size, size))
    if sprite is None and level >= 2:
        sprite = _load(_tower_sprite_path(tower_type, 1), (size, size))
    return sprite


# ─────────────────────────────────────────────
#  SHARED HELPERS
# ─────────────────────────────────────────────

def _glow(screen, x, y, radius, color, alpha=80):
    s = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(s, (*color[:3], alpha), (radius, radius), radius)
    screen.blit(s, (x - radius, y - radius))


def _draw_tower_common(screen, tower, sprite_surface):
    x, y = tower._x, tower._y
    size = sprite_surface.get_width() if sprite_surface else 50

    # Range circle
    range_surf = pygame.Surface((tower._range * 2, tower._range * 2), pygame.SRCALPHA)
    pygame.draw.circle(range_surf, (255, 255, 255, 25),
                       (tower._range, tower._range), tower._range)
    pygame.draw.circle(range_surf, (200, 220, 255, 60),
                       (tower._range, tower._range), tower._range, 1)
    screen.blit(range_surf, (x - tower._range, y - tower._range))

    # Selection ring
    if tower._is_selected:
        sel_surf = pygame.Surface((size + 24, size + 24), pygame.SRCALPHA)
        t = pygame.time.get_ticks() / 300
        pulse = int(180 + 75 * abs(math.sin(t)))
        pygame.draw.circle(sel_surf, (255, 220, 0, pulse),
                           (size // 2 + 12, size // 2 + 12), size // 2 + 10, 3)
        screen.blit(sel_surf, (x - size // 2 - 12, y - size // 2 - 12))

    # Sprite jika ada
    if sprite_surface:
        screen.blit(sprite_surface, (x - size // 2, y - size // 2))

    # Level badge
    badge_size = 16
    bx = x + size // 2 - badge_size - 2
    by = y - size // 2 + 2
    badge_surf = pygame.Surface((badge_size, badge_size), pygame.SRCALPHA)
    pygame.draw.rect(badge_surf, (0, 0, 0, 180), badge_surf.get_rect(), border_radius=4)
    screen.blit(badge_surf, (bx, by))
    lv_font = pygame.font.SysFont('arial', 11, bold=True)
    lv_text = lv_font.render(str(tower._level), True, (255, 220, 80))
    screen.blit(lv_text, (bx + badge_size // 2 - lv_text.get_width() // 2,
                           by + badge_size // 2 - lv_text.get_height() // 2))

    # Target mode indicator
    from config import TargetMode
    mode_symbols = {
        TargetMode.FIRST:     ('F', (80, 255, 80)),
        TargetMode.LAST:      ('L', (255, 120, 80)),
        TargetMode.STRONGEST: ('S', (255, 80, 200)),
        TargetMode.CLOSEST:   ('C', (80, 200, 255)),
    }
    sym, sym_color = mode_symbols.get(tower._target_mode, ('?', (200, 200, 200)))
    m_font = pygame.font.SysFont('arial', 11, bold=True)
    m_text = m_font.render(sym, True, sym_color)
    m_badge = pygame.Surface((14, 14), pygame.SRCALPHA)
    pygame.draw.rect(m_badge, (0, 0, 0, 180), m_badge.get_rect(), border_radius=3)
    screen.blit(m_badge, (x - size // 2 + 2, y - size // 2 + 2))
    screen.blit(m_text, (x - size // 2 + 9 - m_text.get_width() // 2,
                          y - size // 2 + 9 - m_text.get_height() // 2))


# ─────────────────────────────────────────────
#  ICE TOWER — menara kristal biru
# ─────────────────────────────────────────────

def draw_ice_tower(screen, tower):
    size = 50
    sprite = _load_tower_sprite('ice', tower._level, size)
    if not sprite:
        x, y = tower._x, tower._y
        t = pygame.time.get_ticks() / 800

        # Glow biru
        _glow(screen, x, y, 30, (0, 180, 255), 60)

        # Base platform
        pygame.draw.circle(screen, (10, 40, 80), (x, y), 24)
        pygame.draw.circle(screen, (0, 80, 160), (x, y), 22)

        # Kristal utama (segi enam)
        crystal_points = []
        for i in range(6):
            angle = math.radians(i * 60 + t * 20)
            cx = x + int(14 * math.cos(angle))
            cy = y + int(14 * math.sin(angle))
            crystal_points.append((cx, cy))
        pygame.draw.polygon(screen, (0, 150, 255), crystal_points)
        pygame.draw.polygon(screen, (100, 220, 255), crystal_points, 2)

        # Kristal kecil di atas
        tip_points = [
            (x, y - 22),
            (x - 6, y - 12),
            (x + 6, y - 12),
        ]
        pygame.draw.polygon(screen, (150, 230, 255), tip_points)

        # Kilap
        pygame.draw.circle(screen, (200, 240, 255), (x - 4, y - 6), 4)
        pygame.draw.circle(screen, (255, 255, 255), (x - 5, y - 7), 2)

        # Level color upgrade
        if tower._level >= 2:
            _glow(screen, x, y, 28, (0, 220, 255), 40)
        if tower._level >= 3:
            for i in range(4):
                angle = math.radians(i * 90 + t * 60)
                sx = x + int(20 * math.cos(angle))
                sy = y + int(20 * math.sin(angle))
                pygame.draw.circle(screen, (180, 240, 255), (sx, sy), 3)

    _draw_tower_common(screen, tower, sprite)


# ─────────────────────────────────────────────
#  FIRE TOWER — menara tungku api merah
# ─────────────────────────────────────────────

def draw_fire_tower(screen, tower):
    size = 50
    sprite = _load_tower_sprite('fire', tower._level, size)
    if not sprite:
        x, y = tower._x, tower._y
        t = pygame.time.get_ticks() / 200

        # Glow oranye
        _glow(screen, x, y, 30, (255, 80, 0), 70)

        # Base batu
        pygame.draw.circle(screen, (60, 20, 0), (x, y + 2), 24)
        pygame.draw.circle(screen, (100, 30, 0), (x, y), 22)

        # Badan menara (trapezoid)
        body = [
            (x - 10, y + 14),
            (x + 10, y + 14),
            (x + 7,  y - 8),
            (x - 7,  y - 8),
        ]
        pygame.draw.polygon(screen, (160, 50, 0), body)
        pygame.draw.polygon(screen, (220, 80, 0), body, 2)

        # Api beranimasi (3 lidah api)
        flame_offsets = [(-6, 0), (0, -4), (6, 0)]
        flame_colors = [(255, 60, 0), (255, 140, 0), (255, 220, 0)]
        for i, (ox, _) in enumerate(flame_offsets):
            flicker = int(4 * math.sin(t + i * 2))
            pts = [
                (x + ox, y - 8),
                (x + ox - 4, y - 14 - flicker),
                (x + ox, y - 20 - flicker),
                (x + ox + 4, y - 14 - flicker),
            ]
            pygame.draw.polygon(screen, flame_colors[i], pts)

        # Bara di tengah
        pygame.draw.circle(screen, (255, 200, 50), (x, y + 2), 5)
        pygame.draw.circle(screen, (255, 255, 150), (x, y + 2), 2)

        if tower._level >= 2:
            _glow(screen, x, y, 30, (255, 120, 0), 50)
        if tower._level >= 3:
            for i in range(3):
                angle = math.radians(i * 120 + t * 30)
                sx = x + int(18 * math.cos(angle))
                sy = y + int(18 * math.sin(angle))
                pygame.draw.circle(screen, (255, 180, 0), (sx, sy), 3)

    _draw_tower_common(screen, tower, sprite)


# ─────────────────────────────────────────────
#  LIGHTNING TOWER — antena petir cyan
# ─────────────────────────────────────────────

def draw_lightning_tower(screen, tower):
    size = 50
    sprite = _load_tower_sprite('lightning', tower._level, size)
    if not sprite:
        x, y = tower._x, tower._y
        t = pygame.time.get_ticks() / 150

        # Glow cyan
        _glow(screen, x, y, 30, (0, 220, 255), 60)

        # Base
        pygame.draw.circle(screen, (10, 50, 60), (x, y), 24)
        pygame.draw.circle(screen, (0, 100, 140), (x, y), 22)

        # Tiang antena
        pygame.draw.rect(screen, (0, 160, 200), (x - 3, y - 18, 6, 26))

        # Sayap antena (3 pasang)
        for i, dy in enumerate([-14, -6, 2]):
            w = 12 - i * 2
            pygame.draw.line(screen, (0, 200, 240), (x - w, y + dy), (x + w, y + dy), 2)

        # Ujung antena berkilat
        flash = int(abs(math.sin(t))) == 0
        tip_color = (255, 255, 100) if flash else (0, 230, 255)
        pygame.draw.circle(screen, tip_color, (x, y - 18), 5)
        if flash:
            _glow(screen, x, y - 18, 12, (255, 255, 100), 120)

        # Percikan petir kecil
        if int(t * 3) % 4 == 0:
            for _ in range(2):
                import random
                sx = x + random.randint(-15, 15)
                sy = y + random.randint(-15, 10)
                pygame.draw.line(screen, (200, 240, 255), (x, y - 10), (sx, sy), 1)

        if tower._level >= 2:
            _glow(screen, x, y, 28, (100, 255, 255), 40)
        if tower._level >= 3:
            ring_surf = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (0, 220, 255, 80), (30, 30), 28, 2)
            screen.blit(ring_surf, (x - 30, y - 30))

    _draw_tower_common(screen, tower, sprite)


# ─────────────────────────────────────────────
#  LASER TOWER — cannon laser magenta
# ─────────────────────────────────────────────

def draw_laser_tower(screen, tower):
    size = 50
    sprite = _load_tower_sprite('laser', tower._level, size)
    if not sprite:
        x, y = tower._x, tower._y
        t = pygame.time.get_ticks() / 500

        # Glow magenta
        _glow(screen, x, y, 32, (200, 0, 255), 70)

        # Base hexagonal
        hex_pts = []
        for i in range(6):
            angle = math.radians(i * 60 + 30)
            hex_pts.append((x + int(22 * math.cos(angle)),
                             y + int(22 * math.sin(angle))))
        pygame.draw.polygon(screen, (50, 0, 80), hex_pts)
        pygame.draw.polygon(screen, (150, 0, 200), hex_pts, 2)

        # Badan cannon (silinder)
        pygame.draw.rect(screen, (100, 0, 150), (x - 8, y - 12, 16, 20), border_radius=4)

        # Laras cannon
        barrel_len = 16 + int(3 * math.sin(t))
        pygame.draw.rect(screen, (180, 0, 220), (x - 4, y - 24 - barrel_len + 12, 8, barrel_len), border_radius=3)

        # Lingkaran energi di tengah
        pulse = int(180 + 75 * abs(math.sin(t * 2)))
        energy = pygame.Surface((20, 20), pygame.SRCALPHA)
        pygame.draw.circle(energy, (220, 0, 255, pulse), (10, 10), 8)
        screen.blit(energy, (x - 10, y - 10))
        pygame.draw.circle(screen, (255, 150, 255), (x, y), 4)

        # Detail moncong
        pygame.draw.circle(screen, (255, 0, 255), (x, y - 22), 4)
        pygame.draw.circle(screen, (255, 200, 255), (x, y - 22), 2)

        if tower._level >= 2:
            _glow(screen, x, y, 30, (255, 0, 255), 50)
        if tower._level >= 3:
            for i in range(4):
                angle = math.radians(i * 90 + t * 40)
                sx = x + int(20 * math.cos(angle))
                sy = y + int(20 * math.sin(angle))
                _glow(screen, sx, sy, 6, (255, 0, 255), 150)

    _draw_tower_common(screen, tower, sprite)


# ─────────────────────────────────────────────
#  ENEMY HELPERS
# ─────────────────────────────────────────────

def _draw_health_bar(screen, enemy, y_offset=-12):
    bar_w = enemy._size
    bar_h = 5
    bx = int(enemy._x)
    by = int(enemy._y) + y_offset
    pygame.draw.rect(screen, (60, 0, 0), (bx, by, bar_w, bar_h), border_radius=2)
    hp_ratio = max(0, enemy._health / enemy._max_health)
    fill_color = (int(255 * (1 - hp_ratio)), int(220 * hp_ratio), 0)
    if hp_ratio > 0:
        pygame.draw.rect(screen, fill_color,
                         (bx, by, int(bar_w * hp_ratio), bar_h), border_radius=2)
    pygame.draw.rect(screen, (180, 180, 180), (bx, by, bar_w, bar_h), 1, border_radius=2)


def _draw_slow_overlay(screen, enemy):
    if not enemy._is_slowed:
        return
    overlay = pygame.Surface((enemy._size, enemy._size), pygame.SRCALPHA)
    pygame.draw.rect(overlay, (100, 180, 255, 80), overlay.get_rect(), border_radius=8)
    pygame.draw.rect(overlay, (150, 200, 255, 180), overlay.get_rect(), 2, border_radius=8)
    screen.blit(overlay, (int(enemy._x), int(enemy._y)))


def _draw_enemy_sprite(screen, enemy, sprite_path, fallback_fn,
                       y_offset=0):
    """Coba load PNG, fallback ke fungsi gambar custom."""
    size = enemy._size
    ex = int(enemy._x)
    ey = int(enemy._y + y_offset)
    sprite = _load(sprite_path, (size, size))
    if sprite:
        screen.blit(sprite, (ex, ey))
    else:
        fallback_fn(screen, ex, ey, size, enemy)
    _draw_slow_overlay(screen, enemy)
    _draw_health_bar(screen, enemy, y_offset=int(y_offset) - 10)


# ─────────────────────────────────────────────
#  ENEMY DRAW FUNCTIONS
# ─────────────────────────────────────────────

def draw_fast_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        # Bentuk berlian merah — ramping & tajam
        cx, cy = ex + size // 2, ey + size // 2
        pts = [
            (cx, cy - size // 2),
            (cx + size // 3, cy),
            (cx, cy + size // 2),
            (cx - size // 3, cy),
        ]
        pygame.draw.polygon(screen, (220, 40, 40), pts)
        pygame.draw.polygon(screen, (255, 120, 120), pts, 2)
        # Garis kecepatan
        for i in range(3):
            lx = ex + 4 + i * 5
            pygame.draw.line(screen, (255, 180, 180),
                             (lx, cy - 4), (lx - 8, cy + 4), 1)
        pygame.draw.circle(screen, (255, 200, 200), (cx, cy), 4)

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_fast.png', _draw)


def draw_tank_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        # Badan besar kotak berat
        pygame.draw.rect(screen, (100, 0, 180), (ex + 4, ey + 4, size - 8, size - 8), border_radius=6)
        pygame.draw.rect(screen, (160, 60, 255), (ex + 4, ey + 4, size - 8, size - 8), 2, border_radius=6)
        # Pelat baju besi
        for i in range(2):
            pygame.draw.rect(screen, (130, 20, 200),
                             (ex + 6, ey + 8 + i * 10, size - 12, 6), border_radius=3)
        # Kepala
        pygame.draw.circle(screen, (180, 80, 255), (cx, cy - 4), size // 5)
        pygame.draw.circle(screen, (220, 140, 255), (cx, cy - 4), size // 5, 2)

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_tank.png', _draw)


def draw_slow_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        # Bentuk gemuk bulat
        pygame.draw.ellipse(screen, (200, 120, 0), (ex + 2, ey + 6, size - 4, size - 8))
        pygame.draw.ellipse(screen, (255, 180, 50), (ex + 2, ey + 6, size - 4, size - 8), 2)
        # Perut
        pygame.draw.ellipse(screen, (230, 160, 20), (ex + 8, ey + 12, size - 16, size // 3))
        # Mata
        pygame.draw.circle(screen, (255, 255, 100), (cx - 6, cy - 2), 4)
        pygame.draw.circle(screen, (255, 255, 100), (cx + 6, cy - 2), 4)
        pygame.draw.circle(screen, (0, 0, 0), (cx - 5, cy - 2), 2)
        pygame.draw.circle(screen, (0, 0, 0), (cx + 7, cy - 2), 2)

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_slow.png', _draw)


def draw_flying_enemy(screen, enemy):
    y_off = getattr(enemy, '_hover_offset', 0)

    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        t = pygame.time.get_ticks() / 200
        flap = int(6 * math.sin(t))
        # Sayap kiri
        wing_l = [(cx, cy), (cx - size // 2 - 4, cy - 10 + flap), (cx - size // 3, cy + 6)]
        pygame.draw.polygon(screen, (30, 160, 30), wing_l)
        pygame.draw.polygon(screen, (100, 230, 100), wing_l, 1)
        # Sayap kanan
        wing_r = [(cx, cy), (cx + size // 2 + 4, cy - 10 + flap), (cx + size // 3, cy + 6)]
        pygame.draw.polygon(screen, (30, 160, 30), wing_r)
        pygame.draw.polygon(screen, (100, 230, 100), wing_r, 1)
        # Badan
        pygame.draw.ellipse(screen, (50, 200, 50), (cx - 8, cy - 10, 16, 20))
        pygame.draw.ellipse(screen, (150, 255, 150), (cx - 8, cy - 10, 16, 20), 2)
        # Mata
        pygame.draw.circle(screen, (255, 255, 0), (cx - 3, cy - 4), 3)
        pygame.draw.circle(screen, (0, 0, 0), (cx - 2, cy - 4), 1)

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_flying.png', _draw, y_offset=y_off)


def draw_boss_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        t = pygame.time.get_ticks() / 300
        # Aura boss
        aura = pygame.Surface((size + 20, size + 20), pygame.SRCALPHA)
        pulse = int(60 + 40 * abs(math.sin(t)))
        pygame.draw.circle(aura, (255, 140, 0, pulse), (size // 2 + 10, size // 2 + 10), size // 2 + 8)
        screen.blit(aura, (ex - 10, ey - 10))
        # Badan besar
        pygame.draw.rect(screen, (180, 80, 0), (ex + 2, ey + 2, size - 4, size - 4), border_radius=8)
        pygame.draw.rect(screen, (255, 160, 0), (ex + 2, ey + 2, size - 4, size - 4), 3, border_radius=8)
        # Mahkota
        crown_pts = [
            (cx - 14, ey + 8),
            (cx - 14, ey),
            (cx - 8, ey + 5),
            (cx, ey - 2),
            (cx + 8, ey + 5),
            (cx + 14, ey),
            (cx + 14, ey + 8),
        ]
        pygame.draw.polygon(screen, (255, 200, 0), crown_pts)
        pygame.draw.polygon(screen, (255, 255, 100), crown_pts, 2)
        # Mata merah
        pygame.draw.circle(screen, (255, 30, 0), (cx - 8, cy - 4), 6)
        pygame.draw.circle(screen, (255, 30, 0), (cx + 8, cy - 4), 6)
        pygame.draw.circle(screen, (255, 200, 0), (cx - 8, cy - 4), 3)
        pygame.draw.circle(screen, (255, 200, 0), (cx + 8, cy - 4), 3)
        # HP%
        hp_pct = int(enemy._health / enemy._max_health * 100)
        f = pygame.font.SysFont('arial', 10, bold=True)
        t_surf = f.render(f'BOSS {hp_pct}%', True, (255, 255, 255))
        screen.blit(t_surf, (ex + size // 2 - t_surf.get_width() // 2, ey - 22))

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_boss.png', _draw)


def draw_shield_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        # Badan biru
        pygame.draw.rect(screen, (0, 80, 180), (ex + 4, ey + 4, size - 8, size - 8), border_radius=8)
        pygame.draw.rect(screen, (0, 160, 255), (ex + 4, ey + 4, size - 8, size - 8), 2, border_radius=8)
        # Perisai
        if enemy._shield_hp > 0:
            shield_pts = [
                (cx, ey + 2),
                (cx + 14, ey + 8),
                (cx + 14, cy),
                (cx, cy + 14),
                (cx - 14, cy),
                (cx - 14, ey + 8),
            ]
            shield_surf = pygame.Surface((size + 10, size + 10), pygame.SRCALPHA)
            pygame.draw.polygon(screen, (0, 200, 255), shield_pts, 3)
            t = pygame.time.get_ticks() / 500
            pulse_r = size // 2 + 5 + int(3 * math.sin(t))
            ring_surf = pygame.Surface((pulse_r * 2 + 4, pulse_r * 2 + 4), pygame.SRCALPHA)
            pygame.draw.circle(ring_surf, (0, 220, 255, 160),
                               (pulse_r + 2, pulse_r + 2), pulse_r, 3)
            screen.blit(ring_surf, (cx - pulse_r - 2, cy - pulse_r - 2))
            f = pygame.font.SysFont('arial', 10, bold=True)
            t_surf = f.render(f'S{enemy._shield_hp}', True, (0, 230, 255))
            screen.blit(t_surf, (ex + 3, ey + size - 14))
        # Wajah
        pygame.draw.circle(screen, (100, 200, 255), (cx, cy - 2), size // 5)

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_shield.png', _draw)

    # Shield ring overlay terpisah (tetap tampil)
    if enemy._shield_hp > 0:
        cx = int(enemy._x) + enemy._size // 2
        cy = int(enemy._y) + enemy._size // 2
        t = pygame.time.get_ticks() / 500
        pulse_r = enemy._size // 2 + 5 + int(3 * math.sin(t))
        ring_surf = pygame.Surface((pulse_r * 2 + 4, pulse_r * 2 + 4), pygame.SRCALPHA)
        pygame.draw.circle(ring_surf, (0, 220, 255, 80),
                           (pulse_r + 2, pulse_r + 2), pulse_r, 3)
        screen.blit(ring_surf, (cx - pulse_r - 2, cy - pulse_r - 2))


def draw_healer_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        # Badan pink
        pygame.draw.ellipse(screen, (220, 120, 160), (ex + 2, ey + 4, size - 4, size - 6))
        pygame.draw.ellipse(screen, (255, 180, 210), (ex + 2, ey + 4, size - 4, size - 6), 2)
        # Tanda plus (heal)
        arm = size // 5
        pygame.draw.rect(screen, (255, 255, 255), (cx - arm, cy - 3, arm * 2, 6), border_radius=2)
        pygame.draw.rect(screen, (255, 255, 255), (cx - 3, cy - arm, 6, arm * 2), border_radius=2)
        # Mata
        pygame.draw.circle(screen, (255, 80, 120), (cx - 5, cy - 6), 3)
        pygame.draw.circle(screen, (255, 80, 120), (cx + 5, cy - 6), 3)
        # Heal radius ring
        hr = enemy._heal_radius
        ring = pygame.Surface((hr * 2, hr * 2), pygame.SRCALPHA)
        pygame.draw.circle(ring, (255, 100, 150, 25), (hr, hr), hr)
        pygame.draw.circle(ring, (255, 100, 150, 70), (hr, hr), hr, 1)
        screen.blit(ring, (cx - hr, cy - hr))

    _draw_enemy_sprite(screen, enemy, 'assets/images/enemy_healer.png', _draw)


def draw_split_enemy(screen, enemy):
    def _draw(screen, ex, ey, size, enemy):
        cx, cy = ex + size // 2, ey + size // 2
        col = (180, 100, 0) if enemy._is_child else (220, 130, 0)
        border = (255, 180, 50)
        # Bentuk diamond
        pts = [
            (cx, ey + 2),
            (ex + size - 2, cy),
            (cx, ey + size - 2),
            (ex + 2, cy),
        ]
        pygame.draw.polygon(screen, col, pts)
        pygame.draw.polygon(screen, border, pts, 2)
        if not enemy._is_child:
            # Tanda split (dua panah)
            pygame.draw.line(screen, (255, 255, 255), (cx, cy), (cx - 6, cy - 5), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx, cy), (cx + 6, cy - 5), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx, cy), (cx - 6, cy + 5), 2)
            pygame.draw.line(screen, (255, 255, 255), (cx, cy), (cx + 6, cy + 5), 2)

    path = ('assets/images/enemy_split_child.png' if enemy._is_child
            else 'assets/images/enemy_split.png')
    _draw_enemy_sprite(screen, enemy, path, _draw)


# ─────────────────────────────────────────────
#  BULLET DRAW FUNCTIONS
# ─────────────────────────────────────────────

def draw_bullet_ice(screen, bullet):
    sprite = _load('assets/images/bullet_ice.png', (12, 12))
    if sprite:
        screen.blit(sprite, (int(bullet._x) - 6, int(bullet._y) - 6))
    else:
        bx, by = int(bullet._x), int(bullet._y)
        _glow(screen, bx, by, 10, (0, 180, 255), 80)
        pygame.draw.circle(screen, (0, 200, 255), (bx, by), 5)
        pygame.draw.circle(screen, (200, 240, 255), (bx - 1, by - 1), 2)
        # Shard kecil
        for i in range(4):
            angle = math.radians(i * 90 + pygame.time.get_ticks() / 100)
            sx = bx + int(7 * math.cos(angle))
            sy = by + int(7 * math.sin(angle))
            pygame.draw.circle(screen, (150, 230, 255), (sx, sy), 1)


def draw_bullet_fire(screen, bullet):
    sprite = _load('assets/images/bullet_fire.png', (12, 12))
    if sprite:
        screen.blit(sprite, (int(bullet._x) - 6, int(bullet._y) - 6))
    else:
        bx, by = int(bullet._x), int(bullet._y)
        _glow(screen, bx, by, 10, (255, 80, 0), 80)
        pygame.draw.circle(screen, (255, 80, 0), (bx, by), 5)
        pygame.draw.circle(screen, (255, 220, 100), (bx - 1, by - 1), 2)
        # Ekor api
        t = pygame.time.get_ticks() / 100
        pygame.draw.circle(screen, (255, 140, 0),
                           (bx + int(3 * math.cos(t)), by + int(3 * math.sin(t))), 3)


def draw_bullet_laser(screen, bullet):
    sprite = _load('assets/images/bullet_laser.png', (12, 12))
    if sprite:
        screen.blit(sprite, (int(bullet._x) - 6, int(bullet._y) - 6))
    else:
        bx, by = int(bullet._x), int(bullet._y)
        _glow(screen, bx, by, 10, (200, 0, 255), 80)
        pygame.draw.circle(screen, (255, 0, 200), (bx, by), 5)
        pygame.draw.circle(screen, (255, 180, 255), (bx - 1, by - 1), 2)


def draw_bullet_default(screen, bullet):
    bx, by = int(bullet._x), int(bullet._y)
    _glow(screen, bx, by, 8, (255, 230, 0), 70)
    pygame.draw.circle(screen, (255, 230, 0), (bx, by), 5)
    pygame.draw.circle(screen, (255, 255, 200), (bx - 1, by - 1), 2)
