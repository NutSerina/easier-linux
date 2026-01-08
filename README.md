# 🐧 easier-linux

**easier-linux** 是一个旨在简化 Linux 日常操作的脚本集合。这里收集了各种开箱即用的小工具，解决那些"命令太长记不住"或"手动处理太繁琐"的痛点。

## 🛠 脚本列表

### 音频
 - **split-cue.sh**：批量处理 CUE 文件，自动分割音频（FLAC/WAV）为独立音轨，写入元数据标签，并清理源文件
   - 功能：递归扫描目录下的 CUE 文件，使用 shnsplit 分割对应音频文件，用 cuetag.sh 写入标签
   - 依赖：shntool, cuetools, flac
   - 输出格式：`01. 歌手 - 歌名.flac`

### 压缩
 - **dir-to-rar.sh**：批量文件夹打包为 RAR 格式，支持自定义注释、中文密码和恢复记录
   - 功能：遍历当前目录子文件夹，生成带密码保护的 RAR 压缩包，添加个性化注释
   - 依赖：rar
   - 特性：支持中文密码、恢复记录（5%）、自定义注释、排除路径层级

### 视频
- **audio-Bilibili-uploader.py**：单个FLAC音频文件转换为B站Hi-Res标准MKV视频
  - 功能：将FLAC文件转换为1080x1080 2fps的静态视频，自动生成字幕显示文件名
  - 特性：超采样至48kHz/24-bit以满足B站Hi-Res要求，支持自动换行和字号调整
  - 依赖：FFmpeg、封面图片（cover.jpg）
  - 输出：Output_Videos目录下的MKV文件

- **FULLCD-BIliBili-uploader.py**：CUE格式整张CD转换为B站Hi-Res标准MKV视频
  - 功能：解析CUE文件，整张CD生成单个MKV，每首歌自动切换字幕
  - 特性：读取CUE中的音轨信息和时间轴，生成带章节字幕的视频，超采样至Hi-Res标准
  - 依赖：FFmpeg、CUE文件、封面图片
  - 输出：单个带完整CD内容的MKV文件

---

## 🚀 快速开始

### 1. 克隆仓库

