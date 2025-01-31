# modules.py
import cv2
import numpy as np
import functions_sy as fs
import recognition_modules as rs

# 보표 영역 추출 및 그 외 노이즈 제거
def remove_noise(image):
    image = fs.threshold(image)  # 이미지 이진화
    mask = np.zeros(image.shape, np.uint8)  # 보표 영역만 추출하기 위해 마스크 생성

    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(image)  # 레이블링
    for i in range(1, cnt):
        x, y, w, h, area = stats[i]
        if w > image.shape[1] * 0.5:  # 보표 영역에만
            cv2.rectangle(mask, (x+50, y-10, w, h+10), (255, 0, 0), -1)  # 사각형 그리기

    masked_image = cv2.bitwise_and(image, mask)  # 보표 영역 추출

    return masked_image

# 오선 제거
def remove_staves(image):
    height, width = image.shape
    staves = []  # 오선의 좌표들이 저장될 리스트

    for row in range(height):
        pixels = 0
        for col in range(width):
            pixels += (image[row][col] == 255)  # 한 행에 존재하는 흰색 픽셀의 개수를 셈
        if pixels >= width * 0.6:  # 이미지 넓이의 60% 이상이라면
            if len(staves) == 0 or abs(staves[-1][0] + staves[-1][1] - row) > 1:  # 첫 오선이거나 이전에 검출된 오선과 다른 오선
                staves.append([row, 0])  # 오선 추가 [오선의 y 좌표][오선 높이]
            else:  # 이전에 검출된 오선과 같은 오선
                staves[-1][1] += 1  # 높이 업데이트
    for staff in range(len(staves)):
        top_pixel = staves[staff][0]  # 오선의 최상단 y 좌표
        bot_pixel = staves[staff][0] + staves[staff][1]  # 오선의 최하단 y 좌표 (오선의 최상단 y 좌표 + 오선 높이)
        for col in range(width):
            if image[top_pixel - 1][col] == 0 and image[bot_pixel + 1][col] == 0:  # 오선 위, 아래로 픽셀이 있는지 탐색
                for row in range(top_pixel, bot_pixel + 1):
                    image[row][col] = 0  # 오선을 지움

    return image, [x[0] for x in staves]

# 악보 이미지 정규화
def normalization(image, staves, standard):
    avg_distance = 0
    lines = int(len(staves) / 5)  # 보표의 개수
    for line in range(lines):
        for staff in range(4):
            staff_above = staves[line * 5 + staff]
            staff_below = staves[line * 5 + staff + 1]
            avg_distance += abs(staff_above - staff_below)  # 오선의 간격을 누적해서 더해줌
    avg_distance /= len(staves) - lines  # 오선 간의 평균 간격
    height, width = image.shape  # 이미지의 높이와 넓이
    weight = standard / avg_distance  # 기준으로 정한 오선 간격을 이용해 가중치를 구함
    new_width = int(width * weight)  # 이미지의 넓이에 가중치를 곱해줌
    new_height = int(height * weight)  # 이미지의 높이에 가중치를 곱해줌

    image = cv2.resize(image, (new_width, new_height))  # 이미지 리사이징
    ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이미지 이진화
    staves = [x * weight for x in staves]  # 오선 좌표에도 가중치를 곱해줌

    return image, staves

# 악보 이미지 정규화(1500*2100으로 고정)
# def normalization(image, staves, standard):
#     avg_distance = 0
#     lines = int(len(staves) / 5)  # 보표의 개수
#     for line in range(lines):
#         for staff in range(4):
#             staff_above = staves[line * 5 + staff]
#             staff_below = staves[line * 5 + staff + 1]
#             avg_distance += abs(staff_above - staff_below)  # 오선의 간격을 누적해서 더해줌
#     avg_distance /= len(staves) - lines  # 오선 간의 평균 간격

#     # 이미지 크기를 목표 크기로 맞추기 위한 가중치 계산
#     target_width = 1500
#     target_height = 2100
#     weight = min(target_width / image.shape[1], target_height / image.shape[0])

#     new_width = int(image.shape[1] * weight)  # 가중치를 곱한 새로운 너비
#     new_height = int(image.shape[0] * weight)  # 가중치를 곱한 새로운 높이

#     image = cv2.resize(image, (new_width, new_height))  # 이미지 리사이징
#     ret, image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  # 이미지 이진화
#     staves = [x * weight for x in staves]  # 오선 좌표에도 가중치를 곱해줌

#     return image, staves

# 객체 검출
def object_detection(image, staves):
    lines = int(len(staves) / 5)  # 보표의 개수
    objects = []  # 구성요소 정보가 저장될 리스트

    orgin_image =cv2.imread(r"D:\music-sheet-algoritm\sy\music_sheet_jpg\6.jpg", cv2.IMREAD_ANYCOLOR)

    closing_image = fs.closing(image)
    cnt, labels, stats, centroids = cv2.connectedComponentsWithStats(closing_image)  # 모든 객체 검출하기
    for i in range(1, cnt):
        (x, y, w, h, area) = stats[i]
        # 객체 크기 높이 구하기
        cv2.rectangle(orgin_image, (x, y, w, h), (255, 0, 0), 1)
        # fs.put_text(image, w, (x, y + h + 30))
        # fs.put_text(image, h, (x, y + h + 60))
        if w >= fs.weighted(13) and h >= fs.weighted(5):  # 악보의 구성요소가 되기 위한 넓이, 높이 조건
            center = fs.get_center(y, h)
            for line in range(lines):
                area_top = staves[line * 5] - fs.weighted(30)  # 위치 조건 (상단)
                area_bot = staves[(line + 1) * 5 - 1] + fs.weighted(30)  # 위치 조건 (하단)
                if area_top <= center <= area_bot:
                    objects.append([line, (x, y, w, h, area)])  # 객체 리스트에 보표 번호와 객체의 정보(위치, 크기)를 추가
        
    objects.sort()  # 보표 번호 → x 좌표 순으로 오름차순 정렬

    return orgin_image, objects

# 객체 분석
def object_analysis(image, objects):
    for obj in objects:
        stats = obj[1]
        stems = fs.stem_detection(image, stats, 25)  # 객체 내의 모든 직선들을 검출함
        direction = None
        if len(stems) > 0 :  # 직선이 1개 이상 존재함
            if stems[0][0] - stats[0] >= fs.weighted(5):  # 직선이 나중에 발견되면
                direction = True  # 정 방향 음표
            else:  # 직선이 일찍 발견되면
                direction = False  # 역 방향 음표
        obj.append(stems)  # 객체 리스트에 직선 리스트를 추가
        obj.append(direction)  # 객체 리스트에 음표 방향을 추가

        """역 방향 음표에 사각형 그리기(검출 확인용)"""
        # if direction == False:  # direction이 False인 경우에만 사각형 그리기
        #     x, y, w, h, number = stats  # 객체의 위치 정보
        #     cv2.rectangle(image, (x, y), (x + w, y + h), (125, 125, 0), 2)  # 파란색 사각형 그리기
    

    # 기둥에 사각형 그리기(직선 검출 확인)
    # for obj in objects:
    #     stems = obj[2]  # 검출된 기둥 리스트
    #     for stem in stems:
    #         x, y, w, h = stem  # 기둥의 좌표와 크기
    #         cv2.rectangle(image, (x, y), (x + w, y + h), (125, 125, 0), 3)  # 기둥에 네모를 그림
            
    return image, objects


def recognition(image, staves, objects):
    key = 0
    beats = []  # 박자 리스트
    pitches = []  # 음이름 리스트

    for i in range(0, len(objects)-1):
        obj = objects[i]
        line = obj[0]
        stats = obj[1]
        stems = obj[2]
        direction = obj[3]
        (x, y, w, h, area) = stats
        staff = staves[line * 5: (line + 1) * 5]
        
        ts, key = rs.recognize_key(image, staff, stats)
        
        # 박자표 있으면 100 표시
        if ts:
            fs.put_text(image, key, (x, y + h + fs.weighted(20)))

        notes = rs.recognize_note(image, staff, stats, stems, direction)
        if len(notes[0]):
            for beat in notes[0]:
                beats.append(beat)
            for pitch in notes[1]:
                pitches.append(pitch)
        else:
            rest = rs.recognize_rest(image, staff, stats)
            if rest:
                beats.append(rest)
                pitches.append(-1)
            else:
                whole_note, pitch = rs.recognize_whole_note(image, staff, stats)
                if whole_note:
                    beats.append(whole_note)
                    pitches.append(pitch)
        
        cv2.rectangle(image, (x, y, w, h), (255, 0, 0), 1)
        fs.put_text(image, i, (x, y - fs.weighted(20)))

    return image, key, beats, pitches