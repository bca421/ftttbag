# main.py

from enemies import enemies
from events import events
from dev_privileges import grant_dev_privileges
from locations import locations
from bosses import bosses
import random
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout

class FlufftopiaApp(App):
    def build(self):
        self.player = self.player_setup()
        self.current_location = "village"  # Initial location
        self.current_enemy = None
        self.current_boss = None
        self.unlocked_locations = ["village", "enchanted_forest", "ancient_ruins"]

        self.main_layout = BoxLayout(orientation='vertical')

        self.health_bar = ProgressBar(max=100, value=self.player['health'])
        self.main_layout.add_widget(self.health_bar)

        self.info_label = Label(text=f"Welcome to Flufftopia, {self.player['name']}!", size_hint_y=None, height=200)
        self.scroll_view = ScrollView(size_hint=(1, None), size=(400, 400))
        self.scroll_view.add_widget(self.info_label)
        self.main_layout.add_widget(self.scroll_view)

        self.inventory_label = Label(text="Inventory: " + ', '.join(self.player['inventory']))
        self.main_layout.add_widget(self.inventory_label)

        self.skills_label = Label(text="Skills: " + ', '.join(self.player['skills']))
        self.main_layout.add_widget(self.skills_label)

        button_layout = GridLayout(cols=6, size_hint_y=None, height=50)
        self.main_layout.add_widget(button_layout)

        self.next_button = Button(text="Next")
        self.next_button.bind(on_press=self.next_location)
        button_layout.add_widget(self.next_button)

        self.skill_button = Button(text="Use Skill")
        self.skill_button.bind(on_press=self.show_skill_popup)
        button_layout.add_widget(self.skill_button)

        self.attack_button = Button(text="Attack")
        self.attack_button.bind(on_press=self.attack_enemy)
        button_layout.add_widget(self.attack_button)

        self.defend_button = Button(text="Defend")
        self.defend_button.bind(on_press=self.defend)
        button_layout.add_widget(self.defend_button)

        self.run_button = Button(text="Run")
        self.run_button.bind(on_press=self.run_from_combat)
        button_layout.add_widget(self.run_button)

        self.explore_button = Button(text="Explore")
        self.explore_button.bind(on_press=self.explore_area)
        button_layout.add_widget(self.explore_button)

        self.enable_combat_buttons(False)  # Disable combat buttons initially

        grant_dev_privileges(self)  # Grant developer privileges if applicable

        return self.main_layout

    def player_setup(self):
        try:
            with open("player_data.json", "r") as f:
                player_data = json.load(f)
        except FileNotFoundError:
            player_data = {
                "name": "Hero",
                "class": "None",
                "health": 100,
                "strength": 10,
                "defense": 5,
                "agility": 5,
                "inventory": ["health potion","mana potion","1000 gold"],
                "quests": ["find the meaning of it all"],
                "xp": 0,
                "level": 1,
                "skills": []
            }
        return player_data

    def clear_screen(self):
        self.info_label.text = ""

    def describe_location(self, location):
        self.info_label.text += f"\nYou are at the {location.replace('_', ' ').title()}.\n{locations[location]['description']}"

    def random_event(self, location):
        self.clear_screen()
        if location in events:
            event = random.choice(events[location])
            self.info_label.text += f"\n{event}"
            if "guardian" in event or "encounter" in event:
                self.current_enemy = random.choice(enemies)
                self.info_label.text += f"\nA wild {self.current_enemy['name']} appears!"
                self.enable_combat_buttons(True)
                self.enable_exploration_buttons(False)
                self.enable_next_buttons(False)
            elif "boss" in event or "huge" in event:
                self.current_enemy = random.choice(bosses)
                self.info_label.text += f"\nA wild {self.current_enemy['name']} appears!"
                self.enable_combat_buttons(True)
                self.enable_exploration_buttons(False)
                self.enable_next_buttons(False)               
            elif "trap" in event or "escape" in event:
                self.player["health"] -= 10
                self.health_bar.value = self.player["health"]
                self.info_label.text += f"\nYou lose 10 health. Current health: {self.player['health']}"
            elif "potion" in event or "healing" in event:
                self.player["health"] = min(100, self.player["health"] + 10)
                self.health_bar.value = self.player["health"]
                self.info_label.text += f"\nYou gain 10 health. Current health: {self.player['health']}"
        self.check_player_health()

    def combat(self, enemy):
        self.clear_screen()
        self.info_label.text += f"\n{self.player['name']}'s Health: {self.player['health']}"
        self.info_label.text += f"\n{enemy['name']}'s Health: {enemy['health']}"

        player_damage = max(0, self.player["strength"] - enemy["defense"] + random.randint(-5, 5))
        enemy["health"] -= player_damage
        self.info_label.text += f"\nYou attack the {enemy['name']} for {player_damage} damage!"

        if enemy["health"] <= 0:
            self.info_label.text += f"\nYou have defeated the {enemy['name']}!"
            loot = random.choice(enemy["loot"])
            self.player["inventory"].append(loot)
            self.inventory_label.text = "Inventory: " + ', '.join(self.player["inventory"])
            self.info_label.text += f"\nYou found a {loot} on the {enemy['name']}!"
            self.enable_combat_buttons(False)
            self.proceed_if_enemy_defeated()
            self.gain_xp(10)
            return

        enemy_damage = max(0, enemy["strength"] - self.player["defense"] + random.randint(-5, 5))
        self.player["health"] -= enemy_damage
        self.health_bar.value = self.player["health"]
        self.info_label.text += f"\nThe {enemy['name']} attacks you for {enemy_damage} damage!"
        self.enable_exploration_buttons(False)
        self.enable_next_buttons(False)

        self.check_player_health()

    def defend(self, instance):
        self.clear_screen()
        if self.current_enemy:
            self.display_player_stats()
            self.display_enemy_stats(self.current_enemy)
            self.info_label.text += f"\n{self.player['name']} is defending!"
            reduced_damage = max(0, self.current_enemy["strength"] - (self.player["defense"] * 2) + random.randint(-5, 5))
            self.player["health"] -= reduced_damage
            self.health_bar.value = self.player["health"]
            self.info_label.text += f"\nThe {self.current_enemy['name']} attacks you for {reduced_damage} reduced damage!"
            self.check_player_health()
        

    def check_player_health(self):
        if self.player["health"] <= 0:
            self.info_label.text += f"\n{self.player['name']} has been defeated. Game over."
            self.enable_combat_buttons(False)
            self.enable_exploration_buttons(False)
            self.enable_next_buttons(False)
        

    def gain_xp(self, amount):
        self.player["xp"] += amount
        self.info_label.text += f"\nYou gained {amount} XP. Total XP: {self.player['xp']}"
        self.level_up()

    def level_up(self):
        level_threshold = 10
        if self.player["xp"] >= level_threshold:
            self.player["level"] += 1
            self.player["xp"] -= level_threshold
            self.player["health"] = 100
            self.player["health"] += 10
            self.player["strength"] += 5
            self.player["defense"] += 5
            self.player["agility"] += 5
            self.info_label.text += f"\nCongratulations! You have reached level {self.player['level']}!"
            self.display_player_stats()
            self.health_bar.value = self.player["health"]
            self.unlock_new_skill()
            self.unlock_new_location()
            

    def display_player_stats(self):
        self.info_label.text += f"\nPlayer Stats: Level {self.player['level']}, Health {self.player['health']}, Strength {self.player['strength']}, Defense {self.player['defense']}, Agility {self.player['agility']}"

    def display_enemy_stats(self, enemy):
        self.info_label.text += f"\nEnemy Stats: {enemy['name']}, Health {enemy['health']}, Strength {enemy['strength']}, Defense {enemy['defense']}"

    def enable_exploration_buttons(self, enable):
        self.explore_button.disabled = not enable
    
    def enable_next_buttons(self, enable):
        self.next_button.disabled = not enable


    def enable_combat_buttons(self, enable):
        self.attack_button.disabled = not enable
        self.defend_button.disabled = not enable
        self.run_button.disabled = not enable
        self.skill_button.disabled = not enable

    def attack_enemy(self, instance):
        if self.current_enemy:
            self.combat(self.current_enemy)
            

    def run_from_combat(self, instance):
        self.clear_screen()
        if self.current_enemy:
            if random.random() < 0.5:
                self.info_label.text += f"\nYou successfully ran away from the {self.current_enemy['name']}!"
                self.enable_combat_buttons(False)
                self.enable_exploration_buttons(True)
                self.enable_next_buttons(True)
            else:
                self.info_label.text += f"\nFailed to run away from the {self.current_enemy['name']}!"
                self.combat(self.current_enemy)
                self.display_player_stats()
                self.display_enemy_stats(self.current_enemy)
        
    def explore_area(self, instance):
        self.clear_screen()
        self.describe_location(self.current_location)
        if random.random() < 0.5:
            self.random_event(self.current_location)
        else:
            self.info_label.text += "\nNothing of interest found while exploring."

    def next_location(self, instance):
        self.clear_screen()
        popup_layout = BoxLayout(orientation='vertical')
        popup_layout.add_widget(Label(text="Choose your next location:"))

        for loc in self.unlocked_locations:
            btn = Button(text=loc.replace("_", " ").title())
            btn.bind(on_press=lambda btn: self.set_location(btn.text.lower().replace(" ", "_")))
            popup_layout.add_widget(btn)

        close_button = Button(text="Close")
        close_button.bind(on_press=lambda btn: self.popup.dismiss())
        popup_layout.add_widget(close_button)

        self.popup = Popup(title="Locations", content=popup_layout, size_hint=(0.9, 0.9))
        self.popup.open()

    def set_location(self, location):
        self.current_location = location
        self.info_label.text += f"\nMoved to {location.replace('_', ' ').title()}."
        self.describe_location(location)
        self.popup.dismiss()

    def show_skill_popup(self, instance):
        self.clear_screen()
        if self.player["skills"]:
            skill_popup_layout = BoxLayout(orientation='vertical')
            skill_popup_layout.add_widget(Label(text="Choose a skill to use:"))

            for skill in self.player["skills"]:
                btn = Button(text=skill)
                btn.bind(on_press=lambda btn: self.use_skill(btn.text))
                skill_popup_layout.add_widget(btn)

            close_button = Button(text="Close")
            close_button.bind(on_press=lambda btn: self.skill_popup.dismiss())
            skill_popup_layout.add_widget(close_button)

            self.skill_popup = Popup(title="Skills", content=skill_popup_layout, size_hint=(0.9, 0.9))
            self.skill_popup.open()
        else:
            self.info_label.text += "\nYou have no skills to use."

    def use_skill(self, skill):
        self.clear_screen()
        self.info_label.text += f"\nYou used the skill: {skill}!"
        self.display_player_stats()
        self.display_enemy_stats(self.current_enemy)
        self.skill_popup.dismiss()
        
    def proceed_if_enemy_defeated(self):
        if self.current_enemy:
            self.info_label.text += f"\nYou have defeated the {self.current_enemy['name']}! Continue your adventure."
            self.current_enemy = None
            self.enable_combat_buttons(False)
            self.enable_exploration_buttons(True)
            self.enable_next_buttons(True)

    # Developer functions
    def dev_test_combat(self, instance):
        self.clear_screen()
        self.current_enemy = random.choice(enemies)
        self.info_label.text += f"\nTesting combat with {self.current_enemy['name']}."
        self.enable_combat_buttons(True)
        self.display_enemy_stats(self.current_enemy)

    def dev_test_random_event(self, instance):
        self.clear_screen()
        self.random_event(self.current_location)

    def dev_test_next_location(self, instance):
        self.clear_screen()
        self.next_location(instance)

    def dev_test_use_skill(self, instance):
        self.clear_screen()
        self.show_skill_popup(instance)

    def dev_increase_health(self, instance):
        self.clear_screen()
        self.player["health"] = min(100, self.player["health"] + 10)
        self.health_bar.value = self.player["health"]
        self.info_label.text += f"\nHealth increased by 10. Current health: {self.player['health']}"

    def dev_add_item(self, instance):
        self.clear_screen()
        new_item = "magic stone"
        self.player["inventory"].append(new_item)
        self.inventory_label.text = "Inventory: " + ', '.join(self.player["inventory"])
        self.info_label.text += f"\nAdded {new_item} to inventory."

    def unlock_new_skill(self):
        new_skills = {
            "Warrior": ["Power Strike", "Battle Cry"],
            "Mage": ["Lightning Bolt", "Mana Shield"],
            "Rogue": ["Shadow Step", "Poison Blade"]
        }
        available_skills = new_skills[self.player["class"]]
        new_skill = random.choice(available_skills)
        self.player["skills"].append(new_skill)
        self.info_label.text += f"\nYou unlocked a new skill: {new_skill}!"

    
    def unlock_new_location(self):
        new_locations = {

            "level_2": ["fairy_glade",],
            "level_3": ["enchanted_forest"],
            "level_4": ["hidden_village"],
        }
        current_level = f"level_{self.player['level']}"
        if current_level in new_locations:
            for loc in new_locations[current_level]:
                if loc not in self.unlocked_locations:
                    self.unlocked_locations.append(loc)
                    self.info_label.text += f"\nYou unlocked a new location: {loc.replace('_', ' ').title()}!"

if __name__ == "__main__":
    FlufftopiaApp().run()