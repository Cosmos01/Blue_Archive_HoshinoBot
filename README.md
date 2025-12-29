# Blue_Archive_HoshinoBot
  
碧蓝档案图形化活动日历、模拟抽卡、官推转发、角色查询、攻略获取、助战查询插件, 适用于 HoshinoBot v2.  

    
项目地址  https://github.com/Cosmos01/Blue_Archive_HoshinoBot  
纯净整合包  https://github.com/Cosmos01/HoshinoBot_Blue

-------------
  
日程参考项目：https://github.com/zyujs/pcr_calendar  
承接该项目的抽卡功能并加入更新卡池功能：https://github.com/azmiao/bluearchive_hoshino_plugin  
本想加入B站几位UP动态推送功能，但已经有bili-notice-hoshino、rss之类的推送插件，有需要可以另外安装。
<br><br>

![FYBN %B61EG``_OG~B8XZ$B](https://user-images.githubusercontent.com/37209685/165712652-5b221387-f0cc-41c2-9b6c-9b6b76063ed5.PNG)

<br><br>
## 信息源
- 日历: [GameKee](https://ba.gamekee.com/)、[SchaleDB](https://schaledb.com)、[EnWiki](https://bluearchive.wiki/wiki/Main_Page)  
- 角色信息：[SchaleDB](https://lonqie.github.io/SchaleDB/)
- 游戏攻略：[arona](https://doc.arona.diyigemt.com/api/)
- 总力排名：[日服](https://yuzutrends.vercel.app/)、[国服](https://arona.icu/)
- 助战：[arona.icu](https://arona.icu/)
<br><br>
## 安装方法

1. 在HoshinoBot的插件目录modules下clone本项目 `git clone https://github.com/Cosmos01/Blue_Archive_HoshinoBot.git`
2. 在 `config/__bot__.py`的MODULES_ON列表里加入 `Blue_Archive_HoshinoBot`
3. 将bluearchive文件夹移动到HoshinoBot\res\img目录下
4. 重启HoshinoBot

部分模块默认是关闭状态，抽卡前请先更新卡池  
使用bot指令开启功能：  
- `启用 ba_calendar`
- `启用 ba_twitter`(日服推特获取)
- `启用 arona_icu`(助战查询，需要token)
- `ba(日,国,国际,en日,db日,db国际)服日历 on`
- `ba更新卡池` 

<br><br>
## 指令列表
- `帮助ba日历` : 获取以下帮助内容
- `ba日历` : 本群订阅服务器日历，需要先订阅(见第三条)，取第一位，调整顺序先off掉其他服
- `ba(日/国/db日/en日/国际/db国际)服日历` : 指定服务器日程
- `ba(日/国/db日/en日/国际/db国际)服日历 on/off` : 订阅/取消订阅指定服务器的日历推送
- `ba日历 time 时:分` : 设置日历推送时间
- `ba日历 status` : 查看本群日历推送设置
- `ba日历 cardimage` : (go-cqhttp限定)切换是否使用cardimage模式发送日历图片(我也不晓得有啥区别)
- `ba来一井\ba十连\ba单抽` : 模拟抽卡
- `ba更新卡池` : 更新角色列表、卡池、资源文件，默认会自动更新
- `ba氪金+@目标` : 恢复抽卡次数，可@多个目标
- `ba角色列表` : 列出所有角色头像及昵称
- `ba查询+角色名或昵称` : 查询角色信息
- `国服/国际服+千里眼/未来视` : 获取卡池排期和抽卡推荐
- `ba攻略(攻略查询、/攻略)+关键词` : 查询攻略，支持模糊查询，关键词可为学生/地图/活动等，`杂图`做关键词获取详情 
- `balogo+上文/下文` : 生成你游风格logo,上下文使用`/`分隔
- `(日/国/B服)(第X期)总力/大决战排名` : 为空默认为日历服务器最新一期
- `我要借/助战查询 (X服)(总力/演习)(X星)(s/专X)角色名(页码)`：查询助战，需要在config.json填写token。[获取token](https://arona.icu/about)

<br><br>
## ARONA攻略查询
  感谢arona提供的api  
  使用本地缓存+hash校验，位置在`HoshinoBot\res\img\bluearchive\wiki`  
  支持查询的关键词请看[arona用户手册](https://doc.arona.diyigemt.com/v1/command/manual#%E5%AD%A6%E7%94%9F%E4%B8%8E%E4%B8%BB%E7%BA%BF%E5%9C%B0%E5%9B%BE%E6%94%BB%E7%95%A5%E7%B3%BB%E5%88%97)    

<br><br>
## 注意事项  
1. 如果需要更久以后的日历，可以将[generate.py](https://github.com/Cosmos01/Blue_Archive_HoshinoBot/blob/main/ba_calendar/generate.py)的`get_events(server, 0, 7)`的7改成14或更久以后的天数
2. 推特5分钟获取一次，01分时获取，可以在诸如1分10秒，6分10秒这样的时间运行bot,可以更早获取到推特
3. 使用非本机QQ端会导致部分图片无法发送，在hoshino\config\__bot__.py中修改RES_PROTOCOL为base64（http配好RES_URL应该也可以）
4. 角色数据源是SchaleDB，有时候更新的晚会出现无头像情况，等一两天就好。卡池是我手动更新，由于我只玩日服，可能更新的不及时，复刻池也可能懒得更新，欢迎pr

<br><br>
## 鸣谢
感谢[arona](https://doc.arona.diyigemt.com/api/)和[arona.icu](https://arona.icu)提供的API    
感谢[@benx1n](https://github.com/benx1n)提供的代码    
感谢[SchaleDB](https://schaledb.com)的数据    
感谢群友帮忙整理角色名，欢迎加社团(日服id:911)    


