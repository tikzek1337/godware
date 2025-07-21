import json
import os
import time

CONFIG_FILE = "config.json"
DEFAULT_CONFIG = {
    "esp_rendering": True,
    "box_rendering": True,
    "hp_bar_rendering": True,
    "hp_text_rendering": False,
    "bons": True,
    "esp_mode_enemies_only": True,
    "box_line_thickness": 1.2
}

ASCII_ART = """
  ▄████  ▒█████  ▓█████▄  █     █░ ▄▄▄       ██▀███  ▓█████ 
 ██▒ ▀█▒▒██▒  ██▒▒██▀ ██▌▓█░ █ ░█░▒████▄    ▓██ ▒ ██▒▓█   ▀ 
▒██░▄▄▄░▒██░  ██▒░██   █▌▒█░ █ ░█ ▒██  ▀█▄  ▓██ ░▄█ ▒▒███   
░▓█  ██▓▒██   ██░░▓█▄   ▌░█░ █ ░█ ░██▄▄▄▄██ ▒██▀▀█▄  ▒▓█  ▄ 
░▒▓███▀▒░ ████▓▒░░▒████▓ ░░██▒██▓  ▓█   ▓██▒░██▓ ▒██▒░▒████▒
 ░▒   ▒ ░ ▒░▒░▒░  ▒▒▓  ▒ ░ ▓░▒ ▒   ▒▒   ▓▒█░░ ▒▓ ░▒▓░░░ ▒░ ░
  ░   ░   ░ ▒ ▒░  ░ ▒  ▒   ▒ ░ ░    ▒   ▒▒ ░  ░▒ ░ ▒░ ░ ░  ░
░ ░   ░ ░ ░ ░ ▒   ░ ░  ░   ░   ░    ░   ▒     ░░   ░    ░   
      ░     ░ ░     ░        ░          ░  ░   ░        ░  ░
                  ░                                         
"""

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    except (IOError, json.JSONDecodeError):
        return DEFAULT_CONFIG

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def set_line_thickness_menu():
    while True:
        os.system('cls')
        print(ASCII_ART)
        print("Выберите толщину линий:")
        print("1. Тонкие (1.2)")
        print("2. Средние (2.0)")
        print("3. Толстые (3.0)")
        print("4. Назад")
        
        try:
            choice = input("> ")
            config = load_config()
            if choice == '1':
                config["box_line_thickness"] = 1.2
            elif choice == '2':
                config["box_line_thickness"] = 2.0
            elif choice == '3':
                config["box_line_thickness"] = 3.0
            else: # Go back on any other key
                break
            save_config(config)

        except (KeyboardInterrupt, EOFError):
            break
        except Exception:
            pass

def main():
    while True:
        os.system('cls')
        config = load_config()
        
        esp_status = "ВКЛ" if config.get("esp_rendering") else "ВЫКЛ"
        bons_status = "ВКЛ" if config.get("bons") else "ВЫКЛ"
        box_status = "ВКЛ" if config.get("box_rendering") else "ВЫКЛ"
        hp_status = "ВКЛ" if config.get("hp_bar_rendering") else "ВЫКЛ"
        hp_text_status = "ВКЛ" if config.get("hp_text_rendering") else "ВЫКЛ"
        line_thickness = config.get("box_line_thickness", 1.2)

        print(ASCII_ART)
        print(f"1. Включить/Выключить ESP           [{esp_status}]")
        print(f"2. Включить/Выключить Боксы         [{box_status}]")
        print(f"3. Включить/Выключить HP Бар        [{hp_status}]")
        print(f"4. Включить/Выключить HP в цифрах    [{hp_text_status}]")
        print(f"5. Включить/Выключить Кости         [{bons_status}]")
        print(f"6. Настроить толщину линий        (Текущая: {line_thickness:.1f})")
        print("\nВведите номер, чтобы выбрать опцию.")
        
        try:
            choice = input("> ")
            if choice == '1':
                config["esp_rendering"] = not config.get("esp_rendering", True)
            elif choice == '2':
                config["box_rendering"] = not config.get("box_rendering", True)
            elif choice == '3':
                config["hp_bar_rendering"] = not config.get("hp_bar_rendering", True)
            elif choice == '4':
                config["hp_text_rendering"] = not config.get("hp_text_rendering", False)
            elif choice == '5':
                config["bons"] = not config.get("bons", True)
            elif choice == '6':
                set_line_thickness_menu()
                continue
            
            save_config(config)

        except (KeyboardInterrupt, EOFError):
            break
        except Exception:
            pass
        
        time.sleep(0.1)

if __name__ == "__main__":
    main() 