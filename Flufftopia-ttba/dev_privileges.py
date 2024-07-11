# dev_privileges.py

from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
import random
from enemies import enemies
from events import events
from locations import locations

def grant_dev_privileges(self):
    if self.player['name'].lower() == "brian allen":
        self.info_label.text += "\nDeveloper mode activated. You have full access to all functions."

        dev_button_layout = GridLayout(cols=2, size_hint_y=None, height=200)
        self.main_layout.add_widget(dev_button_layout)

        buttons = [
            ("Test Combat", self.dev_test_combat),
            ("Test Random Event", self.dev_test_random_event),
            ("Test Next Location", self.dev_test_next_location),
            ("Test Use Skill", self.dev_test_use_skill),
            ("Increase Health", self.dev_increase_health),
            ("Add Item", self.dev_add_item),
            ("Unlock Location", self.dev_unlock_location)
        ]

        for text, func in buttons:
            btn = Button(text=text)
            btn.bind(on_press=func)
            dev_button_layout.add_widget(btn)
    elif self.player['name'].lower() == "erin allen":
        self.info_label.text += "\nAdmin mode activated. You have access to some functions."

        self.player["health"] += 10000 # Increase health for admin user