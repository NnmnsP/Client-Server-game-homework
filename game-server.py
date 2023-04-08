import random

import asyncio
import logging
from dataclasses import dataclass

@dataclass
class Player:
    x: float
    y: float
    id: int
    writer: asyncio.StreamWriter

    speed_x: float = 0
    speed_y: float = 0
    hit_points: int = 5

@dataclass
class Bullet:
    x: float
    y: float
    id: int
    player_id: int

    speed_x: float = 0
    speed_y: float = 0

class GameServer:
    def __init__(self):
        self.players = []
        self.bullets = []
        self.game_field_width = 800
        self.game_field_height = 800
        self.acceleration = 0.1
        self.player_width = 50
        self.player_height = 50

    async def update_and_send_state(self):
        while True:
            if len(self.players) == 0:
                await asyncio.sleep(0.1)
                continue

            logging.info(f'Updating and sending state')
            game_state_encoded = ''

            for player in self.players:
                player.x += player.speed_x
                player.y += player.speed_y

                # prevent player from going off screen
                if player.x < 0:
                    player.x = 0
                    player.speed_x = 0
                elif player.x > self.game_field_width - self.player_width:
                    player.x = self.game_field_width - self.player_width
                    player.speed_x = 0
                if player.y < 0:
                    player.y = 0
                    player.speed_y = 0
                elif player.y > self.game_field_height - self.player_height:
                    player.y = self.game_field_height - self.player_height
                    player.speed_y = 0

                # add friction
                if player.speed_x > 0:
                    player.speed_x -= self.acceleration * 0.5
                elif player.speed_x < 0:
                    player.speed_x += self.acceleration * 0.5
                if player.speed_y > 0:
                    player.speed_y -= self.acceleration * 0.5
                elif player.speed_y < 0:
                    player.speed_y += self.acceleration * 0.5

                # aabb collision detection with a knokback
                for other_player in self.players:
                    if other_player == player:
                        continue

                    if (player.x < other_player.x + self.player_width and
                        player.x + self.player_width > other_player.x and
                        player.y < other_player.y + self.player_height and
                        player.y + self.player_height > other_player.y):
                        if player.x < other_player.x:
                            player.x -= 10
                        else:
                            player.x += 10
                        if player.y < other_player.y:
                            player.y -= 10
                        else:
                            player.y += 10
                    
                # aabb collision detection with bullets
                for bullet in self.bullets:
                    if bullet.player_id == player.id:
                        continue
                    if (player.x < bullet.x + 5 and
                        player.x + self.player_width > bullet.x and
                        player.y < bullet.y + 5 and
                        player.y + self.player_height > bullet.y):
                        player.hit_points -= 1
                        self.bullets.remove(bullet)
                        if player.hit_points <= 0:
                            self.players.remove(player)
                
                
                game_state_encoded += f'{player.id},{player.x},{player.y},{player.hit_points},'

            game_state_encoded += ':' # end of player state

            for bullet in self.bullets:
                bullet.x += bullet.speed_x
                bullet.y += bullet.speed_y

                # remove bullet if it goes off screen
                if bullet.x < 0 or bullet.x > self.game_field_width or bullet.y < 0 or bullet.y > self.game_field_height:
                    self.bullets.remove(bullet)
                    continue

                # logging.error(f'Bullet {bullet.id} at {bullet.x}, {bullet.y}')
                game_state_encoded += f'{bullet.id},{bullet.player_id},{bullet.x},{bullet.y},'

            for player in self.players:
                player.writer.write(f"{game_state_encoded[:-1]}\n".encode())
                try:
                    await player.writer.drain()
                except:
                    logging.error(f'Player {player.id} disconnected')
                    if player in self.players:
                        self.players.remove(player)
                    continue

            logging.info(f'State sent: {game_state_encoded}')
            await asyncio.sleep(0.05)
            
    async def handle_client(self, reader, writer):
        # Get the client's name
        logging.error(f'New player connected - total player: {len(self.players)}')

        # create unique player id
        new_id = 0
        while new_id in [player.id for player in self.players]:
            new_id += 1

        # get random position
        player = Player(random.randint(0, self.game_field_width), random.randint(0, self.game_field_height), new_id, writer)

        writer.write(f"id:{player.id}\n".encode())
        await writer.drain()

        self.players.append(player)

        # Listen for messages from the client and broadcast them to all other clients
        while True:
            try:
                message = (await reader.readline()).decode()
                if not message:
                    break

                logging.info(f'Player sent: {message}')
                x_action, y_action, fire_action = message.split(',')
                player.speed_x += float(x_action)
                player.speed_y += float(y_action)

                b_id = 0
                if fire_action == '1\n':
                    while b_id in [bullet.id for bullet in self.bullets]:
                        b_id += 1
                    bullet = Bullet(player.x + self.player_width // 2, player.y - self.player_height // 2, b_id, new_id, 0, -10)
                    self.bullets.append(bullet)                    

            except(ConnectionResetError, BrokenPipeError):
                if player in self.players:
                    logging.error(f'Player {player.id} disconnected')
                    self.players.remove(player)
                break

        # Remove the client from the list of connected clients
        # del self.clients[name]
        logging.info(f'Client disconnected')

    async def start(self):
        server = await asyncio.start_server(self.handle_client, '0.0.0.0', 8888)
        print(f'Server started at {server.sockets[0].getsockname()}')

        async with server:
            await server.serve_forever()

    async def run(self):
        await asyncio.gather(self.start(), self.update_and_send_state())

if __name__ == '__main__':

    format = "SRV: %(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.ERROR,
                        datefmt="%F-%H-%M-%S")

    game_server = GameServer()

    asyncio.run(game_server.run())

    asyncio.run()