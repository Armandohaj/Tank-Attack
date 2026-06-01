"""
Simple text screen editor module for Tank Attack.

This module loads editable level configuration from text files.
The user can edit level screens without modifying the main game code.
"""


class ScreenEditor:
    """
    Loads level configuration from simple text files.
    """

    def __init__(self, levels_folder="levels"):
        self.levels_folder = levels_folder

    def load_level_config(self, level_number):
        """
        Load the configuration for a specific level.

        Example file:
        objective_x=18
        objective_y=8
        player_min_distance=8
        guardian_radius=160
        """

        config = self._get_default_config(level_number)

        file_path = f"{self.levels_folder}/level{level_number}.txt"

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                for line in file:
                    line = line.strip()

                    if not line:
                        continue

                    if line.startswith("#"):
                        continue

                    if "=" not in line:
                        continue

                    key, value = line.split("=", 1)

                    key = key.strip()
                    value = value.strip()

                    if key in config:
                        config[key] = int(value)

        except FileNotFoundError:
            print(f"Warning: level config not found: {file_path}")
            print("Using default level configuration.")

        return config

    def _get_default_config(self, level_number):
        """
        Return default values in case the text file does not exist.
        """

        if level_number == 1:
            return {
                "objective_x": 18,
                "objective_y": 8,
                "player_min_distance": 8,
                "guardian_radius": 160,
                "player_health": 150
                
            }

        if level_number == 2:
            return {
                "objective_x": 19,
                "objective_y": 9,
                "player_min_distance": 9,
                "guardian_radius": 160,
                "player_health" : 100
            }

        return {
            "objective_x": 20,
            "objective_y": 10,
            "player_min_distance": 10,
            "guardian_radius": 150,
            "player_health" : 100
        }