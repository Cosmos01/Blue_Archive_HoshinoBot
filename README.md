## 特殊情况
BWIKI无了，自动更新抽卡已经无法使用了，日历数据已经替换为enwiki的，具体情况：https://t.bilibili.com/669346949195890741    
BWIKI开启前只能自行更新卡池了，Releases中给出了一份卡池数据，可以自行替换。（反正你游卡池更新慢，影响应该不大）
### bwiki好像开始甘地行为了，萌百还在他们好像就不开了的样子，算了，之后自己搞吧

# Blue_Archive_HoshinoBot
碧蓝档案图形化活动日历、模拟抽卡、官推转发、总力攻略图\汉化漫画获取插件, 适用于 HoshinoBot v2.  

项目地址 https://github.com/Cosmos01/Blue_Archive_HoshinoBot  

日程参考项目：https://github.com/zyujs/pcr_calendar  
承接该项目的抽卡功能并加入更新卡池功能：https://github.com/azmiao/bluearchive_hoshino_plugin.git

![FYBN %B61EG``_OG~B8XZ$B](https://user-images.githubusercontent.com/37209685/165712652-5b221387-f0cc-41c2-9b6c-9b6b76063ed5.PNG)

## 日程信息源
日服新数据来源: [EnWiki](https://bluearchive.wiki/wiki/Main_Page)
国际服：[SchaleDB](https://lonqie.github.io/SchaleDB/)

弃用：
日服: [BiliWiki](https://wiki.biligame.com/bluearchive/%E9%A6%96%E9%A1%B5)  



## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/Cosmos01/Blue_Archive_HoshinoBot.git`
2. 进入本项目目录运行 `pip install -r requirements.txt `安装必要的第三方库
3. (可选)申请推特API，将项目目录下的twtter-template.json改名为twtter.json，并填入密钥等参数 (具体申请方法自行搜索)
4. 在 `config/__bot__.py`的MODULES_ON列表里加入 `Blue_Archive_HoshinoBot`
5. 将bluearchive文件夹移动到\HoshinoBot\res\img目录下
6. 重启HoshinoBot

部分模块默认是关闭状态，抽卡前请先更新卡池  
使用bot指令开启功能：  
- `启用 ba_twitter`(确认已经填写好密钥再开启)
- `启用 ba_calendar`
- `启用 ba_comic_cn`
- `ba日服日历 on`(必要)
- `ba更新卡池`(目前无法使用，可以手动下载[卡池资源](https://github.com/Cosmos01/Blue_Archive_HoshinoBot/releases)替换对应文件)


## 指令列表
- `ba日历` : 查看本群订阅服务器日历
- `ba日(国际、台、韩、美)服日历` : 查看指定服务器日程
- `ba日(国际、台、韩、美)服日历 on/off` : 订阅/取消订阅指定服务器的日历推送
- `ba日历 time 时:分` : 设置日历推送时间
- `ba日历 status` : 查看本群日历推送设置
- `ba日历 cardimage` : (go-cqhttp限定)切换是否使用cardimage模式发送日历图片
- `(x服)总力一图流` : 查看当前总力一图流,服务器名为空时默认日服
- `ba来一井\ba十连\ba单抽` : 模拟抽卡
- `ba更新卡池` : 更新卡池
- `氪金+@目标` : 恢复抽卡次数，可@多个目标
