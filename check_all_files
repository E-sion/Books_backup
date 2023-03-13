import os
import zipfile
import gzip
import PyPDF2

def check_file(filepath):
    if filepath.endswith('.rar'):
        try:
            with open(filepath, 'rb') as f:
                header = f.read(7)
                if header != b'Rar!\x1a\x07\x00':
                    return False
                else:
                    return True
        except:
            return False
    elif filepath.endswith('.zip'):
        try:
            with zipfile.ZipFile(filepath, 'r') as zf:
                zf.testzip()
                return True
        except:
            return False
    elif filepath.endswith('.pdf'):
        try:
            with open(filepath, 'rb') as f:
                pdf = PyPDF2.PdfFileReader(f)
                pdf.getNumPages()
                return True
        except:
            return False
    elif filepath.endswith('.gz'):
        try:
            with gzip.open(filepath, 'r') as f:
                f.read(1)
                return True
        except:
            return False
    else:
        return False

if __name__ == '__main__':
    directory = 'downloads'
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            if check_file(filepath):
                print(f'{filepath} is not corrupted.')
            else:
                print(f'{filepath} is corrupted.')
