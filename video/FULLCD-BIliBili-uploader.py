# ============================================================
# 这是一个用于将CUE格式的CD转换为B站Hi-Res标准MKV视频的脚本
# 视频格式：1080x1080 2fps
# 会自动读取CUE文件中的歌曲名生成字幕
#
# 这玩意会超采样（为了B站hires），仅供上传B站用，平时闲得没事别用！！！
#
# 依赖：FFmpeg
# ============================================================

import re
import subprocess
import os

# --- 配置区 ---
CUE_FILE = "你的CUE文件路径"
COVER_IMG = "你的封面图片路径" 
OUTPUT_NAME = "你的输出文件名.mkv"
FONT_NAME = "Noto Sans CJK SC" 

def cue_to_seconds(cue_time):
    parts = list(map(int, cue_time.split(':')))
    return parts[0] * 60 + parts[1] + parts[2] / 75.0

def parse_cue(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    audio_match = re.search(r'FILE "(.*)" WAVE', content)
    audio_file = audio_match.group(1) if audio_match else "audio.flac"
    raw_tracks = re.findall(r'TRACK (\d+) AUDIO\s+TITLE "(.*?)"\s+INDEX 01 (\d+:\d+:\d+)', content)
    tracks = []
    for i in raw_tracks:
        tracks.append({'start': cue_to_seconds(i[2]), 'title': i[1]})
    return audio_file, tracks

def generate_ass(tracks, ass_file):
    header = f"[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1080\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\nStyle: Default,{FONT_NAME},45,&H00FFFFFF,&H00000000,&H00000000,1,0,0,0,100,100,0,0,1,3,2,2,10,10,100,1\n\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    with open(ass_file, 'w', encoding='utf-8') as f:
        f.write(header)
        for i, track in enumerate(tracks):
            start = track['start']
            end = tracks[i+1]['start'] if i+1 < len(tracks) else 99999
            def to_t(s):
                return f"{int(s//3600)}:{int((s%3600)//60):02d}:{s%60:05.2f}"
            f.write(f"Dialogue: 0,{to_t(start)},{to_t(end)},Default,,0,0,0,,Now Playing: {track['title']}\n")

def run_ffmpeg(audio_file, ass_file):
    print(f"正在进行 Hi-Res 级别渲染 (24-bit/48kHz FLAC + MKV)...")
    
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "2", "-i", COVER_IMG,
        "-i", audio_file,
        # 视频滤镜：缩放并加上字幕
        "-vf", f"scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,subtitles={ass_file}",
        # 视频编码：NVENC 极速压制
        "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "24",
        # 音频编码：重采样至 48kHz, 设置 24-bit (s32p是ffmpeg常见的flac中间位深)
        "-c:a", "flac", 
        "-ar", "48000",        # 采样率 48khz
        "-sample_fmt", "s32",  # 确保位深，FLAC会根据此输出24或32位
        "-shortest",
        OUTPUT_NAME
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"\n渲染成功！符合B站Hi-Res标准的MKV文件已生成：{OUTPUT_NAME}")
    except subprocess.CalledProcessError as e:
        print(f"\n渲染失败，错误码：{e.returncode}")

if __name__ == "__main__":
    if not os.path.exists(CUE_FILE):
        print(f"未找到 CUE 文件: {CUE_FILE}")
    else:
        audio_path, track_list = parse_cue(CUE_FILE)
        ass_path = "temp_simple.ass"
        generate_ass(track_list, ass_path)
        run_ffmpeg(audio_path, ass_path)
        if os.path.exists(ass_path):
            os.remove(ass_path)