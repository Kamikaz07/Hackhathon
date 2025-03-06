import socketio
import asyncio
from aiohttp import web
from dataclasses import dataclass, asdict
from typing import Dict, List
import random
import pymunk
import math
import signal
import traceback
import logging
import socket
import time
from levels import get_level, SCREEN_WIDTH, SCREEN_HEIGHT

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constantes de física
JUMP_FORCE = -800  # Aumentado de -600 para -800
MOVE_SPEED = 400
MAX_VELOCITY_Y = 800  # Aumentado para permitir pulos mais altos

@dataclass
class Player:
    id: str
    x: float = 400
    y: float = 300
    velocity_x: float = 0
    velocity_y: float = 0
    color: str = "red"
    health: int = 100
    weapon: str = None
    facing_right: bool = True
    can_jump: bool = False
    body: pymunk.Body = None
    shape: pymunk.Shape = None
    is_dodging: bool = False
    dodge_timer: float = 0
    class_type: str = "Fighter"
    damage_boost: float = 1.0
    speed_boost: float = 1.0
    buff_timer: float = 0
    projectile_speed: float = 400
    animation_state: str = "idle"
    animation_frame: int = 0
    is_climbing: bool = False
    climb_target: tuple = None

@dataclass
class Weapon:
    type: str
    x: float
    y: float
    damage: int = 20
    cooldown: float = 0.5
    body: pymunk.Body = None
    shape: pymunk.Shape = None

@dataclass
class Platform:
    x: float
    y: float
    width: float
    height: float
    body: pymunk.Body = None
    shape: pymunk.Shape = None
    movement_type: str = None
    amplitude: float = 0
    frequency: float = 0
    phase: float = 0
    initial_x: float = 0
    initial_y: float = 0

@dataclass
class Projectile:
    x: float
    y: float
    velocity_x: float
    velocity_y: float
    owner_id: str
    damage: int
    body: pymunk.Body = None
    shape: pymunk.Shape = None

@dataclass
class Buff:
    type: str
    x: float
    y: float
    duration: float = 10.0
    body: pymunk.Body = None
    shape: pymunk.Shape = None

class GameServer:
    def __init__(self, level_name="level1"):
        self.sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='aiohttp')
        self.app = web.Application()
        self.sio.attach(self.app)
        
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        self.space.damping = 0.9
        
        self.players: Dict[str, Player] = {}
        self.weapons: List[Weapon] = []
        self.platforms: List[Platform] = []
        self.projectiles: List[Projectile] = []
        self.buffs: List[Buff] = []
        self.colors = ["red", "blue"]
        self.last_attack_time: Dict[str, float] = {}
        self.scores: Dict[str, int] = {}
        
        self.running = True
        self.game_loop_task = None
        self.current_level = level_name
        
        self.setup_routes()
        self.load_level(level_name)
        self.spawn_weapons()

    def load_level(self, level_name: str):
        # Limpar plataformas existentes
        for platform in self.platforms:
            if platform.body:
                self.space.remove(platform.body, platform.shape)
        self.platforms.clear()

        # Carregar novo nível
        level = get_level(level_name)
        
        for platform_config in level.platforms:
            platform = Platform(
                x=platform_config['x'],
                y=platform_config['y'],
                width=platform_config['width'],
                height=platform_config['height']
            )
            
            if platform_config['movement_type'] == 'static':
                platform.body = pymunk.Body(body_type=pymunk.Body.STATIC)
            else:
                platform.body = pymunk.Body(1, float('inf'), body_type=pymunk.Body.KINEMATIC)
            
            platform.shape = pymunk.Poly.create_box(platform.body, (platform.width, platform.height))
            platform.shape.friction = 1.0
            platform.shape.elasticity = 0.0
            platform.shape.collision_type = 1
            
            platform.movement_type = platform_config['movement_type']
            if platform.movement_type != 'static':
                platform.amplitude = platform_config['amplitude']
                platform.frequency = platform_config['frequency']
                platform.phase = platform_config.get('phase', 0)
                platform.initial_x = platform_config['x']
                platform.initial_y = platform_config['y']
            
            platform.body.position = platform_config['x'], platform_config['y']
            self.space.add(platform.body, platform.shape)
            self.platforms.append(platform)

    def create_player_physics(self, player: Player):
        mass = 10.0
        width, height = 20, 40
        moment = pymunk.moment_for_box(mass, (width, height))
        player.body = pymunk.Body(mass, moment)
        player.body.position = (400, SCREEN_HEIGHT - 150)
        
        player.shape = pymunk.Poly.create_box(player.body, (width, height))
        player.shape.friction = 1.0
        player.shape.elasticity = 0.0
        player.shape.collision_type = 2
        
        def begin_collision(arbiter, space, data):
            player.can_jump = True
            return True
        
        def separate_collision(arbiter, space, data):
            player.can_jump = False
        
        handler = self.space.add_collision_handler(1, 2)
        handler.begin = begin_collision
        handler.separate = separate_collision
        
        self.space.add(player.body, player.shape)

    def setup_routes(self):
        @self.sio.event
        async def connect(sid, environ):
            if len(self.players) >= 2:
                return False
            
            color = next((c for c in self.colors if c not in [p.color for p in self.players.values()]), "red")
            player = Player(id=sid, color=color, class_type="Fighter")
            self.create_player_physics(player)
            
            # Posicionar jogador em um ponto de spawn aleatório
            level = get_level(self.current_level)
            spawn_point = random.choice(level.spawn_points)
            player.body.position = (spawn_point['x'], spawn_point['y'])
            
            self.players[sid] = player
            self.scores[sid] = 0
            print(f"Player {sid} connected")
            await self.sio.emit('choose_class', {'player_id': sid})

        @self.sio.event
        async def disconnect(sid):
            if sid in self.players:
                if self.players[sid].body:
                    self.space.remove(self.players[sid].body, self.players[sid].shape)
                del self.players[sid]
                del self.scores[sid]
                print(f"Player {sid} disconnected")
                await self.broadcast_game_state()

        @self.sio.event
        async def player_input(sid, data):
            if sid in self.players:
                player = self.players[sid]
                
                if data.get('left'):
                    player.body.velocity = (-MOVE_SPEED * player.speed_boost, player.body.velocity.y)
                    player.facing_right = False
                elif data.get('right'):
                    player.body.velocity = (MOVE_SPEED * player.speed_boost, player.body.velocity.y)
                    player.facing_right = True
                else:
                    player.body.velocity = (0, player.body.velocity.y)
                
                if data.get('jump') and player.can_jump:
                    player.body.velocity = (player.body.velocity.x, JUMP_FORCE)
                    player.can_jump = False
                
                if data.get('attack'):
                    current_time = asyncio.get_event_loop().time()
                    last_attack = self.last_attack_time.get(sid, 0)
                    if current_time - last_attack >= 0.5:
                        self.last_attack_time[sid] = current_time
                        if player.weapon:
                            player.animation_state = "attacking"
                            await self.handle_attack(player)
                            print(f"Player {sid} attacked with {player.weapon}")
                
                if data.get('dodge') and not player.is_dodging:
                    player.is_dodging = True
                    player.dodge_timer = 0.5
                    direction = 1 if player.facing_right else -1
                    player.body.apply_impulse_at_local_point((direction * 5000, 0))
                    player.animation_state = "dodging"
                
                if data.get('climb'):
                    self.try_climb(player)

        @self.sio.event
        async def class_choice(sid, data):
            if sid in self.players:
                self.players[sid].class_type = data['class_type']
                if self.players[sid].class_type == "Fighter":
                    self.players[sid].health = 150
                    self.players[sid].damage_boost = 1.2
                elif self.players[sid].class_type == "Mage":
                    self.players[sid].health = 100
                    self.players[sid].projectile_speed = 500
                elif self.players[sid].class_type == "Archer":
                    self.players[sid].health = 80
                    self.players[sid].projectile_speed = 600

        @self.sio.event
        async def request_level_change(sid, data):
            if sid in self.players:
                new_level = data.get('level_name', 'level1')
                await self.change_level(new_level)

    def try_climb(self, player: Player):
        for platform in self.platforms:
            px, py = player.body.position
            plat_x, plat_y = platform.body.position
            if (abs(px - plat_x) < platform.width / 2 + 10 and 
                py > plat_y - platform.height / 2 - 50 and 
                py < plat_y + platform.height / 2):
                player.is_climbing = True
                player.climb_target = (plat_x, plat_y - platform.height / 2 - 20)
                player.animation_state = "climbing"
                break

    async def handle_attack(self, attacker: Player):
        if attacker.class_type == "Fighter" and attacker.weapon == "sword":
            attack_range = 80
            damage = int(30 * attacker.damage_boost)
            attack_arc = math.pi / 2
            for player in self.players.values():
                if player.id != attacker.id and not player.is_dodging:
                    dx = player.body.position.x - attacker.body.position.x
                    dy = player.body.position.y - attacker.body.position.y
                    distance = math.sqrt(dx*dx + dy*dy)
                    if distance <= attack_range:
                        angle = math.atan2(dy, dx)
                        facing_angle = 0 if attacker.facing_right else math.pi
                        if abs(angle - facing_angle) <= attack_arc / 2:
                            player.health -= damage
                            knockback = 2000
                            player.body.apply_impulse_at_local_point(
                                (knockback * math.cos(angle), knockback * math.sin(angle)),
                                (0, 0)
                            )
                            player.animation_state = "hit"
                            if player.health <= 0:
                                await self.handle_player_death(player, attacker.id)
                            await self.sio.emit('attack', {'attacker': attacker.id, 'target': player.id})
        else:
            speed = attacker.projectile_speed
            direction = 1 if attacker.facing_right else -1
            damage = 20 if attacker.class_type == "Archer" else 25 if attacker.class_type == "Mage" else 20
            projectile = Projectile(
                x=attacker.body.position.x + (direction * 30),
                y=attacker.body.position.y,
                velocity_x=speed * direction,
                velocity_y=0,
                owner_id=attacker.id,
                damage=damage
            )
            projectile.body = pymunk.Body(1, 100)
            projectile.body.position = (projectile.x, projectile.y)
            projectile.body.velocity = (projectile.velocity_x, projectile.velocity_y)
            projectile.shape = pymunk.Circle(projectile.body, 5)
            projectile.shape.collision_type = 3
            self.space.add(projectile.body, projectile.shape)
            self.projectiles.append(projectile)
            await self.sio.emit('shoot', {'attacker': attacker.id, 'direction': direction})

    async def handle_player_death(self, player: Player, attacker_id: str):
        player.health = 100
        player.body.position = (random.randint(100, 700), 100)
        player.body.velocity = (0, 0)
        player.weapon = None
        if attacker_id:
            self.scores[attacker_id] += 1
            if self.scores[attacker_id] >= 5:
                await self.sio.emit('game_over', {'winner': attacker_id})

    def spawn_weapons(self):
        if len(self.weapons) < 3:
            weapon_type = random.choice(["sword", "gun"])
            x = random.randint(100, 700)
            y = 0  # Começa no topo
            damage = 30 if weapon_type == "sword" else 20
            weapon = Weapon(type=weapon_type, x=x, y=y, damage=damage)
            weapon.body = pymunk.Body(1, 100)
            weapon.body.position = (x, y)
            weapon.shape = pymunk.Circle(weapon.body, 10)
            weapon.shape.friction = 1.0
            weapon.shape.elasticity = 0.5
            weapon.shape.collision_type = 4
            self.space.add(weapon.body, weapon.shape)
            self.weapons.append(weapon)

    def spawn_buffs(self):
        if len(self.buffs) < 2:
            buff_type = random.choice(["damage", "speed", "heal"])
            x = random.randint(100, 700)
            y = 0  # Começa no topo
            buff = Buff(type=buff_type, x=x, y=y)
            buff.body = pymunk.Body(1, 100)
            buff.body.position = (x, y)
            buff.shape = pymunk.Circle(buff.body, 10)
            buff.shape.friction = 1.0
            buff.shape.elasticity = 0.5
            buff.shape.collision_type = 5
            self.space.add(buff.body, buff.shape)
            self.buffs.append(buff)

    async def update_game_state(self):
        try:
            self.space.step(1/60.0)
            current_time = time.time()
            
            # Atualizar posições das plataformas
            for platform in self.platforms:
                if platform.movement_type == 'horizontal':
                    new_x = platform.initial_x + platform.amplitude * math.sin(current_time * platform.frequency + platform.phase)
                    platform.body.position = (new_x, platform.initial_y)
                    platform.x = new_x
                    platform.y = platform.initial_y
            
            for player in self.players.values():
                player.x = player.body.position.x
                player.y = player.body.position.y
                
                if player.is_climbing:
                    target_x, target_y = player.climb_target
                    player.body.position = (player.body.position.x, player.body.position.y - 10)
                    if player.body.position.y <= target_y:
                        player.is_climbing = False
                        player.animation_state = "idle"
                        player.body.position = (target_x, target_y)
                
                max_velocity = MOVE_SPEED * player.speed_boost
                if player.body.velocity.length > max_velocity:
                    scale = max_velocity / player.body.velocity.length
                    player.body.velocity = player.body.velocity * scale
                
                if abs(player.body.velocity.y) > MAX_VELOCITY_Y:
                    player.body.velocity = (
                        player.body.velocity.x,
                        math.copysign(MAX_VELOCITY_Y, player.body.velocity.y)
                    )
                
                if player.buff_timer > 0:
                    player.buff_timer -= 1/60
                    if player.buff_timer <= 0:
                        player.damage_boost = 1.0
                        player.speed_boost = 1.0
                
                if player.is_dodging:
                    player.dodge_timer -= 1/60
                    if player.dodge_timer <= 0:
                        player.is_dodging = False
                        player.animation_state = "idle"

                if player.animation_state == "attacking":
                    player.animation_frame += 1
                    if player.animation_frame > 10:
                        player.animation_state = "idle"
                        player.animation_frame = 0

            # Atualizar armas e buffs
            for weapon in self.weapons:
                weapon.x = weapon.body.position.x
                weapon.y = weapon.body.position.y

            for buff in self.buffs:
                buff.x = buff.body.position.x
                buff.y = buff.body.position.y

            for projectile in self.projectiles[:]:
                if (projectile.body.position.x < 0 or 
                    projectile.body.position.x > SCREEN_WIDTH or
                    projectile.body.position.y < 0 or 
                    projectile.body.position.y > SCREEN_HEIGHT):
                    self.space.remove(projectile.body, projectile.shape)
                    self.projectiles.remove(projectile)
                    continue
                
                for player in self.players.values():
                    if player.id != projectile.owner_id and not player.is_dodging:
                        dx = player.body.position.x - projectile.body.position.x
                        dy = player.body.position.y - projectile.body.position.y
                        distance = math.sqrt(dx*dx + dy*dy)
                        if distance < 25:
                            player.health -= projectile.damage
                            knockback = 1000
                            player.body.apply_impulse_at_local_point(
                                (knockback * math.copysign(1, dx), -500),
                                (0, 0)
                            )
                            player.animation_state = "hit"
                            if player.health <= 0:
                                await self.handle_player_death(player, projectile.owner_id)
                            self.space.remove(projectile.body, projectile.shape)
                            self.projectiles.remove(projectile)
                            break

            for player in self.players.values():
                for weapon in self.weapons[:]:
                    if (abs(player.body.position.x - weapon.x) < 30 and 
                        abs(player.body.position.y - weapon.y) < 30):
                        player.weapon = weapon.type
                        self.space.remove(weapon.body, weapon.shape)
                        self.weapons.remove(weapon)
                        print(f"Player {player.id} collected {weapon.type}")

                for buff in self.buffs[:]:
                    if (abs(player.body.position.x - buff.x) < 30 and 
                        abs(player.body.position.y - buff.y) < 30):
                        if buff.type == "damage":
                            player.damage_boost = 1.5
                            player.buff_timer = buff.duration
                        elif buff.type == "speed":
                            player.speed_boost = 1.5
                            player.buff_timer = buff.duration
                        elif buff.type == "heal":
                            player.health = min(100, player.health + 50)
                        self.space.remove(buff.body, buff.shape)
                        self.buffs.remove(buff)

            self.spawn_weapons()
            self.spawn_buffs()
            await self.broadcast_game_state()
        except Exception as e:
            print(f"Error in update_game_state: {e}")

    async def broadcast_game_state(self):
        try:
            game_state = {
                'players': {
                    pid: {
                        **asdict(player),
                        'body': None,
                        'shape': None
                    }
                    for pid, player in self.players.items()
                },
                'weapons': [{'type': w.type, 'x': w.x, 'y': w.y} for w in self.weapons],
                'platforms': [
                    {
                        'x': p.body.position.x,
                        'y': p.body.position.y,
                        'width': p.width,
                        'height': p.height
                    }
                    for p in self.platforms
                ],
                'projectiles': [
                    {
                        'x': p.body.position.x,
                        'y': p.body.position.y
                    }
                    for p in self.projectiles
                ],
                'buffs': [{'type': b.type, 'x': b.x, 'y': b.y} for b in self.buffs],
                'scores': self.scores
            }
            await self.sio.emit('game_state', game_state)
        except Exception as e:
            print(f"Error in broadcast_game_state: {e}")

    async def game_loop(self):
        while self.running:
            try:
                await self.update_game_state()
                await asyncio.sleep(1/60)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in game loop: {e}")

    async def cleanup(self):
        self.running = False
        if self.game_loop_task:
            self.game_loop_task.cancel()
            try:
                await self.game_loop_task
            except asyncio.CancelledError:
                pass

    async def change_level(self, level_name: str):
        """Muda o nível atual do jogo"""
        self.load_level(level_name)
        self.current_level = level_name
        
        # Reposicionar jogadores
        level = get_level(level_name)
        for player in self.players.values():
            spawn_point = random.choice(level.spawn_points)
            player.body.position = (spawn_point['x'], spawn_point['y'])
            player.body.velocity = (0, 0)
        
        # Limpar armas e buffs
        for weapon in self.weapons[:]:
            self.space.remove(weapon.body, weapon.shape)
        self.weapons.clear()
        
        for buff in self.buffs[:]:
            self.space.remove(buff.body, buff.shape)
        self.buffs.clear()
        
        # Notificar clientes sobre a mudança de nível
        await self.sio.emit('level_changed', {
            'level_name': level_name,
            'level_title': level.name
        })

    def run(self, host='0.0.0.0', port=5000):
        async def init_game():
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    sock.bind((host, port))
                    sock.close()
                except socket.error:
                    logger.error(f"Port {port} is already in use")
                    return

                runner = web.AppRunner(self.app)
                await runner.setup()
                site = web.TCPSite(runner, host, port)
                
                await site.start()
                logger.info(f"Server running on http://{host}:{port}")
                
                self.game_loop_task = asyncio.create_task(self.game_loop())
                
                await self.game_loop_task
            except Exception as e:
                logger.error(f"Server initialization error: {str(e)}")
                logger.error(traceback.format_exc())
                
        def signal_handler(signum, frame):
            logger.info("Received shutdown signal")
            if self.running:
                self.running = False
                
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
                
        try:
            asyncio.run(init_game())
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Failed to start server: {str(e)}")

if __name__ == '__main__':
    server = GameServer()
    server.run()