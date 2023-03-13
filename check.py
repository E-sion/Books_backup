import os
import zipfile
import PyPDF2
import rarfile


class FileChecker:
    def __init__(self, filepath):
        self.filepath = filepath
        self.filetype = os.path.splitext(self.filepath)[1].lower()

    def check_file(self):
        if self.filetype == '.zip':
            return self.check_zipfile()
        elif self.filetype == '.pdf':
            return self.check_pypdf2()
        elif self.filetype == '.rar':
            return self.check_rarfile()
        else:
            print(f"已经跳过【{self.filepath}】文件的完整性检测，请补充 【{self.filetype}】后缀的检测代码")
            return True

    def check_zipfile(self):
        try:
            with zipfile.ZipFile(self.filepath) as zf:
                if zf.testzip() is not None:
                    return False
        except zipfile.BadZipFile:
            return False
        return True

    def check_pypdf2(self):
        try:
            with open(self.filepath, 'rb') as f:
                pdf_reader = PyPDF2.PdfFileReader(f)
                if pdf_reader.isEncrypted:
                    return False
                for i in range(pdf_reader.getNumPages()):
                    page = pdf_reader.getPage(i)
                    if '/Font' not in page['/Resources']:
                        return False
        except PyPDF2.utils.PdfReadError:
            return False
        return True

    def check_rarfile(self):
        try:
            with rarfile.RarFile(self.filepath) as rf:
                if rf.testrar() is not None:
                    return False
        except rarfile.Error:
            return False
        return True
