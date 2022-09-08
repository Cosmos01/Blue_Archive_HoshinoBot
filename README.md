# Blue_Archive_HoshinoBot
碧蓝档案图形化活动日历、模拟抽卡、官推转发、总力攻略图、角色查询插件, 适用于 HoshinoBot v2.  

项目地址 https://github.com/Cosmos01/Blue_Archive_HoshinoBot    

日程参考项目：https://github.com/zyujs/pcr_calendar  
承接该项目的抽卡功能并加入更新卡池功能：https://github.com/azmiao/bluearchive_hoshino_plugin.git  
本想加入B站几位UP动态推送功能，但已经有bili-notice-hoshino、rss之类的推送插件，有需要可以另外安装。

![FYBN %B61EG``_OG~B8XZ$B](https://user-images.githubusercontent.com/37209685/165712652-5b221387-f0cc-41c2-9b6c-9b6b76063ed5.PNG)     

## 日程信息源
日服新数据来源: [EnWiki](https://bluearchive.wiki/wiki/Main_Page)  
国际服：[SchaleDB](https://lonqie.github.io/SchaleDB/) ←这玩意儿经常改数据结构，获取不到了就来更新，没更新就提issues

弃用：
[BiliWiki](https://wiki.biligame.com/bluearchive/%E9%A6%96%E9%A1%B5)    



## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/Cosmos01/Blue_Archive_HoshinoBot.git`
2. 进入本项目目录运行 `pip install -r requirements.txt `安装必要的第三方库
3. 在 `config/__bot__.py`的MODULES_ON列表里加入 `Blue_Archive_HoshinoBot`
4. 将bluearchive文件夹移动到\HoshinoBot\res\img目录下
5. 重启HoshinoBot

部分模块默认是关闭状态，抽卡前请先更新卡池  
使用bot指令开启功能：  
- `启用 ba_calendar`
- `启用 ba_twitter`(如果修改了代码为本地获取，请确认已经填写好密钥并修改配置文件名再开启)  
- `ba日(国际、台、韩、美)服日历 on`(必要)
- `ba更新卡池` 


## 指令列表
- `ba日历` : 查看本群订阅服务器日历，需要先订阅(见第三条)，服务器取第一位，需要调整顺序可以先off掉其他服
- `ba日(国际、台、韩、美)服日历` : 查看指定服务器日程
- `ba日(国际、台、韩、美)服日历 on/off` : 订阅/取消订阅指定服务器的日历推送
- `ba日历 time 时:分` : 设置日历推送时间
- `ba日历 status` : 查看本群日历推送设置
- `ba日历 cardimage` : (go-cqhttp限定)切换是否使用cardimage模式发送日历图片
- `(x服)总力一图流` : 查看当前总力一图流,服务器名为空时默认日服(同推特，可以改为本地获取,见注意事项3)
- `ba来一井\ba十连\ba单抽` : 模拟抽卡
- `ba更新卡池` : 自动更新角色列表、卡池、资源文件。由于SchaleDB似乎没有提前更新的习惯，一般会在当晚更新卡池，最迟第二天早上。
- `ba氪金+@目标` : 恢复抽卡次数，可@多个目标
- `ba查询+角色名或昵称` : 查询角色信息  

## 注意事项  
1. 修改角色表(_ba_data.json)文件时需要注意，数组第一位必需为DevName,否则自动获取图片无法使用，DevName见[SchaleDB](https://raw.githubusercontent.com/lonqie/SchaleDB/main/data/jp/students.json)  
2. 如果不想使用我的api，可以注释掉twitter.py上半部分代码，取消注释下面部分代码，申请推特API，将项目目录下的twtter-template.json改名为twtter.json，并填入密钥等参数 (具体申请方法自行搜索)，注意配置代理(推荐使用Proxifier,)
3. 总力一图流可以改为本地获取，注释上面代码，取消注释下面代码，配置代理(可以直接在代码中设置proxy参数，见注释，也可以用Proxifier给"*.gamer.com.tw"设置代理)
4. 之前的图片获取存在问题，如果安装了2022年8月10日前的版本，遇到问题可以删除资源文件'unit'中'icon_unit_1000.png'以外的图片，使用'ba更新卡池'指令更新。

## 鸣谢
感谢沙雕群友提供的代码  
