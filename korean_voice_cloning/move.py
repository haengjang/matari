import os
import shutil
from tqdm import tqdm

# 소스 폴더 경로
source_folder = r"F:\Korean-Voice-Cloning\KsponSpeech\KsponSpeech"

# 대상 폴더 경로
target_folder = r"F:\Korean-Voice-Cloning\KsponSpeech\SV2TTS\encoder"

# 대상 폴더의 상위 폴더 생성
os.makedirs(target_folder, exist_ok=True)

# 소스 폴더의 하위 폴더 리스트
subfolders = os.listdir(source_folder)

# 진행 상황 표시를 위한 tqdm 인스턴스 생성
pbar = tqdm(total=len(subfolders), desc="이동 중")

# 각 하위 폴더에 대해서 WAV 파일 이동
for subfolder in subfolders:
    subfolder_path = os.path.join(source_folder, subfolder)  # 하위 폴더 경로
    
    # 대상 폴더 내에 동일한 이름의 하위 폴더 생성
    target_subfolder_path = os.path.join(target_folder, subfolder)
    os.makedirs(target_subfolder_path, exist_ok=True)
    
    # 하위 폴더 내의 모든 파일에 대해서 이동
    file_count = 0
    for root, dirs, files in os.walk(subfolder_path):
        file_count += len(files)

    with tqdm(total=file_count, desc=subfolder, leave=False) as subfolder_pbar:
        for root, dirs, files in os.walk(subfolder_path):
            for file in files:
                source_file_path = os.path.join(root, file)  # 소스 파일 경로
                target_file_path = os.path.join(target_subfolder_path, file)  # 대상 파일 경로

                # 대상 폴더에 파일을 이동시키기 전에 해당 파일을 삭제합니다.
                if os.path.exists(target_file_path):
                    os.remove(target_file_path)

                shutil.move(source_file_path, target_file_path)
                subfolder_pbar.update(1)  # 진행 상황 업데이트

    pbar.update(1)  # 상위 진행 상황 업데이트

pbar.close()  # 진행 상황 표시 종료
