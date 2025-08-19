import pymem
import pymem.process
import win32gui
import win32con
import time
import os
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import OpenGL.GL as gl
import requests
import sys
import json
import threading

print("waiting for cs2.exe... // Telegram channel - @godware1337 // creator - @tikzek1337")

if hasattr(sys, "frozen"):
    exe_dir = os.path.dirname(sys.executable)
    os.environ["PATH"] = exe_dir + os.pathsep + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(exe_dir)

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

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

def initialize_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)

print("getting offsets...")
offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()

try:
    m_bBombTicking = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_bBombTicking']
    m_flC4Blow = client_dll['client.dll']['classes']['C_PlantedC4']['fields']['m_flC4Blow']
    m_flGameTime = offsets['client.dll']['dwGlobalVars'] + 0x2C # Using curtime
except KeyError:
    print("Warning: Could not find bomb timer offsets. Using hardcoded values.")
    m_bBombTicking = 0xE80
    m_flC4Blow = 0xED0
    m_flGameTime = offsets['client.dll']['dwGlobalVars'] + 0x2C

dwEntityList = offsets['client.dll']['dwEntityList']
dwLocalPlayerPawn = offsets['client.dll']['dwLocalPlayerPawn']
dwViewMatrix = offsets['client.dll']['dwViewMatrix']
dwPlantedC4 = offsets['client.dll']['dwPlantedC4']

m_iTeamNum = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iTeamNum']
m_lifeState = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_lifeState']
m_pGameSceneNode = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_pGameSceneNode']

m_modelState = client_dll['client.dll']['classes']['CSkeletonInstance']['fields']['m_modelState']

m_hPlayerPawn = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_hPlayerPawn']

m_iHealth = client_dll['client.dll']['classes']['C_BaseEntity']['fields']['m_iHealth']

# ИСПРАВЛЕНИЕ: переносим m_pClippingWeapon в правильный класс
m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawn']['fields']['m_pClippingWeapon']
m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']

try:
    m_vecAbsOrigin = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_vecAbsOrigin']
except KeyError:
    print("Warning: Could not find 'm_vecAbsOrigin'. Using hardcoded 0x160.")
    m_vecAbsOrigin = 0x160

try:
    m_sSanitizedPlayerName = client_dll['client.dll']['classes']['CCSPlayerController']['fields']['m_sSanitizedPlayerName']
except KeyError:
    print("Warning: Could not find 'm_sSanitizedPlayerName'. Using hardcoded 0x750.")
    m_sSanitizedPlayerName = 0x750

try:
    m_hParent = client_dll['client.dll']['classes']['CGameSceneNode']['fields']['m_hParent']
except KeyError:
    print("Warning: Could not find 'm_hParent'. Using hardcoded 0x30.")
    m_hParent = 0x30

try:
    m_pEntity = client_dll['client.dll']['classes']['CEntityInstance']['fields']['m_pEntity']
except KeyError:
    print("Warning: Could not find 'm_pEntity'. Using hardcoded 0x10.")
    m_pEntity = 0x10

try:
    m_designerName = client_dll['client.dll']['classes']['CEntityIdentity']['fields']['m_designerName']
except KeyError:
    print("Warning: Could not find 'm_designerName'. Using hardcoded 0x20.")
    m_designerName = 0x20


pm = None
client = None

while pm is None:
    try:
        pm = pymem.Pymem("cs2.exe")
    except pymem.exception.ProcessNotFound:
        time.sleep(1)
        
print("cs2.exe found!")
print("getting client.dll...")

while client is None:
    try:
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
    except:
        time.sleep(0.5)
print("client.dll found!")

time.sleep(1)
os.system("cls")
print("""⣇⣿⡿⣿⠏⣸⣎⣻⣟⣿⣿⣿⢿⣿⣿⣿⣿⠟⣩⣼⢆⠻⣿⡆⣿⣿⣿⣿⣿⣿
⢸⣿⡿⠋⠈⠉⠄⠉⠻⣽⣿⣿⣯⢿⣿⣿⡻⠋⠉⠄⠈⠑⠊⠃⣿⣿⣿⣿⣿⣿
⣿⣿⠄⠄⣰⠱⠿⠄⠄⢨⣿⣿⣿⣿⣿⣿⡆⢶⠷⠄⠄⢄⠄⠄⣿⣿⣿⣿⣿⣿
⣿⣿⠘⣤⣿⡀⣤⣤⣤⢸⣿⣿⣿⣿⣿⣿⡇⢠⣤⣤⡄⣸⣀⡆⣿⣿⣿⣿⣿⣿
⣿⣿⡀⣿⣿⣷⣌⣉⣡⣾⣿⣿⣿⣿⣿⣿⣿⣌⣛⣋⣴⣿⣿⢣⣿⣿⣿⣿⡟⣿
⢹⣿⢸⣿⣻⣶⣿⢿⣿⣿⣿⢿⣿⣿⣻⣿⣿⣿⡿⣿⣭⡿⠻⢸⣿⣿⣿⣿⡇⢹
⠈⣿⡆⠻⣿⣏⣿⣿⣿⣿⣿⡜⣭⣍⢻⣿⣿⣿⣿⣿⣛⣿⠃⣿⣿⣿⣿⡿⠄⣼ Have a good game)""")

initialize_config()
os.system("start cmd /c python menu.py")


def w2s(mtx, posx, posy, posz, width, height):
    screenW = mtx[12]*posx + mtx[13]*posy + mtx[14]*posz + mtx[15]
    if screenW > 0.001:
        screenX = mtx[0]*posx + mtx[1]*posy + mtx[2]*posz + mtx[3]
        screenY = mtx[4]*posx + mtx[5]*posy + mtx[6]*posz + mtx[7]
        camX = width / 2
        camY = height / 2
        x = camX + (camX * screenX / screenW) // 1
        y = camY - (camY * screenY / screenW) // 1
        return [x, y]
    return [-999, -999]

def draw_bones(draw_list, pm, bone_matrix, view_matrix, width, height):
    bone_ids = {
        "head": 6, "neck": 5, "spine": 4, "pelvis": 0,
        "left_shoulder": 13, "left_elbow": 14, "left_wrist": 15,
        "right_shoulder": 9, "right_elbow": 10, "right_wrist": 11,
        "left_hip": 25, "left_knee": 26, "left_ankle": 27,
        "right_hip": 22, "right_knee": 23, "right_ankle": 24,
    }
    bone_connections = [
        ("head", "neck"), ("neck", "spine"), ("spine", "pelvis"),
        ("pelvis", "left_hip"), ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
        ("pelvis", "right_hip"), ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
        ("neck", "left_shoulder"), ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
        ("neck", "right_shoulder"), ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ]
    bone_positions = {}
    color = imgui.get_color_u32_rgba(1, 1, 1, 0.5)

    try:
        for bone_name, bone_id in bone_ids.items():
            boneX = pm.read_float(bone_matrix + bone_id * 0x20)
            boneY = pm.read_float(bone_matrix + bone_id * 0x20 + 0x4)
            boneZ = pm.read_float(bone_matrix + bone_id * 0x20 + 0x8)
            bone_pos = w2s(view_matrix, boneX, boneY, boneZ, width, height)
            if bone_pos[0] != -999 and bone_pos[1] != -999:
                bone_positions[bone_name] = bone_pos
        
        for connection in bone_connections:
            if connection[0] in bone_positions and connection[1] in bone_positions:
                pos1 = bone_positions[connection[0]]
                pos2 = bone_positions[connection[1]]
                draw_list.add_line(pos1[0], pos1[1], pos2[0], pos2[1], color, 1.2)
    except Exception as e:
        pass

def esp(draw_list, config):
    try:
        view_matrix = [pm.read_float(client + dwViewMatrix + i * 4) for i in range(16)]
        
        local_player = pm.read_longlong(client + dwLocalPlayerPawn)
        local_team = pm.read_int(local_player + m_iTeamNum)
        entity_list = pm.read_longlong(client + dwEntityList)
    except pymem.exception.MemoryReadError:
        return

    if not entity_list:
        return

    for i in range(64):
        try:
            list_entry = pm.read_longlong(entity_list + (8 * (i & 0x7FF) >> 9) + 16)
            if not list_entry:
                continue

            entity_controller = pm.read_longlong(list_entry + 120 * (i & 0x1FF))
            if not entity_controller:
                continue

            entity_controller_pawn = pm.read_longlong(entity_controller + m_hPlayerPawn)
            if not entity_controller_pawn:
                continue

            list_entry_pawn = pm.read_longlong(entity_list + (0x8 * ((entity_controller_pawn & 0x7FFF) >> 9) + 16))
            if not list_entry_pawn:
                continue

            entity_pawn = pm.read_longlong(list_entry_pawn + (120) * (entity_controller_pawn & 0x1FF))
            if not entity_pawn or entity_pawn == local_player:
                continue

            if pm.read_int(entity_pawn + m_lifeState) != 256:
                continue

            entity_team = pm.read_int(entity_pawn + m_iTeamNum)
            if config.get("esp_mode_enemies_only", True) and entity_team == local_team:
                continue

            color = imgui.get_color_u32_rgba(1, 0, 0, 1) if entity_team != local_team else imgui.get_color_u32_rgba(0, 1, 0, 1)

            game_scene = pm.read_longlong(entity_pawn + m_pGameSceneNode)
            bone_matrix = pm.read_longlong(game_scene + m_modelState + 0x80)

            headX = pm.read_float(bone_matrix + 6 * 0x20)
            headY = pm.read_float(bone_matrix + 6 * 0x20 + 0x4)
            headZ = pm.read_float(bone_matrix + 6 * 0x20 + 0x8) + 8
            head_pos = w2s(view_matrix, headX, headY, headZ, WINDOW_WIDTH, WINDOW_HEIGHT)

            if head_pos[0] == -999:
                continue

            legZ = pm.read_float(bone_matrix + 28 * 0x20 + 0x8)
            leg_pos = w2s(view_matrix, headX, headY, legZ, WINDOW_WIDTH, WINDOW_HEIGHT)

            delta = abs(head_pos[1] - leg_pos[1])
            
            leftX = head_pos[0] - delta / 3
            rightX = head_pos[0] + delta / 3

            if config.get("box_rendering", True):
                line_thickness = config.get("box_line_thickness", 1.2)
                draw_list.add_line(leftX,  leg_pos[1],  rightX, leg_pos[1],  color, line_thickness)
                draw_list.add_line(leftX,  leg_pos[1],  leftX,  head_pos[1], color, line_thickness)
                draw_list.add_line(rightX, leg_pos[1],  rightX, head_pos[1], color, line_thickness)
                draw_list.add_line(leftX,  head_pos[1], rightX, head_pos[1], color, line_thickness)

            if config.get("bons", True):
                draw_bones(draw_list, pm, bone_matrix, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT)

            entity_hp = pm.read_int(entity_pawn + m_iHealth)

            if config.get("hp_bar_rendering", True):
                hp_bar_height = delta
                hp_bar_width = 2
                hp_bar_x = leftX - hp_bar_width - 3
                hp_bar_y_top = head_pos[1]
                hp_bar_y_bottom = leg_pos[1]

                hp_percentage = max(0.0, min(1.0, entity_hp / 100.0))

                if hp_percentage > 0.7:
                    hp_color = imgui.get_color_u32_rgba(0, 1, 0, 1)
                elif hp_percentage > 0.3:
                    hp_color = imgui.get_color_u32_rgba(1, 1, 0, 1)
                else:
                    hp_color = imgui.get_color_u32_rgba(1, 0, 0, 1)

                draw_list.add_rect_filled(
                    hp_bar_x, hp_bar_y_top,
                    hp_bar_x + hp_bar_width, hp_bar_y_bottom,
                    imgui.get_color_u32_rgba(0, 0, 0, 0.5)
                )

                current_hp_height = hp_bar_height * hp_percentage
                current_hp_y_top = hp_bar_y_top + (hp_bar_height - current_hp_height)
                draw_list.add_rect_filled(
                    hp_bar_x, current_hp_y_top,
                    hp_bar_x + hp_bar_width, hp_bar_y_bottom,
                    hp_color
                )
            
            if config.get("hp_text_rendering", False):
                hp_text = str(entity_hp)
                text_color = imgui.get_color_u32_rgba(1, 1, 1, 1)
                text_size = imgui.calc_text_size(hp_text)
                
                # Position the text centered, just above the head.
                draw_list.add_text(head_pos[0] - text_size.x / 2, head_pos[1] - text_size.y - 2, text_color, hp_text)

        except pymem.exception.MemoryReadError:
            continue
        except Exception:
            continue

def main():
    global WINDOW_WIDTH, WINDOW_HEIGHT

    if not glfw.init():
        exit(1)

    try:
        monitor = glfw.get_primary_monitor()
        if monitor:
            video_mode = glfw.get_video_mode(monitor)
            WINDOW_WIDTH = video_mode.size.width
            WINDOW_HEIGHT = video_mode.size.height
    except:
        print("warning: could not get monitor info")

    glfw.window_hint(glfw.TRANSPARENT_FRAMEBUFFER, glfw.TRUE)
    window = glfw.create_window(WINDOW_WIDTH, WINDOW_HEIGHT, "title", None, None)

    hwnd = glfw.get_win32_window(window)

    style = win32gui.GetWindowLong(hwnd, win32con.GWL_STYLE)
    style &= ~(win32con.WS_CAPTION | win32con.WS_THICKFRAME)
    win32gui.SetWindowLong(hwnd, win32con.GWL_STYLE, style)

    ex_style = win32con.WS_EX_TRANSPARENT | win32con.WS_EX_LAYERED
    win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE, ex_style)

    win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, -2, -2, 0, 0,
                          win32con.SWP_NOSIZE | win32con.SWP_NOACTIVATE)

    glfw.make_context_current(window)

    imgui.create_context()
    
    io = imgui.get_io()
    font = io.fonts.add_font_from_file_ttf("C:\\Windows\\Fonts\\arial.ttf", 20.0)
    io.fonts.add_font_default()
    impl = GlfwRenderer(window)
    impl.refresh_font_texture()

    last_time = time.time()
    while not glfw.window_should_close(window):
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()

        imgui.set_next_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        imgui.set_next_window_position(0, 0)
        
        imgui.begin("overlay", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_BACKGROUND)
        draw_list = imgui.get_window_draw_list()

        watermark1 = "telegram channel - @godware1337"
        watermark2 = "creator - tikzek"
        text_size1 = imgui.calc_text_size(watermark1)
        text_size2 = imgui.calc_text_size(watermark2)

        draw_list.add_text(WINDOW_WIDTH - text_size1.x - 10, 10, imgui.get_color_u32_rgba(1, 1, 1, 0.5), watermark1)
        draw_list.add_text(WINDOW_WIDTH - text_size2.x - 10, 10 + text_size1.y + 5, imgui.get_color_u32_rgba(1, 1, 1, 0.5), watermark2)

        version_text = "Version - 1.1.3"
        text_size = imgui.calc_text_size(version_text)
        draw_list.add_text(
            WINDOW_WIDTH - text_size.x - 10,
            WINDOW_HEIGHT - text_size.y - 10,
            imgui.get_color_u32_rgba(1, 1, 1, 0.5),
            version_text
        )

        config = DEFAULT_CONFIG
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except (IOError, json.JSONDecodeError):
            pass
                
        if config.get("esp_rendering"):
            esp(draw_list, config)

        current_time = time.time()
        fps = 1.0 / (current_time - last_time) if (current_time - last_time) > 0 else 0
        last_time = current_time

        fps_text = f"FPS: {fps:.0f}"
        draw_list.add_text(10, 10, imgui.get_color_u32_rgba(1, 1, 1, 0.5), fps_text)
        
        imgui.end()
        imgui.end_frame()
        gl.glClearColor(0, 0, 0, 0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        impl.render(imgui.get_draw_data())
        glfw.swap_buffers(window)
    impl.shutdown()
    glfw.terminate()

if __name__ == '__main__':
    main()