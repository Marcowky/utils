#!/bin/bash

# 检查是否提供了模型名称参数
if [ -z "$1" ]; then
    echo "huggingface model name"
    echo "usage: $0 <model_name>"
    exit 1
fi

# 设置基础路径和模型名称
base_path="$HOME/Model/"
model_name="$1"

# 组合路径
path="${base_path}${model_name}"

# 设置 Hugging Face 端点
export HF_ENDPOINT="https://hf-mirror.com"

# 下载模型的函数
download_model() {
    huggingface-cli download "$model_name" --local-dir "$path"
}

# 尝试下载模型，直到成功为止
while true; do
    download_model
    if [ $? -eq 0 ]; then
        echo "successed！"
        break
    else
        echo "can't download..."
        sleep 5
    fi
done