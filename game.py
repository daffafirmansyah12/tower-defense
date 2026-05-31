import pygame
import random
import math
from abc import ABC, abstractmethod
from config import *
import sprites as spr

class GameObject(ABC):
    def __init__(self, x, y, color):
        self._x = x
        self._y = y
        self._color = color

    @abstractmethod
    def draw(self, screen):
        pass

    @abstractmethod
    def move(self):
        pass


class Enemy(GameObject):
    def __init__(self, x, y, speed, health, color, difficulty_multiplier=None):
        super().__init__(x, y, color)

        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}

        self._speed = speed * difficulty_multiplier['enemy_speed_multiplier']
        self._original_speed = self._speed
        self._health = health * difficulty_multiplier['enemy_health_multiplier']
        self._max_health = self._health
        self._size = 40
        self._is_slowed = False
        self._has_special_ability = False
        self._ability_type = None

    @property
    def speed(self):
        return self._speed

    @speed.setter
    def speed(self, value):
        self._speed = value

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = max(0, value)

    def move(self):
        self._x += self._speed
        min_y = 90 + 50
        max_y = 520 - 50

        if self._y < min_y:
            self._y = min_y
        elif self._y > max_y:
            self._y = max_y

    def take_damage(self, damage):
        self._health -= damage
        if self._health < 0:
            self._health = 0

    def apply_slow(self, slow_amount=0.5):
        self._original_speed = self._speed
        self._speed = self._original_speed * slow_amount
        self._is_slowed = True

    def remove_slow(self):
        if self._is_slowed:
            self._speed = self._original_speed
            self._is_slowed = False

    def draw(self, screen):
        # Fallback generik — subclass override dengan sprite spesifik
        spr._draw_enemy_sprite(screen, self, '', self._color)

    def get_rect(self):
        return pygame.Rect(
            self._x,
            self._y,
            self._size,
            self._size
        )

    @abstractmethod
    def get_reward(self):
        pass


class ShieldEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 1.2, 4, BLUE, difficulty_multiplier)
        self._size = 45
        self._has_special_ability = True
        self._ability_type = "SHIELD"
        self._shield_hp = 3
        self._max_shield = 3

    def take_damage(self, damage):
        if self._shield_hp > 0:
            self._shield_hp -= damage
            if self._shield_hp < 0:
                remaining_damage = abs(self._shield_hp)
                self._shield_hp = 0
                self._health -= remaining_damage
        else:
            self._health -= damage

        if self._health < 0:
            self._health = 0

    def draw(self, screen):
        spr.draw_shield_enemy(screen, self)

    def get_reward(self):
        return 30


class HealingEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 1.0, 6, PINK, difficulty_multiplier)
        self._size = 42
        self._has_special_ability = True
        self._ability_type = "HEALING"
        self._heal_radius = 100
        self._heal_amount = 1
        self._heal_cooldown = 0
        self._heal_interval = 30

    def move(self):
        self._x += self._speed
        self._heal_cooldown -= 1

    def draw(self, screen):
        spr.draw_healer_enemy(screen, self)

    def heal_nearby(self, enemies):
        if self._heal_cooldown <= 0:
            for enemy in enemies:
                if enemy is not self:
                    distance = math.hypot(
                        self._x - enemy._x,
                        self._y - enemy._y
                    )

                    if distance <= self._heal_radius:
                        enemy._health = min(enemy._health + self._heal_amount, enemy._max_health)

            self._heal_cooldown = self._heal_interval

    def get_reward(self):
        return 35


class SplitEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None, is_child=False):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}

        speed = 1.0 if not is_child else 2.0
        health = 3 if not is_child else 1

        super().__init__(x, y, speed, health, ORANGE, difficulty_multiplier)
        self._size = 45 if not is_child else 25
        self._has_special_ability = True
        self._ability_type = "SPLIT"
        self._is_child = is_child

    def draw(self, screen):
        spr.draw_split_enemy(screen, self)

    def create_splits(self):
        split1 = SplitEnemy(self._x - 20, self._y - 20, is_child=True)
        split2 = SplitEnemy(self._x + 20, self._y + 20, is_child=True)
        return [split1, split2]

    def get_reward(self):
        return 15 if not self._is_child else 5


class FastEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 3.5, 2, RED, difficulty_multiplier)
        self._size = 40

    def draw(self, screen):
        spr.draw_fast_enemy(screen, self)

    def get_reward(self):
        return 10


class TankEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 1.5, 5, PURPLE, difficulty_multiplier)
        self._size = 55

    def draw(self, screen):
        spr.draw_tank_enemy(screen, self)

    def get_reward(self):
        return 15


class SlowEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 0.8, 8, ORANGE, difficulty_multiplier)
        self._size = 50

    def draw(self, screen):
        spr.draw_slow_enemy(screen, self)

    def get_reward(self):
        return 20


class FlyingEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 2.5, 3, LIME, difficulty_multiplier)
        self._size = 35
        self._hover_offset = 0

    def move(self):
        self._x += self._speed
        self._hover_offset = math.sin(pygame.time.get_ticks() * 0.005) * 10

    def draw(self, screen):
        spr.draw_flying_enemy(screen, self)

    def get_reward(self):
        return 25


class BossEnemy(Enemy):
    def __init__(self, x, y, difficulty_multiplier=None):
        if difficulty_multiplier is None:
            difficulty_multiplier = {'enemy_speed_multiplier': 1.0, 'enemy_health_multiplier': 1.0}
        super().__init__(x, y, 1.0, 20, DARK_ORANGE, difficulty_multiplier)
        self._size = 70

    def move(self):
        self._x += self._speed

    def draw(self, screen):
        spr.draw_boss_enemy(screen, self)

    def get_reward(self):
        return 100


class Bullet(GameObject):
    def __init__(self, x, y, target, damage, offset_y=0):
        super().__init__(x, y, YELLOW)

        self.target = target
        self.damage = damage
        self._speed = 7
        self._radius = 5
        self.offset_y = offset_y

    def move(self):
        if self.target:
            dx = self.target._x - self._x
            dy = self.target._y - self._y

            distance = math.sqrt(dx ** 2 + dy ** 2)

            if distance != 0:
                self._x += dx / distance * self._speed
                self._y += dy / distance * self._speed

    def draw(self, screen):
        spr.draw_bullet_default(screen, self)

    def hit_target(self):
        if self.target:
            return math.hypot(
                self._x - self.target._x,
                self._y - self.target._y
            ) < 20

        return False


class LightningBolt(GameObject):
    def __init__(self, x, y, targets, damage):
        super().__init__(x, y, LIGHT_CYAN)
        self.targets = targets
        self.damage = damage
        self._lifetime = 10
        self._duration = 0

    def move(self):
        self._duration += 1

    def draw(self, screen):
        for target in self.targets:
            pygame.draw.line(
                screen,
                LIGHT_CYAN,
                (int(self._x), int(self._y)),
                (int(target._x + target._size // 2), int(target._y + target._size // 2)),
                3
            )

            pygame.draw.circle(
                screen,
                LIGHT_CYAN,
                (int(target._x + target._size // 2), int(target._y + target._size // 2)),
                10,
                2
            )

    def is_alive(self):
        return self._duration < self._lifetime


class LaserBeam(GameObject):
    def __init__(self, x, y, target, damage):
        super().__init__(x, y, MAGENTA)
        self.target = target
        self.damage = damage
        self._lifetime = 20
        self._duration = 0

    def move(self):
        self._duration += 1

    def draw(self, screen):
        if self.target:
            pygame.draw.line(
                screen,
                MAGENTA,
                (int(self._x), int(self._y)),
                (int(self.target._x + self.target._size // 2),
                 int(self.target._y + self.target._size // 2)),
                5
            )

            pygame.draw.circle(
                screen,
                MAGENTA,
                (int(self.target._x + self.target._size // 2),
                 int(self.target._y + self.target._size // 2)),
                15,
                3
            )

    def is_alive(self):
        return self._duration < self._lifetime


class Tower(GameObject):
    def __init__(self, x, y, color, damage, range_radius):
        super().__init__(x, y, color)

        self._damage = damage
        self._range = range_radius
        self._cooldown = 0
        self._level = 1
        self._base_cost = 0
        self._is_selected = False
        self._target_mode = TargetMode.FIRST

    @property
    def damage(self):
        return self._damage

    @property
    def range(self):
        return self._range

    @property
    def level(self):
        return self._level

    @property
    def target_mode(self):
        return self._target_mode

    def move(self):
        pass

    def draw(self, screen):
        # Subclass override dengan sprite spesifik
        spr._draw_tower_base(screen, self, self._color)
        spr._draw_tower_common(screen, self, None)

    def get_target(self, enemies):
        if not enemies:
            return None

        in_range_enemies = []
        for enemy in enemies:
            distance = math.hypot(
                self._x - enemy._x,
                self._y - enemy._y
            )
            if distance <= self._range:
                in_range_enemies.append(enemy)

        if not in_range_enemies:
            return None

        if self._target_mode == TargetMode.FIRST:
            return min(in_range_enemies, key=lambda e: e._x)

        elif self._target_mode == TargetMode.LAST:
            return max(in_range_enemies, key=lambda e: e._x)

        elif self._target_mode == TargetMode.STRONGEST:
            return max(in_range_enemies, key=lambda e: e._health)

        elif self._target_mode == TargetMode.CLOSEST:
            return min(in_range_enemies, key=lambda e: math.hypot(
                self._x - e._x,
                self._y - e._y
            ))

        return None

    def shoot(self, enemies):
        bullets = []

        if self._cooldown > 0:
            self._cooldown -= 1
            return bullets

        target = self.get_target(enemies)

        if target:
            bullets.append(
                Bullet(
                    self._x,
                    self._y,
                    target,
                    self._damage
                )
            )
            self._cooldown = 40

        return bullets

    def upgrade(self):
        self._level += 1
        self._damage += 1
        self._range += 10

    def cycle_target_mode(self):
        modes = [TargetMode.FIRST, TargetMode.LAST, TargetMode.STRONGEST, TargetMode.CLOSEST]
        current_index = modes.index(self._target_mode)
        self._target_mode = modes[(current_index + 1) % len(modes)]

    def get_sell_value(self):
        total_investment = self._base_cost + ((self._level - 1) * 30)
        return int(total_investment * 0.5)

    @abstractmethod
    def get_cost(self):
        pass


class IceTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, 1, 140)
        self._base_cost = 40

    def get_cost(self):
        return 40

    def draw(self, screen):
        spr.draw_ice_tower(screen, self)

    def shoot(self, enemies):
        bullets = []

        if self._cooldown > 0:
            self._cooldown -= 1
            return bullets

        target = self.get_target(enemies)

        if target:
            b = Bullet(self._x, self._y, target, self._damage)
            b.draw = lambda s: spr.draw_bullet_ice(s, b)
            bullets.append(b)
            self._cooldown = 40

        return bullets


class FireTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 2, 120)
        self._base_cost = 60

    def get_cost(self):
        return 60

    def draw(self, screen):
        spr.draw_fire_tower(screen, self)

    def shoot(self, enemies):
        bullets = []

        if self._cooldown > 0:
            self._cooldown -= 1
            return bullets

        target1 = self.get_target(enemies)

        if target1:
            b1 = Bullet(self._x, self._y, target1, self._damage)
            b1.draw = lambda s: spr.draw_bullet_fire(s, b1)
            bullets.append(b1)

            in_range_enemies = []
            for enemy in enemies:
                if enemy is not target1:
                    distance = math.hypot(self._x - enemy._x, self._y - enemy._y)
                    if distance <= self._range:
                        in_range_enemies.append(enemy)

            if in_range_enemies:
                target2 = min(in_range_enemies, key=lambda e: math.hypot(self._x - e._x, self._y - e._y))
                b2 = Bullet(self._x, self._y, target2, self._damage)
            else:
                b2 = Bullet(self._x, self._y, target1, self._damage)
            b2.draw = lambda s: spr.draw_bullet_fire(s, b2)
            bullets.append(b2)

            self._cooldown = 35

        return bullets


class LightningTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, LIGHT_CYAN, 1, 160)
        self._base_cost = 80

    def get_cost(self):
        return 80

    def draw(self, screen):
        spr.draw_lightning_tower(screen, self)

    def shoot(self, enemies):
        bullets = []

        if self._cooldown > 0:
            self._cooldown -= 1
            return bullets

        in_range_enemies = []
        for enemy in enemies:
            distance = math.hypot(
                self._x - enemy._x,
                self._y - enemy._y
            )
            if distance <= self._range:
                in_range_enemies.append(enemy)

        if in_range_enemies:
            targets = in_range_enemies[:3]
            bullets.append(
                LightningBolt(
                    self._x,
                    self._y,
                    targets,
                    self._damage
                )
            )
            self._cooldown = 50

        return bullets


class LaserTower(Tower):
    def __init__(self, x, y):
        super().__init__(x, y, MAGENTA, 4, 130)
        self._base_cost = 100

    def get_cost(self):
        return 100

    def draw(self, screen):
        spr.draw_laser_tower(screen, self)

    def shoot(self, enemies):
        bullets = []

        if self._cooldown > 0:
            self._cooldown -= 1
            return bullets

        target = self.get_target(enemies)

        if target:
            bullets.append(
                LaserBeam(
                    self._x,
                    self._y,
                    target,
                    self._damage
                )
            )
            self._cooldown = 30

        return bullets


class Wave:
    def __init__(self, wave_number, difficulty_config):
        self.wave_number = wave_number
        self.enemies_to_spawn = []
        self.current_spawn_index = 0
        self.state = WaveState.IDLE
        self.spawn_timer = 0
        self.difficulty_config = difficulty_config
        self.spawn_rate = difficulty_config['spawn_rate']

        self._generate_enemies()

    def _generate_enemies(self):
        fast_count = 3 + (self.wave_number // 2)
        tank_count = 1 + (self.wave_number // 3)
        slow_count = self.wave_number // 4
        flying_count = 0 if self.wave_number < 3 else (self.wave_number - 2) // 2

        boss_count = 1 if (self.wave_number % 5 == 0 and self.wave_number > 0) else 0

        shield_count = 0 if self.wave_number < 5 else (self.wave_number - 4) // 2
        healing_count = 0 if self.wave_number < 6 else (self.wave_number - 5) // 3
        split_count = 0 if self.wave_number < 7 else (self.wave_number - 6) // 2

        enemy_classes = (
                [FastEnemy] * fast_count +
                [TankEnemy] * tank_count +
                [SlowEnemy] * slow_count +
                [FlyingEnemy] * flying_count +
                [BossEnemy] * boss_count +
                [ShieldEnemy] * shield_count +
                [HealingEnemy] * healing_count +
                [SplitEnemy] * split_count
        )

        random.shuffle(enemy_classes)

        for enemy_class in enemy_classes:
            self.enemies_to_spawn.append(enemy_class)

    def get_wave_preview(self):
        fast_count = self.enemies_to_spawn.count(FastEnemy)
        tank_count = self.enemies_to_spawn.count(TankEnemy)
        slow_count = self.enemies_to_spawn.count(SlowEnemy)
        flying_count = self.enemies_to_spawn.count(FlyingEnemy)
        boss_count = self.enemies_to_spawn.count(BossEnemy)
        shield_count = self.enemies_to_spawn.count(ShieldEnemy)
        healing_count = self.enemies_to_spawn.count(HealingEnemy)
        split_count = self.enemies_to_spawn.count(SplitEnemy)

        preview = ""
        if fast_count > 0:
            preview += f"Fast:{fast_count} "
        if tank_count > 0:
            preview += f"Tank:{tank_count} "
        if slow_count > 0:
            preview += f"Slow:{slow_count} "
        if flying_count > 0:
            preview += f"Flying:{flying_count} "
        if boss_count > 0:
            preview += f"BOSS:{boss_count} "
        if shield_count > 0:
            preview += f"Shield:{shield_count} "
        if healing_count > 0:
            preview += f"Heal:{healing_count} "
        if split_count > 0:
            preview += f"Split:{split_count} "

        return preview.strip()

    def start(self):
        self.state = WaveState.SPAWNING
        self.current_spawn_index = 0
        self.spawn_timer = 0

    def update(self):
        if self.state != WaveState.SPAWNING:
            return None

        self.spawn_timer += 1

        if self.spawn_timer >= self.spawn_rate:
            if self.current_spawn_index < len(self.enemies_to_spawn):
                enemy_class = self.enemies_to_spawn[self.current_spawn_index]
                new_enemy = enemy_class(-50, random.randint(100, 500), self.difficulty_config)

                self.current_spawn_index += 1
                self.spawn_timer = 0

                return new_enemy
            else:
                self.state = WaveState.IN_PROGRESS
                return None

        return None

    def is_completed(self, remaining_enemies_count):
        return (self.state == WaveState.IN_PROGRESS and
                self.current_spawn_index >= len(self.enemies_to_spawn) and
                remaining_enemies_count == 0)


class WaveManager:
    def __init__(self, difficulty_config):
        self.current_wave = None
        self.wave_number = 0
        self.state = WaveState.IDLE
        self.gap_timer = 0
        self.gap_duration = 120
        self.difficulty_config = difficulty_config

    def start_next_wave(self):
        self.wave_number += 1
        self.current_wave = Wave(self.wave_number, self.difficulty_config)
        self.current_wave.start()
        self.state = WaveState.SPAWNING

    def update(self):
        if self.current_wave:
            new_enemy = self.current_wave.update()
            return new_enemy
        return None

    def check_wave_completed(self, remaining_enemies_count):
        if self.current_wave and self.current_wave.is_completed(remaining_enemies_count):
            return True
        return False

    def get_wave_info(self):
        if self.current_wave:
            return {
                'number': self.wave_number,
                'preview': self.current_wave.get_wave_preview(),
                'spawned': self.current_wave.current_spawn_index,
                'total': len(self.current_wave.enemies_to_spawn)
            }
        return None


class Game:
    def __init__(self, difficulty=Difficulty.NORMAL):
        self.difficulty = difficulty
        self.difficulty_config = DifficultyConfig.get_config(difficulty)

        self.enemies = []
        self.towers = []
        self.bullets = []
        self.special_bullets = []

        self.wave_manager = WaveManager(self.difficulty_config)
        self.game_state = GameState.PLAYING
        self.gap_timer = 0
        self.gap_duration = 120

        self.score = 0
        self.money = self.difficulty_config['starting_money']
        self.base_health = self.difficulty_config['base_health']
        self.wave_bonus = 0

        # Tracking statistik untuk GameOverScreen
        self.enemies_killed     = 0
        self.total_money_earned = self.difficulty_config['starting_money']
        self.towers_placed      = 0

        self.selected_tower = None
        self.sell_feedback_timer = 0
        self.sell_feedback_text = ""
        self.mode_change_feedback_timer = 0
        self.mode_change_text = ""

        self.running = True

        self.is_paused = False
        self.turbo_mode = False
        self.turbo_toggle_timer = 0

        # Load gameplay background
        try:
            self._bg = pygame.image.load('assets/images/gameplay_bg.png').convert()
            self._bg = pygame.transform.scale(self._bg, (WIDTH, HEIGHT))
        except Exception:
            self._bg = None

    def start_first_wave(self):
        self.wave_manager.start_next_wave()

    def is_valid_tower_placement(self, x, y):
        min_x = 0 + 100
        max_x = WIDTH - 100
        min_y = 90 + 100
        max_y = 520 - 100

        return min_x <= x <= max_x and min_y <= y <= max_y

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused and self.turbo_mode:
            self.turbo_mode = False

    def toggle_turbo(self):
        if not self.is_paused:
            self.turbo_mode = not self.turbo_mode

    def update(self):

        if self.game_state == GameState.WAVE_GAP:
            self._handle_wave_gap()
            return

        if self.is_paused:
            return

        speed_multiplier = 2.0 if self.turbo_mode else 1.0

        new_enemy = self.wave_manager.update()
        if new_enemy:
            self.enemies.append(new_enemy)

        for enemy in self.enemies[:]:
            enemy.move()

            if enemy._x > WIDTH:
                self.base_health -= 1
                self.enemies.remove(enemy)

        if len(self.enemies) > 200:
            self.enemies = self.enemies[-150:]

        for enemy in self.enemies:
            if isinstance(enemy, HealingEnemy):
                enemy.heal_nearby(self.enemies)

        for tower in self.towers:
            new_bullets = tower.shoot(self.enemies)
            for b in new_bullets:
                if isinstance(b, (LightningBolt, LaserBeam)):
                    self.special_bullets.append(b)
                else:
                    self.bullets.append(b)

        for bullet in self.bullets[:]:
            bullet.move()

            if bullet.hit_target():
                bullet.target.take_damage(bullet.damage)

                if bullet.target.health <= 0:
                    reward = bullet.target.get_reward()
                    self.score += reward
                    self.money += reward
                    self.enemies_killed += 1
                    self.total_money_earned += reward

                    if isinstance(bullet.target, SplitEnemy) and not bullet.target._is_child:
                        splits = bullet.target.create_splits()
                        self.enemies.extend(splits)

                    if bullet.target in self.enemies:
                        self.enemies.remove(bullet.target)

                self.bullets.remove(bullet)

        for special in self.special_bullets[:]:
            special.move()

            if isinstance(special, LightningBolt):
                for target in special.targets:
                    target.take_damage(special.damage)

                    if target.health <= 0:
                        reward = target.get_reward()
                        self.score += reward
                        self.money += reward
                        self.enemies_killed += 1
                        self.total_money_earned += reward

                        if isinstance(target, SplitEnemy) and not target._is_child:
                            splits = target.create_splits()
                            self.enemies.extend(splits)

                        if target in self.enemies:
                            self.enemies.remove(target)

            elif isinstance(special, LaserBeam):
                if special.target and special.target in self.enemies:
                    special.target.take_damage(special.damage)

                    if special.target.health <= 0:
                        reward = special.target.get_reward()
                        self.score += reward
                        self.money += reward
                        self.enemies_killed += 1
                        self.total_money_earned += reward

                        if isinstance(special.target, SplitEnemy) and not special.target._is_child:
                            splits = special.target.create_splits()
                            self.enemies.extend(splits)

                        if special.target in self.enemies:
                            self.enemies.remove(special.target)

            if not special.is_alive():
                self.special_bullets.remove(special)

        if self.wave_manager.check_wave_completed(len(self.enemies)):
            self._complete_wave()

        if self.base_health <= 0:
            self.game_state = GameState.GAME_OVER

        if self.sell_feedback_timer > 0:
            self.sell_feedback_timer -= 1

        if self.mode_change_feedback_timer > 0:
            self.mode_change_feedback_timer -= 1

    def _complete_wave(self):
        self.wave_bonus = 50
        self.money += self.wave_bonus
        self.score += self.wave_bonus

        self.game_state = GameState.WAVE_GAP
        self.gap_timer = 0

    def _handle_wave_gap(self):
        self.gap_timer += 1

        if self.gap_timer >= self.gap_duration:
            self.wave_manager.start_next_wave()
            self.game_state = GameState.PLAYING

    def draw_map(self):
        if self._bg:
            screen.blit(self._bg, (0, 0))
        else:
            screen.fill(BLACK)
            pygame.draw.rect(screen, (58, 92, 30), (0, 90, WIDTH, 430))
            pygame.draw.rect(screen, (107, 90, 58), (0, 140, WIDTH, 340))

    def draw_ui(self):
        score_text = font.render(
            f"Score: {self.score}",
            True,
            WHITE
        )

        money_text = font.render(
            f"Money: ${self.money}",
            True,
            GREEN if self.money >= 80 else YELLOW if self.money >= 40 else RED
        )

        health_text = font.render(
            f"Base HP: {self.base_health}",
            True,
            RED if self.base_health <= 3 else WHITE
        )

        wave_text = font.render(
            f"Wave: {self.wave_manager.wave_number}",
            True,
            CYAN
        )

        difficulty_text = font.render(
            f"[{self.difficulty_config['difficulty_name']}]",
            True,
            YELLOW
        )

        screen.blit(score_text, (20, 20))
        screen.blit(money_text, (20, 55))
        screen.blit(health_text, (250, 20))
        screen.blit(wave_text, (250, 55))
        screen.blit(difficulty_text, (550, 20))

        tower_count_text = small_font.render(
            f"Towers: {len(self.towers)}/25",
            True,
            CYAN if len(self.towers) < 20 else YELLOW if len(self.towers) < 24 else RED
        )
        screen.blit(tower_count_text, (750, 20))

        wave_info = self.wave_manager.get_wave_info()
        if wave_info:
            preview_text = tiny_font.render(
                f"Next: {wave_info['preview']} | {wave_info['spawned']}/{wave_info['total']}",
                True,
                YELLOW
            )
            screen.blit(preview_text, (20, 530))

        info = small_font.render(
            "1=Ice 2=Fire 3=Lightning 4=Laser | U=Upgrade T=Target RC=Sell",
            True,
            WHITE
        )
        screen.blit(info, (20, 550))

        if self.turbo_mode:
            turbo_text = font.render("TURBO x2", True, RED)
            screen.blit(turbo_text, (WIDTH // 2 - 80, 50))

        if self.is_paused:
            pause_text = font.render("PAUSED", True, YELLOW)
            screen.blit(pause_text, (WIDTH // 2 - 70, HEIGHT // 2 - 50))

            resume_text = small_font.render("Press SPACE to Resume", True, WHITE)
            screen.blit(resume_text, (WIDTH // 2 - 130, HEIGHT // 2 + 20))

        if self.game_state == GameState.WAVE_GAP:
            gap_time_left = (self.gap_duration - self.gap_timer) / 60
            gap_text = font.render(
                f"Wave Complete! Next in {gap_time_left:.1f}s",
                True,
                GREEN
            )
            screen.blit(gap_text, (WIDTH // 2 - 180, HEIGHT // 2 - 100))

        if self.selected_tower:
            sell_value = self.selected_tower.get_sell_value()

            tower_names = {
                IceTower: "Ice Tower",
                FireTower: "Fire Tower",
                LightningTower: "Lightning Tower",
                LaserTower: "Laser Tower"
            }
            tower_type = tower_names.get(type(self.selected_tower), "Tower")

            mode_names = {
                TargetMode.FIRST: "FIRST",
                TargetMode.LAST: "LAST",
                TargetMode.STRONGEST: "STRONGEST",
                TargetMode.CLOSEST: "CLOSEST"
            }

            panel_x = 20
            panel_y = 540

            info_text = small_font.render(
                f"{tower_type} | Lvl: {self.selected_tower.level} | DMG: {self.selected_tower.damage}",
                True,
                YELLOW
            )
            mode_text = small_font.render(
                f"Target: {mode_names[self.selected_tower.target_mode]} | Sell: ${sell_value}",
                True,
                CYAN
            )

            screen.blit(info_text, (panel_x, panel_y))
            screen.blit(mode_text, (panel_x, panel_y + 25))

        if self.sell_feedback_timer > 0:
            feedback_text = font.render(
                self.sell_feedback_text,
                True,
                GREEN
            )
            screen.blit(feedback_text, (WIDTH // 2 - 100, HEIGHT // 2 - 50))

        if self.mode_change_feedback_timer > 0:
            feedback_text = font.render(
                self.mode_change_text,
                True,
                CYAN
            )
            screen.blit(feedback_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))

    def draw(self):
        self.draw_map()

        for tower in self.towers:
            tower.draw(screen)

        for enemy in self.enemies:
            enemy.draw(screen)

        for bullet in self.bullets:
            bullet.draw(screen)

        for special in self.special_bullets:
            special.draw(screen)

        # HUD dan display.update() dihandle oleh GameRunner di main.py
        # Panggil draw_ui() hanya jika dijalankan standalone (tanpa GameRunner)
        if not hasattr(self, '_managed_by_runner'):
            self.draw_ui()
            pygame.display.update()

    def game_over(self):
        screen.fill(BLACK)

        text = font.render(
            "GAME OVER",
            True,
            RED
        )

        score = font.render(
            f"Final Score: {self.score}",
            True,
            WHITE
        )

        wave = font.render(
            f"Wave Reached: {self.wave_manager.wave_number}",
            True,
            WHITE
        )

        difficulty = font.render(
            f"Difficulty: {self.difficulty_config['difficulty_name']}",
            True,
            YELLOW
        )

        screen.blit(text, (WIDTH // 2 - 120, HEIGHT // 2 - 100))
        screen.blit(score, (WIDTH // 2 - 140, HEIGHT // 2 - 20))
        screen.blit(wave, (WIDTH // 2 - 140, HEIGHT // 2 + 20))
        screen.blit(difficulty, (WIDTH // 2 - 140, HEIGHT // 2 + 60))

        pygame.display.update()

        pygame.time.delay(4000)

    def place_tower(self, tower_type):
        if len(self.towers) >= 25:
            return

        x, y = pygame.mouse.get_pos()

        if not self.is_valid_tower_placement(x, y):
            return

        y = max(140, min(y, 480))

        if tower_type == "ice" and self.money >= 40:
            self.towers.append(IceTower(x, y))
            self.money -= 40
            self.selected_tower = None
            self.towers_placed += 1

        elif tower_type == "fire" and self.money >= 60:
            self.towers.append(FireTower(x, y))
            self.money -= 60
            self.selected_tower = None
            self.towers_placed += 1

        elif tower_type == "lightning" and self.money >= 80:
            self.towers.append(LightningTower(x, y))
            self.money -= 80
            self.selected_tower = None
            self.towers_placed += 1

        elif tower_type == "laser" and self.money >= 100:
            self.towers.append(LaserTower(x, y))
            self.money -= 100
            self.selected_tower = None
            self.towers_placed += 1

    def upgrade_tower(self):
        if self.selected_tower and self.money >= 30:
            self.selected_tower.upgrade()
            self.money -= 30

    def change_target_mode(self):
        if self.selected_tower:
            self.selected_tower.cycle_target_mode()

            mode_names = {
                TargetMode.FIRST: "FIRST (Leftmost)",
                TargetMode.LAST: "LAST (Rightmost)",
                TargetMode.STRONGEST: "STRONGEST (High HP)",
                TargetMode.CLOSEST: "CLOSEST (To Tower)"
            }

            self.mode_change_text = f"Target: {mode_names[self.selected_tower.target_mode]}"
            self.mode_change_feedback_timer = 60

    def select_tower(self, x, y):
        for tower in self.towers:
            distance = math.hypot(x - tower._x, y - tower._y)
            if distance <= 30:
                self.selected_tower = tower
                tower._is_selected = True
                return

        for tower in self.towers:
            tower._is_selected = False
        self.selected_tower = None

    def sell_tower(self, x, y):
        for tower in self.towers[:]:
            distance = math.hypot(x - tower._x, y - tower._y)
            if distance <= 30:
                sell_value = tower.get_sell_value()
                self.money += sell_value
                self.towers.remove(tower)

                self.sell_feedback_text = f"Tower Sold! +${sell_value}"
                self.sell_feedback_timer = 60
                self.selected_tower = None

                for t in self.towers:
                    t._is_selected = False

                return

    def run(self):
        self.start_first_wave()

        while self.running:
            clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_SPACE:
                        self.toggle_pause()

                    if event.key == pygame.K_z:
                        self.toggle_turbo()

                    if event.key == pygame.K_1:
                        self.place_tower("ice")

                    if event.key == pygame.K_2:
                        self.place_tower("fire")

                    if event.key == pygame.K_3:
                        self.place_tower("lightning")

                    if event.key == pygame.K_4:
                        self.place_tower("laser")

                    if event.key == pygame.K_u:
                        self.upgrade_tower()

                    if event.key == pygame.K_t:
                        self.change_target_mode()

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    if event.button == 1:
                        self.select_tower(mouse_x, mouse_y)

                    elif event.button == 3:
                        self.sell_tower(mouse_x, mouse_y)

            self.update()
            self.draw()

            if self.game_state == GameState.GAME_OVER:
                self.game_over()
                self.running = False
