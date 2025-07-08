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

print("waiting for cs2.exe... // Telegram channel - @godware1337 // creator - @tikzek1337")

if hasattr(sys, "frozen"):
    exe_dir = os.path.dirname(sys.executable)
    os.environ["PATH"] = exe_dir + os.pathsep + os.environ.get("PATH", "")
    if hasattr(os, "add_dll_directory"):
        os.add_dll_directory(exe_dir)

WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

esp_rendering = 1
esp_mode = 1
line_rendering = 1
hp_bar_rendering = 1
head_hitbox_rendering = 1
bons = 1
weapon = 1
bomb_esp = 1

print("getting offsets...")
offsets = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/offsets.json').json()
client_dll = requests.get('https://raw.githubusercontent.com/a2x/cs2-dumper/main/output/client_dll.json').json()

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

m_pClippingWeapon = client_dll['client.dll']['classes']['C_CSPlayerPawnBase']['fields']['m_pClippingWeapon']
m_AttributeManager = client_dll['client.dll']['classes']['C_EconEntity']['fields']['m_AttributeManager']
m_Item = client_dll['client.dll']['classes']['C_AttributeContainer']['fields']['m_Item']
m_iItemDefinitionIndex = client_dll['client.dll']['classes']['C_EconItemView']['fields']['m_iItemDefinitionIndex']

while True:
    time.sleep(1)
    try:
        pm = pymem.Pymem("cs2.exe")
        client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll
        break
    except:
        pass

time.sleep(1)
os.system("cls")

print("cs2.exe found!")
print("getting client.dll...")

pm = pymem.Pymem("cs2.exe")
client = pymem.process.module_from_name(pm.process_handle, "client.dll").lpBaseOfDll

print("client.dll found!")

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

def esp(draw_list):
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
            if esp_mode == 1 and entity_team == local_team:
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

            draw_list.add_line(leftX,  leg_pos[1],  rightX, leg_pos[1],  color, 1.2)
            draw_list.add_line(leftX,  leg_pos[1],  leftX,  head_pos[1], color, 1.2)
            draw_list.add_line(rightX, leg_pos[1],  rightX, head_pos[1], color, 1.2)
            draw_list.add_line(leftX,  head_pos[1], rightX, head_pos[1], color, 1.2)

            if bons:
                draw_bones(draw_list, pm, bone_matrix, view_matrix, WINDOW_WIDTH, WINDOW_HEIGHT)

            entity_hp = pm.read_int(entity_pawn + m_iHealth)

            if hp_bar_rendering:
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

    prev_time = time.perf_counter()
    fps = 0
    while not glfw.window_should_close(window):
        now = time.perf_counter()
        dt = now - prev_time
        prev_time = now
        if dt > 0:
            fps = int(1.0 / dt)
        glfw.poll_events()
        impl.process_inputs()
        imgui.new_frame()
        imgui.set_next_window_size(WINDOW_WIDTH, WINDOW_HEIGHT)
        imgui.set_next_window_position(0,0)
        imgui.begin("overlay", flags=imgui.WINDOW_NO_TITLE_BAR | imgui.WINDOW_NO_RESIZE | imgui.WINDOW_NO_SCROLLBAR | imgui.WINDOW_NO_COLLAPSE | imgui.WINDOW_NO_BACKGROUND)
        draw_list = imgui.get_window_draw_list()
        esp(draw_list)
        fps_text = f"FPS: {fps}"
        draw_list.add_text(10, 10, imgui.get_color_u32_rgba(1, 1, 1, 0.5), fps_text)
        watermark_text1 = "telegram channel - @godware1337"
        watermark_text2 = "creator - @tikzek1337"
        text_width1 = imgui.calc_text_size(watermark_text1)[0]
        text_width2 = imgui.calc_text_size(watermark_text2)[0]
        text_height = imgui.calc_text_size(watermark_text1)[1]
        draw_list.add_text(WINDOW_WIDTH - text_width1 - 10, 10, imgui.get_color_u32_rgba(1, 1, 1, 0.5), watermark_text1)
        draw_list.add_text(WINDOW_WIDTH - text_width2 - 10, 10 + text_height + 5, imgui.get_color_u32_rgba(1, 1, 1, 0.5), watermark_text2)
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