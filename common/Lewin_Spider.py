#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys
from datetime import datetime
from multiprocessing import Process, Queue, Pool, Manager
import threading
import requests

from LewinTools.common.Lewin_Logging import Lewin_Logging
from LewinTools.common.Lewin_File import Lewin_Findfiles

# ————————————————————————————————————————————————————————
class Lewin_Spider:
    __date__ = "2019.04.10"

    def __init__(self, logger: Lewin_Logging):
        self.logger = logger
        self.web = None
        self.url = ""

    def catch(self, url):
        self.url = url
        import requests
        try:
            self.web = requests.get(url)
            self.web.encoding = 'utf-8'
            self.logger.info("Success get: %s" % url)
        except:
            self.logger.error("Failed in get: %s" % url)
            self.logger.get_except()
        return self

    def to_file(self, path_text="", path_cont="", dirname=""):
        default_text = 'spider_%s_%s.txt' % (
        self.url.replace("http://", "").replace(".", "_")[:15], datetime.now().strftime("%H%M%S"))
        default_cont = 'spider_%s_%s.bin' % (
        self.url.replace("http://", "").replace(".", "_")[:15], datetime.now().strftime("%H%M%S"))
        default_dir = os.path.dirname(sys._getframe(1).f_code.co_filename)
        path_text = Lewin_Findfiles.easy_path(path_text, dirname, "", default_dir, default_text)
        path_cont = Lewin_Findfiles.easy_path(path_cont, dirname, "", default_dir, default_cont)
        Lewin_Findfiles(os.path.dirname(path_text), touch=True)
        Lewin_Findfiles(os.path.dirname(path_cont), touch=True)

        try:
            with open(path_text, 'w', encoding='utf-8') as f:
                f.write(self.web.text)
            self.logger.info("Success saved: %s" % path_text)
        except:
            self.logger.error("Failed in saving: %s" % path_text)
            self.logger.get_except()
        try:
            with open(path_cont, 'wb') as f:
                f.write(self.web.content)
                self.logger.info("Success saved: %s" % path_cont)
        except:
            self.logger.error("Failed in saving: %s" % path_cont)
            self.logger.get_except()

    def to_json_dict(self):
        import json
        dic = {}
        try:
            dic = json.loads(self.web.text)
            self.logger.info("Read json, keys= %s..." % str(dic.keys())[:100])
        except:
            self.logger.error("Failed in reading json!")
            self.logger.get_except()
        return dic


class Lewin_Spider_Threading:
    __date__ = "2019.04.10"

    def get_threading(self, q_urls: Queue, q_back: Queue, q_log: Queue):
        ts = []
        for i in range(7):
            t = threading.Thread(target=Lewin_Spider_Threading._get_worker, args=(q_urls, q_back, q_log))
            ts.append(t)
        for t in ts:
            t.start()
        for t in ts:
            t.join()

    @staticmethod
    def _get_worker(q_urls: Queue, q_back: Queue, q_log: Queue):
        while not q_urls.empty():
            try:
                url = q_urls.get(timeout=1)
            except:
                break
            else:
                q_log.put("getting %s" % url, timeout=1)
            try:
                web = requests.get(url)
                web.encoding = 'utf-8'
            except:
                q_log.put("Failed! %s" % url, timeout=1)
                # q_in.put(url)
            else:
                q_back.put([web, url], timeout=1)
                q_log.put("Success get: %s" % url, timeout=1)

    # def main_download(logger:Lewin_Logging):
    #     manager = Manager()
    #     q_in, q_out, q_log= manager.Queue(), manager.Queue(), manager.Queue()
    #
    #     # 准备q_in
    #     today = datetime.strptime('20170101', '%Y%m%d').date()    #strptime('201902251100', '%Y%m%d%H%M')
    #     since = datetime.strptime('20130101', '%Y%m%d').date()
    #     while True:
    #         if since > today:
    #             break
    #         q_in.put("http://www.shfe.com.cn/data/dailydata/kx/pm{}.dat".format(since.strftime("%Y%m%d")))
    #         since = since + timedelta(1)
    #
    #     p = Process(target=Lewin_Spider_Threading, args=(q_in, q_out, q_log))
    #     p.start()
    #
    #     while (p.is_alive()) or (not q_out.empty()):
    #         while not q_log.empty():
    #             print(q_log.get_nowait())
    #         try:
    #             web, url = q_out.get(timeout=1)

    #             ##### do something! #####
    ### 可以考虑再做一个Queue，继续使用多进程对爬取的数据进行处理 ###

    #         except Exception as e:
    #             print("Failed! %s"%e)
    #     p.join()

    def post_threading(self, q_post: Queue, q_back: Queue, q_log: Queue):
        """q_post:Queue<(url, post_dic),(url, post_dic),(url, post_dic),...>"""
        ts = []
        for i in range(7):
            t = threading.Thread(target=Lewin_Spider_Threading._post_worker,
                                 args=(q_post, q_back, q_log, "Thread-%d" % i))
            ts.append(t)
        for t in ts:
            t.start()
        for t in ts:
            t.join()

    @staticmethod
    def _post_worker(q_post: Queue, q_back: Queue, q_log: Queue, name: str = "unnamed-thread"):
        q_log.put("Create thread: %s" % name, timeout=1)
        while True:
            try:
                url, dic_post = q_post.get(timeout=3)
            except:
                break
            else:
                q_log.put("posting '%s' : '%s' ." % (url, str(dic_post)[:200]), timeout=1)
            try:
                web = requests.post(url, dic_post)
                web.encoding = 'utf-8'
            except:
                q_log.put("Failed! %s" % url, timeout=1)
                # q_in.put(url)
            else:
                q_back.put([web, [url, dic_post]], timeout=1)
                q_log.put("Success post.", timeout=1)
        q_log.put("Quit thread: %s" % name, timeout=1)

    @staticmethod
    def post_processor(func, q_back: Queue, q_result: Queue, q_log: Queue, name: str = "unnamed-processor", *args,
                       **kwargs):
        q_log.put("Create processor: %s" % name, timeout=1)
        while True:
            try:
                spider_web, spider_post = q_back.get(timeout=10)
            except:
                break
            else:
                q_log.put("%s is processing a new back data." % name, timeout=1)
            try:
                result = func(spider_web=spider_web, spider_post=spider_post, q_log=q_log, *args, **kwargs)
            except Exception as e:
                q_log.put("%s failed process: %s" % (name, e), timeout=1)
                # q_in.put(url)
            else:
                q_result.put(result, timeout=1)
                q_log.put("%s success process." % (name,), timeout=1)
        q_log.put("Quit processor: %s" % name, timeout=1)
