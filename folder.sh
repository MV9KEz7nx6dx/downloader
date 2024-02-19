#!/bin/bash

# 从命令行参数获取字符串
input=$1

# 获取字符串的第一个字符
first_char=$(echo "$input" | cut -c 1)

# 判断第一个字符是否是字母
if [[ $first_char =~ [a-zA-Z] ]]; then
    # 如果是字母，转换成大写
    first_char=$(echo $first_char | tr '[:lower:]' '[:upper:]')
fi


# 判断输入是否包含数字或字母
if [[ $first_char =~ [0-9a-zA-Z] ]]; then
    folder=$first_char
else
    folder="videos"
fi


echo $folder
