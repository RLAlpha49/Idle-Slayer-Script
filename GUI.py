import configparser
import os
import sys
import customtkinter
import webbrowser
import time
import threading
from tkinter import messagebox
from configparser import ConfigParser
from PIL import Image
from CTkToolTip import *
from Log import write_log_entry
from Wrapper import timer
import AutoSlayer

version = "v1.7"

customtkinter.set_appearance_mode("Dark")  # Modes: "Dark" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Get the base directory of the application (works when running from executable)
base_dir = os.path.dirname(os.path.abspath(sys.argv[0]))

# Create a directory called "AutoSlayerLogs" if it doesn't exist
logs_dir = os.path.join(base_dir, "AutoSlayerLogs")
os.makedirs(logs_dir, exist_ok=True)

# Use the logs_dir to construct file paths
settings_file_path = os.path.join(logs_dir, "settings.txt")
log_file_path = os.path.join(logs_dir, "log.txt")
stats_file_path = os.path.join(logs_dir, "stats.txt")

default_settings = {
    "paused": "False", 
    "jumpratevalue": "150", "autobuyvalue": "600", "cycleportalcount": "1", "autoascensionslider": "20", "ragestate": "1",
    "autobuyupgradestate": "False", "cycleportalsstate": "False", "skipbonusstagestate": "True", 
    "craftsoulbonusstate": "False", "craftragepillstate": "False", "craftdimensionalstaffstate": "False", 
    "craftbidimensionalstaffstate": "False", "quicktoolbeststate": "False",
    "disableragehordestate": "False", "nolockpicking100state": "True", 
    "chesthuntactivestate": "False", "autoascensionstate": "False", "ragesoulbonusstate": "False", 
    "slayerpoints": "False"
}

# Check if the log file exists, and create it if not
if not os.path.exists(log_file_path):
    with open(log_file_path, "w") as logfile:
        write_log_entry(f"Script Directory: {base_dir}")
        write_log_entry(f"Log File: Created")
        write_log_entry(f"Log Path: {log_file_path}")
    

# Check if the settings file exists, and create it if not
if not os.path.exists(settings_file_path):
    with open(settings_file_path, "w") as configfile:
        configfile.write("[Settings]\n" +"\n".join([f"{setting} = {default}" for setting, default in default_settings.items()]))
    write_log_entry(f"Settings File: Created")
    write_log_entry(f"Settings Path: {settings_file_path}")
    
default_stats = {
    "Rage with only MegaHorde": "0", "Rage with Soul Bonus": "0", "Rage with MegaHorde and Soul Bonus": "0",
    "Claimed Quests": "0", "Claimed Minions": "0",
    "ChestHunts": "0", "Perfect ChestHunts": "0",
    "Collected Silver Boxes": "0", "Portals Cycled": "0", "Failed/Skipped Bonus Stages": "0",
}

# Check if the Stats file exists, and create it if not
if not os.path.exists(stats_file_path):
    with open(stats_file_path, "w") as configfile:
        for setting, default in default_stats.items():
            configfile.write(f"{setting}: {default}\n")
    write_log_entry(f"Stats File: Created")
    write_log_entry(f"Stats Path: {stats_file_path}")


class MyTabView(customtkinter.CTkTabview):
    @timer
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.configure(height=155, width=740)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid(row=1, column=0, sticky="nsew")
        
        # create tabs
        self.add("General")
        self.add("Extra")

        # add widgets on tabs
        self.create_tab_content("General")
        self.create_tab_2_content("Extra")
        #self.set("General")
    
    
    @timer
    def create_tab_content(self, tab_name):
        self.settings = configparser.ConfigParser()
        self.settings.read(settings_file_path)
        tab = self.tab(tab_name)

        general_description_label = customtkinter.CTkLabel(master=tab, text="Jump Rate(ms)", font=customtkinter.CTkFont(size=16, weight="bold"))
        general_description_label.grid(row=0, column=0, padx=20, pady=(0, 5))

        jump_rate_value = self.settings.get("Settings", "JumpRateValue", fallback="150")

        self.general_text_box = customtkinter.CTkTextbox(master=tab, height=5, width=75)
        self.general_text_box.grid(row=1, column=0, padx=20, pady=(0, 5))
        self.general_text_box.insert("1.0", jump_rate_value)
        

        update_button = customtkinter.CTkButton(master=tab, text="Update Settings", command=self.update_settings)
        update_button.grid(row=2, column=0, padx=20, pady=(0, 0))

        label_texts = ["General", "MiniGames", "Crafting"]
        checkbox_texts = [
            ["Auto Buy Upgrade", "Cycle Portals"],
            ["Skip Bonus Stage", "No Lockpicking100"],
            ["Craft dimensional Staff", "Craft bidimensional Staff"]
        ]
        
        self.checkboxes = []

        checkbox_tooltips = [
            ["Will automatically buy equipment/upgrades\nWill activate 10 seconds after turning on", "Cycle's through portal whenever available"],
            ["Will go through bonus stage letting time run out", "Check if you have Lockpicking100, for faster chesthunts"],
            ["Tooltip for Craft dimensional Staff (WIP)", "Tooltip for Craft bidimensional Staff (WIP)"]
        ]

        for col, label_text in enumerate(label_texts, start=0):
            label = customtkinter.CTkLabel(master=tab, text=label_text, font=customtkinter.CTkFont(size=16, weight="bold"))
            label.grid(row=0, column=col + 1, padx=20, pady=(0, 5))
            
            checkbox_column = []  # Create a list to hold checkboxes in this column
            for row, checkbox_text in enumerate(checkbox_texts[col], start=1):
                checkbox = customtkinter.CTkCheckBox(master=tab, command=self.update_settings, text=checkbox_text, font=customtkinter.CTkFont(size=12))
                checkbox.grid(row=row, column=col + 1, padx=20, pady=(0, 5), sticky="w")
                
                # Retrieve and set the state of each checkbox from the settings
                checkbox_state_key = checkbox_text.replace(" ", "") + "State"
                checkbox_state = self.settings.getboolean("Settings", checkbox_state_key, fallback=False)
                if checkbox_state is True:
                    checkbox.select()
                
                checkbox_tooltip = checkbox_tooltips[col][row - 1]  # Get the corresponding tooltip
                CTkToolTip(checkbox, message=checkbox_tooltip)  # Create a CTkToolTip instance for each checkbox
                
                checkbox_column.append(checkbox)
                
            self.checkboxes.append(checkbox_column)  # Add the checkbox column to the checkboxes list
    
    @timer
    def create_tab_2_content(self, tab_name):
        settings = self.load_settings()
        tab = self.tab(tab_name)

        # Create the first label in the first row
        self.label1 = customtkinter.CTkLabel(master=tab, text="Rage", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label1.grid(row=0, column=0, padx=20, pady=(0, 0), sticky="w")

        # Create a combobox under the first label with 3 different options
        combobox_options = ["Rage at Megahorde with Soul Bonus", "Rage at Megahorde", "Rage with Soul Bonus"]
        self.combobox = customtkinter.CTkComboBox(master=tab, values=combobox_options, state="readonly", command=self.update_combobox_value)
        self.combobox.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="w")

        # Set the current ragestate setting value as the selected option
        current_ragestate = settings.getint("Settings", "ragestate", fallback=1)
        self.combobox.set(combobox_options[current_ragestate - 1])
        
        self.checkbox1_var = customtkinter.IntVar()
        checkbox1 = customtkinter.CTkCheckBox(master=tab, text="Craft Soul Bonus", variable=self.checkbox1_var, command=self.update_settings, font=customtkinter.CTkFont(size=13), checkbox_height=20, checkbox_width=20, height=20)
        checkbox1.grid(row=2, column=0, padx=20, pady=(0, 5), sticky="w")
        self.checkbox1_var.set(settings.getboolean("Settings", "CraftSoulBonusState", fallback=False))
        CTkToolTip(checkbox1, message="Will craft Soul Bonus when rage is activated\nWill do this regardless of rage setting")

        self.checkbox2_var = customtkinter.IntVar()
        checkbox2 = customtkinter.CTkCheckBox(master=tab, text="Craft Rage Pill", variable=self.checkbox2_var, command=self.update_settings, font=customtkinter.CTkFont(size=13), checkbox_height=20, checkbox_width=20, height=20)
        checkbox2.grid(row=3, column=0, padx=20, pady=(0, 0), sticky="w")
        self.checkbox2_var.set(settings.getboolean("Settings", "CraftRagePillState", fallback=False))
        CTkToolTip(checkbox2, message="Will craft Rage Pill if rage has cooldown\nWill do this regardless of rage setting")
    
        # Create the second label in the first row
        self.label2 = customtkinter.CTkLabel(master=tab, text="Auto Ascension (%)", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label2.grid(row=0, column=1, padx=40, pady=(0, 0), sticky="w")
        CTkToolTip(self.label2, message= "Percentage of total slayer points to ascend\nSlider Tooltip may not display exact value, for exact value change setting in settings file")

        # Create the slider under the second label
        self.slider = customtkinter.CTkSlider(master=tab, from_=0, to=200, command=self.show_slider_value)
        self.slider.grid(row=1, column=1, padx=20, pady=(0, 10), sticky="w")
        self.slider.set(settings.getint("Settings", "autoascensionslider"))
        CTkToolTip(self.slider, message=str(settings.getint("Settings", "autoascensionslider")))
        
        # Create checkbox for Ascension Slider
        self.checkbox3_var = customtkinter.IntVar()
        checkbox3 = customtkinter.CTkCheckBox(master=tab, text="Auto Ascension", variable=self.checkbox3_var, command=self.update_settings, font=customtkinter.CTkFont(size=13), checkbox_height=20, checkbox_width=20, height=20)
        checkbox3.grid(row=2, column=1, padx=20, pady=(0, 5), sticky="w")
        self.checkbox3_var.set(settings.getboolean("Settings", "autoascensionstate", fallback=False))
        CTkToolTip(checkbox3, message="Activate/Deactivate Auto Ascension\nWill only work when you have at least ONE Hundred Thousand Slayer Points\nKeeping this on should not break anything")
        
        self.label2 = customtkinter.CTkLabel(master=tab, text="Miscellaneous", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.label2.grid(row=0, column=3, padx=40, pady=(0, 0), sticky="w")
        CTkToolTip(self.label2, message= "")
        
        auto_buy_value = self.settings.get("Settings", "AutoBuyValue", fallback="600")

        self.general_text_box2 = customtkinter.CTkTextbox(master=tab, height=5, width=75, font=customtkinter.CTkFont(size=13), border_spacing=0)
        self.general_text_box2.grid(row=1, column=3, padx=20, pady=(0, 0))
        self.general_text_box2.insert("1.0", auto_buy_value)
        CTkToolTip(self.general_text_box2, message="How often the Auto Buy Function should be run in Seconds")
        
        self.update_button = customtkinter.CTkButton(master=tab, text="Update Auto Buy Timer", height=25, command=self.update_auto_buy_value, font=customtkinter.CTkFont(size=13))
        self.update_button.grid(row=2, column=3, padx=20, pady=(0, 0))
        
        self.belt_checkbox_var = customtkinter.IntVar()
        self.belt_checkbox = customtkinter.CTkCheckBox(master=tab, text="Quick Tool Belt", variable=self.belt_checkbox_var, command=self.update_settings, font=customtkinter.CTkFont(size=13), checkbox_height=20, checkbox_width=20, height=20)
        self.belt_checkbox.grid(row=3, column=3, padx=40, sticky="w")
        self.belt_checkbox_var.set(settings.getboolean("Settings", "quicktoolbeltstate", fallback=False))
        CTkToolTip(self.belt_checkbox, message="Will craft items using the quick tool belt\nWill use original crafting tab if the items are not found in belt")
    
    @timer
    def update_combobox_value(self, *args):
        settings = self.load_settings()

        # Map combobox options to corresponding ragestate values
        ragestate_mapping = {
            "Rage at Megahorde with Soul Bonus": 1,
            "Rage at Megahorde": 2,
            "Rage with Soul Bonus": 3
        }

        selected_option = self.combobox.get()
        selected_ragestate = ragestate_mapping.get(selected_option, 1)  # Default to 1 if option not found

        # Update the ragestate setting in the settings file
        settings.set("Settings", "ragestate", str(selected_ragestate))

        # Save the changes to the configuration file
        self.save_settings(settings)
    
    @timer
    def update_auto_buy_value(self):
        new_auto_buy_value = self.general_text_box2.get("1.0", "end-1c")

        if not new_auto_buy_value.isdigit():
            messagebox.showerror("Invalid Input", "Auto Buy Timer must be a number.")
            return

        current_auto_buy_value = self.settings.get("Settings", "AutoBuyValue", fallback="")
        if new_auto_buy_value != current_auto_buy_value:
            self.settings.set("Settings", "AutoBuyValue", new_auto_buy_value)
            write_log_entry(f"Auto Buy Timer updated to: {new_auto_buy_value}")
            
        self.save_settings(self.settings)
    
    @timer
    def show_slider_value(self, value):
        self.slider_tooltip = CTkToolTip(self.slider, message=str(int(value)))
        
        settings = self.load_settings()
        
        settings.set("Settings", "autoascensionslider", str(int(value)))
        with open(settings_file_path, "w") as configfile:
            settings.write(configfile)
    
    @timer
    def update_settings(self):
        print("Update settings")
        settings = self.load_settings()
        
        # Update settings in general tab
        new_jump_rate_value = self.general_text_box.get("1.0", "end-1c")

        if not new_jump_rate_value.isdigit():
            messagebox.showerror("Invalid Input", "Jump rate must be a number.")
            return
    
        current_jump_rate_value = settings.get("Settings", "JumpRateValue", fallback="")
        if new_jump_rate_value != current_jump_rate_value:
            settings.set("Settings", "JumpRateValue", new_jump_rate_value)
            write_log_entry(f"Jump rate updated to: {new_jump_rate_value}")

        checkbox_names = ["Auto Buy Upgrade", "Cycle Portals", "Disable Rage Horde",
                        "Skip Bonus Stage", "No Lockpicking100", "Rage Soul Bonus",
                        "Craft dimensional Staff", "Craft bidimensional staff"]
        for col, checkbox_column in enumerate(self.checkboxes):
            for row, checkbox in enumerate(checkbox_column, start=1):
                checkbox_state_key = checkbox.cget("text").replace(" ", "") + "State"
                new_checkbox_state = bool(int(checkbox.get()))
                current_checkbox_state = settings.get("Settings", checkbox_state_key, fallback="False")

                if new_checkbox_state != (current_checkbox_state == "True"):
                    settings.set("Settings", checkbox_state_key, str(new_checkbox_state))
                    write_log_entry(f"Checkbox '{checkbox_names[col * 3 + row - 1]}' updated to: {new_checkbox_state}")

        # Update settings in Extra tab
        settings.set("Settings", "CraftSoulBonusState", "True" if (str(self.checkbox1_var.get()) == "1") else "False")

        settings.set("Settings", "CraftRagePillState", "True" if (str(self.checkbox2_var.get()) == "1") else "False")

        settings.set("Settings", "autoascensionstate", "True" if (str(self.checkbox3_var.get()) == "1") else "False")
        
        settings.set("Settings", "quicktoolbeltstate", "True" if (str(self.belt_checkbox_var.get()) == "1") else "False")
        
        # Save the changes to the configuration file
        self.save_settings(settings)
    
    @timer
    def save_settings(self, settings):
        with open(settings_file_path, "w") as configfile:
            settings.write(configfile)
    
    def load_settings(self):
        settings = ConfigParser()
        settings_file_path = os.path.join(logs_dir, "settings.txt")
        settings.read(settings_file_path)
        return settings

class App(customtkinter.CTk):
    @timer
    def __init__(self):
        super().__init__()

        self.settings = configparser.ConfigParser()
        self.settings.read(settings_file_path)
        
        # configure window
        self.title(f"AutoSlayer {version}")
        self.geometry(f"{930}x{160}")
        

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=2)

        # Create frames for different sections
        self.home_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.general_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.log_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.create_general_frame_with_tabs()
        self.create_home_frame()
        self.create_log_frame()

        # Initialize current_frame to the home_frame
        self.current_frame = self.home_frame
        
        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")  # Update rowspan to 6
        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Configure all rows
        
        # Create a dictionary to store button descriptions
        button_descriptions = {
            "Home": "Go back to the home screen",
            "General": "Access gameplay settings",
            "Log": "View activity logs, updates every 5 seconds"
        }

        # Add tooltips to the buttons
        button_texts = ["Home", "General", "Log"]
        for row, text in enumerate(button_texts, start=0):
            
            button = customtkinter.CTkButton(self.sidebar_frame, text=text, command=lambda t=text: self.show_text(t), bg_color="transparent", fg_color="transparent", border_width=1, corner_radius=0)
            if text == "Home":
                button.grid(row=row, column=0, padx=20, pady=(10,0), sticky="w")
            else:
                button.grid(row=row, column=0, padx=20, sticky="w")
            
            # Create a CTkToolTip instance for each button using the description from the dictionary
            tooltip = CTkToolTip(button, message=button_descriptions[text])
            
        # Create the "Pause" button
        self.pause_button = customtkinter.CTkButton(self.sidebar_frame, text="Pause", command=self.toggle_pause, bg_color="transparent", fg_color="transparent", border_width=1, corner_radius=0)
        self.pause_button.grid(row=4, column=0, padx=20, sticky="w")
        
        # Create a CTkToolTip instance for the "Pause" button
        pause_tooltip = CTkToolTip(self.pause_button, message="Pause the application")
        
        # Create the "Exit" button
        self.exit_button = customtkinter.CTkButton(self.sidebar_frame, text="Exit", command=self.on_closing, bg_color="transparent", fg_color="transparent", border_width=1, corner_radius=0)
        self.exit_button.grid(row=5, column=0, padx=20, pady=(0,10), sticky="w")
        
        # Create a CTkToolTip instance for the "Exit" button
        exit_tooltip = CTkToolTip(self.exit_button, message="Exit the application")
        
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    @timer
    def create_general_frame_with_tabs(self):
        self.general_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.general_frame.grid(row=1, column=1, columnspan=3, padx=(0, 0), pady=(0, 0), sticky="nsew")

        self.tab_view = MyTabView(master=self.general_frame)  # Use the custom tab view
        self.tab_view.grid(row=0, column=0, padx=5, pady=0)
    
    def load_settings(self):
        settings = ConfigParser()
        settings_file_path = os.path.join(logs_dir, "settings.txt")
        settings.read(settings_file_path)
        return settings
    
    @timer
    def toggle_pause(self):
        settings = self.load_settings()
        paused = settings.getboolean("Settings", "paused")
        paused = not paused
        self.pause_button.configure(text="Pause" if not paused else "Resume")
        
        # Update the "paused" setting in the settings file
        settings.set("Settings", "paused", str(paused))
        with open(settings_file_path, "w") as configfile:
            settings.write(configfile)
    
    @timer
    def create_home_frame(self):
        
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        image_directory = os.path.join(base_path, "Resources")
        image1dir = os.path.join(image_directory, "Discord.png")
        image2dir = os.path.join(image_directory, "Github.png")

        # Convert resized images to PhotoImage (PIL) format
        image1_tk = customtkinter.CTkImage(light_image=Image.open(image1dir), size=(240,81.6))
        image2_tk = customtkinter.CTkImage(light_image=Image.open(image2dir), size=(240,83.48))

        self.home_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.home_frame.grid(row=1, column=1, columnspan=3, padx=(0, 0), pady=(0, 0), sticky="nsew")

        # Add a title label
        title_label = customtkinter.CTkLabel(self.home_frame, text="Welcome to AutoSlayer!", font=customtkinter.CTkFont(size=24, weight="bold"))
        title_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(10, 0))
        
        version_label = customtkinter.CTkLabel(self.home_frame, text=f"{version}", font=customtkinter.CTkFont(size=18, weight="bold"))
        version_label.grid(row=1, column=0, columnspan=2, padx=20, pady=(0, 0))

        # Add picture buttons with links
        image_label1 = customtkinter.CTkLabel(self.home_frame, image=image1_tk, cursor="hand2", text="")
        image_label1.bind("<Button-1>", lambda e: self.open_link1())
        image_label1.grid(row=2, column=0, padx=20, pady=0)

        image_label2 = customtkinter.CTkLabel(self.home_frame, image=image2_tk, cursor="hand2", text="")
        image_label2.bind("<Button-1>", lambda e: self.open_link2())
        image_label2.grid(row=2, column=1, padx=20, pady=0)

    def open_link1(self):
        webbrowser.open("https://github.com/RLAlpha49")

    def open_link2(self):
        webbrowser.open("https://github.com/RLAlpha49")
    
    @timer
    def show_text(self, button_text):
        if button_text == "Home":
            self.show_frame(self.home_frame)
        elif button_text == "General":
            self.show_frame(self.general_frame)
        elif button_text == "Log":
            self.show_frame(self.log_frame)
        elif button_text == "Pause" or "Resume":
            self.toggle_pause()
        elif button_text == "Exit":
            self.on_closing()  # Close the program
    
    @timer
    def show_frame(self, frame_to_show):
        if self.current_frame is not None:
            self.current_frame.grid_forget()  # Hide the current frame
        frame_to_show.grid(row=1, column=1, columnspan=3, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.current_frame = frame_to_show
    
    @timer
    def create_log_frame(self):
        # Add a label for statistics
        stats_label = customtkinter.CTkLabel(self.log_frame, text="Statistics", font=customtkinter.CTkFont(size=18, weight="bold"))
        stats_label.grid(row=0, column=0, padx=20, pady=(0, 10), sticky="w")

        # Add a text box for displaying statistics
        self.stats_text_box = customtkinter.CTkTextbox(self.log_frame, height=115, width=300)
        self.stats_text_box.grid(row=1, column=0, padx=20)
        self.stats_text_box.insert("1.0", "WIP")  # Set default text
        self.stats_text_box.configure(state="disabled")

        # Add a label for log
        log_label = customtkinter.CTkLabel(self.log_frame, text="Log", font=customtkinter.CTkFont(size=18, weight="bold"))
        log_label.grid(row=0, column=1, padx=20, pady=(0, 10), sticky="w")

        # Add a text box for displaying log entries
        self.log_text_box = customtkinter.CTkTextbox(self.log_frame, height=115, width=300)
        self.log_text_box.grid(row=1, column=1, padx=20)
        self.log_text_box.insert("1.0", "Log entries here")  # Set default text
        
        with open(log_file_path, "r") as logfile:
            log_contents = logfile.read()
            self.log_text_box.insert("1.0", log_contents)
            
        
        update_log_textbox_thread = threading.Thread(target=self.update_log_text_box)
        update_log_textbox_thread.start()    
            
        #self.update_log_text_box()  # Call the function to start real-time updating

    def update_log_text_box(self):
        previous_log_contents = ""
        previous_stats_contents = ""

        while True:
            with open(log_file_path, "r") as logfile:
                log_contents = logfile.read()

            with open(stats_file_path, "r") as statsfile:
                stats_contents = statsfile.read()

            if log_contents != previous_log_contents:
                # Clear the existing log contents and insert new log contents
                self.log_text_box.configure(state="normal")
                self.log_text_box.delete("1.0", "end")
                self.log_text_box.insert("1.0", log_contents)
                self.log_text_box.yview_moveto(1.0)
                self.log_text_box.configure(state="disabled")
                previous_log_contents = log_contents

            if stats_contents != previous_stats_contents:
                # Clear the existing stats contents and insert new stats contents
                self.stats_text_box.configure(state="normal")
                self.stats_text_box.delete("1.0", "end")
                self.stats_text_box.insert("1.0", stats_contents)
                self.stats_text_box.yview_moveto(1.0)
                self.stats_text_box.configure(state="disabled")
                previous_stats_contents = stats_contents

            time.sleep(5)
    
    def on_closing(self):
        # Stop scheduled events and close the GUI window
        self.after_cancel(self.update_log_text_box)
        AutoSlayer.stop_threads() # Stop
        self.destroy()

if __name__ == "__main__":
    app = App()
    app.mainloop()