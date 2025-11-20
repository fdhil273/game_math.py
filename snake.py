import random
import time
import os
from enum import Enum

class Direction(Enum):
    NORTH = "n"
    SOUTH = "s"
    EAST = "e"
    WEST = "w"

class Player:
    def __init__(self):
        self.health = 100
        self.max_health = 100
        self.attack = 10
        self.defense = 5
        self.level = 1
        self.experience = 0
        self.gold = 0
        self.inventory = {"potion": 3, "key": 0}
        self.position = (0, 0)
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        return actual_damage
    
    def heal(self, amount):
        self.health = min(self.max_health, self.health + amount)
    
    def add_experience(self, exp):
        self.experience += exp
        if self.experience >= self.level * 50:
            self.level_up()
    
    def level_up(self):
        self.level += 1
        self.max_health += 20
        self.health = self.max_health
        self.attack += 5
        self.defense += 2
        self.experience = 0
        return f"Level Up! Sekarang level {self.level}!"

class Enemy:
    def __init__(self, name, health, attack, defense, exp_reward, gold_reward, level):
        self.name = name
        self.health = health
        self.max_health = health
        self.attack = attack
        self.defense = defense
        self.exp_reward = exp_reward
        self.gold_reward = gold_reward
        self.level = level
    
    def take_damage(self, damage):
        actual_damage = max(1, damage - self.defense)
        self.health -= actual_damage
        return actual_damage

class Room:
    def __init__(self, description, has_enemy=False, has_treasure=False, has_boss=False, is_exit=False):
        self.description = description
        self.has_enemy = has_enemy
        self.has_treasure = has_treasure
        self.has_boss = has_boss
        self.is_exit = is_exit
        self.visited = False
        self.enemy = None
        self.treasure_collected = False

class GameLevel:
    def __init__(self, level_number, size=5):
        self.level_number = level_number
        self.size = size
        self.grid = {}
        self.player_start = (0, 0)
        self.exit_pos = None
        self.generate_level()
    
    def generate_level(self):
        # Generate empty grid
        for x in range(self.size):
            for y in range(self.size):
                self.grid[(x, y)] = Room(f"Ruangan kosong di ({x}, {y})")
        
        # Set player start
        self.player_start = (0, 0)
        self.grid[self.player_start].description = "Pintu masuk dungeon"
        
        # Set exit (far from start)
        self.exit_pos = (self.size-1, self.size-1)
        
        # Add enemies based on level
        enemy_count = min(self.level_number + 2, self.size * self.size // 2)
        self._place_random_rooms(enemy_count, "enemy")
        
        # Add treasures
        treasure_count = min(self.level_number + 1, self.size * self.size // 3)
        self._place_random_rooms(treasure_count, "treasure")
        
        # Set exit room
        self.grid[self.exit_pos].is_exit = True
        if self.level_number % 3 == 0:  # Every 3rd level has boss
            self.grid[self.exit_pos].has_boss = True
            self.grid[self.exit_pos].description = "Ruangan Boss! Hati-hati!"
        else:
            self.grid[self.exit_pos].description = "Pintu keluar level"
    
    def _place_random_rooms(self, count, room_type):
        positions = [(x, y) for x in range(self.size) for y in range(self.size)]
        positions.remove(self.player_start)
        positions.remove(self.exit_pos)
        
        for _ in range(count):
            if not positions:
                break
            pos = random.choice(positions)
            positions.remove(pos)
            
            if room_type == "enemy":
                self.grid[pos].has_enemy = True
                self.grid[pos].description = f"Ruangan berbahaya di ({pos[0]}, {pos[1]})"
            elif room_type == "treasure":
                self.grid[pos].has_treasure = True
                self.grid[pos].description = f"Ruangan berharta di ({pos[0]}, {pos[1]})"

class Game:
    def __init__(self):
        self.player = Player()
        self.current_level_num = 1
        self.current_level = None
        self.player_position = (0, 0)
        self.game_over = False
        self.victory = False
        self.enemies_defeated = 0
        
        # Enemy templates by level range
        self.enemy_templates = [
            {"name": "Goblin", "health": 30, "attack": 8, "defense": 2, "exp": 15, "gold": 10},
            {"name": "Orc", "health": 50, "attack": 12, "defense": 4, "exp": 25, "gold": 20},
            {"name": "Troll", "health": 80, "attack": 15, "defense": 6, "exp": 40, "gold": 35},
            {"name": "Dragon", "health": 150, "attack": 25, "defense": 10, "exp": 100, "gold": 100}
        ]
    
    def start_game(self):
        self._load_level(self.current_level_num)
        self._show_welcome()
        
        while not self.game_over and not self.victory:
            self._display_room()
            self._handle_input()
            
            if self.player.health <= 0:
                self.game_over = True
                self._show_game_over()
    
    def _load_level(self, level_num):
        size = min(5 + level_num, 10)  # Level semakin besar
        self.current_level = GameLevel(level_num, size)
        self.player_position = self.current_level.player_start
    
    def _show_welcome(self):
        print("=" * 50)
        print("🎮 DUNGEON EXPLORER")
        print("=" * 50)
        print("Selamat datang, petualang!")
        print("Jelajahi dungeon, kalahkan monster, dan kumpulkan harta!")
        print("\nPerintah:")
        print("n/s/e/w - Bergerak (Utara/Selatan/Timur/Barat)")
        print("map     - Tampilkan peta")
        print("stats   - Status pemain")
        print("inv     - Inventory")
        print("use     - Gunakan potion")
        print("quit    - Keluar game")
        print("=" * 50)
        input("Tekan Enter untuk memulai...")
    
    def _display_room(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        current_room = self.current_level.grid[self.player_position]
        
        print("=" * 50)
        print(f"Level {self.current_level_num} - Posisi: {self.player_position}")
        print("=" * 50)
        
        if not current_room.visited:
            print(f"🔍 {current_room.description}")
            current_room.visited = True
        else:
            print(f"🏠 {current_room.description} (Sudah dikunjungi)")
        
        # Show room contents
        if current_room.has_enemy and current_room.enemy:
            print(f"⚔️  Ada {current_room.enemy.name} di sini! (Level {current_room.enemy.level})")
        elif current_room.has_enemy:
            print("⚔️  Ada monster di sini!")
        
        if current_room.has_treasure and not current_room.treasure_collected:
            print("💰 Ada harta karun!")
        
        if current_room.is_exit:
            if current_room.has_boss:
                print("🐉 BOSS MENUNGGU! Siapkan diri!")
            else:
                print("🚪 Pintu keluar level!")
        
        print("\nArah yang bisa dituju:")
        directions = self._get_available_directions()
        for direction in directions:
            print(f"- {direction.name} ({direction.value})")
        
        print("-" * 50)
    
    def _get_available_directions(self):
        directions = []
        x, y = self.player_position
        
        if x > 0:
            directions.append(Direction.NORTH)
        if x < self.current_level.size - 1:
            directions.append(Direction.SOUTH)
        if y > 0:
            directions.append(Direction.WEST)
        if y < self.current_level.size - 1:
            directions.append(Direction.EAST)
        
        return directions
    
    def _handle_input(self):
        command = input("\nApa yang ingin kamu lakukan? ").lower().strip()
        
        if command in [d.value for d in Direction]:
            self._move_player(command)
        elif command == "map":
            self._show_map()
        elif command == "stats":
            self._show_stats()
        elif command == "inv":
            self._show_inventory()
        elif command == "use":
            self._use_potion()
        elif command == "quit":
            self.game_over = True
            print("Terima kasih telah bermain!")
        else:
            print("Perintah tidak dikenali. Coba lagi.")
            input("Tekan Enter untuk melanjutkan...")
    
    def _move_player(self, direction):
        x, y = self.player_position
        new_position = self.player_position
        
        if direction == Direction.NORTH.value:
            new_position = (x - 1, y)
        elif direction == Direction.SOUTH.value:
            new_position = (x + 1, y)
        elif direction == Direction.EAST.value:
            new_position = (x, y + 1)
        elif direction == Direction.WEST.value:
            new_position = (x, y - 1)
        
        if new_position in self.current_level.grid:
            self.player_position = new_position
            self._handle_room_events()
    
    def _handle_room_events(self):
        current_room = self.current_level.grid[self.player_position]
        
        # Spawn enemy if needed
        if current_room.has_enemy and not current_room.enemy:
            current_room.enemy = self._create_enemy()
        
        # Combat with enemy
        if current_room.has_enemy and current_room.enemy:
            self._start_combat(current_room.enemy)
            if current_room.enemy.health <= 0:
                current_room.has_enemy = False
                current_room.enemy = None
        
        # Collect treasure
        if current_room.has_treasure and not current_room.treasure_collected:
            self._collect_treasure(current_room)
        
        # Check for exit
        if current_room.is_exit:
            if current_room.has_boss and current_room.enemy:
                print("Kamu harus mengalahkan boss terlebih dahulu!")
            else:
                self._handle_level_exit()
    
    def _create_enemy(self):
        level_index = min((self.current_level_num - 1) // 2, len(self.enemy_templates) - 1)
        template = self.enemy_templates[level_index].copy()
        
        # Scale enemy stats based on level
        scale_factor = 1 + (self.current_level_num - 1) * 0.3
        template["health"] = int(template["health"] * scale_factor)
        template["attack"] = int(template["attack"] * scale_factor)
        template["defense"] = int(template["defense"] * scale_factor)
        template["exp"] = int(template["exp"] * scale_factor)
        template["gold"] = int(template["gold"] * scale_factor)
        
        if self.current_level.grid[self.player_position].has_boss:
            # Boss is stronger
            template["health"] = int(template["health"] * 2)
            template["attack"] = int(template["attack"] * 1.5)
            template["name"] = f"BOSS {template['name']}"
        
        return Enemy(
            name=template["name"],
            health=template["health"],
            attack=template["attack"],
            defense=template["defense"],
            exp_reward=template["exp"],
            gold_reward=template["gold"],
            level=self.current_level_num
        )
    
    def _start_combat(self, enemy):
        print(f"\n⚔️  Pertarungan dengan {enemy.name}! ⚔️")
        print(f"HP Musuh: {enemy.health}/{enemy.max_health}")
        
        while enemy.health > 0 and self.player.health > 0:
            print(f"\nHP kamu: {self.player.health}/{self.player.max_health}")
            action = input("Serang (a) atau Kabur (r)? ").lower()
            
            if action == "a":
                # Player attacks
                player_damage = max(1, self.player.attack + random.randint(-2, 3))
                enemy_taken = enemy.take_damage(player_damage)
                print(f"Kamu menyerang! {enemy.name} menerima {enemy_taken} damage!")
                
                if enemy.health <= 0:
                    self._defeat_enemy(enemy)
                    break
                
                # Enemy attacks
                enemy_damage = max(1, enemy.attack + random.randint(-2, 2))
                player_taken = self.player.take_damage(enemy_damage)
                print(f"{enemy.name} menyerang balik! Kamu menerima {player_taken} damage!")
                
            elif action == "r":
                if random.random() < 0.7:  # 70% chance to escape
                    print("Kamu berhasil kabur!")
                    # Move player back to previous room
                    return
                else:
                    print("Gagal kabur! Musuh menyerang!")
                    enemy_damage = max(1, enemy.attack + random.randint(-2, 2))
                    player_taken = self.player.take_damage(enemy_damage)
                    print(f"{enemy.name} menyerang! Kamu menerima {player_taken} damage!")
            else:
                print("Perintah tidak valid!")
            
            if self.player.health <= 0:
                break
            
            input("Tekan Enter untuk lanjut...")
    
    def _defeat_enemy(self, enemy):
        print(f"\n🎉 Kamu mengalahkan {enemy.name}!")
        self.player.add_experience(enemy.exp_reward)
        self.player.gold += enemy.gold_reward
        self.enemies_defeated += 1
        
        print(f"➕ EXP: +{enemy.exp_reward}")
        print(f"💰 Emas: +{enemy.gold_reward}")
        
        # Chance to drop potion
        if random.random() < 0.3:
            self.player.inventory["potion"] += 1
            print("🧪 Mendapatkan 1 Potion!")
        
        if self.current_level.grid[self.player_position].has_boss:
            print("🌟 VICTORY! Boss terkalahkan!")
            self.player.inventory["key"] += 1
            print("🗝️  Mendapatkan Kunci Boss!")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def _collect_treasure(self, room):
        gold_found = random.randint(20, 50) * self.current_level_num
        self.player.gold += gold_found
        room.treasure_collected = True
        
        print(f"\n💰 Kamu menemukan harta karun!")
        print(f"💰 Emas: +{gold_found}")
        
        # Chance to find special item
        if random.random() < 0.4:
            self.player.inventory["potion"] += random.randint(1, 3)
            print("🧪 Mendapatkan Potion!")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def _handle_level_exit(self):
        print(f"\n🎊 LEVEL {self.current_level_num} SELESAI! 🎊")
        print("Kamu menemukan pintu ke level berikutnya...")
        
        # Reward for completing level
        completion_bonus = self.current_level_num * 25
        self.player.gold += completion_bonus
        self.player.heal(self.player.max_health // 2)
        
        print(f"💰 Bonus penyelesaian: {completion_bonus} emas")
        print("❤️  HP dipulihkan 50%")
        
        if self.current_level_num >= 5:
            self.victory = True
            self._show_victory()
        else:
            self.current_level_num += 1
            self._load_level(self.current_level_num)
            print(f"\nMemasuki Level {self.current_level_num}...")
            input("Tekan Enter untuk melanjutkan...")
    
    def _show_map(self):
        print("\n" + "=" * 30)
        print("🗺️  PETA DUNGEON")
        print("=" * 30)
        
        for x in range(self.current_level.size):
            row = ""
            for y in range(self.current_level.size):
                pos = (x, y)
                if pos == self.player_position:
                    row += "👤 "  # Player
                elif pos == self.current_level.exit_pos:
                    row += "🚪 "  # Exit
                elif self.current_level.grid[pos].has_enemy:
                    row += "👹 "  # Enemy
                elif self.current_level.grid[pos].has_treasure:
                    row += "💰 "  # Treasure
                elif self.current_level.grid[pos].visited:
                    row += "⬜ "  # Visited room
                else:
                    row += "❓ "  # Unexplored
            print(row)
        
        print("\nLegenda:")
        print("👤 - Kamu")
        print("🚪 - Pintu Keluar")
        print("👹 - Monster")
        print("💰 - Harta Karun")
        print("⬜ - Ruangan yang sudah dikunjungi")
        print("❓ - Ruangan belum dijelajahi")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def _show_stats(self):
        print("\n" + "=" * 30)
        print("📊 STATUS PEMAIN")
        print("=" * 30)
        print(f"Level: {self.player.level}")
        print(f"HP: {self.player.health}/{self.player.max_health}")
        print(f"Attack: {self.player.attack}")
        print(f"Defense: {self.player.defense}")
        print(f"EXP: {self.player.experience}/{(self.player.level * 50)}")
        print(f"Emas: {self.player.gold}")
        print(f"Musuh dikalahkan: {self.enemies_defeated}")
        print(f"Level saat ini: {self.current_level_num}")
        print("=" * 30)
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def _show_inventory(self):
        print("\n" + "=" * 30)
        print("🎒 INVENTORY")
        print("=" * 30)
        for item, quantity in self.player.inventory.items():
            print(f"{item.capitalize()}: {quantity}")
        print("=" * 30)
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def _use_potion(self):
        if self.player.inventory["potion"] > 0:
            heal_amount = 30
            self.player.heal(heal_amount)
            self.player.inventory["potion"] -= 1
            print(f"🧪 Menggunakan potion! HP +{heal_amount}")
            print(f"HP sekarang: {self.player.health}/{self.player.max_health}")
        else:
            print("❌ Tidak ada potion di inventory!")
        
        input("\nTekan Enter untuk melanjutkan...")
    
    def _show_game_over(self):
        print("\n" + "=" * 50)
        print("💀 GAME OVER")
        print("=" * 50)
        print("Petualanganmu berakhir di dungeon...")
        print(f"Pencapaian:")
        print(f"- Level yang dicapai: {self.current_level_num}")
        print(f"- Level karakter: {self.player.level}")
        print(f"- Emas dikumpulkan: {self.player.gold}")
        print(f"- Musuh dikalahkan: {self.enemies_defeated}")
        print("=" * 50)
    
    def _show_victory(self):
        print("\n" + "=" * 50)
        print("🏆 VICTORY! 🏆")
        print("=" * 50)
        print("Selamat! Kamu berhasil menyelesaikan semua level!")
        print("Kamu adalah pahlawan sejati dungeon!")
        print(f"\nStatistik Akhir:")
        print(f"- Level tertinggi: {self.current_level_num}")
        print(f"- Level karakter: {self.player.level}")
        print(f"- Total emas: {self.player.gold}")
        print(f"- Total musuh dikalahkan: {self.enemies_defeated}")
        print("=" * 50)
        print("Terima kasih telah bermain Dungeon Explorer!")

# Main execution
if __name__ == "__main__":
    game = Game()
    game.start_game()