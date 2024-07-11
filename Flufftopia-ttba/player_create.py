# player_create.py is a module that contains a Kivy app for creating a player character in Flufftopia.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup
import json
import subprocess

class PlayerCreate(App):
    def build(self):
        self.main_layout = BoxLayout(orientation='vertical')

        self.info_label = Label(text="Welcome to Flufftopia! Please enter your details below.", size_hint_y=None, height=200)
        self.main_layout.add_widget(self.info_label)

        self.name_input = TextInput(hint_text="Enter your name", multiline=False, size_hint_y=None, height=50)
        self.main_layout.add_widget(self.name_input)

        self.class_label = Label(text="Choose your class", size_hint_y=None, height=50)
        self.main_layout.add_widget(self.class_label)

        class_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=50)
        self.main_layout.add_widget(class_layout)

        self.class_choice = None

        classes = ["Warrior", "Mage", "Rogue"]
        for c in classes:
            btn = Button(text=c, size_hint_y=None, height=50)
            btn.bind(on_press=lambda instance, c=c: self.set_class(c))
            class_layout.add_widget(btn)

        self.submit_button = Button(text="Create Player", size_hint_y=None, height=50)
        self.submit_button.bind(on_press=self.create_player)
        self.main_layout.add_widget(self.submit_button)

        return self.main_layout

    def set_class(self, chosen_class):
        self.class_choice = chosen_class
        self.class_label.text = f"Chosen class: {chosen_class}"

    def create_player(self, instance):
        player_name = self.name_input.text.strip()

        if not player_name or not self.class_choice:
            self.show_popup("Error", "Both name and class must be provided.")
            return

        initial_skills = {
            "Warrior": ["Slash"],
            "Mage": ["Fireball"],
            "Rogue": ["Backstab"]
        }

        player_data = {
            "name": player_name,
            "class": self.class_choice,
            "health": 100,
            "strength": 10,
            "defense": 5,
            "agility": 5,
            "inventory": ["health potion"],
            "quests": [],
            "xp": 0,
            "level": 1,
            "skills": initial_skills[self.class_choice]
        }

        with open("player_data.json", "w") as f:
            json.dump(player_data, f)

        self.show_popup("Success", f"Player {player_name} the {self.class_choice} created successfully!")
        self.stop()  # Close the PlayerCreate app
        self.launch_game()

    def show_popup(self, title, message):
        popup_layout = BoxLayout(orientation='vertical')
        popup_label = Label(text=message)
        close_button = Button(text="Close", size_hint_y=None, height=50)
        popup_layout.add_widget(popup_label)
        popup_layout.add_widget(close_button)

        popup = Popup(title=title, content=popup_layout, size_hint=(0.5, 0.5))
        close_button.bind(on_press=popup.dismiss)
        popup.open()

    def launch_game(self):
        subprocess.Popen(["python", "test.py"])

if __name__ == "__main__":
    PlayerCreate().run()
