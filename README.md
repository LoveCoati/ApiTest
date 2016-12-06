#ApiTest 


**ApiTest** 这是一个用于api接口测试的工具，主要是用于json数据格式的测试

目前支持的请求类型：
- [ ]post
  - [x] 只支持传json数据
  
- [ ]get
  - [x] 数据类型不限
  
## 1 环境与依赖

此版本只能运行于Python 3环境 。

**ApiTest** 用到了Python **requests** , **xlrd** , **matplotlib** 以及 **xlwt** 库。

使用之前需要所依赖的库:

```bash
pip install xlwt
pip install xlrd
pip install requests
pip install matplotlib
```


## 2 ApiTest 的使用说明


### 2.1 创建测试任务

通过添加API请求来组合创建一个测试任务，添加API请求如图:

![add_api](img/add_api.png)

添加多个API后，可以组合成一个任务，如下图所示：

![api_list](img/api_list.png)

### 2.2 任务保存至文件

将任务保存至文件，方便下一次使用，保存方法示意图如图所示：

![save_api](img/save_api.png)

### 2.3 从文件中加载任务

从文件中加载已保存的任务，如图所示:

![read_api](img/read_api.png)

### 2.4 将任务添加到运行列表

点击添加任务到列表，可以将任务加到运行列表，如图所示:

![add_task](img/add_task.png)

将任务添加到运行列表后，点击开始任务，即开始对任务进行相应测试，刷新列表或双击测试任务两次，可以看到测试结果列表。

### 2.5 参数的配置和获取

####1.随机数的生成

**随机生成字符串:** $.random_str.6.10.$     
     
后面两位数字表示随机字符串的最小长度和最大长度

**随机生成整数:** $.random_int.10.100.$ 
    
后面两位数字表示随机生成的整数的取值范围

**随机数的拼接:** 如果要生成包含字母与数字的字符串，如“sdfdf325”这样的，可以使用上述拼接，如下所示

```
$.srandom_str_4.10.$$.random_int.100.1000$
```

####2.获取一个接口的返回参数

在API列表中有接口的编号，可以通过接口编号及想要获取的	返回参数变量名来获取一个接口的返回参数：

![get_members](img/get_members.png)

例如第二个接口想获取到第一个接口返回的参数：

第一个接口返回的参数格式为：

```
{"result":200,"description":"增加摄像头成功","cameraId":"2982"}
```

这是一个json格式的数据,若第二个接口要获取第一个接口的cameraId则使用$.str.0.cameraId.$即可获取对应的cameraId。

如果返回参数中包含数组，假如第一个接口返回参数如下：

```
{
"result": "200",
"description": "查询成功",
"total": 624,
"list": [{
"mosaicGroupIds": [{"groupId": "3122","groupType": 0}],
"chnlIds": [],
"mosaicIds": [3942,
3943],
"detail": "西安村1组34号电力杆",
"type": 2,
"isPlay": 0,
"cameraId": "3121",
"cameraName": "西安村1组34号电力杆",
"inputUrls": [
"rtsp://admin:a12345678@10.63.237.92:554/cam/realmonitor?channel=1&subtype=1",
"rtsp://admin:a12345678@10.63.237.92:554/cam/realmonitor?channel=1&subtype=0"]
}]
}
```

想要获取数组中的参数，例如想获取inputUrls里面的第一个值，则使用如下语句即可获得相应的inputUrls：

```
$.str.0.list.0.inputUrls.0.$
```

其中，里面的数字都是相对应的索引。

### 2.6 返回数据的查看

运行测试任务后，通过双击任务或刷新列表可以查看到列表中显示测试用例相关信息。

其中，请求结果列表中的200表示请求的状态，根据http状态分析得到。

![get_result](img/get_result.png)


通过右边的列表可以查询每一个请求的状态，如图所示:

![data_info](img/data_info.png)

## ApiTest 源码的编译

```
pyinstaller.exe -w --onefile --icon="3.ico" smcenter_test.py
```

将源代码生成.exe文件，方便使用，首先要安装pyinstaller，前面是pyinstaller的路径。上述命令生成的.exe文件会隐藏命令窗口，看不到程序中的相关输出，若不隐藏命令窗口，则将-w换成--console即可。






