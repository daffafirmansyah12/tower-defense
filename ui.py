"""
ui.py - Tower Defense UI & Menu System
=============================================

GAMBAR YANG DIBUTUHKAN (taruh di folder /assets/images/):
----------------------------------------------------------
BACKGROUND & MENU:
  - assets/images/menu_bg.png         → Background utama menu (1000x600), Medieval Theme
  - assets/images/menu_logo.png       → Logo "Tower Defense" (500x150), bisa PNG transparan
  - assets/images/stars_overlay.png   → Overlay bintang-bintang animasi (1000x600, transparan)
  - assets/images/planet_bg.png       → Planet dekoratif di background menu (300x300, transparan)

TOMBOL (bisa satu spritesheet atau file terpisah):
  - assets/images/btn_normal.png      → Tombol state normal (220x50)
  - assets/images/btn_hover.png       → Tombol state hover/highlighted (220x50)
  - assets/images/btn_pressed.png     → Tombol state ditekan (220x50)
  - assets/images/btn_disabled.png    → Tombol state disabled/abu-abu (220x50)

ICON UI:
  - assets/images/icon_coin.png       → Ikon koin/money (24x24)
  - assets/images/icon_heart.png      → Ikon health/nyawa (24x24)
  - assets/images/icon_wave.png       → Ikon wave/gelombang (24x24)
  - assets/images/icon_tower.png      → Ikon tower (24x24)
  - assets/images/icon_clock.png      → Ikon waktu/timer (24x24)
  - assets/images/icon_skull.png      → Ikon enemies killed (24x24)
  - assets/images/icon_star.png       → Ikon score/bintang (24x24)

PANEL & FRAME:
  - assets/images/panel_dark.png      → Panel gelap untuk dialog/overlay (9-slice: 400x300)
  - assets/images/panel_glow.png      → Panel dengan glow effect (9-slice: 400x300)
  - assets/images/hud_bar.png         → Bar atas HUD background (1000x85)
  - assets/images/hud_bottom.png      → Bar bawah HUD background (1000x55)

ENEMY PREVIEW (untuk wave preview):
  - assets/images/enemy_fast.png      → Icon enemy fast (32x32)
  - assets/images/enemy_tank.png      → Icon enemy tank (32x32)
  - assets/images/enemy_flying.png    → Icon enemy flying (32x32)
  - assets/images/enemy_boss.png      → Icon enemy boss (32x32)
  - assets/images/enemy_shield.png    → Icon enemy shield (32x32)
  - assets/images/enemy_heal.png      → Icon enemy healer (32x32)
  - assets/images/enemy_split.png     → Icon enemy split (32x32)
  - assets/images/enemy_slow.png      → Icon enemy slow (32x32)

EFEK:
  - assets/images/particle.png        → Titik partikel untuk animasi (4x4, putih)
  - assets/images/glow_circle.png     → Glow bulat untuk efek highlight (64x64, transparan)
  - assets/images/scanline.png        → Overlay scanline efek retro (1000x600, transparan)

CATATAN: Semua gambar yang tidak ada akan di-fallback ke bentuk primitif pygame (rect/circle/text),
         sehingga game tetap bisa berjalan tanpa gambar.
"""

import pygame
import math
import time
import os
from config import *


# ─────────────────────────────────────────────
#  ASSET LOADER (dengan fallback graceful)
# ─────────────────────────────────────────────

class AssetLoader:
    """Load gambar dengan fallback jika file tidak ditemukan."""
    _cache = {}

    @staticmethod
    def load(path, size=None):
        key = (path, size)
        if key in AssetLoader._cache:
            return AssetLoader._cache[key]

        if os.path.exists(path):
            try:
                img = pygame.image.load(path).convert_alpha()
                if size:
                    img = pygame.transform.smoothscale(img, size)
                AssetLoader._cache[key] = img
                return img
            except Exception:
                pass
        return None  # fallback ke primitif


# ─────────────────────────────────────────────
#  WARNA & TEMA
# ─────────────────────────────────────────────

THEME = {
    'bg_dark':       (8, 8, 20),
    'bg_panel':      (15, 15, 35, 200),
    'border':        (0, 180, 255),
    'border_glow':   (0, 100, 200),
    'btn_normal':    (20, 40, 80),
    'btn_hover':     (0, 120, 220),
    'btn_pressed':   (0, 80, 160),
    'btn_danger':    (140, 20, 20),
    'btn_danger_h':  (200, 40, 40),
    'btn_success':   (20, 100, 40),
    'btn_success_h': (30, 160, 60),
    'btn_text':      (220, 240, 255),
    'title':         (0, 220, 255),
    'subtitle':      (150, 200, 255),
    'accent':        (255, 200, 0),
    'warning':       (255, 140, 0),
    'danger':        (255, 60, 60),
    'success':       (0, 220, 100),
    'money':         (255, 215, 0),
    'health':        (255, 60, 60),
    'info':          (100, 200, 255),
    'muted':         (100, 120, 150),
}


def hex_color(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


# ─────────────────────────────────────────────
#  FONT SYSTEM
# ─────────────────────────────────────────────

class Fonts:
    _loaded = {}

    @staticmethod
    def get(name='arial', size=20, bold=False):
        key = (name, size, bold)
        if key not in Fonts._loaded:
            try:
                Fonts._loaded[key] = pygame.font.SysFont(name, size, bold=bold)
            except Exception:
                Fonts._loaded[key] = pygame.font.SysFont('arial', size, bold=bold)
        return Fonts._loaded[key]

    title    = None  # di-init setelah pygame.init()
    heading  = None
    body     = None
    small    = None
    tiny     = None

    @classmethod
    def init(cls):
        cls.title   = cls.get('impact', 52, bold=False)
        cls.heading = cls.get('arial', 30, bold=True)
        cls.body    = cls.get('arial', 22)
        cls.small   = cls.get('arial', 17)
        cls.tiny    = cls.get('arial', 13)


# ─────────────────────────────────────────────
#  HELPER DRAWING
# ─────────────────────────────────────────────

def draw_panel(surface, rect, alpha=210, border_color=None, border_width=2, radius=12):
    """Panel gelap dengan border glow."""
    panel = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel, (*THEME['bg_dark'], alpha), panel.get_rect(), border_radius=radius)
    surface.blit(panel, rect.topleft)

    bc = border_color or THEME['border']
    pygame.draw.rect(surface, bc, rect, border_width, border_radius=radius)


def draw_text_centered(surface, text, font, color, cx, cy):
    surf = font.render(text, True, color)
    r = surf.get_rect(center=(cx, cy))
    surface.blit(surf, r)


def draw_text_left(surface, text, font, color, x, y):
    surf = font.render(text, True, color)
    surface.blit(surf, (x, y))


def draw_glow_text(surface, text, font, color, cx, cy, glow_color=None, glow_radius=3):
    """Teks dengan efek glow blur sederhana."""
    gc = glow_color or (*color[:3], 80)
    for dx in range(-glow_radius, glow_radius+1, 2):
        for dy in range(-glow_radius, glow_radius+1, 2):
            if dx or dy:
                s = font.render(text, True, gc[:3])
                s.set_alpha(60)
                r = s.get_rect(center=(cx+dx, cy+dy))
                surface.blit(s, r)
    surf = font.render(text, True, color)
    r = surf.get_rect(center=(cx, cy))
    surface.blit(surf, r)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i]) * t) for i in range(3))


def draw_progress_bar(surface, rect, value, max_value, fg_color, bg_color=(40,40,60), radius=4):
    pygame.draw.rect(surface, bg_color, rect, border_radius=radius)
    if max_value > 0:
        fill_w = int(rect.width * (value / max_value))
        if fill_w > 0:
            fill_rect = pygame.Rect(rect.x, rect.y, fill_w, rect.height)
            pygame.draw.rect(surface, fg_color, fill_rect, border_radius=radius)
    pygame.draw.rect(surface, THEME['border'], rect, 1, border_radius=radius)


def draw_stars_bg(surface, stars, t):
    """Gambar background bintang bergerak."""
    surface.fill(THEME['bg_dark'])
    for (x, y, speed, size, brightness) in stars:
        twinkle = int(brightness * (0.7 + 0.3 * math.sin(t * speed * 2 + x)))
        c = (twinkle, twinkle, twinkle)
        if size == 1:
            surface.set_at((int(x), int(y)), c)
        else:
            pygame.draw.circle(surface, c, (int(x), int(y)), size)


def init_stars(count=120):
    import random
    stars = []
    for _ in range(count):
        x = random.uniform(0, WIDTH)
        y = random.uniform(0, HEIGHT)
        speed = random.uniform(0.3, 1.5)
        size = random.choice([1, 1, 1, 2])
        brightness = random.randint(80, 255)
        stars.append((x, y, speed, size, brightness))
    return stars


# ─────────────────────────────────────────────
#  BUTTON WIDGET
# ─────────────────────────────────────────────

class Button:
    """
    Button widget yang menggunakan btn_normal/hover/pressed/disabled assets.

    Styles:
      'default'  → btn asset (normal/hover/pressed)
      'success'  → btn asset + green tint overlay
      'danger'   → btn asset + red tint overlay
      'ghost'    → btn asset dengan alpha rendah (disabled look tapi tetap klikable)
      'small'    → sama seperti default tapi font lebih kecil
      'disabled' → btn_disabled asset, tidak bisa diklik

    Asset asli 260x50; akan di-scale ke self.rect secara otomatis.
    """

    # Cache tint surface agar tidak dibuat ulang setiap frame
    _TINT_CACHE: dict = {}

    def __init__(self, rect, label, style='default', icon=None, shortcut=None, disabled=False):
        self.rect     = pygame.Rect(rect)
        self.label    = label
        self.style    = style
        self.icon     = icon
        self.shortcut = shortcut
        self.disabled = disabled or (style == 'disabled')

        self.hovered  = False
        self.pressed  = False
        self._hover_t = 0.0   # 0..1 untuk animasi smooth

    # ── state helpers ────────────────────────────────────────────────
    def enable(self):  self.disabled = False
    def disable(self): self.disabled = True

    # ── update & event ───────────────────────────────────────────────
    def update(self, mouse_pos, dt=1):
        self.hovered = (not self.disabled) and self.rect.collidepoint(mouse_pos)
        target = 1.0 if self.hovered else 0.0
        self._hover_t += (target - self._hover_t) * 0.22

    def handle_event(self, event):
        if self.disabled:
            return False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.pressed = True
                return True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.pressed = False
        return False

    # ── drawing ──────────────────────────────────────────────────────
    def draw(self, surface):
        w, h = self.rect.width, self.rect.height
        t    = self._hover_t

        # 1. Pilih base asset
        if self.disabled:
            base_img = AssetLoader.load('assets/images/btn_disabled.png', (w, h))
        elif self.pressed:
            base_img = AssetLoader.load('assets/images/btn_pressed.png',  (w, h))
        elif t > 0.45:
            base_img = AssetLoader.load('assets/images/btn_hover.png',    (w, h))
        else:
            base_img = AssetLoader.load('assets/images/btn_normal.png',   (w, h))

        # 2. Gambar base (asset atau fallback rect)
        if base_img:
            surface.blit(base_img, self.rect.topleft)
        else:
            # Fallback tanpa asset
            fb_colors = {
                'danger':  (lerp_color((100,15,15), (180,35,35), t)),
                'success': (lerp_color((15,70,25),  (25,120,45), t)),
                'ghost':   (lerp_color((20,20,40),  (30,50,80),  t)),
            }
            fc = fb_colors.get(self.style, lerp_color(THEME['btn_normal'], THEME['btn_hover'], t))
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(s, (*fc, 220), s.get_rect(), border_radius=8)
            surface.blit(s, self.rect.topleft)
            pygame.draw.rect(surface, lerp_color(THEME['border_glow'], THEME['border'], t),
                             self.rect, 2, border_radius=8)

        # 3. Style color-tint overlay di atas asset (hanya untuk danger/success/ghost)
        TINT_MAP = {
            'danger':  (180, 30,  30,  55),
            'success': (20,  130, 40,  45),
            'ghost':   (10,  10,  30,  80),
        }
        if self.style in TINT_MAP and not self.disabled:
            tr, tg, tb, ta = TINT_MAP[self.style]
            # Hover membuat tint lebih terang
            ta_final = int(ta * (0.7 + 0.6 * t))
            tint = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(tint, (tr, tg, tb, ta_final), tint.get_rect(), border_radius=6)
            surface.blit(tint, self.rect.topleft)

        # 4. Glow effect saat hover
        if t > 0.08 and not self.disabled:
            glow_alpha = int(55 * t)
            glow_col   = THEME.get('border', (0, 180, 255))
            glow_s = pygame.Surface((w + 10, h + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_s, (*glow_col, glow_alpha), glow_s.get_rect(), border_radius=10)
            surface.blit(glow_s, (self.rect.x - 5, self.rect.y - 5))

        # 5. Label teks
        cx, cy = self.rect.centerx, self.rect.centery
        # Saat pressed, geser teks 1px ke bawah (feel klik)
        if self.pressed:
            cy += 1

        if self.icon:
            ic_rect = self.icon.get_rect(midright=(cx - 6, cy))
            surface.blit(self.icon, ic_rect)
            cx = cx + self.icon.get_width() // 2 + 4

        fnt = Fonts.small if self.style == 'small' else Fonts.body
        tc  = THEME['muted'] if self.disabled else THEME['btn_text']
        draw_text_centered(surface, self.label, fnt, tc, cx, cy)

        # 6. Shortcut hint (pojok kanan atas tombol)
        if self.shortcut and not self.disabled:
            sh = Fonts.tiny.render(f'[{self.shortcut}]', True, THEME['muted'])
            surface.blit(sh, (self.rect.right - sh.get_width() - 5, self.rect.y + 3))


# ─────────────────────────────────────────────
#  SLIDER WIDGET
# ─────────────────────────────────────────────

class Slider:
    """
    Slider widget dengan support custom colors untuk theming.

    params:
      - color_track:     (R,G,B) untuk track background
      - color_fill:      (R,G,B) untuk filled portion
      - color_handle:    (R,G,B) untuk handle circle
      - color_label:     (R,G,B) untuk label text
    """
    def __init__(self, rect, label, min_val=0, max_val=100, value=50,
                 color_track=None, color_fill=None, color_handle=None, color_label=None):
        self.rect = pygame.Rect(rect)
        self.label = label
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.dragging = False

        # Custom colors (fallback ke THEME jika tidak diberikan)
        self.color_track   = color_track   or (40, 40, 70)
        self.color_fill    = color_fill    or THEME.get('border', (0, 180, 255))
        self.color_handle  = color_handle  or THEME.get('btn_hover', (0, 120, 220))
        self.color_label   = color_label   or THEME.get('subtitle', (150, 200, 255))

    @property
    def ratio(self):
        return (self.value - self.min_val) / (self.max_val - self.min_val)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.dragging = True
                self._update_value(event.pos[0])
        if event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        if event.type == pygame.MOUSEMOTION and self.dragging:
            self._update_value(event.pos[0])

    def _update_value(self, mx):
        t = max(0, min(1, (mx - self.rect.x) / self.rect.width))
        self.value = int(self.min_val + t * (self.max_val - self.min_val))

    def draw(self, surface):
        # Label
        lbl = Fonts.small.render(f'{self.label}: {self.value}', True, self.color_label)
        surface.blit(lbl, (self.rect.x, self.rect.y - 22))

        # Track background
        track = pygame.Rect(self.rect.x, self.rect.centery - 3, self.rect.width, 6)
        pygame.draw.rect(surface, self.color_track, track, border_radius=3)

        # Filled portion
        fill_w = int(self.rect.width * self.ratio)
        if fill_w > 0:
            pygame.draw.rect(surface, self.color_fill, pygame.Rect(track.x, track.y, fill_w, 6), border_radius=3)

        # Handle circle
        hx = int(self.rect.x + self.ratio * self.rect.width)
        hy = self.rect.centery
        pygame.draw.circle(surface, self.color_handle, (hx, hy), 10)
        pygame.draw.circle(surface, (*self.color_handle, 150), (hx, hy), 10, 2)


# ─────────────────────────────────────────────
#  3.1  MAIN MENU
# ─────────────────────────────────────────────

class MainMenu:
    """
    Layar utama ketika game dibuka.
    Gambar yang dipakai:
      - menu_bg.png (background), menu_logo.png (logo), stars_overlay.png (dekorasi)
      - planet_bg.png (dekorasi sudut kanan bawah)
    """

    def __init__(self):
        Fonts.init()
        self.stars = init_stars(150)
        self.t = 0.0
        self.choice = None     # 'new_game' | 'load_game' | 'settings' | 'leaderboard' | 'quit'
        self.bg_img    = AssetLoader.load('assets/images/menu_bg.png', (WIDTH, HEIGHT))
        self.logo_img  = AssetLoader.load('assets/images/menu_logo.png', (540, 158))
        self.planet_img = None  # dihapus

        bw, bh = 260, 50
        cx = WIDTH // 2
        by = 230
        gap = 58

        self.buttons = [
            Button((cx-bw//2, by,        bw, bh), 'NEW GAME',     'success', shortcut='N'),
            Button((cx-bw//2, by+gap,    bw, bh), 'LOAD GAME',    'default', shortcut='L'),
            Button((cx-bw//2, by+gap*2,  bw, bh), 'SETTINGS',     'default', shortcut='S'),
            Button((cx-bw//2, by+gap*3,  bw, bh), 'LEADERBOARD',  'default', shortcut='B'),
            Button((cx-bw//2, by+gap*4,  bw, bh), 'EXIT',         'danger',  shortcut='ESC'),
        ]
        self._actions = ['new_game', 'load_game', 'settings', 'leaderboard', 'quit']

        self._key_map = {
            pygame.K_n: 'new_game',
            pygame.K_l: 'load_game',
            pygame.K_s: 'settings',
            pygame.K_b: 'leaderboard',
            pygame.K_ESCAPE: 'quit',
        }

        # Partikel bintang jatuh (dekoratif)
        self._particles = []
        self._spawn_timer = 0

    def _update_particles(self):
        import random
        self._spawn_timer += 1
        if self._spawn_timer >= 6:
            self._spawn_timer = 0
            self._particles.append({
                'x': random.uniform(0, WIDTH),
                'y': -5,
                'speed': random.uniform(1.5, 4.0),
                'alpha': 255,
                'size': random.randint(1, 3),
            })
        for p in self._particles[:]:
            p['y'] += p['speed']
            p['alpha'] -= 3
            if p['alpha'] <= 0 or p['y'] > HEIGHT:
                self._particles.remove(p)

    def _draw_particles(self, surface):
        for p in self._particles:
            s = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (200, 220, 255, p['alpha']), (p['size'], p['size']), p['size'])
            surface.blit(s, (p['x'] - p['size'], p['y'] - p['size']))

    def handle_event(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                self.choice = self._actions[i]
                return

        if event.type == pygame.KEYDOWN:
            if event.key in self._key_map:
                self.choice = self._key_map[event.key]

    def update(self):
        self.t += 0.016
        mp = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mp)
        self._update_particles()

    def draw(self, surface):
        # Background — stretch penuh ke layar
        if self.bg_img:
            surface.blit(self.bg_img, (0, 0))
        else:
            draw_stars_bg(surface, self.stars, self.t)

        # Partikel
        self._draw_particles(surface)

        # Dark overlay di belakang area tombol agar terbaca
        btn_area = pygame.Surface((340, 310), pygame.SRCALPHA)
        btn_area.fill((0, 0, 0, 110))
        cx = WIDTH // 2
        surface.blit(btn_area, (cx - 170, 218))
        # Border tipis area tombol
        pygame.draw.rect(surface, (160, 120, 40, 80),
                         pygame.Rect(cx - 170, 218, 340, 310), 1, border_radius=8)

        # Logo — lebih besar, posisi lebih ke atas
        if self.logo_img:
            float_offset = int(math.sin(self.t * 1.5) * 4)
            lr = self.logo_img.get_rect(center=(WIDTH // 2, 105 + float_offset))
            surface.blit(self.logo_img, lr)
        else:
            glow_offset = int(math.sin(self.t * 1.5) * 3)
            draw_glow_text(surface, 'TOWER DEFENSE', Fonts.title, THEME['accent'],
                           WIDTH // 2, 105 + glow_offset, glow_radius=5)

        # Versi — warna blend dengan bg hijau gelap pojok kanan bawah
        ver = Fonts.tiny.render('v1.0.0', True, WHITE)
        ver.set_alpha(160)
        surface.blit(ver, (WIDTH - ver.get_width() - 10, HEIGHT - 20))

        # Tombol
        for btn in self.buttons:
            btn.draw(surface)

        # Credit bawah — blend dengan bg hijau gelap pojok kiri bawah
        cr = Fonts.tiny.render('© 2025 Tower Defense', True, WHITE)
        cr.set_alpha(160)
        surface.blit(cr, (10, HEIGHT - 20))


# ─────────────────────────────────────────────
#  3.2  PAUSE MENU
# ─────────────────────────────────────────────

class PauseMenu:
    """
    Overlay semi-transparan di atas gameplay.
    Gambar yang dipakai:
      - panel_glow.png (panel popup utama)
      - scanline.png (efek retro opsional di overlay)
    """

    def __init__(self):
        self.choice = None  # 'resume' | 'settings' | 'leaderboard' | 'main_menu'

        bw, bh = 220, 46
        cx = WIDTH // 2
        by = 260
        gap = 58

        self.buttons = [
            Button((cx-bw//2, by,       bw, bh), 'RESUME',      'success', shortcut='ESC'),
            Button((cx-bw//2, by+gap,   bw, bh), 'SETTINGS',    'default', shortcut='S'),
            Button((cx-bw//2, by+gap*2, bw, bh), 'LEADERBOARD', 'default', shortcut='B'),
            Button((cx-bw//2, by+gap*3, bw, bh), 'MAIN MENU',   'danger',  shortcut='M'),
        ]
        self._actions = ['resume', 'settings', 'leaderboard', 'main_menu']
        self._key_map = {
            pygame.K_ESCAPE: 'resume',
            pygame.K_s: 'settings',
            pygame.K_b: 'leaderboard',
            pygame.K_m: 'main_menu',
        }
        self.scanline_img = AssetLoader.load('assets/images/scanline.png', (WIDTH, HEIGHT))
        self._t = 0.0

    def handle_event(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                self.choice = self._actions[i]
                return
        if event.type == pygame.KEYDOWN and event.key in self._key_map:
            self.choice = self._key_map[event.key]

    def update(self):
        self._t += 0.016
        mp = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mp)

    def draw(self, surface):
        # Blur overlay (darken + blur effect via semi-transparent overlay)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 160))
        surface.blit(overlay, (0, 0))

        # Scanline efek
        if self.scanline_img:
            surface.blit(self.scanline_img, (0, 0))

        # Panel tengah
        pw, ph = 320, 380
        panel_rect = pygame.Rect(WIDTH//2 - pw//2, HEIGHT//2 - ph//2, pw, ph)
        draw_panel(surface, panel_rect, alpha=240, radius=16)

        # Judul PAUSED - solid text, clear tanpa glow blur
        pulse = int(220 + 35 * math.sin(self._t * 3))
        pulse_color = (pulse, pulse, 80)  # Gold-ish yang pulse
        paused_surf = Fonts.heading.render('⏸  PAUSED', True, pulse_color)
        paused_rect = paused_surf.get_rect(center=(WIDTH//2, panel_rect.y + 50))
        surface.blit(paused_surf, paused_rect)

        # Divider
        pygame.draw.line(surface, THEME['border'],
                         (panel_rect.x+20, panel_rect.y+80),
                         (panel_rect.right-20, panel_rect.y+80), 1)

        # Tombol
        for btn in self.buttons:
            btn.draw(surface)


# ─────────────────────────────────────────────
#  3.3  SETTINGS MENU
# ─────────────────────────────────────────────

class SettingsMenu:
    """
    Layar pengaturan dengan background landscape medieval (menu_bg.png).

    Color Palette (match landscape hijau):
    - Background: menu_bg.png (landscape dengan langit light, grass hijau, ground coklat)
    - Panel: dark brown wood (80, 50, 20, 230) dengan border emas
    - Text: warm cream/gold
    - Sections: gold accent dengan garis halus
    - Sliders: warm orange/gold

    Layout (lebar panel 500px, centered):
    ┌──────────────────────────────────────────┐
    │  ⚙  SETTINGS                             │
    ├──────────────────────────────────────────┤
    │  🔊 AUDIO                                │
    │   Master Volume  ━━━━●───  80            │
    │   SFX Volume     ━━━●────  70            │
    │   Music Volume   ━━●─────  60            │
    ├──────────────────────────────────────────┤
    │  🖥 GRAPHICS QUALITY                     │
    │   [ Low ]  [ Medium ]  [ High ]          │
    ├──────────────────────────────────────────┤
    │  ⚔ DIFFICULTY                            │
    │   [ EASY ]  [ NORMAL ]  [ HARD ]         │
    ├──────────────────────────────────────────┤
    │       [ RESET ]        [ APPLY ]         │
    │              [ ← BACK ]                  │
    └──────────────────────────────────────────┘
    """

    _GFX_LABELS  = ['Low', 'Medium', 'High']
    _DIFF_LABELS = ['EASY', 'NORMAL', 'HARD']
    _DIFF_COLORS = None  # di-set di __init__

    # Medieval/landscape color palette untuk Settings
    _SETTINGS_THEME = {
        'bg_sky':          (204, 224, 224),        # light sky dari menu_bg
        'bg_ground':       (225, 168, 34),         # warm golden ground
        'panel_wood':      (80, 50, 20),           # dark brown wood
        'panel_border':    (220, 175, 50),         # gold border
        'section_label':   (240, 210, 110),        # warm gold text
        'section_line':    (180, 140, 60),         # muted gold
        'slider_bg':       (50, 40, 20),           # dark brown track
        'slider_fill':     (220, 160, 40),         # warm gold slider
        'text_primary':    (245, 235, 200),        # warm cream text
        'text_muted':      (160, 135, 80),         # muted earth tone
        'toggle_unselect': (100, 80, 40),          # unselected toggle bg
    }

    # Layout constants
    PANEL_W  = 500
    PANEL_H  = 450
    PANEL_X  = None
    PANEL_Y  = 95

    def __init__(self, settings=None):
        self.choice = None
        self.settings = settings or {
            'vol_master': 80,
            'vol_sfx':    70,
            'vol_music':  60,
            'graphics':   1,
            'difficulty': 1,
            'fullscreen': False,
            'show_fps':   False,
        }
        SettingsMenu._DIFF_COLORS = [
            (80, 160, 50),   # EASY - green
            (160, 120, 40),  # NORMAL - gold
            (180, 50, 40),   # HARD - red
        ]

        # Load background
        self.bg_img = AssetLoader.load('assets/images/menu_bg.png', (WIDTH, HEIGHT))

        cx       = WIDTH  // 2
        px       = cx - self.PANEL_W // 2
        self.PANEL_X = px
        inner_x  = px + 30
        inner_w  = self.PANEL_W - 60

        # ── Sliders ─────────────────────────────────────────────────
        sy_start = self.PANEL_Y + 120
        self.sliders = [
            Slider((inner_x, sy_start,       inner_w, 20), 'Master Volume', 0, 100,
                   self.settings['vol_master'],
                   color_track=self._SETTINGS_THEME['slider_bg'],
                   color_fill=self._SETTINGS_THEME['slider_fill'],
                   color_handle=self._SETTINGS_THEME['slider_fill'],
                   color_label=self._SETTINGS_THEME['text_muted']),
            Slider((inner_x, sy_start + 58,  inner_w, 20), 'SFX Volume', 0, 100,
                   self.settings['vol_sfx'],
                   color_track=self._SETTINGS_THEME['slider_bg'],
                   color_fill=self._SETTINGS_THEME['slider_fill'],
                   color_handle=self._SETTINGS_THEME['slider_fill'],
                   color_label=self._SETTINGS_THEME['text_muted']),
            Slider((inner_x, sy_start + 116, inner_w, 20), 'Music Volume', 0, 100,
                   self.settings['vol_music'],
                   color_track=self._SETTINGS_THEME['slider_bg'],
                   color_fill=self._SETTINGS_THEME['slider_fill'],
                   color_handle=self._SETTINGS_THEME['slider_fill'],
                   color_label=self._SETTINGS_THEME['text_muted']),
        ]

        # ── Toggle buttons Graphics (3 tombol kecil sejajar) ────────
        self._gfx_y   = self.PANEL_Y + 292
        gfx_btn_w     = 100
        gfx_btn_h     = 36
        gfx_total_w   = gfx_btn_w * 3 + 14 * 2
        gfx_sx        = cx - gfx_total_w // 2
        self._gfx_btns = [
            Button((gfx_sx + i * (gfx_btn_w + 14), self._gfx_y + 24, gfx_btn_w, gfx_btn_h),
                   lbl, 'small')
            for i, lbl in enumerate(self._GFX_LABELS)
        ]
        self._gfx_rects = [b.rect for b in self._gfx_btns]

        # ── Toggle buttons Difficulty (3 tombol kecil sejajar) ──────
        self._diff_y  = self.PANEL_Y + 362
        diff_btn_w    = 110
        diff_btn_h    = 36
        diff_total_w  = diff_btn_w * 3 + 12 * 2
        diff_sx       = cx - diff_total_w // 2
        self._diff_btns = [
            Button((diff_sx + i * (diff_btn_w + 12), self._diff_y + 24, diff_btn_w, diff_btn_h),
                   lbl, 'small')
            for i, lbl in enumerate(self._DIFF_LABELS)
        ]
        self._diff_rects = [b.rect for b in self._diff_btns]

        # ── Action buttons (RESET / APPLY / BACK) ───────────────────
        act_y   = self.PANEL_Y + self.PANEL_H + 12
        act_bw  = 160
        act_bh  = 44
        gap     = 20
        self.btn_reset = Button((cx - act_bw - gap // 2, act_y,          act_bw, act_bh), 'RESET',  'danger')
        self.btn_apply = Button((cx + gap // 2,           act_y,          act_bw, act_bh), 'APPLY',  'success')
        self.btn_back  = Button((cx - act_bw // 2,        act_y + act_bh + 10, act_bw, act_bh), '← BACK', 'ghost')

        self._action_btns = [self.btn_reset, self.btn_apply, self.btn_back]
        self._action_keys  = ['reset', 'apply', 'back']

    # ── Event handling ───────────────────────────────────────────────
    def handle_event(self, event):
        # Sliders
        for s in self.sliders:
            s.handle_event(event)

        # Action buttons
        for key, btn in zip(self._action_keys, self._action_btns):
            if btn.handle_event(event):
                if key == 'reset':   self._reset()
                elif key == 'apply': self._apply(); self.choice = 'apply'
                else:                self.choice = 'back'

        # Toggle graphics & difficulty via klik rect
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._gfx_rects):
                if r.collidepoint(event.pos):
                    self.settings['graphics'] = i
            for i, r in enumerate(self._diff_rects):
                if r.collidepoint(event.pos):
                    self.settings['difficulty'] = i

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.choice = 'back'

    # ── Internal helpers ─────────────────────────────────────────────
    def _reset(self):
        defaults = {'vol_master': 80, 'vol_sfx': 70, 'vol_music': 60,
                    'graphics': 1, 'difficulty': 1}
        self.settings.update(defaults)
        for s in self.sliders:
            if 'Master' in s.label: s.value = 80
            elif 'SFX'   in s.label: s.value = 70
            elif 'Music'  in s.label: s.value = 60

    def _apply(self):
        self.settings['vol_master'] = self.sliders[0].value
        self.settings['vol_sfx']    = self.sliders[1].value
        self.settings['vol_music']  = self.sliders[2].value
        try:
            pygame.mixer.music.set_volume(self.sliders[2].value / 100.0)
        except Exception:
            pass

    # ── Update ───────────────────────────────────────────────────────
    def update(self):
        mp = pygame.mouse.get_pos()
        for btn in self._action_btns + self._gfx_btns + self._diff_btns:
            btn.update(mp)

    # ── Draw ─────────────────────────────────────────────────────────
    def draw(self, surface):
        # Background: menu_bg landscape dengan dark overlay agar teks terbaca
        if self.bg_img:
            surface.blit(self.bg_img, (0, 0))
        else:
            surface.fill(self._SETTINGS_THEME['bg_sky'])

        # Dark overlay di atas landscape agar UI lebih terbaca
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        cx = WIDTH // 2
        px = self.PANEL_X
        pw = self.PANEL_W
        py = self.PANEL_Y
        ph = self.PANEL_H

        # ── Judul halaman dengan gold glow ───────────────────────────
        draw_glow_text(surface, 'SETTINGS', Fonts.heading, self._SETTINGS_THEME['section_label'],
                       cx, py - 30, glow_color=self._SETTINGS_THEME['panel_border'], glow_radius=4)
        pygame.draw.line(surface, self._SETTINGS_THEME['panel_border'], (px, py - 10), (px + pw, py - 10), 2)

        # ── Panel utama: dark brown wood ─────────────────────────────
        panel_rect = pygame.Rect(px, py, pw, ph)
        # Panel background - dark brown dengan sedikit transparan
        panel_bg = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel_bg, (*self._SETTINGS_THEME['panel_wood'], 230),
                         panel_bg.get_rect(), border_radius=14)
        # Wood grain texture overlay (optional subtle effect)
        for grain_y in range(0, ph, 25):
            grain_h = 12
            grain_alpha = 8
            grain_surf = pygame.Surface((pw, grain_h), pygame.SRCALPHA)
            pygame.draw.rect(grain_surf, (255, 255, 255, grain_alpha),
                             grain_surf.get_rect(), border_radius=4)
            panel_bg.blit(grain_surf, (0, grain_y))
        surface.blit(panel_bg, panel_rect.topleft)

        # Panel border - gold
        pygame.draw.rect(surface, self._SETTINGS_THEME['panel_border'], panel_rect, 3, border_radius=14)
        # Inner highlight
        pygame.draw.rect(surface, (*self._SETTINGS_THEME['panel_border'], 80),
                         panel_rect.inflate(-6, -6), 1, border_radius=12)

        # ── Section: AUDIO ───────────────────────────────────────────
        sec_audio_y = py + 18
        self._draw_section_header(surface, px + 18, sec_audio_y, pw - 36, 'AUDIO')

        # Sliders dengan warna landscape sudah di-set di __init__
        for s in self.sliders:
            s.draw(surface)

        # ── Divider ──────────────────────────────────────────────────
        div1_y = py + 270
        pygame.draw.line(surface, (*self._SETTINGS_THEME['section_line'], 120),
                         (px + 16, div1_y), (px + pw - 16, div1_y), 1)

        # ── Section: GRAPHICS QUALITY ────────────────────────────────
        self._draw_section_header(surface, px + 18, div1_y + 8, pw - 36, 'GRAPHICS QUALITY')
        for i, btn in enumerate(self._gfx_btns):
            self._draw_toggle_btn(surface, btn,
                                  selected=(self.settings['graphics'] == i),
                                  color=self._SETTINGS_THEME['section_label'])

        # ── Divider ──────────────────────────────────────────────────
        div2_y = div1_y + 80
        pygame.draw.line(surface, (*self._SETTINGS_THEME['section_line'], 120),
                         (px + 16, div2_y), (px + pw - 16, div2_y), 1)

        # ── Section: DIFFICULTY ──────────────────────────────────────
        self._draw_section_header(surface, px + 18, div2_y + 8, pw - 36, 'DIFFICULTY')
        diff_colors = self._DIFF_COLORS
        for i, btn in enumerate(self._diff_btns):
            self._draw_toggle_btn(surface, btn,
                                  selected=(self.settings['difficulty'] == i),
                                  color=diff_colors[i])

        # ── Action buttons ───────────────────────────────────────────
        for btn in self._action_btns:
            btn.draw(surface)

    # ── Private drawing helpers ──────────────────────────────────────
    def _draw_section_header(self, surface, x, y, w, title):
        """Gambar label section dengan gold accent dan garis halus."""
        lbl = Fonts.small.render(title, True, self._SETTINGS_THEME['section_label'])
        surface.blit(lbl, (x, y))
        line_x = x + lbl.get_width() + 10
        line_y = y + lbl.get_height() // 2
        if line_x < x + w:
            pygame.draw.line(surface, self._SETTINGS_THEME['section_line'],
                             (line_x, line_y), (x + w, line_y), 1)

    def _draw_toggle_btn(self, surface, btn: 'Button', selected: bool, color: tuple):
        """
        Gambar tombol toggle dengan landscape colors:
        - Selected: btn_hover + border dengan warna difficulty
        - Unselected: btn_normal dengan overlay gelap
        """
        w, h = btn.rect.width, btn.rect.height

        if selected:
            img = AssetLoader.load('assets/images/btn_hover.png', (w, h))
        else:
            img = AssetLoader.load('assets/images/btn_normal.png', (w, h))

        if img:
            if not selected:
                # Unselected: darker overlay
                dim = pygame.Surface((w, h), pygame.SRCALPHA)
                dim.fill((0, 0, 0, 100))
                s_copy = img.copy()
                s_copy.blit(dim, (0, 0))
                surface.blit(s_copy, btn.rect.topleft)
            else:
                surface.blit(img, btn.rect.topleft)
        else:
            # Fallback: rectangle dengan landscape colors
            bg = (*color[:3], 180) if selected else self._SETTINGS_THEME['toggle_unselect']
            s = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(s, bg, s.get_rect(), border_radius=6)
            surface.blit(s, btn.rect.topleft)

        # Border: color untuk selected, muted untuk unselected
        border_color = color if selected else self._SETTINGS_THEME['section_line']
        border_width = 2 if selected else 1
        pygame.draw.rect(surface, border_color, btn.rect, border_width, border_radius=6)

        # Teks label dengan warna sesuai state
        tc = self._SETTINGS_THEME['text_primary'] if selected else self._SETTINGS_THEME['text_muted']
        draw_text_centered(surface, btn.label, Fonts.small, tc,
                           btn.rect.centerx, btn.rect.centery)


# ─────────────────────────────────────────────
#  3.4  GAME OVER SCREEN
# ─────────────────────────────────────────────

class GameOverScreen:
    """
    Layar setelah game berakhir.
    Gambar:
      - panel_dark.png (panel statistik)
      - icon_skull.png, icon_coin.png, icon_star.png, icon_clock.png, icon_wave.png
    """

    def __init__(self, stats: dict):
        """
        stats: {
            'score': int,
            'wave': int,
            'playtime': float,        # detik
            'enemies_killed': int,
            'money_earned': int,
            'difficulty': str,
            'towers_placed': int,
        }
        """
        self.stats = stats
        self.choice = None  # 'retry' | 'main_menu'
        self._t = 0.0
        self._reveal_t = 0.0   # animasi reveal statistik

        bw, bh = 200, 48
        cx = WIDTH // 2
        self.buttons = [
            Button((cx - bw - 20, 510, bw, bh), '↺ RETRY',     'success', shortcut='R'),
            Button((cx + 20,      510, bw, bh), '⌂ MAIN MENU', 'danger',  shortcut='ESC'),
        ]
        self._actions = ['retry', 'main_menu']
        self._stars = init_stars(80)

        # Load icons
        self._icons = {
            'score':   AssetLoader.load('assets/images/icon_star.png',  (22, 22)),
            'wave':    AssetLoader.load('assets/images/icon_wave.png',   (22, 22)),
            'time':    AssetLoader.load('assets/images/icon_clock.png',  (22, 22)),
            'kills':   AssetLoader.load('assets/images/icon_skull.png',  (22, 22)),
            'money':   AssetLoader.load('assets/images/icon_coin.png',   (22, 22)),
        }

    def handle_event(self, event):
        for i, btn in enumerate(self.buttons):
            if btn.handle_event(event):
                self.choice = self._actions[i]
                return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                self.choice = 'retry'
            elif event.key == pygame.K_ESCAPE:
                self.choice = 'main_menu'

    def update(self):
        self._t += 0.016
        self._reveal_t = min(1.0, self._reveal_t + 0.008)
        mp = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.update(mp)

    def _fmt_time(self, seconds):
        m = int(seconds) // 60
        s = int(seconds) % 60
        return f'{m:02d}:{s:02d}'

    def draw(self, surface):
        draw_stars_bg(surface, self._stars, self._t)

        # Judul GAME OVER
        shake = int(math.sin(self._t * 8) * 2) if self._reveal_t < 0.3 else 0
        draw_glow_text(surface, 'GAME OVER', Fonts.title, THEME['danger'],
                       WIDTH//2 + shake, 80, glow_color=(200, 0, 0), glow_radius=8)

        diff_c = {'EASY': THEME['success'], 'NORMAL': THEME['info'], 'HARD': THEME['danger']}
        dc = diff_c.get(self.stats.get('difficulty', 'NORMAL'), THEME['info'])
        draw_text_centered(surface, self.stats.get('difficulty', 'NORMAL'),
                           Fonts.body, dc, WIDTH//2, 130)

        # Panel statistik
        pw, ph = 460, 330
        pr = pygame.Rect(WIDTH//2 - pw//2, 155, pw, ph)
        draw_panel(surface, pr, alpha=220, radius=14)

        # Header panel
        draw_text_centered(surface, 'BATTLE STATISTICS', Fonts.small, THEME['subtitle'],
                           WIDTH//2, pr.y + 22)
        pygame.draw.line(surface, THEME['border'],
                         (pr.x+20, pr.y+42), (pr.right-20, pr.y+42), 1)

        # Daftar statistik
        stat_data = [
            ('score',   '⭐ Final Score',     str(self.stats.get('score', 0))),
            ('wave',    '🌊 Wave Reached',    str(self.stats.get('wave', 0))),
            ('time',    '⏱ Playtime',         self._fmt_time(self.stats.get('playtime', 0))),
            ('kills',   '💀 Enemies Killed',  str(self.stats.get('enemies_killed', 0))),
            ('money',   '💰 Money Earned',    f"${self.stats.get('money_earned', 0)}"),
        ]

        row_h = 46
        for idx, (key, label, val) in enumerate(stat_data):
            ry = pr.y + 55 + idx * row_h
            reveal_progress = max(0, min(1, (self._reveal_t - idx * 0.12) / 0.1))
            if reveal_progress <= 0:
                continue

            # Animasi slide-in dari kiri
            slide = int((1 - reveal_progress) * 40)

            # Row alternating background
            if idx % 2 == 0:
                row_bg = pygame.Surface((pw - 20, row_h - 4), pygame.SRCALPHA)
                row_bg.fill((255, 255, 255, 12))
                surface.blit(row_bg, (pr.x + 10, ry))

            # Icon
            icon = self._icons.get(key)
            if icon:
                surface.blit(icon, (pr.x + 20 - slide, ry + (row_h - 22)//2))

            alpha_s = pygame.Surface((1, 1))  # dummy
            lbl_s = Fonts.small.render(label, True, THEME['subtitle'])
            lbl_s.set_alpha(int(255 * reveal_progress))
            surface.blit(lbl_s, (pr.x + 50 - slide, ry + (row_h - lbl_s.get_height())//2))

            val_s = Fonts.body.render(val, True, THEME['accent'])
            val_s.set_alpha(int(255 * reveal_progress))
            surface.blit(val_s, (pr.right - val_s.get_width() - 20 - slide,
                                 ry + (row_h - val_s.get_height())//2))

        # Tombol
        for btn in self.buttons:
            btn.draw(surface)

        # Hint POST leaderboard (placeholder - API nanti)
        if self._reveal_t > 0.8:
            hint = Fonts.tiny.render('Score auto-saved to leaderboard (coming soon)', True, THEME['muted'])
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, 568))


# ─────────────────────────────────────────────
#  3.5  IN-GAME HUD  (improvements)
# ─────────────────────────────────────────────

class InGameHUD:
    """
    HUD overlay di atas gameplay.
    Gambar:
      - hud_bar.png       (bar atas)
      - hud_bottom.png    (bar bawah)
      - icon_coin.png, icon_heart.png, icon_wave.png, icon_tower.png, icon_clock.png
      - enemy_fast.png, enemy_tank.png, dll (preview wave)
    """

    MAX_TOWERS = 25

    def __init__(self):
        Fonts.init()
        self._health_flash_t = 0.0
        self._money_flash_t  = 0.0
        self._wave_anim_t    = 0.0
        self._countdown_t    = 0.0

        # Load HUD background bars
        self._hud_top    = AssetLoader.load('assets/images/hud_bar.png', (WIDTH, 88))
        self._hud_bottom = AssetLoader.load('assets/images/hud_bottom.png', (WIDTH, 54))

        # Load icons
        self._ic = {
            'coin':   AssetLoader.load('assets/images/icon_coin.png',   (20, 20)),
            'heart':  AssetLoader.load('assets/images/icon_heart.png',  (20, 20)),
            'wave':   AssetLoader.load('assets/images/icon_wave.png',   (20, 20)),
            'tower':  AssetLoader.load('assets/images/icon_tower.png',  (20, 20)),
            'clock':  AssetLoader.load('assets/images/icon_clock.png',  (20, 20)),
        }
        # Enemy preview icons
        self._enemy_ic = {
            'Fast':    AssetLoader.load('assets/images/enemy_fast.png',   (24, 24)),
            'Tank':    AssetLoader.load('assets/images/enemy_tank.png',   (24, 24)),
            'Slow':    AssetLoader.load('assets/images/enemy_slow.png',   (24, 24)),
            'Flying':  AssetLoader.load('assets/images/enemy_flying.png', (24, 24)),
            'BOSS':    AssetLoader.load('assets/images/enemy_boss.png',   (24, 24)),
            'Shield':  AssetLoader.load('assets/images/enemy_shield.png', (24, 24)),
            'Heal':    AssetLoader.load('assets/images/enemy_heal.png',   (24, 24)),
            'Split':   AssetLoader.load('assets/images/enemy_split.png',  (24, 24)),
        }
        self._enemy_colors = {
            'Fast': RED, 'Tank': PURPLE, 'Slow': ORANGE,
            'Flying': LIME, 'BOSS': DARK_ORANGE, 'Shield': BLUE,
            'Heal': PINK, 'Split': ORANGE,
        }
        self._t = 0.0

    def update(self, base_health, money, dt=1):
        self._t += 0.016

        # Flash health rendah
        if base_health <= 3:
            self._health_flash_t += 0.08
        else:
            self._health_flash_t = 0.0

        # Flash money rendah
        if money < 40:
            self._money_flash_t += 0.06
        else:
            self._money_flash_t = 0.0

    def _draw_icon_stat(self, surface, icon_key, label, value, x, y, value_color=None):
        """Gambar ikon + label + nilai di posisi x, y (top-left)."""
        ic = self._ic.get(icon_key)
        ox = x
        if ic:
            surface.blit(ic, (x, y + 1))
            ox += 24
        lbl = Fonts.tiny.render(label, True, THEME['muted'])
        surface.blit(lbl, (ox, y - 1))
        vc = value_color or THEME['btn_text']
        val = Fonts.body.render(str(value), True, vc)
        surface.blit(val, (ox, y + 14))

    def draw_top_bar(self, surface, game_state_data: dict):
        """
        game_state_data: {
            'score', 'money', 'base_health', 'wave',
            'tower_count', 'difficulty', 'gap_timer', 'gap_duration',
            'turbo_mode', 'is_paused'
        }

        Layout top bar (lebar 1000px, tinggi 88px):
        ┌─────────────────────────────────────────────────────────────────────────┐
        │  [SCORE]  [MONEY]  [BASE HP]  [WAVE]  [TOWERS]  │ badge TURBO │ badge DIFF │
        │                  [Next wave in X.Xs] ← center baris ke-2                │
        └─────────────────────────────────────────────────────────────────────────┘
        5 stat di baris atas (y=10), badge di pojok kanan.
        Countdown muncul di baris bawah tengah (y=52) agar tidak tumpang tindih.
        """
        # Background bar atas
        if self._hud_top:
            surface.blit(self._hud_top, (0, 0))
        else:
            bar = pygame.Surface((WIDTH, 88), pygame.SRCALPHA)
            bar.fill((8, 8, 25, 200))
            surface.blit(bar, (0, 0))
            pygame.draw.line(surface, THEME['border'], (0, 88), (WIDTH, 88), 1)

        money     = game_state_data.get('money', 0)
        health    = game_state_data.get('base_health', 10)
        score     = game_state_data.get('score', 0)
        wave      = game_state_data.get('wave', 1)
        towers    = game_state_data.get('tower_count', 0)
        diff      = game_state_data.get('difficulty', 'NORMAL')
        gap_timer = game_state_data.get('gap_timer', 0)
        gap_dur   = game_state_data.get('gap_duration', 120)
        turbo     = game_state_data.get('turbo_mode', False)

        # ── Hitung lebar area stats (sisakan ruang untuk badge kanan)
        # Badge: DIFF (90px) + TURBO (95px jika aktif) + margin = maks ~210px dari kanan
        badge_area_w = 210
        stats_area_w = WIDTH - badge_area_w  # ~790px untuk 5 stat

        # 5 stat dengan jarak rata: kolom di tengah setiap slot
        STAT_Y = 10
        slot_w = stats_area_w // 5  # ~158px per slot

        # Warna dinamis
        money_flash = abs(math.sin(self._money_flash_t * 5)) if self._money_flash_t > 0 else 1
        money_c = THEME['money'] if money >= 80 else (
                  THEME['warning'] if money >= 40 else
                  lerp_color(THEME['danger'], THEME['warning'], money_flash))

        health_flash = abs(math.sin(self._health_flash_t * 6)) if self._health_flash_t > 0 else 1
        health_c = THEME['success']
        if health <= 6:
            health_c = THEME['warning']
        if health <= 3:
            health_c = lerp_color((200, 0, 0), (255, 100, 100), health_flash)
            flash_overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            flash_overlay.fill((255, 0, 0, int(30 * health_flash)))
            surface.blit(flash_overlay, (0, 0))

        tower_c = CYAN if towers < 20 else YELLOW if towers < self.MAX_TOWERS else RED

        stats = [
            ('wave',  'SCORE',   f'{score:,}',           None),
            ('coin',  'MONEY',   f'${money}',             money_c),
            ('heart', 'BASE HP', str(health),             health_c),
            ('wave',  'WAVE',    str(wave),               None),
            ('tower', 'TOWERS',  f'{towers}/{self.MAX_TOWERS}', tower_c),
        ]

        for i, (icon_key, label, value, color) in enumerate(stats):
            col_cx = i * slot_w + slot_w // 2   # center x tiap slot
            # Gambar icon + label + value secara centered di kolom
            ic = self._ic.get(icon_key)
            # Hitung total lebar blok agar bisa di-center
            val_surf = Fonts.body.render(str(value), True, color or THEME['btn_text'])
            lbl_surf = Fonts.tiny.render(label, True, THEME['muted'])
            block_w = max(val_surf.get_width(), lbl_surf.get_width()) + (22 if ic else 0)
            bx = col_cx - block_w // 2
            if ic:
                icon_y = STAT_Y + (val_surf.get_height() + lbl_surf.get_height()) // 2 - 10
                surface.blit(ic, (bx, icon_y))
                bx += 24
            surface.blit(lbl_surf, (bx, STAT_Y))
            surface.blit(val_surf, (bx, STAT_Y + lbl_surf.get_height() + 2))

        # ── Badges di pojok kanan (tidak tumpang tindih dengan stats)
        diff_colors = {'EASY': THEME['success'], 'NORMAL': THEME['info'], 'HARD': THEME['danger']}
        dc = diff_colors.get(diff, THEME['info'])

        # Badge difficulty selalu di kanan
        dbadge = pygame.Rect(WIDTH - 98, 8, 88, 28)
        pygame.draw.rect(surface, (*dc, 60), dbadge, border_radius=6)
        pygame.draw.rect(surface, dc, dbadge, 1, border_radius=6)
        draw_text_centered(surface, diff, Fonts.small, dc, dbadge.centerx, dbadge.centery)

        # Badge difficulty baris bawah - info mode turbo/paused
        if turbo:
            pulse = abs(math.sin(self._t * 5))
            tc = lerp_color(YELLOW, RED, pulse)
            tb = pygame.Rect(WIDTH - 98, 44, 88, 26)
            pygame.draw.rect(surface, (*tc, 80), tb, border_radius=6)
            pygame.draw.rect(surface, tc, tb, 1, border_radius=6)
            draw_text_centered(surface, '⚡ TURBO', Fonts.tiny, tc, tb.centerx, tb.centery)

        # ── Countdown timer: baris bawah tengah bar atas (y=52)
        if gap_timer > 0 and gap_dur > 0:
            time_left = (gap_dur - gap_timer) / 60.0
            timer_s = f'Next wave in  {time_left:.1f}s'
            # Background kecil agar terbaca
            ic = self._ic.get('clock')
            ts = Fonts.small.render(timer_s, True, THEME['accent'])
            tx = WIDTH // 2 - ts.get_width() // 2 - (12 if ic else 0)
            ty = 54
            if ic:
                surface.blit(ic, (tx, ty + 1))
                tx += 22
            surface.blit(ts, (tx, ty))

    def draw_bottom_bar(self, surface, game_state_data: dict, wave_info: dict = None):
        """
        Bar bawah (tinggi 54px, y = HEIGHT-54 .. HEIGHT):
        Layout:
          [WAVE preview: icon×n ...]   │   [Tower info ATAU shortcut hints]   │  [progress bar]
          ←── kiri (maks ~420px) ──→       ←── kanan (maks ~560px) ──→

        Wave preview di kiri, tower info / shortcut di kanan (tidak saling tumpang tindih).
        Progress bar spawn di bawah wave preview (baris ke-2 bar bawah).
        """
        BAR_Y = HEIGHT - 54
        BAR_H = 54

        # Background bar bawah
        if self._hud_bottom:
            surface.blit(self._hud_bottom, (0, BAR_Y))
        else:
            bar = pygame.Surface((WIDTH, BAR_H), pygame.SRCALPHA)
            bar.fill((8, 8, 25, 200))
            surface.blit(bar, (0, BAR_Y))
            pygame.draw.line(surface, THEME['border'], (0, BAR_Y), (WIDTH, BAR_Y), 1)

        ICON_Y   = BAR_Y + 8      # baris atas dalam bar
        LABEL_Y  = BAR_Y + 8      # y teks label (tiny)
        TEXT_Y   = BAR_Y + 8      # y teks shortcut / tower info
        PROG_Y   = HEIGHT - 8     # progress bar spawn di paling bawah

        # ─── KIRI: Wave preview (maks 420px dari x=8)
        LEFT_MAX = 440

        if wave_info:
            preview_str = wave_info.get('preview', '')
            spawned     = wave_info.get('spawned', 0)
            total       = wave_info.get('total', 0)

            x_cur = 8
            # Label "WAVE:"
            wave_lbl = Fonts.tiny.render('WAVE:', True, THEME['muted'])
            surface.blit(wave_lbl, (x_cur, LABEL_Y + 3))
            x_cur += wave_lbl.get_width() + 6

            # Enemy icons + counts
            for part in preview_str.split():
                if ':' not in part:
                    continue
                etype, ecount = part.split(':', 1)
                ec = self._enemy_colors.get(etype, WHITE)
                ic = self._enemy_ic.get(etype)

                # Estimasi lebar item ini
                txt_w = Fonts.tiny.render(f'×{ecount}', True, ec).get_width()
                item_w = (26 if ic else 0) + txt_w + 10

                if x_cur + item_w > LEFT_MAX:
                    break   # jangan overflow ke area kanan

                if ic:
                    surface.blit(ic, (x_cur, ICON_Y - 2))
                    x_cur += 26
                lbl = Fonts.tiny.render(f'×{ecount}', True, ec)
                surface.blit(lbl, (x_cur, LABEL_Y + 5))
                x_cur += lbl.get_width() + 8

            # Progress bar spawn (baris bawah, kiri)
            pb_rect = pygame.Rect(8, PROG_Y - 4, 200, 5)
            draw_progress_bar(surface, pb_rect, spawned, max(total, 1), THEME['success'])

        # ─── Garis pemisah vertikal
        pygame.draw.line(surface, (*THEME['border'], 80),
                         (LEFT_MAX, BAR_Y + 4), (LEFT_MAX, HEIGHT - 4), 1)

        # ─── KANAN: Tower info ATAU shortcut hints (dari x=LEFT_MAX+8)
        RIGHT_X = LEFT_MAX + 8
        RIGHT_W = WIDTH - RIGHT_X - 8   # ruang tersedia

        sel_tower = game_state_data.get('selected_tower_info')
        if sel_tower:
            # Tower info: 2 baris supaya tidak terlalu panjang
            line1 = Fonts.small.render(
                f"{sel_tower['type']}  Lv.{sel_tower['level']}  DMG:{sel_tower['damage']}",
                True, YELLOW
            )
            line2 = Fonts.tiny.render(
                f"Target: {sel_tower['mode']}   Sell: ${sel_tower['sell_value']}   "
                f"[U]=Upgrade  [T]=Target  [RC]=Sell",
                True, THEME['info']
            )
            surface.blit(line1, (RIGHT_X, BAR_Y + 6))
            surface.blit(line2, (RIGHT_X, BAR_Y + 28))
        else:
            # Shortcut hints: 2 baris
            hint1 = Fonts.tiny.render(
                '1=Ice($40)   2=Fire($60)   3=Lightning($80)   4=Laser($100)',
                True, THEME['muted']
            )
            hint2 = Fonts.tiny.render(
                'U=Upgrade   T=Target   RC=Sell   Z=Turbo   ESC=Pause',
                True, THEME['muted']
            )
            surface.blit(hint1, (RIGHT_X, BAR_Y + 8))
            surface.blit(hint2, (RIGHT_X, BAR_Y + 28))

    def draw_wave_complete_banner(self, surface, wave_num: int, bonus: int, time_left: float):
        """Banner animasi gelombang selesai."""
        alpha = min(255, int(255 * (time_left / 2.0)))
        scale = 1.0 + 0.05 * math.sin(self._t * 4)

        msg1 = f'✓  WAVE {wave_num} COMPLETE!'
        msg2 = f'+${bonus} Bonus'
        msg3 = f'Next wave in {time_left:.1f}s...'

        panel_w, panel_h = 440, 120
        pr = pygame.Rect(WIDTH//2 - panel_w//2, HEIGHT//2 - 120, panel_w, panel_h)

        p = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(p, (10, 40, 15, alpha), p.get_rect(), border_radius=12)
        surface.blit(p, pr.topleft)
        pygame.draw.rect(surface, (*THEME['success'], alpha), pr, 2, border_radius=12)

        s1 = Fonts.heading.render(msg1, True, (*THEME['success'], alpha))
        surface.blit(s1, s1.get_rect(center=(WIDTH//2, pr.y + 35)))
        s2 = Fonts.body.render(msg2, True, (*THEME['accent'], alpha))
        surface.blit(s2, s2.get_rect(center=(WIDTH//2, pr.y + 72)))
        s3 = Fonts.small.render(msg3, True, (*THEME['muted'], alpha))
        surface.blit(s3, s3.get_rect(center=(WIDTH//2, pr.y + 100)))

    def draw_sell_feedback(self, surface, text: str, alpha_ratio: float):
        a = int(255 * alpha_ratio)
        s = Fonts.heading.render(text, True, (*THEME['success'], a))
        # Melayang ke atas
        y_offset = int((1 - alpha_ratio) * 40)
        r = s.get_rect(center=(WIDTH//2, HEIGHT//2 - 40 - y_offset))
        surface.blit(s, r)

    def draw_mode_change_feedback(self, surface, text: str, alpha_ratio: float):
        a = int(255 * alpha_ratio)
        s = Fonts.body.render(text, True, (*THEME['info'], a))
        r = s.get_rect(center=(WIDTH//2, HEIGHT//2 + 50))
        surface.blit(s, r)


# ─────────────────────────────────────────────
#  3.1b  DIFFICULTY SELECT (upgrade versi lama)
# ─────────────────────────────────────────────

class DifficultySelectMenu:
    """
    Layar pilihan difficulty sebelum memulai game.
    Gambar: menu_bg.png, panel_glow.png
    """

    def __init__(self):
        self.choice = None
        self._t = 0.0
        self._stars = init_stars(100)
        self.bg_img = AssetLoader.load('assets/images/menu_bg.png', (WIDTH, HEIGHT))

        configs = [
            {
                'label': 'EASY',
                'desc':  ['Enemies 30% weaker & slower', 'Starting money: $200', 'Base HP: 20'],
                'color': THEME['success'],
                'diff':  'EASY',
            },
            {
                'label': 'NORMAL',
                'desc':  ['Balanced challenge', 'Starting money: $100', 'Base HP: 10'],
                'color': THEME['info'],
                'diff':  'NORMAL',
            },
            {
                'label': 'HARD',
                'desc':  ['Enemies 50% stronger', 'Starting money: $50', 'Base HP: 5'],
                'color': THEME['danger'],
                'diff':  'HARD',
            },
        ]
        self._configs = configs

        card_w, card_h = 250, 220
        total_w = card_w * 3 + 30 * 2
        sx = WIDTH//2 - total_w//2
        self._card_rects = []
        self._hover = -1

        for i in range(3):
            r = pygame.Rect(sx + i * (card_w + 30), 220, card_w, card_h)
            self._card_rects.append(r)

        self.back_btn = Button((20, HEIGHT - 60, 120, 40), '← BACK', 'ghost')

    def handle_event(self, event):
        if self.back_btn.handle_event(event):
            self.choice = 'back'
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, r in enumerate(self._card_rects):
                if r.collidepoint(event.pos):
                    self.choice = self._configs[i]['diff']
                    return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_1:   self.choice = 'EASY'
            elif event.key == pygame.K_2: self.choice = 'NORMAL'
            elif event.key == pygame.K_3: self.choice = 'HARD'
            elif event.key == pygame.K_ESCAPE: self.choice = 'back'

    def update(self):
        self._t += 0.016
        mp = pygame.mouse.get_pos()
        self._hover = -1
        for i, r in enumerate(self._card_rects):
            if r.collidepoint(mp):
                self._hover = i
        self.back_btn.update(mp)

    def draw(self, surface):
        if self.bg_img:
            surface.blit(self.bg_img, (0, 0))
        else:
            draw_stars_bg(surface, self._stars, self._t)

        # Dark overlay agar teks terbaca di atas background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 100))
        surface.blit(overlay, (0, 0))

        # Judul — gold medieval, tanpa blur
        draw_text_centered(surface, 'SELECT DIFFICULTY', Fonts.heading,
                           (220, 175, 40), WIDTH//2, 95)

        # Divider emas
        pygame.draw.line(surface, (180, 140, 30), (80, 122), (WIDTH-80, 122), 2)
        pygame.draw.line(surface, (240, 200, 60), (80, 124), (WIDTH-80, 124), 1)

        draw_text_centered(surface, 'Pilih tingkat kesulitan — sanggupkah kamu bertahan?',
                           Fonts.small, (220, 200, 150), WIDTH//2, 150)

        # Warna card per difficulty
        card_colors = {
            'EASY':   {'bg': (30, 70, 20),   'border': (80, 180, 40),  'label': (100, 230, 60),  'shine': (150, 255, 100)},
            'NORMAL': {'bg': (20, 50, 90),   'border': (60, 140, 220), 'label': (100, 180, 255), 'shine': (160, 220, 255)},
            'HARD':   {'bg': (80, 20, 15),   'border': (220, 60, 40),  'label': (255, 100, 70),  'shine': (255, 160, 140)},
        }

        for i, (r, cfg) in enumerate(zip(self._card_rects, self._configs)):
            hovered = (self._hover == i)
            cc = card_colors[cfg['diff']]
            hover_off = int(-6 * (0.5 + 0.5 * math.sin(self._t * 3))) if hovered else 0
            draw_r = r.move(0, hover_off)

            # Card body — solid dark wood dengan tint warna
            card_surf = pygame.Surface((draw_r.width, draw_r.height), pygame.SRCALPHA)
            bg_alpha = 245 if hovered else 230
            pygame.draw.rect(card_surf,
                             (*cc['bg'], bg_alpha),
                             card_surf.get_rect(), border_radius=12)
            # Wood grain overlay
            for gy in range(0, draw_r.height, 10):
                ga = 15 if (gy//10) % 2 == 0 else 8
                pygame.draw.rect(card_surf, (60, 40, 10, ga),
                                 (0, gy, draw_r.width, 9))
            surface.blit(card_surf, draw_r.topleft)

            # Outer border — kayu gelap
            pygame.draw.rect(surface, (50, 32, 8),
                             draw_r, 4, border_radius=12)
            # Inner border — warna difficulty
            bw = 3 if hovered else 2
            pygame.draw.rect(surface, cc['border'],
                             draw_r.inflate(-4, -4), bw, border_radius=10)
            # Inner shine border
            if hovered:
                pygame.draw.rect(surface, cc['shine'],
                                 draw_r.inflate(-8, -8), 1, border_radius=8)

            # Top shine strip
            shine_surf = pygame.Surface((draw_r.width - 10, 18), pygame.SRCALPHA)
            pygame.draw.rect(shine_surf, (255, 255, 255, 25 if not hovered else 45),
                             shine_surf.get_rect(), border_radius=6)
            surface.blit(shine_surf, (draw_r.x + 5, draw_r.y + 5))

            # Corner rivets (gold)
            for rx, ry in [(draw_r.x+10, draw_r.y+10),
                           (draw_r.right-10, draw_r.y+10),
                           (draw_r.x+10, draw_r.bottom-10),
                           (draw_r.right-10, draw_r.bottom-10)]:
                pygame.draw.circle(surface, (140, 100, 10), (rx, ry), 5)
                pygame.draw.circle(surface, (240, 195, 50), (rx, ry), 5, 1)
                pygame.draw.circle(surface, (255, 235, 130), (rx-1, ry-1), 2)

            # Key shortcut badge
            badge_r = pygame.Rect(draw_r.x + 8, draw_r.y + 8, 26, 22)
            pygame.draw.rect(surface, (40, 28, 5, 180), badge_r, border_radius=4)
            pygame.draw.rect(surface, cc['border'], badge_r, 1, border_radius=4)
            ks = Fonts.small.render(f'{i+1}', True, (220, 195, 100))
            surface.blit(ks, (badge_r.centerx - ks.get_width()//2,
                               badge_r.centery - ks.get_height()//2))

            # Label difficulty
            draw_glow_text(surface, cfg['label'], Fonts.heading,
                           cc['label'], draw_r.centerx, draw_r.y + 55,
                           glow_color=cc['border'], glow_radius=4)

            # Divider kecil di bawah label
            div_y = draw_r.y + 80
            pygame.draw.line(surface, (*cc['border'], 120),
                             (draw_r.x + 20, div_y), (draw_r.right - 20, div_y), 1)

            # Deskripsi — putih agar terbaca
            for j, line in enumerate(cfg['desc']):
                lc = (240, 230, 200) if hovered else (190, 175, 145)
                ls = Fonts.small.render(line, True, lc)
                surface.blit(ls, (draw_r.x + 14, draw_r.y + 92 + j * 34))

        self.back_btn.draw(surface)

        # Hint bawah
        hint = Fonts.tiny.render('Tekan 1/2/3 atau klik card untuk memilih', True, (200, 185, 150))
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 25))
