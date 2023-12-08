import time
import win32con
import win32gui
import win32ui
import pyautogui
import cv2

x_flow_speed = 900    # 流动速度 x轴
midx = 477            # 判定中心 可修改
midy = 363
k = (215 - 420) / (1274 - 382) # 斜率(每个人都一样)
b = -k * midx + midy  # 根据判定中心自动计算的b
click_delay = 0       # 自动计算的数值 点击延迟平均值
click_cnt = 0         # 点击次数 用于计算点击延迟
screenshot_delay = 0  # 自动计算的数值 截图延迟平均值
screenshot_cnt = 0    # 截图次数 用于计算点击延迟


def click_left():
    global click_delay
    global click_cnt
    click_cnt += 1
    t1 = time.time()
    pyautogui.click(64, 377)
    click_delay += time.time() - t1
    click_delay /= click_cnt


def click_right():
    global click_delay
    global click_cnt
    click_cnt += 1
    t1 = time.time()
    pyautogui.click(1215, 377)
    click_delay += time.time() - t1
    click_delay /= click_cnt


def window_capture():
    global screenshot_delay
    global screenshot_cnt
    screenshot_cnt += 1
    beg = time.time()
    hwnd = 0  # 窗口的编号，0号表示当前活跃窗口
    # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    hwndDC = win32gui.GetWindowDC(hwnd)
    # 根据窗口的DC获取mfcDC
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # mfcDC创建可兼容的DC
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建bigmap准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    w = 1280
    h = 800
    # print w,h　　　#图片大小
    # 为bitmap开辟空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    # 高度saveDC，将截图保存到saveBitmap中
    saveDC.SelectObject(saveBitMap)
    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveDC.BitBlt((0, 0), (1280, 800), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, 'runtime.png')
    img = cv2.imread('runtime.png')
    end = time.time()
    screenshot_delay += end - beg
    screenshot_delay /= screenshot_cnt
    return img



def f(x):
    return int(k * x + b)


def judge_rgb_range(shot_array, x, y, r_min, r_max, g_min, g_max, b_min, b_max):
    if r_min <= shot_array[y][x][2] <= r_max and \
            g_min <= shot_array[y][x][1] <= g_max and \
            b_min <= shot_array[y][x][0] <= b_max:
        return True
    return False


def blue_judge(img, x):
    if judge_rgb_range(img, x, f(x), 47, 67, 186, 206, 186, 206) :
        return True
    return False


def yellow_judge(img, x):
    if judge_rgb_range(img, x, f(x), 210, 230, 170, 210, 0, 20) :
        return True
    return False


def start_play(difficulty):
    if difficulty == "normal" or difficulty == "hard" or difficulty == "very hard":
        t_total = 150
    elif difficulty == "special":
        t_total = 135
    t_start = time.time()
    while time.time() - t_start < t_total:
        img = window_capture()
        i = 371
        first = False
        while 350 <= i <= 477 + x_flow_speed*0.07:  # 首次点击
            if blue_judge(img, i):
                print("first left",i)
                click_left()
                i = i + 100
                first = True
                break
            elif yellow_judge(img, i):
                print("first right",i)
                click_right()
                i = i + 100
                first = True
                break
            i = i + 2
        dealt_i = 0
        if first:                                  # 连续点击
            while 477+x_flow_speed*0.07 < i + dealt_i <= 1280 and dealt_i <= 100:
                if blue_judge(img, i + dealt_i):
                    print("连续left", i + dealt_i)
                    if difficulty == "very hard":
                        time.sleep(0.08)
                    click_left()
                    i = i + dealt_i + 100
                    dealt_i = 0
                elif yellow_judge(img, i + dealt_i):
                    print("连续right", i + dealt_i)
                    if difficulty == "very hard":
                        time.sleep(0.08)
                    click_right()
                    i = i + dealt_i + 100
                    dealt_i = 0
                dealt_i += 2


start_play('very hard')
