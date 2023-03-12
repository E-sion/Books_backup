import concurrent.futures
import os
import csv
import requests
from tqdm import tqdm

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
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            url = next((s for s in row if s and 'http' in s), None)
            if not url:
                continue
            if check_if_downloaded(downloaded_file, url):
                print(f'链接 {url} 已经下载 ~ 跳过')
                continue
            try:
                filepath = os.path.join(dest_folder, download_file(url, dest_folder))
                append_to_csv(downloaded_file, url)
                result = rename_file(filepath, [s for s in row if s and 'http' not in s])
                if result:
                    print(f'文件下载成功： {result}')
            except requests.exceptions.HTTPError:
                # if
                print(f"【{url}】 似乎无法下载，请检查链接是否正确 ~ 跳过")
                print(f"你也可以试着重新启动该脚本")
                pass




if __name__ == '__main__':
    # 进行下载
    csv_file = '书籍.csv'
    dest_folder = 'downloads'
    main(csv_file, dest_folder)