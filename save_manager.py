"""
save_manager.py - Sistem Save/Load Game Tower Defense
======================================================
Menyimpan data game ke file savegame.json di folder project.
Tidak perlu database — pure Python + JSON.
"""

import json
import os
from datetime import datetime

SAVE_FILE = 'savegame.json'

# Mapping nama class tower ke string dan sebaliknya
TOWER_TYPE_MAP = {
    'IceTower':       'ice',
    'FireTower':      'fire',
    'LightningTower': 'lightning',
    'LaserTower':     'laser',
}
TOWER_CLASS_MAP = {v: k for k, v in TOWER_TYPE_MAP.items()}

TARGET_MODE_MAP = {
    'TargetMode.FIRST':     'FIRST',
    'TargetMode.LAST':      'LAST',
    'TargetMode.STRONGEST': 'STRONGEST',
    'TargetMode.CLOSEST':   'CLOSEST',
}


class SaveManager:

    @staticmethod
    def save(game) -> bool:
        """
        Simpan state game ke savegame.json.
        Mengembalikan True jika berhasil.
        """
        from config import TargetMode

        mode_to_str = {
            TargetMode.FIRST:     'FIRST',
            TargetMode.LAST:      'LAST',
            TargetMode.STRONGEST: 'STRONGEST',
            TargetMode.CLOSEST:   'CLOSEST',
        }

        towers_data = []
        for tower in game.towers:
            tower_type = TOWER_TYPE_MAP.get(type(tower).__name__, 'ice')
            towers_data.append({
                'type':        tower_type,
                'x':           tower._x,
                'y':           tower._y,
                'level':       tower._level,
                'target_mode': mode_to_str.get(tower._target_mode, 'FIRST'),
            })

        data = {
            'saved_at':          datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'difficulty':        game.difficulty.name,
            'wave':              game.wave_manager.wave_number,
            'score':             game.score,
            'money':             game.money,
            'base_health':       game.base_health,
            'enemies_killed':    game.enemies_killed,
            'total_money_earned': game.total_money_earned,
            'towers_placed':     game.towers_placed,
            'towers':            towers_data,
        }

        try:
            with open(SAVE_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"[SaveManager] Game disimpan: Wave {data['wave']}, Score {data['score']}")
            return True
        except Exception as e:
            print(f"[SaveManager] Gagal menyimpan: {e}")
            return False

    @staticmethod
    def load(game) -> bool:
        """
        Load state dari savegame.json ke object game yang sudah ada.
        Mengembalikan True jika berhasil.
        """
        from config import TargetMode, Difficulty, DifficultyConfig
        from game import IceTower, FireTower, LightningTower, LaserTower

        if not os.path.exists(SAVE_FILE):
            print("[SaveManager] File save tidak ditemukan.")
            return False

        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[SaveManager] Gagal membaca save: {e}")
            return False

        str_to_mode = {
            'FIRST':     TargetMode.FIRST,
            'LAST':      TargetMode.LAST,
            'STRONGEST': TargetMode.STRONGEST,
            'CLOSEST':   TargetMode.CLOSEST,
        }

        class_map = {
            'ice':       IceTower,
            'fire':      FireTower,
            'lightning': LightningTower,
            'laser':     LaserTower,
        }

        # Restore stats
        game.score             = data.get('score', 0)
        game.money             = data.get('money', 100)
        game.base_health       = data.get('base_health', 10)
        game.enemies_killed    = data.get('enemies_killed', 0)
        game.total_money_earned = data.get('total_money_earned', 0)
        game.towers_placed     = data.get('towers_placed', 0)

        # Restore wave number
        saved_wave = data.get('wave', 1)
        game.wave_manager.wave_number = saved_wave

        # Restore towers
        game.towers.clear()
        for td in data.get('towers', []):
            cls = class_map.get(td['type'])
            if cls:
                tower = cls(td['x'], td['y'])
                # Upgrade ke level yang tersimpan
                for _ in range(td['level'] - 1):
                    tower.upgrade()
                tower._target_mode = str_to_mode.get(td['target_mode'], TargetMode.FIRST)
                game.towers.append(tower)

        print(f"[SaveManager] Game dimuat: Wave {saved_wave}, Score {game.score}")
        return True

    @staticmethod
    def has_save() -> bool:
        """Cek apakah ada file save."""
        return os.path.exists(SAVE_FILE)

    @staticmethod
    def get_save_info() -> dict | None:
        """
        Ambil info singkat dari save file untuk ditampilkan di menu.
        Return None jika tidak ada save.
        """
        if not os.path.exists(SAVE_FILE):
            return None
        try:
            with open(SAVE_FILE, 'r') as f:
                data = json.load(f)
            return {
                'saved_at':   data.get('saved_at', '-'),
                'wave':       data.get('wave', 0),
                'score':      data.get('score', 0),
                'difficulty': data.get('difficulty', 'NORMAL'),
            }
        except Exception:
            return None

    @staticmethod
    def delete_save():
        """Hapus file save."""
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
            print("[SaveManager] Save dihapus.")
