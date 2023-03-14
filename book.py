import os
import csv
import requests

from tqdm import tqdm

# TODO 
#修改为断点+多线程下载，支持下载到一半之后再重新再那个进度进行下载操作
# 下载文件的函数，返回下载的文件名
import os
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

# 下载文件的函数，返回下载的文件名
def download_file(url, dest_folder):
    filename = os.path.basename(url)
    filepath = os.path.join(dest_folder, filename)
    try:
        # 检查文件是否已经存在
        if os.path.exists(filepath):
            total_size = os.path.getsize(filepath)
            headers = {'Range': f'bytes={total_size}-'}
            with requests.get(url, headers=headers, stream=True) as r:
                r.raise_for_status()
                total_size += int(r.headers.get('content-length', 0))
                progress_bar = tqdm(total=total_size, initial=total_size, unit='iB', unit_scale=True)
                # 追加写入文件
                with open(filepath, 'ab') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            break
                        f.write(chunk)
                        progress_bar.update(len(chunk))
        else:
            with requests.get(url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
                # 写入新文件
                with open(filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            break
                        f.write(chunk)
                        progress_bar.update(len(chunk))
                        
        progress_bar.close()
    except requests.exceptions.RequestException as e:
        # 删除正在下载的文件
        if os.path.exists(filepath):
            os.remove(filepath)
        raise e
    return filename


# 重命名文件的函数，返回重命名后的文件名
def rename_file(filepath, name_parts):
    filename, ext = os.path.splitext(filepath)
    new_filename = '_'.join(name_parts) + ext
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
                print(f" {url} 似乎不是下载链接 ")
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
                print(f"【 {url} 】请检查该链接的有效性 ~ 跳过")
                continue

if __name__ == '__main__':
    # 进行下载
    csv_file = 'books.csv'
    
    #设置文件要下载到那个目录
    dest_folder = 'downloads'
    main(csv_file, dest_folder)
