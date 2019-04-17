#!/usr/bin/env python3
# -*- coding: utf-8 -*-
__author__ = 'lewin'
__date__ = '2019/4/10'
"""

"""

import os, sys
import pandas as pd
from datetime import datetime
from LewinTools.common.Lewin_Logging import Lewin_Logging


# ————————————————————————————————————————————————————————
class AP_Database:
    """从mysql中直接查询trades数据，等效于在网页上查询。"""
    __date__ = "2019.04.10"

    def __init__(self, db_login_command="", lib="sqlalchemy", logger=None):
        self.lib = lib
        if logger == None:
            self.logger = Easy_Logging_Time()
        else:
            self.logger = logger
        if lib == "sqlalchemy":
            from sqlalchemy import create_engine
            if not db_login_command: db_login_command = self._default_database()
            self.ENGINE = create_engine(db_login_command)
        elif lib == "pymysql":
            pass
        else:
            raise Exception("wrong lib name! choose [sqlalchemy, pymysql]")

    def _default_database(self):
        if self.lib != "sqlalchemy":
            raise Exception("wanna use this func, pls set lib as 'sqlalchemy'.")
        PATH_HOME = os.path.expanduser('~')

        if PATH_HOME.startswith('/'):  # linux环境下
            PATH_LEWIN_AP = "/home/users/lewin/mycode/AP"
            sys.path.insert(0, PATH_LEWIN_AP) if not (PATH_LEWIN_AP in sys.path) else None
            from lewin_config import MYSQL_apmosdb as MYSQL_apmosdb
        elif PATH_HOME == "C:\\Users\\lewin":  # windows环境下
            PATH_LEWIN_AP = "C:/Users/lewin/mycode/AP"
            sys.path.insert(0, PATH_LEWIN_AP) if not (PATH_LEWIN_AP in sys.path) else None
            from lewin_config import MYSQL_win_apmosdb as MYSQL_apmosdb
        else:
            raise Exception("%s模块无法识别linux/windows环境，无法加载环境变量。" % __file__)
        return MYSQL_apmosdb

    def search_ap_code(self, search_value):
        if self.lib != "sqlalchemy":
            raise Exception("wanna use this func, pls set lib as 'sqlalchemy'.")
        import pandas as pd
        command = "SELECT * FROM Trade WHERE ap_code ='%s';" % (search_value,)
        df_search = pd.read_sql_query(command, con=self.ENGINE)
        return df_search

    def select_as_DataFrame(self, command_str: str):
        """ give a SELECT command, and return a pandas.DataFrame object."""
        if self.lib != "sqlalchemy":
            raise Exception("wanna use this func, pls set lib as 'sqlalchemy'.")
        import pandas as pd
        if not command_str.lower().startswith("select "):
            raise Exception("Pls starts with 'SELECT ': %s" % command_str)
        if not command_str.strip().endswith(";"):
            command_str = command_str.strip() + ";"
        self.logger.info(command_str)
        df_search = pd.read_sql_query(command_str, con=self.ENGINE)
        return df_search

    def pd_to_sql(self, df: pd.DataFrame, cmd):
        if self.lib != "pymysql":
            raise Exception("wanna use this func, pls set lib as 'pymysql'.")
        return

    @staticmethod
    def insert_df(logger: Lewin_Logging, df_no_dpl: pd.DataFrame, host, user, password, database, table):
        rowcount = 0
        if len(df_no_dpl) == 0:
            logger.warning("0 row to insert!")
            return rowcount

        cols = list(df_no_dpl.columns)
        cmd_values = "({})".format(",".join(["%s" for x in range(len(cols))]))
        cmd_cols = "({})".format(",".join(cols))
        cmd_sql = "INSERT INTO `{}` {} VALUES {}".format(table, cmd_cols, cmd_values)

        values = []
        for line in df_no_dpl.index:
            values.append(tuple(str(x) for x in df_no_dpl.loc[line]))

        import pymysql.cursors
        db = pymysql.connect(host=host, user=user, password=password, database=database)
        logger.info("connect to mysql via pymysql.")
        try:
            logger.info(cmd_sql)
            with db.cursor() as cursor:
                cursor.executemany(cmd_sql, values)
                # 是否逐条插入比较好？如果遇到重复的该如何处理？warning？
            db.commit()
            rowcount = cursor.rowcount
            logger.info("Insert %d rows." % rowcount)
        except Exception as e:
            logger.error("Failed when insert: (%s)" % e)
            logger.get_except()
            db.rollback()
            return rowcount
        finally:
            db.close()
            logger.info("close mysql connector.")
        return rowcount

    @staticmethod
    def insert_dic(logger: Lewin_Logging, insert: dict, host, user, password, database, table):
        rowcount = 0
        if len(insert) == 0:
            logger.warning("0 row to insert!")
            return rowcount

        cmd_cols = "({})".format(",".join(list(insert.keys())))
        cmd_values = "({})".format(",".join(["'%s'" % x for x in insert.values()]))
        cmd_sql = "INSERT INTO `{}` {} VALUES {};".format(table, cmd_cols, cmd_values)

        import pymysql.cursors
        db = pymysql.connect(host=host, user=user, password=password, database=database)
        logger.info("connect to mysql via pymysql.")
        try:
            logger.info(cmd_sql)
            with db.cursor() as cursor:
                cursor.execute(cmd_sql)
            db.commit()
            rowcount = cursor.rowcount
            logger.info("Insert %d rows." % rowcount)
        except Exception as e:
            logger.error("Failed when insert: (%s)" % e)
            logger.get_except()
            db.rollback()
            return rowcount
        finally:
            db.close()
            logger.info("close mysql connector.")
        return rowcount

    @staticmethod
    def update_dic(logger: Lewin_Logging, where: dict, update: dict, host, user, password, database, table):
        rowcount = 0
        if (len(where) == 0) or (len(update) == 0):
            logger.warning("pls give 'where' and 'update' to update!")
            return rowcount

        cmd_update = ",".join(["%s='%s'" % (key, value) for key, value in update.items()])
        cmd_where = "({})".format(" and ".join(["%s='%s'" % (key, value) for key, value in where.items()]))
        cmd_sql = "UPDATE `{}` SET {} WHERE {}".format(table, cmd_update, cmd_where)

        import pymysql.cursors
        db = pymysql.connect(host=host, user=user, password=password, database=database)
        logger.info("connect to mysql via pymysql.")
        try:
            logger.info(cmd_sql)
            with db.cursor() as cursor:
                cursor.execute(cmd_sql)
                # 是否逐条插入比较好？如果遇到重复的该如何处理？warning？
            db.commit()
            rowcount = cursor.rowcount
            logger.info("Update %d rows." % rowcount)
        except Exception as e:
            logger.error("Failed when Update: (%s)" % e)
            logger.get_except()
            db.rollback()
            return rowcount
        finally:
            db.close()
            logger.info("close mysql connector.")
        return rowcount


# ————————————————————————————————————————————————————————
class Easy_Logging_Time:
    __date__ = "2019.04.10"

    def debug(self, s):
        print("[%s][debug] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def info(self, s):
        print("[%s][info] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def warning(self, s):
        print("[%s][warning] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def error(self, s):
        print("[%s][error] %s" % (datetime.now().strftime("%H:%M:%S"), s))

    def critical(self, s):
        print("[%s][critical] %s" % (datetime.now().strftime("%H:%M:%S"), s))