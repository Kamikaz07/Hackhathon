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
from levels import get_level, SCREEN_WIDTH, SCREEN_HEIGHT, JUMP_HEIGHT

# Configuração de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constantes de física
JUMP_FORCE = -800
MOVE_SPEED = 400
MAX_VELOCITY_Y = 800

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
    steal_ability_timer: float = 0
    blind_timer: float = 0
    is_blinded: bool = False
    invincible_timer: float = 0
    has_queijada: bool = False

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
    def __init__(self, level_name="pastelaria"):
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
        self.colors = ["red", "blue", "green", "yellow"]
        self.last_attack_time: Dict[str, float] = {}
        self.scores: Dict[str, int] = {}
        
        self.running = True
        self.game_loop_task = None
        self.current_level = level_name
        self.level_order = ["pastelaria", "estacao", "floresta", "montanha", "palacio"]
        self.current_level_index = 0
        self.round_time = 120  # Tempo de cada round em segundos
        self.round_timer = self.round_time
        self.round_count = 0
        self.max_rounds = 10  # Máximo de rounds antes de acabar o jogo
        self.queijada_spawned = False
        self.queijada_position = None  # Será determinada dinamicamente
        self.pombo_timer = 0  # Timer para o pombo roubar a queijada em caso de empate
        
        self.setup_routes()
        self.load_level(level_name)
        self.spawn_weapons()

    def load_level(self, level_name: str):
        for platform in self.platforms:
            if platform.body:
                self.space.remove(platform.body, platform.shape)
        self.platforms.clear()

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
            platform.shape.elasticity = 0.1  # Aumentar elasticidade para evitar que o jogador fique preso
            platform.shape.collision_type = 1
            
            platform.movement_type = platform_config['movement_type']
            if platform.movement_type != 'static':
                platform.amplitude = platform_config['amplitude']
                platform.frequency = platform_config['frequency']
                platform.phase = platform_config.get('phase', 0)
                platform.initial_x = platform_config['x']
                platform.initial_y = platform_config['y']
            
            platform.body.position = (platform.x, platform.y)
            self.space.add(platform.body, platform.shape)
            self.platforms.append(platform)

    def create_player_physics(self, player: Player):
        mass = 10.0
        width, height = 25, 45  # Ajustar tamanho do jogador para melhor colisão
        moment = pymunk.moment_for_box(mass, (width, height))
        player.body = pymunk.Body(mass, moment)
        player.body.position = (400, SCREEN_HEIGHT - 150)
        
        player.shape = pymunk.Poly.create_box(player.body, (width, height))
        player.shape.friction = 1.0
        player.shape.elasticity = 0.1
        player.shape.collision_type = 2
        
        # Armazenar a referência do servidor para usar em callbacks
        server_ref = self
        
        def pre_solve_collision(arbiter, space, data):
            shapes = arbiter.shapes
            platform_shape = shapes[0]
            player_shape = shapes[1]
            
            # Verificar se o jogador está acima da plataforma
            # (a posição Y menor significa "mais acima" na tela)
            platform_top = platform_shape.body.position.y - platform_shape.bb.height/2
            player_bottom = player_shape.body.position.y + player_shape.bb.height/2
            
            # Se o jogador está subindo ou caindo
            player_velocity_y = player_shape.body.velocity.y
            
            # Se o jogador está subindo ou está acima da plataforma, desabilita a colisão
            if player_velocity_y < 0 or player_bottom < platform_top + 5:
                return False
            
            for p_id, p in server_ref.players.items():
                if p.shape == player_shape:
                    p.can_jump = True
            
            return True
        
        def separate_collision(arbiter, space, data):
            shapes = arbiter.shapes
            if shapes[1] == player.shape:
                player.can_jump = False
            return True
        
        handler = self.space.add_collision_handler(1, 2)
        handler.pre_solve = pre_solve_collision
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
                    self.players[sid].damage_boost = 1.3
                    self.players[sid].weapon = "sword"
                elif self.players[sid].class_type == "Mage":
                    self.players[sid].health = 100
                    self.players[sid].projectile_speed = 500
                    self.players[sid].weapon = "gun"
                elif self.players[sid].class_type == "Archer":
                    self.players[sid].health = 90
                    self.players[sid].speed_boost = 1.2
                    self.players[sid].projectile_speed = 600
                    self.players[sid].weapon = "gun"

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
            attack_range = 90
            damage = int(35 * attacker.damage_boost)
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
                            if not player.invincible_timer > 0:
                                player.health -= damage
                                knockback = 2500
                                player.body.apply_impulse_at_local_point(
                                    (knockback * math.cos(angle), knockback * math.sin(angle)),
                                    (0, 0)
                                )
                                player.animation_state = "hit"
                                if player.health <= 0:
                                    await self.handle_player_death(player, attacker.id)
                                await self.sio.emit('attack', {'attacker': attacker.id, 'target': player.id, 'type': 'tabuleiro'})
        else:
            speed = attacker.projectile_speed
            direction = 1 if attacker.facing_right else -1
            
            if attacker.class_type == "Mage":
                damage = 15
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
                projectile.shape = pymunk.Circle(projectile.body, 8)
                projectile.shape.collision_type = 3
                
                server_ref = self
                
                def projectile_collision(arbiter, space, data):
                    shapes = arbiter.shapes
                    if len(shapes) >= 2 and hasattr(shapes[1], 'body'):
                        for pid, player in server_ref.players.items():
                            if player.shape == shapes[1] and player.id != attacker.id and not player.is_dodging:
                                player.is_blinded = True
                                player.blind_timer = 3.0
                                server_ref.space.remove(projectile.body, projectile.shape)
                                server_ref.projectiles.remove(projectile)
                                return False
                    return True
                
                handler = self.space.add_collision_handler(3, 2)
                handler.begin = projectile_collision
                self.space.add(projectile.body, projectile.shape)
                self.projectiles.append(projectile)
                await self.sio.emit('shoot', {'attacker': attacker.id, 'direction': direction, 'type': 'açúcar'})
                
            elif attacker.class_type == "Archer":
                damage = 10
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
                
                server_ref = self
                
                def steal_buff_collision(arbiter, space, data):
                    shapes = arbiter.shapes
                    if len(shapes) >= 2 and hasattr(shapes[1], 'body'):
                        for pid, player in server_ref.players.items():
                            if player.shape == shapes[1] and player.id != attacker.id and not player.is_dodging:
                                if player.damage_boost > 1.0:
                                    attacker.damage_boost = player.damage_boost
                                    player.damage_boost = 1.0
                                    attacker.buff_timer = 5.0
                                    server_ref.space.remove(projectile.body, projectile.shape)
                                    server_ref.projectiles.remove(projectile)
                                    asyncio.create_task(server_ref.sio.emit('steal_buff', {'stealer': attacker.id, 'target': player.id, 'buff': 'damage'}))
                                    return False
                                elif player.speed_boost > 1.0:
                                    attacker.speed_boost = player.speed_boost
                                    player.speed_boost = 1.0
                                    attacker.buff_timer = 5.0
                                    server_ref.space.remove(projectile.body, projectile.shape)
                                    server_ref.projectiles.remove(projectile)
                                    asyncio.create_task(server_ref.sio.emit('steal_buff', {'stealer': attacker.id, 'target': player.id, 'buff': 'speed'}))
                                    return False
                                if player.has_queijada:
                                    player.has_queijada = False
                                    attacker.has_queijada = True
                                    server_ref.space.remove(projectile.body, projectile.shape)
                                    server_ref.projectiles.remove(projectile)
                                    asyncio.create_task(server_ref.sio.emit('steal_queijada', {'stealer': attacker.id, 'target': player.id}))
                                    return False
                    return True
                
                handler = self.space.add_collision_handler(3, 2)
                handler.begin = steal_buff_collision
                self.space.add(projectile.body, projectile.shape)
                self.projectiles.append(projectile)
                await self.sio.emit('shoot', {'attacker': attacker.id, 'direction': direction, 'type': 'garfo'})
            
            else:
                damage = int(20 * attacker.damage_boost)
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
            y = 0
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
        if random.random() < 0.02 and len(self.buffs) < 3:
            buff_types = ["damage", "speed", "heal", "invencivel", "mordida"]
            buff_type = random.choice(buff_types)
            
            x = random.randint(100, SCREEN_WIDTH - 100)
            y = random.randint(100, SCREEN_HEIGHT - 200)
            
            buff = Buff(type=buff_type, x=x, y=y)
            buff.body = pymunk.Body(body_type=pymunk.Body.STATIC)
            buff.body.position = (x, y)
            buff.shape = pymunk.Circle(buff.body, 15)
            buff.shape.collision_type = 4
            self.space.add(buff.body, buff.shape)
            self.buffs.append(buff)

    async def update_game_state(self):
        """Updates the physics and game state"""
        # Step the physics simulation
        dt = 1/60.0
        self.space.step(dt)
        
        # Decrement round timer
        self.round_timer -= dt
        if self.round_timer <= 0:
            await self.end_round()

        # Update player positions and velocities
        for player_id, player in self.players.items():
            # Verificar se o jogador caiu para fora do mapa
            if player.body.position.y > SCREEN_HEIGHT + 50:
                # Reposicionar o jogador no ponto de spawn
                level = get_level(self.current_level)
                spawn_point = random.choice(level.spawn_points)
                player.body.position = (spawn_point['x'], spawn_point['y'])
                player.body.velocity = (0, 0)
                player.health -= 10  # Dano por cair
            
            # Se o jogador está subindo pela plataforma
            if player.is_climbing and player.climb_target:
                target_x, target_y = player.climb_target
                dx = target_x - player.body.position.x
                dy = target_y - player.body.position.y
                
                if abs(dx) < 5 and abs(dy) < 5:
                    player.body.position = (target_x, target_y)
                    player.is_climbing = False
                    player.animation_state = "idle"
                else:
                    player.body.velocity = (dx * 5, dy * 5)

            # Limitando a velocidade Y máxima
            if player.body.velocity.y > MAX_VELOCITY_Y:
                player.body.velocity = (player.body.velocity.x, MAX_VELOCITY_Y)
                
            # Atualizar posição do jogador
            player.x = player.body.position.x
            player.y = player.body.position.y
            player.velocity_x = player.body.velocity.x
            player.velocity_y = player.body.velocity.y
            
            # Atualizar timers do jogador
            if player.is_dodging:
                player.dodge_timer -= dt
                if player.dodge_timer <= 0:
                    player.is_dodging = False
            
            if player.buff_timer > 0:
                player.buff_timer -= dt
                if player.buff_timer <= 0:
                    player.damage_boost = 1.0
                    player.speed_boost = 1.0
                    
            if player.is_blinded:
                player.blind_timer -= dt
                if player.blind_timer <= 0:
                    player.is_blinded = False
                    
            if player.invincible_timer > 0:
                player.invincible_timer -= dt
                
            if player.has_queijada:
                # Animar o jogador segurando a queijada
                # E verificar se ele ganhou o round
                self.scores[player_id] = self.scores.get(player_id, 0) + 1
                player.has_queijada = False
                await self.sio.emit('got_queijada', {'player': player_id})
                await self.end_round()

        # Atualizar plataformas móveis
        for platform in self.platforms:
            if platform.movement_type == 'horizontal':
                t = time.time() * platform.frequency
                platform.x = platform.initial_x + platform.amplitude * math.sin(t * 2 * math.pi + platform.phase)
                platform.body.position = (platform.x, platform.y)
                
                # Adicionar velocidade à plataforma para que os jogadores se movam com ela
                platform.body.velocity = (platform.amplitude * math.cos(t * 2 * math.pi + platform.phase) * 2 * math.pi * platform.frequency, 0)
                
            elif platform.movement_type == 'vertical':
                t = time.time() * platform.frequency
                platform.y = platform.initial_y + platform.amplitude * math.sin(t * 2 * math.pi + platform.phase)
                platform.body.position = (platform.x, platform.y)
                
                # Adicionar velocidade à plataforma para que os jogadores se movam com ela
                platform.body.velocity = (0, platform.amplitude * math.cos(t * 2 * math.pi + platform.phase) * 2 * math.pi * platform.frequency)

        # Atualizar projeteis e remover os que saíram da tela
        for projectile in self.projectiles[:]:
            if (projectile.body.position.x < 0 or 
                projectile.body.position.x > SCREEN_WIDTH or 
                projectile.body.position.y < 0 or 
                projectile.body.position.y > SCREEN_HEIGHT):
                self.space.remove(projectile.body, projectile.shape)
                self.projectiles.remove(projectile)
            else:
                projectile.x = projectile.body.position.x
                projectile.y = projectile.body.position.y

        # Verificar colisões entre jogadores e buffs
        for player in self.players.values():
            for buff in self.buffs[:]:
                px, py = player.body.position
                bx, by = buff.body.position
                distance = math.sqrt((px - bx) ** 2 + (py - by) ** 2)
                
                if distance < 30:  # Raio de colisão
                    if buff.type == "damage":
                        player.damage_boost = 1.5
                        player.buff_timer = 10.0
                    elif buff.type == "speed":
                        player.speed_boost = 1.5
                        player.buff_timer = 10.0
                    elif buff.type == "heal":
                        player.health = min(100, player.health + 25)
                    elif buff.type == "invencivel":
                        # Glacê Indestrutível - invencibilidade temporária
                        player.invincible_timer = 5.0
                    elif buff.type == "mordida":
                        # Mordida Certeira - dano aumentado
                        player.damage_boost = 2.0
                        player.buff_timer = 5.0
                    
                    self.space.remove(buff.body, buff.shape)
                    self.buffs.remove(buff)
                    await self.sio.emit('buff_collected', {'player': player.id, 'buff_type': buff.type})
                    break
        
        # Spawn da Queijada Real
        if not self.queijada_spawned and self.round_timer <= self.round_time/2:
            # Escolher uma plataforma para spawnar a queijada
            # Preferencialmente no meio do nível ou em uma plataforma central
            level = get_level(self.current_level)
            central_platforms = [p for p in self.platforms 
                               if p.x > SCREEN_WIDTH/4 and p.x < SCREEN_WIDTH*3/4
                               and p.y < SCREEN_HEIGHT - JUMP_HEIGHT]
            
            spawn_platform = None
            if central_platforms:
                # Escolher uma plataforma central aleatória
                spawn_platform = random.choice(central_platforms)
                queijada_x = spawn_platform.x
                queijada_y = spawn_platform.y - spawn_platform.height/2 - 30  # Acima da plataforma
            else:
                # Se não houver plataformas centrais, usar uma posição padrão
                queijada_x = SCREEN_WIDTH/2
                queijada_y = SCREEN_HEIGHT - JUMP_HEIGHT - 50
            
            self.queijada_position = (queijada_x, queijada_y)
            self.queijada_spawned = True
            
            # Criar um buff especial para representar a queijada
            queijada = Buff(type="queijada", x=queijada_x, y=queijada_y)
            queijada.body = pymunk.Body(body_type=pymunk.Body.STATIC)
            queijada.body.position = (queijada_x, queijada_y)
            queijada.shape = pymunk.Circle(queijada.body, 25)
            queijada.shape.collision_type = 4
            
            # Adicionar um manipulador de colisão específico para a queijada
            server_ref = self
            def queijada_collision(arbiter, space, data):
                shapes = arbiter.shapes
                if len(shapes) >= 2 and hasattr(shapes[1], 'body'):
                    for pid, p in server_ref.players.items():
                        if p.shape == shapes[1]:
                            p.has_queijada = True
                            server_ref.space.remove(queijada.body, queijada.shape)
                            server_ref.buffs.remove(queijada)
                            return False
                return True
            
            handler = self.space.add_collision_handler(4, 2)
            handler.begin = queijada_collision
            
            self.space.add(queijada.body, queijada.shape)
            self.buffs.append(queijada)
            
            await self.sio.emit('queijada_spawned', {'x': queijada_x, 'y': queijada_y})
        
        # Easter Egg: Os Três Mosqueteiros
        if random.random() < 0.0005:  # 0.05% de chance por atualização (muito raro)
            # Os três mosqueteiros aparecem e todos ganham um buff
            for player in self.players.values():
                player.damage_boost = 1.5
                player.speed_boost = 1.5
                player.buff_timer = 10.0
            await self.sio.emit('easter_egg', {'event': 'Os Três Mosqueteiros apareceram!'})
        
        # Verificar se há empate e acionar o pombo
        if self.round_timer < 10:  # Últimos 10 segundos do round
            highest_score = max(self.scores.values()) if self.scores else 0
            tied_players = [pid for pid, score in self.scores.items() if score == highest_score]
            
            if len(tied_players) > 1 and highest_score > 0:
                self.pombo_timer += dt
                if self.pombo_timer >= 5:  # 5 segundos de empate
                    # Pombo rouba a queijada
                    for buff in self.buffs[:]:
                        if buff.type == "queijada":
                            self.space.remove(buff.body, buff.shape)
                            self.buffs.remove(buff)
                    
                    await self.sio.emit('pombo_roubou', {'message': 'Um pombo roubou a queijada! Todos perdem!'})
                    await self.end_round()
                    
        # Spawn de outros buffs
        self.spawn_buffs()
        await self.broadcast_game_state()

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
        self.load_level(level_name)
        self.current_level = level_name
        
        level = get_level(level_name)
        for player in self.players.values():
            spawn_point = random.choice(level.spawn_points)
            player.body.position = (spawn_point['x'], spawn_point['y'])
            player.body.velocity = (0, 0)
        
        for weapon in self.weapons[:]:
            self.space.remove(weapon.body, weapon.shape)
        self.weapons.clear()
        
        for buff in self.buffs[:]:
            self.space.remove(buff.body, buff.shape)
        self.buffs.clear()
        
        await self.sio.emit('level_changed', {
            'level_name': level_name,
            'level_title': level.name
        })

    async def end_round(self):
        """Finaliza o round atual e prepara o próximo"""
        self.round_count += 1
        
        # Verificar se já atingimos o número máximo de rounds
        if self.round_count >= self.max_rounds:
            # Finalizar o jogo
            winner = max(self.scores.items(), key=lambda x: x[1])[0] if self.scores else None
            if winner:
                await self.sio.emit('game_over', {'winner': winner, 'scores': self.scores})
                self.running = False
                return
        
        # Avançar para o próximo nível
        self.current_level_index = (self.current_level_index + 1) % len(self.level_order)
        next_level = self.level_order[self.current_level_index]
        
        # Limpar todos os buffs e projéteis
        for buff in self.buffs[:]:
            self.space.remove(buff.body, buff.shape)
        self.buffs.clear()
        
        for projectile in self.projectiles[:]:
            self.space.remove(projectile.body, projectile.shape)
        self.projectiles.clear()
        
        # Carregar o próximo nível
        await self.change_level(next_level)
        
        # Resetar os jogadores
        level = get_level(next_level)
        for i, (player_id, player) in enumerate(self.players.items()):
            # Resetar vida e status
            player.health = 100
            if player.class_type == "Fighter":
                player.health = 150
            elif player.class_type == "Archer":
                player.health = 90
            
            player.damage_boost = 1.0
            player.speed_boost = 1.0
            player.is_blinded = False
            player.blind_timer = 0
            player.invincible_timer = 0
            player.has_queijada = False
            player.is_climbing = False
            player.is_dodging = False
            
            # Reposicionar no novo nível
            spawn_index = i % len(level.spawn_points)
            spawn_point = level.spawn_points[spawn_index]
            player.body.position = (spawn_point['x'], spawn_point['y'])
            player.body.velocity = (0, 0)
        
        # Resetar o temporizador e flags
        self.round_timer = self.round_time
        self.queijada_spawned = False
        self.pombo_timer = 0
        
        await self.sio.emit('round_change', {
            'next_level': next_level, 
            'round': self.round_count, 
            'max_rounds': self.max_rounds,
            'scores': self.scores
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