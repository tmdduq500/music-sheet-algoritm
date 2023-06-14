#function
import cv2
import numpy as np

def threshold(image):
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
    return image

# standard에 따라 가중치가 곱해진 값을 리턴
def weighted(value):
    standard = 10
    return int(value * (standard / 10))

# 닫힘 연산-객체의 끊어진 부분 연결
def closing(image):
    kernel = np.ones((weighted(4), weighted(4)), np.uint8)
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernel)
    return image

# 이미지와 텍스트 좌표 표시
def put_text(image, text, loc):
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(image, str(text), loc, font, 0.6, (255, 0, 0), 2)

# 객체의 중간 y좌표 반환
def get_center(y, h):
    return (y + y + h) / 2

VERTICAL = True
HORIZONTAL = False

# 객체를 분류할 때 여러 특징점을 찾아내기 위해 사용
def get_line(image, axis, axis_value, start, end, length):
    if axis:
        points = [(i, axis_value) for i in range(start, end)]  # 수직 탐색
    else:
        points = [(axis_value, i) for i in range(start, end)]  # 수평 탐색
    pixels = 0
    for i in range(len(points)):
        (y, x) = points[i]
        pixels += (image[y][x] == 255)  # 흰색 픽셀의 개수를 셈
        next_point = image[y + 1][x] if axis else image[y][x + 1]  # 다음 탐색할 지점
        if next_point == 0 or i == len(points) - 1:  # 선이 끊기거나 마지막 탐색임
            if pixels >= weighted(length):
                break  # 찾는 길이의 직선을 찾았으므로 탐색을 중지함
            else:
                pixels = 0  # 찾는 길이에 도달하기 전에 선이 끊김 (남은 범위 다시 탐색)
    return y if axis else x, pixels

# 기둥을 검출하는 함수
def stem_detection(image, stats, length):
    (x, y, w, h, area) = stats
    stems = []  # 기둥 정보 (x, y, w, h)
    for col in range(x - weighted(2), x + w + weighted(2)):  # 기둥 탐지 범위 확장
        end, pixels = get_line(image, VERTICAL, col, y, y + h, length)
        if pixels:
            if len(stems) == 0 or abs(stems[-1][0] + stems[-1][2] - col) >= 2:
                (x, y, w, h) = col, end - pixels + 1, 1, pixels
                stems.append([x, y, w, h])
            else:
                stems[-1][2] += 1
    """기둥의 픽셀 수 세기"""
    # for stem in stems:
    #     x, y, w, h = stem
    #     cv2.putText(image, f"{h}", (x, y+h+30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (125, 125, 0), 2)
    #     cv2.putText(image, f"{w}", (x, y+h+50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (125, 125, 0), 2)
    
    return stems


def count_rect_pixels(image, rect):
    x, y, w, h = rect
    pixels = 0
    for row in range(y, y + h):
        for col in range(x, x + w):
            if image[row][col] == 255:
                pixels += 1
    return pixels

def count_pixels_part(image, area_top, area_bot, area_col):
    cnt = 0
    flag = False
    for row in range(area_top, area_bot):
        if not flag and image[row][area_col] == 255:
            flag = True
            cnt += 1
        elif flag and image[row][area_col] == 0:
            flag = False
    return cnt