import os
import csv
import re
import requests
from random import *
from tqdm import tqdm
import itertools
import opencc
from colorama import init, Fore, Style
init()

# TODO 
#修改为断点+多线程下载，支持下载到一半之后再重新再那个进度进行下载操作
# 下载文件的函数，返回下载的文件名
import csv
import requests
import threading
from tqdm import tqdm

# 定义线程类
class DownloadThread(threading.Thread):
    def __init__(self, url, filepath, start_byte, end_byte, progress_bar):
        threading.Thread.__init__(self)
        self.url = url
        self.filepath = filepath
        self.start_byte = start_byte
        self.end_byte = end_byte
        self.progress_bar = progress_bar
        
    def run(self):
        headers = {'Range': f'bytes={self.start_byte}-{self.end_byte}'}
        with requests.get(self.url, headers=headers, stream=True) as r:
            r.raise_for_status()
            with open(self.filepath, 'rb+') as f:
                f.seek(self.start_byte)
                for chunk in r.iter_content(chunk_size=8192):
                    if not chunk:
                        break
                    f.write(chunk)
                    self.progress_bar.update(len(chunk))

def download_file(url, dest_folder):
    filename = os.path.basename(url)
    filepath = os.path.join(dest_folder, filename)
    try:
        if os.path.exists(filepath):
            for i in itertools.count(1):
                filename, ext = os.path.splitext(filepath)
                filepath = f"{filename}_{i}{ext}"
                if not os.path.exists(filepath):
                    break
                    
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
            with open(filepath, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if not chunk:
                        break
                    f.write(chunk)
                    progress_bar.update(len(chunk))
                    
        progress_bar.close()
    except requests.exceptions.RequestException as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e
    except OSError:
        print(Fore.RED + Style.BRIGHT + f" {filename} 文件命名錯誤 ~ 跳过" + Style.RESET_ALL)
        with open("error_log.txt", "a") as f:
            f.write(url + "\n")
    except Exception as e:
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e

    return filepath

# 重命名文件的函数，返回重命名后的文件名
def rename_file(filepath, name_parts):
    filename, ext = os.path.splitext(filepath)
    new_filename_a = '_'.join(name_parts) + ext
    
    # 繁体汉字到简体汉字的转换
    converter = opencc.OpenCC('t2s.json')
    new_filename_a = converter.convert(new_filename_a)
    
    new_filename  = re.sub(r'[\\/:"*?<>|]', '_', new_filename_a).strip('.')
    new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
    os.rename(filepath, new_filepath)
    return new_filename

# 添加
def append_to_csv(filepath, url, filename):
    with open(filepath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url, filename])


# 检查
def check_if_downloaded(filepath, url):
    with open(filepath, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            if url in row:
                return True
    return False


# 主函数
def main(csv_file, dest_folder):

    # 新建/写入
    if not os.path.exists('downloads'):
        os.mkdir('downloads')
    if not os.path.exists('downloads/已经下载.csv'):
        with open('downloads/已经下载.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['下载链接'])
    downloaded_file = os.path.join(dest_folder, '已经下载.csv')
    if not os.path.exists(downloaded_file):
        with open(downloaded_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['下载链接'])
            
    # 获取文件链接
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            url = next((s for s in row if s and 'http' in s), None)
            # 非url
            if not url:
                print(Fore.RED + Style.BRIGHT + f" {url} 可能不是一个链接 ~ 跳过" + Style.RESET_ALL)
                continue
            # url对比，判断是否下载
            if check_if_downloaded(downloaded_file, url):
                print(f' {url} 已下载 ~ 跳过')
                continue             
            try:
                # 下载
                filepath = os.path.join(dest_folder, download_file(url, dest_folder))
                #突然发觉好像写了很多没用的代码。。。
                result = rename_file(filepath, [s for s in row if s and 'http' not in s])
                print(f'文件下载成功：{result}')
                append_to_csv(downloaded_file, url, os.path.basename(filepath))                    
            except requests.exceptions.HTTPError:
                print(Fore.RED + f" {url} 網絡錯誤 ~ 跳过" + Style.RESET_ALL)
                with open("error_log.txt", "a") as f:
                    f.write(url +"\n")
                continue
            except requests.exceptions.InvalidSchema:
                print(Fore.RED + Style.BRIGHT + f" {url} 可能不是一个链接 ~ 跳过" + Style.RESET_ALL)
                with open("error_log.txt", "a") as f:
                    f.write(url +"\n")
                continue


if __name__ == '__main__':
    # 进行下载
    csv_file = 'books.csv'
    
    #设置文件要下载到那个目录
    dest_folder = 'downloads'
    main(csv_file, dest_folder)
