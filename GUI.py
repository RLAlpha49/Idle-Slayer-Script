import configparser
import os
import customtkinter
from CTkToolTip import *

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

# Get the directory of the current Python script
script_directory = os.path.dirname(os.path.abspath(__file__))
print(script_directory)

# Construct the path to the Settings.txt file in the same directory
settings_file_path = os.path.join(script_directory, "Settings.txt")
print(settings_file_path)

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()

        self.settings = configparser.ConfigParser()
        self.settings.read(settings_file_path)
        
        # configure window
        self.title("AutoSlayer")
        self.geometry(f"{900}x{150}") 

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        # Create frames for different sections
        self.home_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.general_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.log_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.create_general_frame()
        
        # Initialize current_frame to the home_frame
        self.current_frame = self.home_frame

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=6, sticky="nsew")  # Update rowspan to 6
        self.sidebar_frame.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)  # Configure all rows
        
        # Create a dictionary to store button descriptions
        button_descriptions = {
            "Home": "Go back to the home screen",
            "General": "Access general settings",
            "Log": "View activity logs",
            "Pause": "Pause the application",
            "Exit": "Exit the application"
        }

        # Create an empty list to store tooltips
        self.tooltips = []

        # Add tooltips to the buttons
        button_texts = ["Home", "General", "Log", "Pause", "Exit"]
        for row, text in enumerate(button_texts, start=0):
            button = customtkinter.CTkButton(self.sidebar_frame, text=text, command=lambda t=text: self.show_text(t), bg_color="transparent", fg_color="transparent", border_width=1, corner_radius=0)
            button.grid(row=row, column=0, padx=20, sticky="w")
            
            # Create a CTkToolTip instance for each button using the description from the dictionary
            tooltip = CTkToolTip(button, message=button_descriptions[text])
            self.tooltips.append(tooltip)
            
    def update_general_text(self):
        new_jump_rate_value = self.general_text_box.get("1.0", "end-1c")

        # Update the JumpRateValue in the Settings section
        if not self.settings.has_section("Settings"):
            self.settings.add_section("Settings")
        self.settings.set("Settings", "JumpRateValue", new_jump_rate_value)

        # Update the checkbox states in the Settings section
        for col, checkbox_column in enumerate(self.checkboxes):
            for row, checkbox in enumerate(checkbox_column, start=1):
                checkbox_state_key = checkbox.cget("text").replace(" ", "") + "State"
                new_checkbox_state = bool(int(checkbox.get()))
                self.settings.set("Settings", checkbox_state_key, str(new_checkbox_state))

        # Save the changes to the configuration file
        with open(settings_file_path, "w") as configfile:
            self.settings.write(configfile)

            
    def show_text(self, button_text):
        print(f"Button '{button_text}' clicked")
        if button_text == "Home":
            self.show_frame(self.home_frame)
        elif button_text == "General":
            self.show_frame(self.general_frame)
        elif button_text == "Log":
            self.show_frame(self.log_frame)
        elif button_text == "Exit":
            self.quit()  # Close the program
            
    def show_frame(self, frame_to_show):
        if self.current_frame is not None:
            self.current_frame.grid_forget()  # Hide the current frame
        frame_to_show.grid(row=1, column=1, columnspan=3, padx=(0, 0), pady=(0, 0), sticky="nsew")
        self.current_frame = frame_to_show
        
    def create_general_frame(self):
        self.general_description_label = customtkinter.CTkLabel(self.general_frame, text="Jump Rate(ms)", font=customtkinter.CTkFont(size=16, weight="bold"))
        self.general_description_label.grid(row=0, column=0, padx=20, pady=(0, 10))

        # Retrieve the JumpRateValue from the settings
        jump_rate_value = self.settings.get("Settings", "JumpRateValue", fallback="150")

        self.general_text_box = customtkinter.CTkTextbox(self.general_frame, height=5, width=75)
        self.general_text_box.grid(row=1, column=0, padx=20, pady=(0, 10))
        
        # Set the retrieved JumpRateValue as the placeholder text
        self.general_text_box.insert("1.0", jump_rate_value)
        
        # Create a CTkToolTip instance for the text box
        CTkToolTip(self.general_text_box, message="Enter your desired Jump Rate in milliseconds(ms)")
        
        self.update_button = customtkinter.CTkButton(self.general_frame, text="Update", command=self.update_general_text)
        self.update_button.grid(row=2, column=0, padx=20, pady=(0, 10))
        
        # Create labels and checkboxes in the second and third columns
        label_texts = ["General", "MiniGames", "Crafting"]
        checkbox_texts = [
            ["Auto Buy Upgrade", "Cycle Portals", "Disable Rage Horde"],
            ["Skip Bonus Stage", "No Lockpicking100", "WIP"],
            ["Craft Soul Bonus", "Craft dimensional Staff", "Craft Rage Pill"]
        ]
        self.checkboxes = []  # Create a list to hold checkbox references
        checkbox_tooltips = [
            ["Tooltip for Auto Buy Upgrade", "Tooltip for Cycle Portals", "Tooltip for Disable Rage Horde"],
            ["Tooltip for Skip Bonus Stage", "Tooltip for No Lockpicking100", "Tooltip for WIP"],
            ["Tooltip for Craft Soul Bonus", "Tooltip for Craft dimensional Staff", "Tooltip for Craft Rage Pill"]
        ]

        for col, label_text in enumerate(label_texts, start=0):
            label = customtkinter.CTkLabel(self.general_frame, text=label_text, font=customtkinter.CTkFont(size=14, weight="bold"))
            label.grid(row=0, column=col + 1, padx=20, pady=(0, 5))
            
            checkbox_column = []  # Create a list to hold checkboxes in this column
            for row, checkbox_text in enumerate(checkbox_texts[col], start=1):
                checkbox = customtkinter.CTkCheckBox(master=self.general_frame, text=checkbox_text, font=customtkinter.CTkFont(size=12))
                checkbox.grid(row=row, column=col + 1, padx=20, pady=(0, 5), sticky="w")
                
                # Retrieve and set the state of each checkbox from the settings
                checkbox_state_key = checkbox_text.replace(" ", "") + "State"
                checkbox_state = self.settings.getboolean("Settings", checkbox_state_key, fallback=False)
                print(f"{checkbox_state_key}, {checkbox_state}")
                if checkbox_state is True:
                    checkbox.select()
                
                checkbox_tooltip = checkbox_tooltips[col][row - 1]  # Get the corresponding tooltip
                CTkToolTip(checkbox, message=checkbox_tooltip)  # Create a CTkToolTip instance for each checkbox
                
                checkbox_column.append(checkbox)
                
            self.checkboxes.append(checkbox_column)  # Add the checkbox column to the checkboxes list
    
    def sidebar_button_event(self):
        print("sidebar_button click")

if __name__ == "__main__":
    app = App()
    app.mainloop()