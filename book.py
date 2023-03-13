import os
import csv
import requests

from tqdm import tqdm
from check import FileChecker
from urllib.parse import urlsplit


# 下载文件的函数，返回下载的文件名
def download_file(url, dest_folder):
    filename = os.path.basename(url)
    filepath = os.path.join(dest_folder, filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        total_size = int(r.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size, unit='iB', unit_scale=True)
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
                progress_bar.update(len(chunk))
    progress_bar.close()
    return filename

# 重命名文件的函数，返回重命名后的文件名
def rename_file(filepath, name_parts):
    filename, ext = os.path.splitext(filepath)
    new_filename = '_'.join(name_parts) + ext
    new_filepath = os.path.join(os.path.dirname(filepath), new_filename)
    os.rename(filepath, new_filepath)
    return new_filename

# 每行数据的处理函数
def process_row(row, dest_folder):
    name_parts = [s for s in row if s and 'http' not in s]
    url = next((s for s in row if s and 'http' in s), None)
    if not url:
        return
    filepath = os.path.join(dest_folder, download_file(url, dest_folder))
    return rename_file(filepath, name_parts)


# 添加
def append_to_csv(filepath, url):
    with open(filepath, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([url])


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
            # 删除下载到一半的文件，防止报错
            else : 
                check_downloading_file = DownloadFile(url, dest_folder)
                check_downloading_file.delete_existing_file()                
            try:
                filepath = os.path.join(dest_folder, download_file(url, dest_folder))
                checker = FileChecker(filepath)
                #检查该文件是否有效
                if checker.check_file():
                    print(f'文件下载成功：', end='')
                    result = rename_file(filepath, [s for s in row if s and 'http' not in s])
                    print(result)
                    append_to_csv(downloaded_file, url,result)
                else:
                    os.remove(filepath)
                    print(f"{result}文件不完整，重新下载")
                    continue
                
            except requests.exceptions.HTTPError:
                # if
                print(f"【{url}】请检查该链接的有效性 ~ 跳过")
                continue

# 获取url，返回给url对应的下载文件名，然后再和文件夹内对比，有的话就代表出现了下载到一半的文件，则删除
class DownloadFile:
    def __init__(self,url,folder):
        self.url = url
        self.filename = self.get_filename_from_url()
        self.download_dir = folder

    def get_filename_from_url(self):
        return self.url.split('/')[-1]

    def delete_existing_file(self):
        file_path = os.path.join(self.download_dir, self.filename)
        if os.path.isfile(file_path):
            os.remove(file_path)
            print("已删除") 


if __name__ == '__main__':
    # 进行下载
    csv_file = 'books.csv'
    
    #设置文件要下载到那个目录
    dest_folder = 'downloads'
    main(csv_file, dest_folder)

