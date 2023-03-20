import os
import opencc

# 定义目录路径和转换器
dir_path = r".\downloads"
converter = opencc.OpenCC('t2s.json')

# 遍历目录下所有文件名
for root, dirs, files in os.walk(dir_path):
    for file_name in files:
        # 将文件名转换为简体中文
        new_file_name = converter.convert(file_name)
        # 如果文件名有变化，则重命名文件
        if new_file_name != file_name:
            os.rename(os.path.join(root, file_name), os.path.join(root, new_file_name))
