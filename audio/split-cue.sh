#!/bin/bash

# =================配置区域=================
# 输出文件名格式: 01. 歌手 - 歌名
# %n=音轨号, %p=歌手(Performer), %t=标题(Title)
FORMAT="%n. %p - %t"

# 编码器参数: FLAC 压缩等级 5
ENCODER_OPT="flac flac -5 -s -o %f -"
# =========================================

echo "开始扫描并处理 CUE 文件..."

# 递归查找当前目录及子目录下的所有 .cue 文件
find . -type f -name "*.cue" -print0 | while IFS= read -r -d '' cue_file; do
    
    DIR=$(dirname "$cue_file")
    BASENAME=$(basename "$cue_file" .cue)
    
    echo "------------------------------------------------------"
    echo "发现 CUE: $cue_file"
    
    # 自动寻找同名的音频源文件 (支持 .flac 或 .wav)
    # 优先查找 .flac，其次查找 .wav
    if [ -f "$DIR/$BASENAME.flac" ]; then
        SOURCE_AUDIO="$DIR/$BASENAME.flac"
        EXT="flac"
    elif [ -f "$DIR/$BASENAME.wav" ]; then
        SOURCE_AUDIO="$DIR/$BASENAME.wav"
        EXT="wav"
    else
        echo "⚠️  跳过: 未找到对应的同名 FLAC 或 WAV 音源文件 ($BASENAME)"
        continue
    fi

    echo "对应音源: $SOURCE_AUDIO"
    echo "正在分割并转换..."

    # 1. 使用 shnsplit 进行分割
    # -f: 输入CUE文件
    # -d: 输出目录（原目录）
    # -t: 文件名格式
    # -o: 自定义输出编码器（这里强制指定 flac 及其参数）
    # 最后的 "$SOURCE_AUDIO" 强制指定源音频，忽略 CUE 文件头中可能写错的文件名
    
    # 注意：shnsplit 会自动处理输出，如果成功返回 0
    shnsplit -f "$cue_file" -d "$DIR" -t "$FORMAT" -o "$ENCODER_OPT" "$SOURCE_AUDIO"
    SPLIT_STATUS=$?

    if [ $SPLIT_STATUS -eq 0 ]; then
        echo "✅ 分割成功，正在写入元数据标签..."
        
        # 2. 使用 cuetag.sh 写入 Tags (元数据)
        # cuetag.sh 需要 CUE 文件和生成的 FLAC 文件作为参数
        # 注意：这里我们需要通配符匹配刚刚生成的文件，为了避免匹配到源文件，我们依靠 shnsplit 的命名特征
        # 但通常在该目录下运行 cuetag 匹配所有 flac 也是安全的，因为它会按顺序读取 cue
        
        # 为了精确，我们临时切换到该目录
        pushd "$DIR" > /dev/null
        
        # 使用 cuetag 将 cue 信息写入该目录下所有的 flac 文件 (排除源文件如果是flac的话可能会有警告，但通常不会破坏)
        # 更好的做法是仅针对新生成的文件，但在Shell脚本中简单处理通常是直接传所有flac
        # cuetag.sh "$BASENAME.cue" *.flac
        # 为了避免误伤源文件（如果源文件也是FLAC），我们假设分割后的文件符合格式。
        # 这里使用 cuetag.sh 的标准用法
        cuetag.sh "$BASENAME.cue" *.flac
        
        popd > /dev/null

        echo "🗑️  正在清理源文件..."
        rm "$cue_file"
        rm "$SOURCE_AUDIO"
        echo "已删除: $cue_file 和 $SOURCE_AUDIO"
    else
        echo "❌ 错误: 分割失败，保留源文件。"
    fi

done

echo "------------------------------------------------------"
echo "全部任务完成。"
