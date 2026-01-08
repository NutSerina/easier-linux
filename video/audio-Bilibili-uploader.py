# ============================================================
# 这是一个用于将单个FLAC音频文件转换为B站Hi-Res标准MKV视频的脚本
# 视频格式：1080x1080 2fps
# 会将文件名作为显示文本生成字幕
#
# 这玩意会超采样（为了B站hires），仅供上传B站用，平时闲得没事别用！！！
#
# 依赖：FFmpeg
# ============================================================

import subprocess
import os
import glob

# --- 配置区 ---
COVER_IMG = "cover.jpg"       
OUTPUT_DIR = "Output_Videos"  
FONT_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc" 
BASE_FONT_SIZE = 60           # 基础字号
FONT_COLOR = "white"          

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

def get_flac_files():
    return glob.glob("*.flac")

def process_text(text, max_chars=25):
    """
    手动处理文本换行和字号
    """
    # 如果文本很长，每 max_chars 个字符插入一个换行符
    processed_text = ""
    for i in range(0, len(text), max_chars):
        processed_text += text[i:i+max_chars] + "\n"
    
    # 根据长度缩放字号（如果换行后依然很长，就缩小字号）
    calculated_size = BASE_FONT_SIZE
    if len(text) > 50:
        calculated_size = 40
    elif len(text) > 80:
        calculated_size = 30
        
    return processed_text.strip(), calculated_size

def render_single_video(audio_file):
    base_name = os.path.splitext(audio_file)[0]
    output_file = os.path.join(OUTPUT_DIR, f"{base_name}.mkv")
    
    # 1. 预处理文本和字号
    display_text, font_size = process_text(base_name)
    
    # 2. 彻底转义特殊字符
    # 在 drawtext 中，反斜杠、单引号和冒号需要极其小心的转义
    safe_title = display_text.replace("'", "").replace(":", "\\:")
    
    print(f"--- 正在处理: {audio_file} ---")
    
    # 滤镜调整：
    # - 移除了 wrap_width
    # - 保持 scale=1080:1080 (拉伸封面)
    vf_filter = (
        f"scale=1080:1080,"
        f"drawtext=fontfile='{FONT_PATH}':text='{safe_title}':"
        f"x=(w-text_w)/2:y=(h-text_h)/2:fontsize={font_size}:fontcolor={FONT_COLOR}:"
        f"shadowcolor=black:shadowx=2:shadowy=2:box=1:boxcolor=black@0.4:line_spacing=10"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "2", "-i", COVER_IMG,
        "-i", audio_file,
        "-vf", vf_filter,
        "-c:v", "h264_nvenc", "-preset", "p4", "-cq", "24",
        "-c:a", "flac", "-ar", "48000", "-sample_fmt", "s32",
        "-shortest",
        output_file
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print(f"✅ 完成: {output_file}\n")
    except subprocess.CalledProcessError as e:
        print(f"❌ 失败: {audio_file} (错误码: {e.returncode})\n")

if __name__ == "__main__":
    # 探测字体
    if not os.path.exists(FONT_PATH):
        alt_fonts = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc"
        ]
        for alt in alt_fonts:
            if os.path.exists(alt):
                FONT_PATH = alt
                break

    flacs = sorted(get_flac_files())
    if not flacs:
        print("错误：未找到 .flac 文件")
    elif not os.path.exists(COVER_IMG):
        print(f"错误：找不到封面 '{COVER_IMG}'")
    else:
        for f in flacs:
            render_single_video(f)