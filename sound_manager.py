"""
sound_manager.py - Tower Defense Sound System
================================================

STRUKTUR FOLDER AUDIO (taruh di assets/sounds/):
--------------------------------------------------
SFX:
  assets/sounds/sfx/shoot_ice.wav        → Suara tembakan Ice Tower  (pendek, ~0.3s)
  assets/sounds/sfx/shoot_fire.wav       → Suara tembakan Fire Tower (pendek, ~0.3s)
  assets/sounds/sfx/shoot_lightning.wav  → Suara petir Lightning Tower (~0.4s)
  assets/sounds/sfx/shoot_laser.wav      → Suara laser LaserTower (~0.3s)
  assets/sounds/sfx/enemy_death.wav      → Suara musuh mati (~0.3s)
  assets/sounds/sfx/wave_complete.wav    → Suara wave selesai (~1.5s)
  assets/sounds/sfx/button_click.wav     → Suara klik tombol (~0.1s)
  assets/sounds/sfx/game_over.wav        → Suara game over (~2s)

MUSIC:
  assets/sounds/music/menu_music.ogg     → BGM menu (loop)
  assets/sounds/music/game_music.ogg     → BGM in-game (loop)

FORMAT YANG DIREKOMENDASIKAN:
  - SFX     : .wav (kualitas lebih baik untuk efek pendek)
  - Music   : .ogg (ukuran kecil, cocok untuk loop panjang)
  - Sample rate: 44100 Hz, stereo
  - Bit depth : 16-bit

TIPS CARI SOUND GRATIS:
  - https://freesound.org
  - https://opengameart.org
  - https://pixabay.com/sound-effects/
  - https://soundsnap.com (berbayar)

CATATAN:
  - Semua suara yang tidak ditemukan akan di-skip secara diam-diam (no error)
  - Volume bisa diatur lewat SoundManager.set_sfx_volume() dan set_music_volume()
  - Panggil SoundManager.init() SETELAH pygame.init() di main.py
"""

import pygame
import os


class SoundManager:
    """
    Singleton sound manager. Akses lewat SoundManager.instance() atau
    langsung memanggil method static/class.
    """

    _instance = None

    # ── Cooldown per jenis tembakan (frame) agar tidak overlap terlalu sering
    _SHOOT_COOLDOWN = {
        'ice':       8,
        'fire':      6,
        'lightning': 10,
        'laser':     8,
    }

    def __init__(self):
        self._initialized = False
        self._sfx: dict[str, pygame.mixer.Sound | None] = {}
        self._sfx_volume   = 0.7   # 0.0 – 1.0
        self._music_volume = 0.5
        self._sfx_enabled  = True
        self._music_enabled = True
        self._current_music = None

        # Cooldown timer per jenis shoot (agar tidak spam terlalu sering)
        self._shoot_cooldowns: dict[str, int] = {k: 0 for k in self._SHOOT_COOLDOWN}

    # ──────────────────────────────────────────
    #  SINGLETON
    # ──────────────────────────────────────────

    @classmethod
    def instance(cls) -> 'SoundManager':
        if cls._instance is None:
            cls._instance = SoundManager()
        return cls._instance

    # ──────────────────────────────────────────
    #  INIT
    # ──────────────────────────────────────────

    @classmethod
    def init(cls):
        """Panggil sekali setelah pygame.init() di main.py."""
        inst = cls.instance()
        if inst._initialized:
            return

        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            pygame.mixer.set_num_channels(16)
            inst._initialized = True
        except Exception as e:
            print(f"[SoundManager] Gagal init mixer: {e}")
            return

        inst._load_all()

    def _load_all(self):
        sfx_files = {
            'shoot_ice':       'assets/sounds/sfx/shoot_ice.wav',
            'shoot_fire':      'assets/sounds/sfx/shoot_fire.wav',
            'shoot_lightning': 'assets/sounds/sfx/shoot_lightning.wav',
            'shoot_laser':     'assets/sounds/sfx/shoot_laser.wav',
            'enemy_death':     'assets/sounds/sfx/enemy_death.wav',
            'wave_complete':   'assets/sounds/sfx/wave_complete.wav',
            'button_click':    'assets/sounds/sfx/button_click.wav',
            'game_over':       'assets/sounds/sfx/game_over.wav',
        }

        for key, path in sfx_files.items():
            self._sfx[key] = self._load_sound(path)

    def _load_sound(self, path: str) -> 'pygame.mixer.Sound | None':
        if not os.path.exists(path):
            return None
        try:
            sound = pygame.mixer.Sound(path)
            return sound
        except Exception as e:
            print(f"[SoundManager] Gagal load {path}: {e}")
            return None

    # ──────────────────────────────────────────
    #  VOLUME CONTROL
    # ──────────────────────────────────────────

    def set_sfx_volume(self, volume: float):
        """volume: 0.0 – 1.0"""
        self._sfx_volume = max(0.0, min(1.0, volume))
        for sound in self._sfx.values():
            if sound:
                sound.set_volume(self._sfx_volume)

    def set_music_volume(self, volume: float):
        """volume: 0.0 – 1.0"""
        self._music_volume = max(0.0, min(1.0, volume))
        if self._initialized:
            pygame.mixer.music.set_volume(self._music_volume)

    def set_sfx_enabled(self, enabled: bool):
        self._sfx_enabled = enabled

    def set_music_enabled(self, enabled: bool):
        self._music_enabled = enabled
        if not enabled:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()

    # ──────────────────────────────────────────
    #  PLAY SFX
    # ──────────────────────────────────────────

    def _play(self, key: str):
        if not self._initialized or not self._sfx_enabled:
            return
        sound = self._sfx.get(key)
        if sound:
            sound.set_volume(self._sfx_volume)
            sound.play()

    def play_shoot_ice(self):
        if self._shoot_cooldowns['ice'] <= 0:
            self._play('shoot_ice')
            self._shoot_cooldowns['ice'] = self._SHOOT_COOLDOWN['ice']

    def play_shoot_fire(self):
        if self._shoot_cooldowns['fire'] <= 0:
            self._play('shoot_fire')
            self._shoot_cooldowns['fire'] = self._SHOOT_COOLDOWN['fire']

    def play_shoot_lightning(self):
        if self._shoot_cooldowns['lightning'] <= 0:
            self._play('shoot_lightning')
            self._shoot_cooldowns['lightning'] = self._SHOOT_COOLDOWN['lightning']

    def play_shoot_laser(self):
        if self._shoot_cooldowns['laser'] <= 0:
            self._play('shoot_laser')
            self._shoot_cooldowns['laser'] = self._SHOOT_COOLDOWN['laser']

    def play_enemy_death(self):
        self._play('enemy_death')

    def play_wave_complete(self):
        self._play('wave_complete')

    def play_button_click(self):
        self._play('button_click')

    def play_game_over(self):
        self.stop_music()
        self._play('game_over')

    # ──────────────────────────────────────────
    #  MUSIC
    # ──────────────────────────────────────────

    def play_music(self, track: str, loops: int = -1):
        """
        track: 'menu' atau 'game'
        loops: -1 = loop selamanya
        """
        if not self._initialized or not self._music_enabled:
            return

        # Support OGG dan MP3
        base_paths = {
            'menu': 'assets/sounds/music/menu_music',
            'game': 'assets/sounds/music/game_music',
        }
        base = base_paths.get(track)
        if not base:
            return

        path = None
        for ext in ['.ogg', '.mp3', '.wav']:
            candidate = base + ext
            if os.path.exists(candidate):
                path = candidate
                break

        if not path:
            return

        if self._current_music == track:
            return  # Sudah main, tidak perlu restart

        try:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._music_volume)
            pygame.mixer.music.play(loops)
            self._current_music = track
        except Exception as e:
            print(f"[SoundManager] Gagal play music {path}: {e}")

    def stop_music(self):
        if self._initialized:
            pygame.mixer.music.stop()
        self._current_music = None

    def pause_music(self):
        if self._initialized:
            pygame.mixer.music.pause()

    def unpause_music(self):
        if self._initialized:
            pygame.mixer.music.unpause()

    # ──────────────────────────────────────────
    #  UPDATE (panggil tiap frame di game loop)
    # ──────────────────────────────────────────

    def update(self):
        """Kurangi cooldown shoot setiap frame. Panggil di game.update()."""
        for key in self._shoot_cooldowns:
            if self._shoot_cooldowns[key] > 0:
                self._shoot_cooldowns[key] -= 1

    # ──────────────────────────────────────────
    #  SINKRONISASI SETTINGS (dari SettingsMenu)
    # ──────────────────────────────────────────

    def apply_settings(self, settings: dict):
        """
        Sync dengan dict settings dari main.py.
        settings keys: 'vol_master', 'vol_sfx', 'vol_music'
        Nilai: 0–100
        """
        master = settings.get('vol_master', 80) / 100
        sfx    = settings.get('vol_sfx',    70) / 100 * master
        music  = settings.get('vol_music',  60) / 100 * master
        self.set_sfx_volume(sfx)
        self.set_music_volume(music)


# ──────────────────────────────────────────────
#  SHORTCUT MODULE-LEVEL (opsional, lebih ringkas)
# ──────────────────────────────────────────────

def sfx(key_method: str):
    """
    Shortcut: sfx('button_click') → SoundManager.instance().play_button_click()
    """
    inst = SoundManager.instance()
    method = getattr(inst, f'play_{key_method}', None)
    if method:
        method()
