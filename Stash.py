#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import zipfile




class Lewin_Zip:
    pass



class PDF_to_txt:
    def __init__(self):
        self.path = "something else."

    def pdf_to_txt(self, pdf_path, txt_path, fmt):
        pdf_path = Lewin_Findfiles.easy_path(filename=pdf_path, default_dir=self.path)
        txt_path = Lewin_Findfiles.easy_path(filename=txt_path, default_dir=self.path)

        import pandas as pd
        import pdfplumber
        # 参考 https://github.com/jsvine/pdfplumber#table-extraction-methods

        with pdfplumber.open(pdf_path) as pdf:
            tables = []
            for page in pdf.pages:
                for table in page.extract_tables(fmt):
                    tables += table
            df = pd.DataFrame(tables)
            df.to_csv(txt_path, index=False)

        return txt_path


# ————————————————————————————————————————————————————————
class Lewin_Ftp:
    __date__ = "20190422"

    def __init__(self, host, username, password, logger=None):
        if logger == None:
            self.logger = Logging_Mute()
        else:
            self.logger = logger
        import ftplib
        self.ftp = ftplib.FTP(host)
        self.ftp.login(username, password)

    def __del__(self):
        try:
            self.ftp.quit()
        except:
            pass

    def download(self, path_remote: str, path_local: str):
        self.logger.info(path_local)
        with open(path_local, 'wb') as f:
            self.ftp.retrbinary("RETR %s" % path_remote, f.write)