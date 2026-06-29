import subprocess
import sys

# Настройки разрешения OpenComputers Tier 3
WIDTH = 160
HEIGHT = 50
TARGET_FPS = 20  # Ограничение для плавности в Minecraft

def convert_video_pure_python(input_path, output_path):
    print("Запуск конвертации видео напрямую через FFmpeg...")
    
    # Команда FFmpeg: меняет размер, подгоняет FPS и выдает сырой RGB поток в stdout
    ffmpeg_cmd = [
        "ffmpeg", "-i", input_path,
        "-vf", f"scale={WIDTH}:{HEIGHT},fps={TARGET_FPS}",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-hide_banner", "-loglevel", "error", "-"
    ]
    
    # Размер одного несжатого кадра в байтах (3 байта на пиксель: R, G, B)
    frame_size = WIDTH * HEIGHT * 3
    
    try:
        # Запускаем FFmpeg как подпроцесс
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, bufsize=10**7)
    except FileNotFoundError:
        print("Ошибка: Утилита FFmpeg не найдена. Сначала выполните: pkg install ffmpeg")
        return

    frame_count = 0
    
    with open(output_path, "w", encoding="utf-8") as f:
        # Пишем заголовок VIF
        f.write(f"{WIDTH},{HEIGHT},{TARGET_FPS}\n")
        
        while True:
            # Читаем ровно один кадр из потока FFmpeg
            raw_frame = process.stdout.read(frame_size)
            if len(raw_frame) < frame_size:
                break  # Видео закончилось
                
            frame_data = []
            # Проходим по байтам кадра с шагом 3 (R, G, B)
            for i in range(0, frame_size, 3):
                r = raw_frame[i]
                g = raw_frame[i+1]
                b = raw_frame[i+2]
                
                # Переводим RGB в HEX формат (0xRRGGBB)
                hex_color = (r << 16) | (g << 8) | b
                frame_data.append(f"{hex_color:06X}")
                
            # Записываем кадр строкой пикселей через пробел
            f.write(" ".join(frame_data) + "\n")
            frame_count += 1
            
            if frame_count % 50 == 0:
                print(f"Обработано кадров: {frame_count}")
                
    process.communicate() # Мягко закрываем процесс FFmpeg
    print(f"\nУспешно обработано {frame_count} кадров!")
    print(f"Результат сохранен в: {output_path}")

if __name__ == "__main__":
    input_file = sys.argv[1] if len(sys.argv) > 1 else "input.mp4"
    output_file = "myvideo.vif"
    convert_video_pure_python(input_file, output_file)
