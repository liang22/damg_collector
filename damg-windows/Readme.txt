打包：
1.windows环境下安装python3软件（若cmd没有python指令需要手动配置环境变量）；
2.pip install psutil
3.双击create_exe.bat


安装：
1.解压eCloudCLI-DAMG-stable01.zip
2.安装eCloudCLI-DAMG-stable01.exe
  第一次安装需要勾选最后的运行（环境适配工作）
3.安装zip软件（若cmd没有zip指令需要手动配置环境变量）；
4.安装openssl软件（若cmd没有openssl指令需要手动配置环境变量）；
5.配置文件C:\damg\etc\damg.conf
[public]
start_time =        # 开始时间，如果不修改默认是第一次安装时间
cycle_time =        # 采集周期，单位是天
limit_cpu = 80      # CPU阈值，超额则停止采集，单位是百分比
limit_iops = 50000  # IO次数阈值，超额则停止采集
listen_host =       # 旁挂机器IP
listen_pwd =        # 旁挂机器administrator密码

[oracle]
health_time = 7     # 健康度参考天数，单位是天
sys_password =      # sys用户密码
users =             # 采集用户


使用：
1.启动服务
dam_collect start

2.暂停服务
dam_collect pause

3.立即收集一次
dam_collect run
注意：安装完成并启动服务（dam_collect start）后，
      在三分钟以后再执行本条指令（最小采集周期三分钟）

4.中断收集(停止并清空信息)
dam_collect abort

5.结束收集
dam_collect finish

6.查看收集状态
dam_collect status


采集：
采集周期到期或者执行dam_collect_run可以在桌面生成加密采集数据DAMG_INFO.enc和原始数据DAMG_INFO.zip
