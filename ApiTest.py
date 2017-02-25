import os
import re
import xlwt
import json
import time
import copy
import xlrd
import random
import threading
import requests
from tkinter import *
from tkinter.ttk import *
from tkinter import font
from tkinter.messagebox import *
import matplotlib.pyplot as plt
from xlutils.copy import copy as xcopy

class Test:
    def __init__(self, test_info):
        self.max_time = 0
        self.quit = False
        self.insert_id = -1
        self.cookies= ""
        self.log_level = "DEBUG"
        self.random_int_min = 0
        self.path = os.getcwd()
        self.use_time_info = []
        self.overtime_count = 0
        self.response_list = []
        self.random_str_min_len = 6
        self.task_response_map = {}
        self.random_str_max_len = 20
        self.random_int_max = 1000000
        self.file_lock = threading.Lock()                                                 # 文件锁
        self.api_list = test_info["api_list"]                                             # 增加的任务列表
        self.task_name = test_info["task_name"]                                           # 任务名称
        self.thread_num = test_info["thread_num"]                                         # 测试的线程数
        self.iscreat_pdf = test_info["creat_pdf"]                                         # 是否创建PDF
        self.over_time = test_info["over_time"]                                           # 允许接口请求的最大时间
        self.test_times = test_info["test_times"]                                         # 接口测试的次数
        self.response_list_lock = threading.Lock()                                        # response_list_lock
        self.data_keys = ['int', 'str', 'random_int', 'random_str']                       # 用户设置的关键字
        self.log_levels = ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]                     # 设置打印的级别
        self.current_time = time.strftime( '%Y%m%d', time.localtime(time.time()))         # 获取现在的时间
        self.headers = {"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch", "Cache-Control":"max-age=0","Connection":"keep-alive",
        "Accept-Language":"zh-CN,zh;q=0.8", "Upgrade-Insecure-Requests": "1" ,
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36"}
        self.init_test()

    def init_test(self):
        #  设置excel表格的样式
        self.style0 = xlwt.easyxf('font:height 200; align:horiz center, vert centre') #20*12pt, 水平居中
        self.style1 = xlwt.easyxf('pattern: pattern solid, fore_colour green; font: bold on;font:height 280;align:horiz center;') # 80% like
        self.style2 = xlwt.easyxf('pattern: pattern solid, fore_colour light_green;font:height 200; align:horiz center, vert centre;') #20*12pt, 水平居中
        self.style3 = xlwt.easyxf('font:height 240;font: bold on;align:horiz center, vert centre')
        self.style4 = xlwt.easyxf('pattern: pattern solid, fore_colour red;font:height 200; align:horiz center, vert centre;') #20*12pt, 水平居中
        self.style5 = xlwt.easyxf('font:height 200; align:horiz left, vert centre')
        self.style6 = xlwt.easyxf('pattern: pattern solid, fore_colour light_blue;font: bold on;font:height 280; align:horiz center, vert centre;')
        try:
            workbook = xlrd.open_workbook(self.task_name + "-" + self.current_time+".xls", formatting_info=True)
            sheet = workbook.sheet_by_index(0)
            self.workbook = xcopy(workbook)
            self.sheet = self.workbook.get_sheet(0)
            self.nrows = len(self.sheet.rows) - 3
            str_count = (sheet.cell_value(self.nrows+2,8))
            m = re.findall(r'(\w*[0-9]+)\w*',str_count)
            self.count = int(m[0])
            print(self.nrows)
            print(self.count)
        except Exception as error:
            print(error)
            print("创建新的")
            self.workbook = xlwt.Workbook()
            self.sheet = self.workbook.add_sheet("self.task_name")
            self.nrows = 1
            self.sheet.col(0).width = 256*20                           # 设置行宽
            self.sheet.col(1).width = 256*20
            self.sheet.col(2).width = 256*30
            self.sheet.col(3).width = 256*30
            self.sheet.col(4).width = 256*20
            self.sheet.col(5).width = 256*20
            self.sheet.col(6).width = 256*30
            self.sheet.col(7).width = 256*30
            self.sheet.col(8).width = 256*30
            self.sheet.col(9).width = 256*30
            self.sheet.write(0, 0, "模块", self.style1)
            self.sheet.write(0, 1, "测试用例ID", self.style1)
            self.sheet.write(0, 2, "测试用例描述", self.style1)
            self.sheet.write(0, 3, "对应接口请求地址", self.style1)
            self.sheet.write(0, 4, "请求方式", self.style1)
            self.sheet.write(0, 5, "请求状态", self.style1)
            self.sheet.write(0, 6, "请求数据", self.style1)            
            self.sheet.write(0, 7, "返回数据", self.style1)
            self.sheet.write(0, 8, "预期结果", self.style1)
            self.sheet.write(0, 9, "是否通过", self.style1)
            self.sheet.write(0, 10, "备注", self.style1)
            self.count = 0
 
    # 随机生成字符串
    def random_str(self):
        char = [
                'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 
                'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 
                'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 
                'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 
                'W', 'X', 'Y', 'Z', '1', '2', '3', '4', '5', '6', '7', '8',
                '9', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '&',
                '!', '~', '@', '%', '^', '*', '(', ')', '-', '_', '+', '='
                ]
        random_data = ""
        if self.random_str_max_len > 10000:
            self.random_str_max_len = 10000
        if self.random_str_min_len < 1:
            self.random_str_min_len = 1
        n = random.randint(self.random_str_min_len, self.random_str_max_len + 1) 
        for i in range(n):
            m = random.randint(0, len(char) - 1)
            random_data = random_data + char[m]
        return random_data

    # 获取上一个接口返回的数据
    def get_data(self, post_data, api_id):
        change_data_list = []
        match = re.compile(r'\$.*?\$')
        change_data_list = match.findall(post_data)
        print(change_data_list)
        for data in change_data_list:
            data_list = data.split('.')
            data_len = len(data_list)
            self.write_log("data_list:\n" + str(data_list), 'main', "DEBUG")
            if data_list[1]  not in self.data_keys:
                self.write_log("key error "+ str(data), 'main', "INFO")
                continue
            elif data_list[1] == 'random_int':
                if data_len == 5:
                    try:
                        self.random_int_min = int(data_list[2])
                    except:
                        self.random_int_min = 0
                        self.write_log("random_int random_int_min error " + str(data), 'main', "INFO")
                    try:
                        self.random_int_max = int(data_list[3])
                    except:
                        self.random_int_max = 100000
                        self.write_log("random_int random_int_max error "+ str(data), 'main', "INFO")
                    random_int = str(random.randint(self.random_int_min, self.random_int_max))
                    post_data = post_data.replace('"' + data + '"', random_int)
                    post_data = post_data.replace(data, random_int)
            elif data_list[1] == 'random_str':
                if data_len ==5:
                    try:
                        self.random_str_min_len = int(data_list[2])
                    except:
                        self.random_str_min_len = 6
                        self.write_log("random_str random_str_min_len error "+ str(data), 'main', "INFO")
                    try:
                        self.random_str_max_len = int(data_list[3])
                    except:
                        self.random_str_max_len = 20
                        self.write_log("random_str random_str_max_len error "+ str(data), 'main', "INFO")
                    post_data = post_data.replace(data, self.random_str())
            elif data_list[1] == 'int' or data_list[1] == 'str':
                if data_len >= 5:
                    try:
                        index = int(data_list[2])
                        if index >= api_id:
                            continue
                        if index >= 0 and index <= len(self.api_list):
                            api_data = self.api_list[index]["response"]
                            for index_data in data_list[3:-1]:
                                if isinstance(api_data, dict):
                                    if index_data in  api_data.keys():
                                        api_data = api_data[index_data]
                                    else:
                                        break
                                elif isinstance(api_data, list):
                                    if int(index_data) < len(api_data):
                                        api_data = api_data[int(index_data)]
                                    else:
                                        break
                                elif isinstance(api_data, str):
                                    break
                                elif isinstance(api_data, int):
                                    break
                            if data_list[1] == 'int':
                                try:
                                    api_data = str(api_data)
                                    post_data = post_data.replace('"' + data + '"', api_data)
                                    post_data = post_data.replace(data, api_data)
                                except:
                                    continue
                            elif data_list[1] == 'str':
                                api_data = str(api_data)
                                post_data = post_data.replace(data, api_data)
                    except:
                        self.write_log("get data error ", 'main'+ str(data), "INFO")
        return post_data

    # 工作函数
    def task_work(self, index):
        count = 0
        # 循环测试多次
        while count < self.test_times and not self.quit:
            start_stamp = time.time()*1000
            response_data = {}
            self.write_log(str(self.api_list), str(index), "DEBUG")
            # 从任务列表中取出任务
            for task in self.api_list:
                response_data = {}
                task["request_id"] = str(task["request_id"])                                              # 任务的id补充为3位
                if len(task["request_id"]) < 3:
                    for t in range(3 - len(task["request_id"])):
                        task["request_id"] = '0' + task["request_id"]
                self.write_log('*'*40 + '\n' + str(task) + '\n' + '*'*40, str(index), "DEBUG")
                task_index = self.api_list.index(task)
                post_data = task["data"]
                # 发送请求
                if int(task["method"]) == 0:                                             # post请求
                    self.write_log(json.dumps(task["data"], ensure_ascii=False), str(index), "DEBUG")
                    post_data = self.get_data(json.dumps(task["data"],  ensure_ascii=False), task_index)
                    self.write_log('post_data' + str(post_data) + '\n\n', str(index), "DEBUG")
                    try:
                        response = requests.post(url = task["url"], data = post_data.encode('utf-8'), headers=self.headers, cookies = self.cookies)
                        self.cookies = response.cookies
                        if index == 0:
                            response_data["id"] = task["id"]
                            response_data["status_code"] = str(response.status_code)
                            response_data["url"] = task["url"]
                            response_data["name"] = task["name"]
                            response_data["method"] = "POST"
                            response_data["from_data"] = post_data
                            response_data["error_info"] = "  "
                            response_data["promising_results"] = task["promising_results"]
                            response_data["request_id"] = task["request_id"]
                        if response.status_code != 200:
                            if index == 0:
                                response_data["response"] = ""
                                self.response_list.append(response_data)
                                self.api_list[task_index]["response"] = ""
                            break
                        else:
                            if index == 0:
                                response_data["response"] = response.text
                                self.response_list.append(response_data)
                                try:
                                    response = json.loads(response.text)
                                    print('response ' + '*'*40 + '\n', response, '\n' + '*'*40, task_index)
                                    self.api_list[task_index]["response"] = response
                                except:
                                    self.api_list[task_index]["response"] = response.text
                    except Exception as error_info:
                        print("Exception--->> ", str(error_info))
                        if index == 0:
                            response_data["id"] = task["id"]
                            response_data["status_code"] = 'error'
                            response_data["url"] = task["url"]
                            response_data["method"] = "POST"
                            response_data["from_data"] = post_data
                            response_data["error_info"] = str(error_info)
                            response_data["name"] = task["name"]
                            response_data["response"] = ""
                            response_data["promising_results"] = task["promising_results"]
                            response_data["request_id"] = task["request_id"]
                            self.response_list.append(response_data)
                            self.api_list[task_index]["response"] = ""
                        self.write_log(str(error_info) + '\n\n', str(index), "DEBUG")
                        break
                else:
                    try:
                        payload =self.get_data(str(task["data"]), task_index)
                        self.write_log(str(payload) + '\n\n', str(index), "DEBUG")
                        if len(payload) > 0:
                            response = requests.get(task["url"], params=payload, headers=self.headers, cookies = self.cookies)
                        else:
                            response = requests.get(task["url"], headers=self.headers, cookies = self.cookies)
                        self.cookies = response.cookies
                        print(response.url)
                        if index == 0:
                            response_data["id"] = task["id"]
                            response_data["status_code"] = str(response.status_code)
                            response_data["url"] = task["url"]
                            response_data["name"] = task["name"]
                            response_data["method"] = "GET"
                            response_data["from_data"] = payload
                            response_data["error_info"] = "成功"
                            response_data["promising_results"] = task["promising_results"]
                            response_data["request_id"] = task["request_id"]
                        if response.status_code != 200:
                            if index == 0:
                                response_data["response"] = ""
                                self.response_list.append(response_data)
                                self.api_list[task_index]["response"] = ""
                            break
                        else:
                            if index == 0:
                                response_data["response"] = response.text
                                try:
                                    data = json.loads(response.text)
                                    print('response ' + '*'*40 + '\n', data, '\n' + '*'*40, task_index)
                                    self.api_list[task_index]["response"] = data
                                except:
                                    self.api_list[task_index]["response"] = response.text
                                self.response_list.append(response_data)
                    except Exception as error_info:
                        print("Exception--->> ", str(error_info))
                        if index == 0:
                            response_data["id"] = task["id"]
                            response_data["status_code"] = 'error'
                            response_data["url"] = task["url"]
                            response_data["method"] = "GET"
                            response_data["from_data"] = payload
                            response_data["error_info"] = str(error_info)
                            response_data["name"] = task["name"]
                            response_data["response"] = ""
                            response_data["promising_results"] = task["promising_results"]
                            response_data["request_id"] = task["request_id"]
                            self.response_list.append(response_data)
                            self.api_list[task_index]["response"] = ""
                        self.write_log(str(error_info) + '\n\n', str(index), "DEBUG")
                        break
            end_stamp = time.time()*1000
            wait_time = end_stamp - start_stamp
            if index == 0:
                if wait_time > self.over_time:
                    self.overtime_count += 1
                if self.max_time < wait_time:
                    self.max_time = wait_time
                self.use_time_info.append(wait_time)
            count += 1
        if index == 0 and self.task_name != 'task_api_test':
            self.write_csv()
        if index == 0 and int(self.test_times) > 1:
            self.write_log("creat pdf", str(index), "DEBUG")
            self.creat_pdf()
        else:
            self.write_log("not creat pdf", str(index), "DEBUG")
        print("end thread: ", index)
        time.sleep(0.3)

    # 开始线程
    def start(self):
        threads = []
        self.use_time_info = []
        for index in range(0, self.thread_num):
            th = threading.Thread(target=self.task_work, args=(index,))
            threads.append(th)

        for th in threads:
            th.start()

        for th in threads:
            threading.Thread.join(th)
        os.chdir(self.path)
        print("任务结束")

    # 数据写入excel
    def write_csv(self):
        for index in range(len(self.response_list)):
            info = self.response_list[index]
            if index == 0:
                self.sheet.write_merge(self.nrows, self.nrows + len(self.response_list) - 1, 0, 0, self.task_name, self.style3)
            self.sheet.write(self.nrows + index, 1, info['request_id'], self.style0)
            self.sheet.write(self.nrows + index, 2, info['name'], self.style5)
            self.sheet.write(self.nrows + index, 3, info["url"], self.style0)
            self.sheet.write(self.nrows + index, 4, info["method"], self.style0)
            self.sheet.write(self.nrows + index, 5, info["status_code"], self.style0)
            self.sheet.write(self.nrows + index, 6, info["from_data"], self.style0)            
            self.sheet.write(self.nrows + index, 7, info["response"], self.style0)
            self.sheet.write(self.nrows + index, 8, info["promising_results"], self.style0)
            print(info["promising_results"])
            if info["response"].find(info["promising_results"]) != -1:
                self.sheet.write(self.nrows + index, 9, "通过", self.style2)
            else:
                self.sheet.write(self.nrows + index, 9, "不通过", self.style4)
                self.count += 1
            self.sheet.write(self.nrows + index, 10, info["error_info"], self.style0)
        total_num = self.nrows+len(self.response_list)-1
        str1 = str(total_num)
        str2 = str(self.count)
        percent = ((total_num - self.count)/total_num) *100
        percent = ("%.2f" % percent)
        print(percent)
        str3 = str(percent) + "%"
        self.sheet.write(total_num + 3, 0, "", self.style6)
        self.sheet.write(total_num + 3, 1, "", self.style6)
        self.sheet.write(total_num + 3, 2, "", self.style6)
        self.sheet.write(total_num + 3, 3, "", self.style6)
        self.sheet.write(total_num + 3, 4, "", self.style6)
        self.sheet.write(total_num + 3, 5, "", self.style6)
        self.sheet.write(total_num + 3, 6, "", self.style6)
        self.sheet.write(total_num + 3, 7, "测试用例总数：" + str1, self.style6)
        self.sheet.write(total_num + 3, 8, "未通过个数：" + str2, self.style6)
        self.sheet.write(total_num + 3, 9, "通过率：" + str3, self.style6)
        self.workbook.save(self.task_name + "-" + self.current_time+".xls")

    # 创建PDF
    def creat_pdf(self):
        fig = plt.figure(1)                                                   # 创建图表1
        ax1 = plt.subplot(111)                                                # 创建子图1
        print(self.use_time_info)
        x1 = [index for index in range(0, len(self.use_time_info))]
        y1 = self.use_time_info
        plt.sca(ax1)
        plt.plot(x1, y1, 'r')
        plt.ylabel('y time (ms)')
        plt.title(self.task_name)
        plt.xlabel('x - - time > ' + str(self.over_time) + 'ms : ' + str(self.overtime_count) + '  max_time: ' + str(self.max_time) + 'ms')
        fig.savefig(self.task_name + str(time.time()) + ".pdf")
        plt.cla()
        print("creat pdf end")

    # 写入日志文件
    def write_log(self, message, thread_id, log_level):
        message = str(message)
        time_stamp = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        data = '[' + str(thread_id) + ']  ' + time_stamp +  '  [' + log_level + ']   ' + message + '\n'
        if self.log_levels.index(log_level) < self.log_levels.index(self.log_level):
            return
        print(data)
        self.file_lock.acquire()
        old_path = os.getcwd()
        new_path = os.path.join(old_path, "log")
        if not os.path.exists(new_path):
            os.mkdir(new_path)
        os.chdir(new_path)
        path = os.path.join(new_path, self.task_name+'.log')
        with open(path, 'a') as file:
            file.write(data)
        os.chdir(old_path)
        self.file_lock.release()


class Main:
    def __init__(self):
        self.task_list = []
        self.api_info = []
        self.select_api_id = -1
        self.path = os.getcwd()
        self.refresh_id = 0
        self.task_response_list = []
        self.log_path = "log"
        self.config_path = 'config'
        self.taks_start_flag = False
        self.config_file_list = []                                                       # 存储任务文件
        self.task_status = {0:'停止', 1:'等待', 2:'运行', 3:'完成'}
        self.thread_quit =False
        self.run_task_list = []                                                          # 任务运行列表
        self.api_num = 0                                                                 # api列表中的api数
        self.task_num = 0                                                                # task列表中的任务数
        self.quit = False                                                                # 是否停止任务标志
        self.threads_class = []                                                          # 记录执行的类
        self.run_task_list_lock = threading.Lock()
        self.method =0                                                                   # api的请求方法 0 是post 1 是get
        self.edit_id = 0                                                                 # 修改的api的id
        self.debug = False                                                               # 是否开启调试打印
        self.root = Tk()                                                                 # 建立主窗口
        self.background = '#212326'                                                      # 背景颜色
        self.foreground = '#3BAEE8'
        self.font = ('宋体', 12)
        self.title = ""                                                                  # 窗口标题
        self.size = ""                                                                   # 窗口大小
        self.width =1000                                                                 # 窗口宽
        self.height = 600                                                                # 窗口高
        self.root.resizable(False, False)                                                # 禁止改变窗口大小
        self.url_value = StringVar()
        self.task_name_value = StringVar()
        self.over_time_value = StringVar()
        self.test_times_value = StringVar()
        self.thread_num_value = StringVar()
        self.request_name_value = StringVar()
        self.request_result_value = StringVar()
        self.request_id_value = StringVar()
        self.cv_left = Canvas(self.root, height=600, width=1000, bg=self.background)
        self.cv_task = Canvas(self.root, height=450, width=1000, scrollregion=(0,0,210,2100), bg=self.background)
        self.api_list = Listbox(self.root, height=23, width = 77, bg= self.background, fg = self.foreground, font=("宋体, 14"))
        self.scrollbar = Scrollbar(self.root,orient='vertical')
        self.api_list["yscrollcommand"] = self.scrollbar.set
        self.scrollbar["command"]=self.api_list.yview
        self.api_list.bind('<Double-Button-1>', self.show_api_info_and_edit)
        self.api_list.bind('<Button-3>', self.popupmenu)

        self.list_task_list = Listbox(self.root, height=27, width = 28, bg= self.background, fg = self.foreground, font=("宋体, 14"))
        self.scrollbar_task = Scrollbar(self.root,orient='vertical')
        self.list_task_list["yscrollcommand"] = self.scrollbar_task.set
        self.scrollbar_task["command"]=self.list_task_list.yview
        self.list_task_list.bind('<Double-Button-1>', self.show_task_response_info)

        self.list_request_list = Listbox(self.root, height=26, width = 48, bg= self.background, fg = self.foreground, font=("宋体, 14"))
        self.scrollbar_request = Scrollbar(self.root,orient='vertical')
        self.list_request_list["yscrollcommand"] = self.scrollbar_request.set
        self.scrollbar_request["command"]=self.list_request_list.yview
        self.scrollbar_request_x = Scrollbar(self.root,orient='horizontal')
        self.list_request_list["xscrollcommand"] = self.scrollbar_request_x.set
        self.scrollbar_request_x["command"]=self.list_request_list.xview
        self.list_request_list.bind('<Double-Button-1>', self.show_api_request_info)

        self.button_creat_task = Button(self.root, text="新建测试任务", width=25, command = self.show_add_task)
        self.button_task_list = Button(self.root,text = "任务列表", width=25, command=lambda :self.show_task_list(-1))
        self.button_api_test = Button(self.root,text = "API测试", width=25, command=self.add_api_test)
        print(self.button_task_list.keys())

        self.labe_task_name = Label(self.root, width=20, text="任务名称:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_task_name = Entry(self.root, width=30, textvariable = self.task_name_value)
        self.labe_over_time = Label(self.root, width=20, text="超时时间:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_over_time = Entry(self.root, width=30, textvariable = self.over_time_value)
        self.labe_test_times = Label(self.root, width=20, text="测试次数:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_test_times = Entry(self.root, width=30, textvariable = self.test_times_value)
        self.labe_thread_num = Label(self.root, width=20, text="线程数量:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_thread_num = Entry(self.root, width=30, textvariable = self.thread_num_value)

        self.button_add = Button(self.root, text="添加请求", width=8, command = self.add_api)
        self.button_read = Button(self.root, text="打开任务", width=8, command = self.read_task)
        self.button_save = Button(self.root, text="保存任务", width=8, command = self.write_task)
        self.button_save_task = Button(self.root, text="添加到任务列表", width=14, command = self.save_task)
        self.button_show_request = Button(self.root, text="刷新列表", width=8, command=lambda : self.refresh_request_list(self.refresh_id))
        self.label_url = Label(self.root, width=20, text="请求地址:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_url = Entry(self.root, width=77, textvariable = self.url_value)
        self.label_request_name = Label(self.root, width=20, text="请求说明:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_request_name = Entry(self.root, width=77, textvariable = self.request_name_value)
        self.method_value = IntVar()
        self.method_value.set(0)
        self.label_method = Label(self.root, width=20, text="请求方式:", foreground = self.foreground, background=self.background, font=self.font)
        self.radio_button_post = Radiobutton(self.root,variable = self.method_value,text = 'POST',value = 0, command=self.select_method_post)
        self.radio_button_get = Radiobutton(self.root,variable = self.method_value,text = 'GET',value = 1, command=self.select_method_get)
        self.label_input = Label(self.root, width=20, text="添加参数:", foreground = self.foreground, background=self.background, font=self.font)
        self.label_output = Label(self.root, width=20, text="返回数据:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_result = Entry(self.root, width=77, textvariable = self.request_result_value )
        self.label_result = Label(self.root, width=10, text="预期结果:", foreground = self.foreground, background=self.background, font=self.font)
        self.entry_id = Entry(self.root, width=77, textvariable = self.request_id_value )
        self.label_id = Label(self.root, width=10, text="请求ID:", foreground = self.foreground, background=self.background, font=self.font)
        self.text_input = Text(self.root, width=54, height=10, font=("宋体",14))
        self.text_output = Text(self.root, width=54, height=10, font=("宋体",14))
        self.button_add_api_test_ok = Button(self.root, width=20, text="发送", command=self.add_api_test_ok)
        self.button_add_api_ok = Button(self.root, width=10, text="确定", command=self.add_api_ok)
        self.button_add_api_cancle = Button(self.root, width=10, text="取消", command=self.add_api_cancle)
        self.button_add_api_back = Button(self.root, width=10, text="确定", command= lambda : self.show_api_list(self.edit_id))
        
        self.button_task_start = Button(self.root, text="开始任务", width=8, command = self.task_start)
        self.button_task_pause = Button(self.root, text="停止任务", width=8, command = self.task_pause)
        self.button_task_clear = Button(self.root, text="清空任务", width=8, command = self.task_clear)

        self.menu = Menu(self.root, tearoff=0)
        self.menu.add_command(label="删除", command=self.add_api_delete)
        self.menu.add_command(label="插入", command=self.insert_api)
        self.menu.add_command(label="向上", command=self.up_api)
        self.menu.add_command(label="向下",command=self.down_api)
        self.init_config()
        self.init_window()
        self.run_start()
        self.root.protocol("WM_DELETE_WINDOW", self.sys_exit)
        self.root.mainloop()

    def init_config(self):
        try:
            self.config_path = os.path.join(self.path, self.config_path)
            if not os.path.exists(self.config_path):
                os.mkdir(self.config_path)
            self.log_path = os.path.join(self.config_path, self.log_path)
            if not os.path.exists(self.log_path):
                os.mkdir(self.log_path)
        except Exception as error:
            print(error)

    def sys_exit(self):
        print ("game over")
        for test_work in self.threads_class:
            test_work.quit = True              # 结束子线程
        self.thread_quit = True
        try:
            self.root.destroy()
        finally:
            threading.Thread.join(self.th)
            print("回收了任务线程")

    def run_start(self):
        self.th = threading.Thread(target = self.run_thread, args = (self.run_task_list,))
        self.th.start()

    def run_thread(self, list):                        # 任务线程
        while True:
            flag = False
            task = {}
            time.sleep(0.2)
            print("thread is runing")
            if self.thread_quit:                       # 退出程序结束线程
                print("收到线程退出")
                for test_work in self.threads_class:
                    test_work.quit = True              # 结束子线程
                break
            if len(self.run_task_list) > 0:
                self.run_task_list_lock.acquire()
                for index in range(len(self.run_task_list)):
                    if self.run_task_list[index]["status"] == 1 and self.taks_start_flag:
                        task = self.run_task_list[index]
                        flag = True
                        print(len(self.run_task_list))
                        break
                self.run_task_list_lock.release()
                if not flag:
                    if self.taks_start_flag:
                        self.taks_start_flag = False
                        self.cv_left.create_window(215,15,anchor=NW, window=self.button_task_start)
                        self.show_task_list(-1)
                        self.refresh_request_list(0)    # 显示第一个任务的请求值
                    continue
                test_work = Test(task)
                self.threads_class.append(test_work)
                self.task_list[index]["status"] = 2
                self.run_task_list[index]["status"] = 2
                self.show_task_list(-1)
                test_work.start()
                if self.thread_quit:
                    print("线程退出")
                    break
                if len(self.task_list) > 0:
                    self.task_list[index]["status"] = 3
                self.run_task_list[index]["status"] = 3
                print(str(self.task_list[index]["task_id"]) + "  任务结束")
                self.show_task_list(-1)

    def init_window(self):
        self.title = "接口测试程序"
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        self.size = '%dx%d+%d+%d' % (self.width, self.height, (screenwidth - self.width)/2, (screenheight - self.height)/2)
        self.root.wm_title(self.title)
        self.root.geometry(self.size)
        self.cv_left.pack(side=LEFT, fill=BOTH)
        self.cv_left.create_window(10, 15, anchor=NW, window=self.button_creat_task)
        self.cv_left.create_window(10, 55, anchor=NW, window=self.button_task_list)
        self.cv_left.create_window(10, 95, anchor=NW, window=self.button_api_test)
        self.cv_left.create_line(205,0,205,600,width=5, fill=self.foreground)
        self.show_add_task()
        

    def show_add_task(self):                                  # 新建任务的回调函数
        self.url_value.set("")
        self.request_name_value.set("")
        self.task_name_value.set("")
        self.over_time_value.set("")
        self.test_times_value.set("")
        self.thread_num_value.set("")
        self.request_result_value.set("")
        self.request_id_value.set("")
        self.api_info = []
        self.api_num = 0
        if len(self.cv_left.find_all()) >3:
            for index in self.cv_task.find_all():
                self.cv_task.delete(index)
            for index in self.cv_left.find_all()[4::]:
                self.cv_left.delete(index)
        self.cv_left.create_window(230,15, anchor=NW, window=self.labe_task_name)
        self.cv_left.create_window(320,15, anchor=NW, window=self.entry_task_name)
        self.cv_left.create_window(560,15, anchor=NW, window=self.labe_over_time)
        self.cv_left.create_window(650,15, anchor=NW, window=self.entry_over_time)
        self.cv_left.create_window(230,45, anchor=NW, window=self.labe_test_times)
        self.cv_left.create_window(320,45, anchor=NW, window=self.entry_test_times)
        self.cv_left.create_window(560,45, anchor=NW, window=self.labe_thread_num)
        self.cv_left.create_window(650,45, anchor=NW, window=self.entry_thread_num)
        self.cv_left.create_line(205,98,1000,98,width=5, fill=self.foreground)
        self.cv_left.create_window(220,105, anchor=NW, window=self.button_add)
        self.cv_left.create_window(300,105, anchor=NW, window=self.button_save)
        self.cv_left.create_window(380,105, anchor=NW, window=self.button_read)
        self.cv_left.create_window(460,105, anchor=NW, window=self.button_save_task)
        self.cv_left.create_line(205,140,1000,140,width=5, fill=self.foreground)
        self.cv_left.create_window(210,145,anchor=NW, window=self.cv_task)
        self.show_api_list(-1)


    def select_method_post(self):
        self.method = 0

    def select_method_get(self):
        self.method= 1

    # 显示新建api的页面
    def add_api(self):
        self.method = 0
        self.method_value.set(0)
        self.url_value.set("")
        self.request_result_value.set("")
        self.request_id_value.set("")
        self.text_input.delete(0.0, END)
        # 清空画布上的组件
        for index in self.cv_task.find_all():
            self.cv_task.delete(index)
        self.cv_task.create_window(20,15,anchor=NW, window=self.label_id)
        self.cv_task.create_window(110,15,anchor=NW, window=self.entry_id)
        self.cv_task.create_window(20,45,anchor=NW, window=self.label_request_name)
        self.cv_task.create_window(110,45,anchor=NW, window=self.entry_request_name)
        self.cv_task.create_window(20,75,anchor=NW, window=self.label_url)
        self.cv_task.create_window(110,75,anchor=NW, window=self.entry_url)
        self.cv_task.create_window(20,115,anchor=NW, window=self.label_result)
        self.cv_task.create_window(110,115,anchor=NW, window=self.entry_result)        
        self.cv_task.create_window(20,155,anchor=NW, window=self.label_method)
        self.cv_task.create_window(110,155,anchor=NW, window=self.radio_button_post)
        self.cv_task.create_window(180,155,anchor=NW, window=self.radio_button_get)
        self.cv_task.create_window(20,195,anchor=NW, window=self.label_input)
        self.cv_task.create_window(110,195,anchor=NW, window=self.text_input)
        self.cv_task.create_window(480,400,anchor=NW, window=self.button_add_api_ok)
        self.cv_task.create_window(570,400,anchor=NW, window=self.button_add_api_cancle)

    def add_api_test(self):
        self.method = 0
        self.method_value.set(0)
        self.url_value.set("")
        self.text_output.delete(0.0, END)
        self.text_input.delete(0.0, END)
        # 清空画布上的组件
        for index in self.cv_task.find_all():
                self.cv_task.delete(index)
        for index in self.cv_left.find_all()[4::]:
            self.cv_left.delete(index)
        self.cv_left.create_window(220,15, anchor=NW, window=self.label_url)
        self.cv_left.create_window(310,15, anchor=NW, window=self.entry_url)
        self.cv_left.create_window(220,45, anchor=NW, window=self.label_method)
        self.cv_left.create_window(310,45, anchor=NW, window=self.radio_button_post)
        self.cv_left.create_window(390,45, anchor=NW, window=self.radio_button_get)
        self.cv_left.create_window(220,75, anchor=NW, window=self.label_input)
        self.cv_left.create_window(310,75,anchor=NW, window=self.text_input)
        self.cv_left.create_window(220,300, anchor=NW, window=self.label_output)
        self.cv_left.create_window(310,300,anchor=NW, window=self.text_output)
        self.cv_left.create_window(700, 510, anchor=NW, window=self.button_add_api_test_ok)

    def add_api_test_ok(self):
        api_data = {}
        task_api_test = {}
        api_list = []
        self.text_output.delete(0.0, END)
        api_data["url"] = self.entry_url.get()
        api_data["name"] = 'api_test'
        api_data["method"] = self.method
        api_data["request_id"] = "0"
        api_data["promising_results"] = "200"
        api_data["id"] = "0"
        input_data = self.text_input.get(0.0,END).strip()
        try:
            if self.method == 0:
                api_data["data"] =  json.loads(input_data)
            else:
                api_data["data"] = input_data
        except Exception as error_info:
            showinfo(title='错误提示', message="api传入参数格式错误, post方式仅支持json数据")
            print(error_info)
            return
        api_list.append(api_data)
        task_api_test["task_name"] = 'task_api_test'
        task_api_test["over_time"] = 20
        task_api_test["thread_num"] = 1
        task_api_test["api_list"] = api_list
        task_api_test["creat_pdf"] = False
        task_api_test["test_times"] = 1

        api_test_class = Test(task_api_test)
        api_test_class.start()
        self.text_output.insert(END, 'status_code: ' + api_test_class.response_list[0]["status_code"] + '\n\n')
        self.text_output.insert(END, 'response: \n\t' + api_test_class.response_list[0]["response"] + '\n\n')
        self.text_output.insert(END, 'error_info: \n\t' + api_test_class.response_list[0]["error_info"] + '\n')


    def add_api_ok(self):                                               # 增加api确定按钮回调函数
        api_data = {}
        api_data["url"] = self.entry_url.get().strip()
        if len(self.entry_url.get().strip()) == 0:
            showinfo(title='错误提示', message="url不能为空")
            return
        if len(self.entry_request_name.get().strip()) == 0:
            showinfo(title='错误提示', message="api名称不能为空")
            return
        api_data["name"] = self.entry_request_name.get().strip()
        api_data["method"] = self.method
        api_data["id"] = self.api_num
        api_data["promising_results"] = self.entry_result.get().strip()
        api_data["request_id"] = self.entry_id.get().strip()
        input_data = self.text_input.get(0.0,END).strip()
        print(input_data)
        try:
            if self.method == 0:
                api_data["data"] =  json.loads(input_data)
            else:
                api_data['data'] = input_data
        except Exception as error_info:
            showinfo(title='错误提示', message="api传入参数格式错误, post方式仅支持json数据")
            print(error_info)
            return

        self.api_info.append(api_data)
        self.show_api_list(self.api_num)
        self.api_num += 1

    def add_api_cancle(self):
        self.select_api_id = -1
        self.show_api_list(-1)

    def add_api_delete(self):
        if self.select_api_id == -1:
            showinfo(title='提示', message="没有选中要删除的请求")
            return 0
        else:
            self.api_info.pop(self.select_api_id)
            self.select_api_id = -1
            self.api_list.delete(0,END)
            for index in range(len(self.api_info)):
                self.api_list.insert(END, "API-" + str(index)+ "-" + self.api_info[index]["url"])

    def up_api(self):
        if self.select_api_id == -1:
            showinfo(title='提示', message="没有选中要调整顺序的请求")
            return 0
        elif self.select_api_id == 0:
            showinfo(title='提示', message="已经在最顶端")
            return 0
        else:
            tmp = self.api_info[self.select_api_id - 1]
            tmp["id"] = self.select_api_id
            self.api_info[self.select_api_id]["id"] = self.select_api_id - 1
            self.api_info[self.select_api_id - 1] = self.api_info[self.select_api_id]
            self.api_info[self.select_api_id] = tmp
            self.select_api_id = -1
            self.api_list.delete(0,END)
            for index in range(len(self.api_info)):
                self.api_list.insert(END, "API-" + str(index)+ "-" + self.api_info[index]["url"])

    def down_api(self):
        if self.select_api_id == -1:
            showinfo(title='提示', message="没有选中要调整顺序的请求")
            return 0
        elif self.select_api_id == len(self.api_info) - 1:
            showinfo(title='提示', message="已经在最底端")
            return 0
        else:
            tmp = self.api_info[self.select_api_id + 1]
            tmp["id"] = self.select_api_id
            self.api_info[self.select_api_id]["id"] = self.select_api_id + 1
            self.api_info[self.select_api_id + 1] = self.api_info[self.select_api_id]
            self.api_info[self.select_api_id] = tmp
            self.select_api_id = -1
            self.api_list.delete(0,END)
            for index in range(len(self.api_info)):
                self.api_list.insert(END, "API-" + str(index)+ "-" + self.api_info[index]["url"])

    def insert_api(self):
        if self.select_api_id == -1:
            showinfo(title='提示', message="没有选中要插入的位置")
            return 0
        else:
            self.add_api()


    def show_api_list(self, info_id):
        print("show_api_list:",info_id)
        if info_id != -1:
            # 保存原先的数据
            self.api_info[info_id]["url"] = self.entry_url.get().strip()
            if len(self.entry_url.get().strip()) == 0:
                showinfo(title='错误提示', message="url不能为空--")
                return
            if len(self.entry_request_name.get().strip()) == 0:
                showinfo(title='错误提示', message="api名称不能为空")
                return
            self.api_info[info_id]["name"] = self.entry_request_name.get().strip()
            self.api_info[info_id]["method"] = self.method
            input_data = self.text_input.get(0.0,END).strip()
            self.api_info[info_id]["promising_results"] = self.entry_result.get().strip()
            self.api_info[info_id]["request_id"] = self.entry_id.get().strip()
            print(input_data)
            try:
                if self.method == 0:
                    self.api_info[info_id]["data"] =  json.loads(input_data)
                else:
                    self.api_info[info_id]['data'] = input_data
            except Exception as error_info:
                showinfo(title='错误提示', message="api传入参数格式错误")
                print(error_info)
                return
        # 清空数据
        self.request_id_value.set("")
        self.url_value.set("")
        self.request_result_value.set("")
        self.request_name_value.set("")
        self.text_input.delete(0.0,END)

        if self.select_api_id != -1:                   # 处理插入的api
            tmp = self.api_info[-1]
            tmp["id"] = self.select_api_id + 1
            for index in range(self.select_api_id + 1, len(self.api_info))[::-1]:
                print("index:", index)
                if index == self.select_api_id + 1:
                     self.api_info[index] = tmp
                self.api_info[index -1 ]["id"] = index
                self.api_info[index] = self.api_info[index - 1]

            self.api_info[self.select_api_id]["id"] = self.api_info[-1]["id"]
            self.api_info[self.select_api_id + 1] = self.api_info[self.select_api_id]
            self.api_info[self.select_api_id] = tmp
            self.select_api_id = -1

        # 清空画布上的组件
        for index in self.cv_task.find_all():
            self.cv_task.delete(index)

        # 显示现在的api列表
        self.api_list.delete(0,END)
        for index in range(len(self.api_info)):
            self.api_list.insert(END, "API-" + str(index)+ "-" + self.api_info[index]["url"])
        self.cv_task.create_window(0,0, anchor=NW, window=self.api_list)
        self.cv_task.create_window(772,0 , anchor=NW, window=self.scrollbar, height=453)

# 
    def show_api_info_and_edit(self, event):
        if len(self.api_list.curselection()) == 0:
            return
        info_id = self.api_list.curselection()[0]
        print("*"*10, info_id)
        info = self.api_info[info_id]
        for index in self.cv_task.find_all():
            self.cv_task.delete(index)
        self.edit_id = int(info_id)
        self.url_value.set(str(info["url"]))
        self.request_name_value.set(info["name"])
        self.method_value.set(int(info["method"]))
        if "promising_results" in info:
            self.request_result_value.set(info["promising_results"])
        else:
            self.request_result_value.set("")
        if "request_id" in info:
            self.request_id_value.set((info["request_id"]))
        else:
            self.request_id_value.set("")
        self.method = int(info["method"])
        print(info["data"])
        if int(info["method"]) == 0:
            self.text_input.insert(END, json.dumps(info["data"], ensure_ascii=False))
        else:
            if len(info["data"]) > 0:
                self.text_input.insert(END, info["data"])
        self.cv_task.config(width=785, height=450)
        self.cv_task.create_window(20,15,anchor=NW, window=self.label_id)
        self.cv_task.create_window(110,15,anchor=NW, window=self.entry_id)
        self.cv_task.create_window(20,45,anchor=NW, window=self.label_request_name)
        self.cv_task.create_window(110,45,anchor=NW, window=self.entry_request_name)
        self.cv_task.create_window(20,75,anchor=NW, window=self.label_url)
        self.cv_task.create_window(110,75,anchor=NW, window=self.entry_url)
        self.cv_task.create_window(20,115,anchor=NW, window=self.label_result)
        self.cv_task.create_window(110,115,anchor=NW, window=self.entry_result)
        self.cv_task.create_window(20,195,anchor=NW, window=self.label_input)
        self.cv_task.create_window(20,155,anchor=NW, window=self.label_method)
        self.cv_task.create_window(110,155,anchor=NW, window=self.radio_button_post)
        self.cv_task.create_window(190,155,anchor=NW, window=self.radio_button_get)
        self.cv_task.create_window(110,195,anchor=NW, window=self.text_input)
        self.cv_task.create_window(570,400,anchor=NW, window=self.button_add_api_back)

    def show_task_list(self, info_id):
        info_id = int(info_id)
        if int(info_id) != -1:
            self.task_list[info_id]["task_name"] = self.entry_task_name.get().strip().replace(r'/', "_")
            if len(self.entry_task_name.get().strip()) == 0:
                showinfo(title='错误提示', message="任务名称不能为空")
                return

            try:
                self.task_list[info_id]["thread_num"] = int(self.entry_thread_num.get())
                if self.task_list[info_id]["thread_num"] > 2000:
                    showinfo(title='错误提示', message="线程数最大为2000")
                    return
            except Exception as error_info:
                print(error_info)
                showinfo(title='错误提示', message="线程数错误")
                return

            try:
                self.task_list[info_id]["over_time"] = int(self.entry_over_time.get())
            except Exception as error_info:
                print(error_info)
                showinfo(title='错误提示', message="超时设置错误")
                return

            try:
                self.task_list[info_id]["test_times"] = int(self.entry_test_times.get())
            except Exception as error_info:
                print(error_info)
                showinfo(title='错误提示', message="测试次数设置错误")
                return

            if len(self.api_info) == 0:
                showinfo(title='错误提示', message="没有可执行的api请求")
                return
            else:
                self.task_list[info_id]["api_list"] = self.api_info
                self.task_list[info_id]["creat_pdf"] = False
                self.task_list[info_id]["status"] = 0

        # 清除右边的模块
        for index in self.cv_task.find_all():
            self.cv_task.delete(index)
            print("task"+ str(index))
        print("show_task_list---------", self.cv_left.find_all())
        for index in self.cv_left.find_all()[4::]:
            self.cv_left.delete(index)
            print("api"+ str(index))

        self.list_task_list.delete(0,END)
        self.list_request_list.delete(0,END)
        for index in range(len(self.task_list)):
            task = self.task_list[index]
            self.list_task_list.insert(END, 'TASK-' + str(task["task_id"]) + '.'+ self.task_status[task["status"]] + ' ' + task["task_name"])
        self.cv_left.create_line(205,3,1000,3,width=5, fill=self.foreground)
        self.cv_left.create_line(205,50,1000,50,width=5, fill=self.foreground)
        self.cv_left.create_line(490,0,490,50,width=16, fill=self.foreground)
        self.cv_left.create_window(206,55, anchor=NW, window=self.list_task_list)
        self.cv_left.create_window(482,55 , anchor=NW, window=self.scrollbar_task, height=550)
        self.cv_left.create_window(500,55, anchor=NW, window=self.list_request_list)
        self.cv_left.create_window(984,55 , anchor=NW, window=self.scrollbar_request, height=550)
        self.cv_left.create_window(500,580 , anchor=NW, window=self.scrollbar_request_x, width=484)
        if self.taks_start_flag:
            self.cv_left.create_window(215,15,anchor=NW, window=self.button_task_pause)
        else:
            self.cv_left.create_window(215,15,anchor=NW, window=self.button_task_start)
        self.cv_left.create_window(295,15,anchor=NW, window=self.button_task_clear)
        self.cv_left.create_window(505,15,anchor=NW, window=self.button_show_request)



    def show_task_response_info(self, event):
        if len(self.list_task_list.curselection()) == 0:
            return
        index = self.list_task_list.curselection()[0]
        self.refresh_id = index
        self.task_response_list = []
        self.list_request_list.delete(0, END)
        if len(self.threads_class) == 0:
            return
        elif len(self.threads_class) - 1 < index:
            return
        self.task_response_list = self.threads_class[index].response_list
        for index in range(len(self.task_response_list)):
            self.list_request_list.insert(END, 'API-' + str(self.task_response_list[index]["id"]) +"-[" + self.task_response_list[index]["status_code"] + ']-' + self.task_response_list[index]["name"] )

    def refresh_request_list(self, index):
        self.task_response_list = []
        self.list_request_list.delete(0, END)
        if len(self.threads_class) == 0 or self.refresh_id == -1:
            return
        self.task_response_list = self.threads_class[index].response_list
        for index in range(len(self.task_response_list)):
            self.list_request_list.insert(END, 'API-' + str(self.task_response_list[index]["id"]) +"-[" + self.task_response_list[index]["status_code"] + ']-' + self.task_response_list[index]["name"] )
        

    def write_task(self):                                         # 将任务保存到文件
        task_info = {}
        task_info["task_name"] = self.entry_task_name.get().strip().replace(r'/', "_")
        if len(self.entry_task_name.get().strip()) == 0:
            showinfo(title='错误提示', message="任务名称不能为空")
            return


        try:
            task_info["thread_num"] = int(self.entry_thread_num.get())
            if task_info["thread_num"] > 2000:
                showinfo(title='错误提示', message="线程数最大为2000")
                return
        except Exception as error_info:
            print(error_info)
            showinfo(title='错误提示', message="线程数错误")
            return

        try:
            task_info["over_time"] = int(self.entry_over_time.get())
        except Exception as error_info:
            print(error_info)
            showinfo(title='错误提示', message="超时设置错误")
            return

        try:
            task_info["test_times"] = int(self.entry_test_times.get())
        except Exception as error_info:
            print(error_info)
            showinfo(title='错误提示', message="测试次数设置错误")
            return

        if len(self.api_info) == 0:
            showinfo(title='错误提示', message="没有可执行的api请求")
            return
        else:
            task_info["api_list"] = self.api_info
            task_info["creat_pdf"] = False
            task_info["status"] = 0

        width = 250
        height = 150
        self.save_file_window = Toplevel()
        self.save_file_window.resizable(False, False)
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        self.save_file_window.wm_title("保存文件")
        self.save_file_window.geometry(size) 
        self.save_file_window["bg"] = self.background
        self.label_save_file_name = Label(self.save_file_window, text="文件名称:", background=self.background, foreground = self.foreground)
        self.entry_save_file_name = Entry(self.save_file_window, width=22)
        self.button_save_file_name = Button(self.save_file_window, text="保存", command = lambda : self.write_file(task_info))
        self.label_save_file_name.grid(row=0, padx=10, pady=10, sticky=W)
        self.entry_save_file_name.grid(row=0, column=1, pady=10, sticky=E)
        self.button_save_file_name.grid(row=1, column=1, pady=10, ipadx=5, stick=E)

    def write_file(self, task_info):
        print("save file")
        file_name = self.entry_save_file_name.get()
        os.chdir(self.config_path)
        if os.path.splitext(file_name)[1] != ".txt":
            showinfo(title='错误提示', message="保存文件名是txt")
        with open(file_name, 'w') as file:
            file.write(json.dumps(task_info, ensure_ascii =False))
        self.save_file_window.destroy()

    def read_task(self):                                          # 读取文件中的任务
        self.config_file_list = []
        os.chdir(self.config_path)
        for item in os.listdir(self.config_path):
            if os.path.isfile(item) and os.path.splitext(item)[1] == ".txt":
                self.config_file_list.append(item)
        if len(self.config_file_list) == 0:
            showinfo(title='错误提示', message="没有可以加载的文件")
            return

        width = 290
        height = 300
        self.show_file_window = Toplevel()
        self.show_file_window.resizable(False, False)
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        self.show_file_window.wm_title("加载文件")
        self.show_file_window.geometry(size)
        self.file_list = Listbox(self.show_file_window, background=self.background, foreground = self.foreground, width=27, font=('宋体', 14))
        self.scrollbar_file = Scrollbar(self.show_file_window,orient='vertical')
        self.file_list["yscrollcommand"] = self.scrollbar_task.set
        self.scrollbar_file["command"]=self.file_list.yview
        self.file_list.bind('<Double-Button-1>', self.select_file)
        self.file_list.pack(side=LEFT, fill=BOTH)
        self.scrollbar_file.pack(side=LEFT, fill=Y)
        self.file_list.delete(0, END)
        for info in self.config_file_list:
            self.file_list.insert(END, info)


    def select_file(self, event):
        index = self.file_list.curselection()[0]
        os.chdir(self.config_path)
        with open(self.config_file_list[index], 'r') as file:
            data = file.read()
        try:
            json_data = json.loads(data)
            self.task_name_value.set(json_data["task_name"])
            self.thread_num_value.set(json_data["thread_num"])
            self.over_time_value.set(json_data["over_time"])
            self.test_times_value.set(json_data["test_times"])
            self.api_list.delete(0, END)
            self.api_info = json_data["api_list"]
            self.api_num = len(self.api_info)
            for index in range(len(self.api_info)):
                self.api_list.insert(END, "API-" + str(index)+ "-" + self.api_info[index]["url"])
            self.show_file_window.destroy()
        except Exception as error_info:
            showinfo(title='错误提示', message="文件内容错误")
            print(error_info)

    def save_task(self):
        task_info = {}
        task_info["task_name"] = self.entry_task_name.get().strip().replace(r'/', "_")
        if len(self.entry_task_name.get().strip()) == 0:
            showinfo(title='错误提示', message="任务名称不能为空")
            return

        for index in range(len(self.task_list)):
            if task_info["task_name"]  == self.task_list[index]["task_name"]:
                showinfo(title='错误提示', message="任务名称不能重复")
                return

        try:
            task_info["thread_num"] = int(self.entry_thread_num.get())
            if task_info["thread_num"] > 2000:
                showinfo(title='错误提示', message="线程数最大为2000")
                return
        except Exception as error_info:
            print(error_info)
            showinfo(title='错误提示', message="线程数错误")
            return

        try:
            task_info["over_time"] = int(self.entry_over_time.get())
        except Exception as error_info:
            print(error_info)
            showinfo(title='错误提示', message="超时设置错误")
            return

        try:
            task_info["test_times"] = int(self.entry_test_times.get())
        except Exception as error_info:
            print(error_info)
            showinfo(title='错误提示', message="测试次数设置错误")
            return

        if len(self.api_info) == 0:
            showinfo(title='错误提示', message="没有可执行的api请求")
            return
        else:
            task_info["api_list"] = self.api_info
            task_info["creat_pdf"] = False
            task_info["status"] = 0
            task_info["task_id"] = self.task_num

        self.task_list.append(task_info)
        self.show_task_list(self.task_num)
        self.task_num += 1

    def task_start(self):
        self.run_task_list = []
        self.refresh_id = 0
        if len(self.task_list) == 0:
            showinfo(title='提示', message="没有任务")
            return
        else:
            self.threads_class = []                                      # 清空记录
        for index in range(len(self.task_list)):
            self.task_list[index]["status"] = 1                          # 等待执行
            self.run_task_list_lock.acquire()
            self.run_task_list.append(self.task_list[index])             # 添加到任务队列
            self.run_task_list_lock.release()

        # 画出停止按钮
        self.taks_start_flag = True
        self.cv_left.create_window(215,15,anchor=NW, window=self.button_task_pause)
        # 刷新任务列表中的状态
        self.list_task_list.delete(0, END)
        for task in self.task_list:
            self.list_task_list.insert(END, 'TASK-' + str(task["task_id"]) + '.'+ self.task_status[task["status"]] + ' ' + task["task_name"])

    def task_pause(self):                                                # 停止任务
        for test_class in self.threads_class:
            test_class.quit = True                                       # 停止执行请求的线程
        self.taks_start_flag = False
        self.cv_left.create_window(215,15,anchor=NW, window=self.button_task_start)
        self.show_task_list(-1)


    def task_clear(self):                                                # 停止并清空任务
        if self.taks_start_flag:
            showinfo(title='提示', message="先停止所有任务再清空")
            return
        for test_class in self.threads_class:
            test_class.quit = True
            print("set----------------->", test_class.quit)
        self.task_list = []
        self.refresh_id = -1
        self.task_response_list = []
        self.task_num = 0
        self.show_task_list(-1)
    
    def show_api_request_info(self, event):
        if len(self.list_request_list.curselection()) == 0:
            return
        index = self.list_request_list.curselection()[0]
        request_info = self.task_response_list[index]
        width = 590
        height = 400
        self.show = Toplevel()
        self.show.resizable(False, False)
        screenwidth = self.root.winfo_screenwidth()
        screenheight = self.root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width)/2, (screenheight - height)/2)
        self.show.wm_title(request_info["name"])
        self.show.geometry(size)
        self.show['bg'] = self.background
        self.scrollbar_request_y = Scrollbar(self.show, orient= 'vertical')
        self.text_request_info = Text(self.show, width=57, height = 20, font=("宋体",14), background=self.background, foreground=self.foreground)
        self.text_request_info["yscrollcommand"] = self.scrollbar_request_y.set
        self.scrollbar_request_y["command"]=self.text_request_info.yview
        self.text_request_info.pack(side = LEFT, fill=Y)
        self.scrollbar_request_y.pack(side=LEFT, fill=Y)
        self.text_request_info.insert(END, 'url: ' + request_info["url"] + '\n')
        self.text_request_info.insert(END, 'method: ' + request_info["method"] + '\n')
        self.text_request_info.insert(END, 'status_code: ' + request_info["status_code"] + '\n\n')
        self.text_request_info.insert(END, 'from_data:\n\n' + request_info["from_data"] + '\n\n')
        self.text_request_info.insert(END, 'response:\n\n' + request_info["response"] + '\n\n')
        self.text_request_info.insert(END, 'error_info:\n\n' + request_info["error_info"] + '\n')

    def get_select_api_id(self, event):
        if len(self.api_list.curselection()) == 0:
            return
        else:
            self.select_api_id = self.api_list.curselection()[0]
        print(self.select_api_id)

    def popupmenu(self, event):
        if len(self.api_list.curselection()) == 0:
            return
        else:
            self.select_api_id = self.api_list.curselection()[0]
        print(self.select_api_id)
        self.menu.post(event.x_root, event.y_root)

if __name__ == "__main__":
    work = Main()