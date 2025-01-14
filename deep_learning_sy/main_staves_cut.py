#main
import cv2
import os
import numpy as np
import functions as fs
import modules as modules_sy

# 악보 이미지들이 들어있는 폴더 경로
input_folder = r"D:\music-sheet-algoritm\deep_learning_sy\dd"

# 보표 추출한 이미지들을 저장할 폴더 경로
output_folder = r"D:\music-sheet-algoritm\easy_drum_img"

# 보표 추출 작업
def extract_symbols_from_images(input_folder, output_folder):
    # 폴더 내의 이미지 파일들을 순회하며 보표 추출
    for filename in os.listdir(input_folder):
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(input_folder, filename)
            image = cv2.imread(image_path, cv2.IMREAD_ANYCOLOR)

            # 보표 영역 추출
            masked_image, extracted_symbols = modules_sy.remove_noise(image)

            # 보표 추출한 이미지들을 저장할 폴더 생성 (없으면 생성)
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            # 보표 추출한 이미지들을 순회하며 파일로 저장
            for i, symbol in enumerate(extracted_symbols):
                symbol_filename = os.path.join(output_folder, f"{filename}_symbol_{i}.jpg")
                cv2.imwrite(symbol_filename, symbol)

# 악보 이미지들로부터 보표 추출 수행
extract_symbols_from_images(input_folder, output_folder)