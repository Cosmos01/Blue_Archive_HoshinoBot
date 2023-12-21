# Blue_Archive_HoshinoBot
  
碧蓝档案图形化活动日历、模拟抽卡、官推转发、角色查询、攻略获取插件, 适用于 HoshinoBot v2.  

  
**临时公告**
- 新增总力排名功能，支持国服、B服、日服，总力战和大决战
- 清理了一下仓库，大小减少到22MB了。无法pull的删除重新clone，data.json文件可以备份一下。
    
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
- 日历: [GameKee](https://ba.gamekee.com/)、[SchaleDB](https://lonqie.github.io/SchaleDB/)、[EnWiki](https://bluearchive.wiki/wiki/Main_Page)  
- 角色信息：[SchaleDB](https://lonqie.github.io/SchaleDB/)   
- 角色评价：[夜猫咪喵喵猫](https://space.bilibili.com/425535005)  
- 游戏攻略：[arona](https://doc.arona.diyigemt.com/api/)
- 总力排名：[日服](https://arona.ai/graph)、[国服](https://arona.icu/)(加群没反应，API已标明出处，每天只获取3次，使用我的服务器分发，如有问题可以联系我)
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
- `ba(日,国,国际,en日,db日,db国际)服日历 on`
- `ba更新卡池` 

<br><br>
## 指令列表
- `帮助ba日历` : 获取以下帮助内容
- `ba日历` : 本群订阅服务器日历，需要先订阅(见第三条)，默认取第一位，需要调整顺序先off掉其他服
- `ba(日/国/db日/en日/国际/db国际)服日历` : 指定服务器日程
- `ba(日/国/db日/en日/国际/db国际)服日历 on/off` : 订阅/取消订阅指定服务器的日历推送
- `ba日历 time 时:分` : 设置日历推送时间
- `ba日历 status` : 查看本群日历推送设置
- `ba日历 cardimage` : (go-cqhttp限定)切换是否使用cardimage模式发送日历图片(我也不晓得有啥区别)
- `(日/国际服)总力一图流` : 当前总力一图流,为空时默认日服
- `ba来一井\ba十连\ba单抽` : 模拟抽卡
- `ba更新卡池` : 更新角色列表、卡池、资源文件，默认会自动更新
- `ba氪金+@目标` : 恢复抽卡次数，可@多个目标
- `ba角色列表` : 列出所有角色头像及昵称
- `ba查询+角色名或昵称` : 查询角色信息
- `国服/国际服+千里眼/未来视` : 获取卡池排期和抽卡推荐
- `ba攻略(攻略查询、/攻略)+关键词` : 查询攻略,支持模糊查询,关键词可以是学生/地图/活动等，使用`杂图`关键词获取详情 
- `balogo+上文/下文` : 生成你游风格logo,上下文使用`/`分隔
- `(日/国B服)(第X期)总力/大决战排名` : 为空默认为日历服务器最新一期

<br><br>
## ARONA攻略查询
  感谢arona提供的api，使用本地缓存+hash校验，位置在`HoshinoBot\res\img\bluearchive\wiki`  
  支持查询的关键词请看[链接](https://doc.arona.diyigemt.com/command/manual#%E5%AD%A6%E7%94%9F%E4%B8%8E%E4%B8%BB%E7%BA%BF%E5%9C%B0%E5%9B%BE%E6%94%BB%E7%95%A5%E7%B3%BB%E5%88%97)    

<br><br>
## 注意事项  
1. 如果需要更久以后的日历，可以将[generate.py](https://github.com/Cosmos01/Blue_Archive_HoshinoBot/blob/main/ba_calendar/generate.py)的`get_events(server, 0, 7)`的7改成14或更久以后的天数。
2. 推特5分钟获取一次，01分时获取，可以在诸如1分10秒，6分10秒这样的时间运行bot,可以更早获取到推特。
3. 总力一图流可以改为本地获取，注释上面代码，取消注释下面代码，配置代理(可以直接在代码中设置proxy参数，见注释，也可以用Proxifier给"*.gamer.com.tw"设置代理)。由于巴哈姆特反爬加强，修改为selenium获取网页，需要配置selenium环境才能够使用。
4. 使用shamrock等非本机QQ端会导致部分图片无法发送，在hoshino\config\__bot__.py中修改RES_PROTOCOL为base64（http配好RES_URL应该也可以）

<br><br>
## 鸣谢
感谢[arona](https://doc.arona.diyigemt.com/api/)提供的API    
感谢[@benx1n](https://github.com/benx1n)提供的代码    
感谢天上掉下来的代码。(所有代码都不是本人所写，都是天上掉下来的，修bug也是天修的)    
感谢群友帮忙整理角色名，欢迎加社团(日服id:20、911，国服群：834923321)。    


