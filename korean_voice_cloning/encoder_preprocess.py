import shutil
import subprocess
from encoder.preprocess import preprocess_librispeech, preprocess_voxceleb1, preprocess_voxceleb2
from utils.argutils import print_args
from pathlib import Path
import argparse
import librosa
import numpy as np

def convert_pcm_to_wav(pcm_file, wav_file):
    """
    PCM 파일을 WAV 파일로 변환합니다.
    """
    command = f"ffmpeg -f s16le -ar 16k -ac 1 -i {pcm_file} {wav_file}"
    subprocess.call(command, shell=True)

def process_audio_to_mel_spectrogram(wav_file):
    # WAV 파일을 로드합니다.
    audio, sr = librosa.load(wav_file, sr=16000)

    # mel spectrogram을 생성합니다.
    mel_spectrogram = librosa.feature.melspectrogram(audio, sr=sr, n_fft=400, hop_length=160, n_mels=80)

    # log 스케일로 변환합니다.
    mel_spectrogram = librosa.power_to_db(mel_spectrogram, ref=np.max)

    return mel_spectrogram

def preprocess_KsponSpeech(datasets_root: Path, out_dir: Path, skip_existing: bool):
    """
    KsponSpeech 데이터셋을 전처리합니다.
    """
    data_root = datasets_root / "KsponSpeech"

    speaker_folders = sorted(data_root.glob("KsponSpeech_*"))

    for speaker_folder in speaker_folders:
        audio_folders = sorted(speaker_folder.glob("*"))

        for audio_folder in audio_folders:
            audio_files = audio_folder.glob("*.pcm")

            for audio_file in audio_files:
                # 오디오 파일 경로와 텍스트 파일 경로 추출
                audio_path = audio_file
                text_file = audio_file.with_suffix(".txt")
                
                # 디렉토리 이름에 기반한 정렬 파일 이름을 구성
                alignment_file = audio_folder / (audio_folder.name + "_alignment.txt")

                # 텍스트 파일에서 텍스트 추출
                with open(text_file, "r", encoding="cp949") as f:
                    text = f.read().strip()

                # 오디오 파일 처리
                pcm_file = audio_path
                wav_file = audio_path.with_suffix(".wav")
                convert_pcm_to_wav(pcm_file, wav_file)

                # 처리된 mel spectrogram을 출력 디렉토리에 저장
                output_dir = out_dir / speaker_folder.name / audio_folder.name
                output_dir.mkdir(parents=True, exist_ok=True)
                mel_spectrogram = process_audio_to_mel_spectrogram(wav_file)
                mel_output_file = output_dir / "mel_spectrogram.npy"
                np.save(mel_output_file, mel_spectrogram)

                # 정렬 파일을 출력 디렉토리에 복사
                alignment_output_file = output_dir / alignment_file.name
                shutil.copy2(alignment_file, alignment_output_file)

                # 진행 상황 출력
                print(f"처리 완료: {audio_path}")

# 나머지 부분은 원본 코드와 동일

if __name__ == "__main__":
    class MyFormatter(argparse.ArgumentDefaultsHelpFormatter, argparse.RawDescriptionHelpFormatter):
        pass
    
    parser = argparse.ArgumentParser(
        description="데이터셋에서 오디오 파일을 전처리하여 mel spectrogram으로 인코딩하고 "
                    "디스크에 저장합니다.",
        formatter_class=MyFormatter
    )
    parser.add_argument("datasets_root", type=Path, help=\
        "KsponSpeech 데이터셋이 있는 디렉토리 경로.")
    parser.add_argument("-o", "--out_dir", type=Path, default=argparse.SUPPRESS, help=\
        "mel spectrogram이 저장될 출력 디렉토리 경로. 지정하지 않으면 "
        "<datasets_root>/SV2TTS/encoder/로 설정됩니다.")
    parser.add_argument("-s", "--skip_existing", action="store_true", help=\
        "이미 같은 이름의 출력 파일이 있는 경우 스킵합니다.")
    args = parser.parse_args()

    # 인자 처리
    if not hasattr(args, "out_dir"):
        args.out_dir = args.datasets_root.joinpath("SV2TTS", "encoder")
    args.out_dir.mkdir(exist_ok=True, parents=True)

    # 데이터셋 전처리
    print_args(args, parser)
    preprocess_func = {
        "KsponSpeech": preprocess_KsponSpeech,
    }
    args = vars(args)
    for dataset in preprocess_func.keys():
        print(f"{dataset} 전처리 중")
        preprocess_func[dataset](**args)
