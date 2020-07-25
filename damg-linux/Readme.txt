打包：
1.安装python3，并使用pip3安装pyinstaller工具；
   Linux上为防止和python3冲突，默认安装在/opt/python3下
2.安装psutil工具，/opt/python3/bin/pip3 install psutil；
3.安装pyinstaller工具，/opt/python3/bin/pip3 install pyinstaller；
4.将代码部署在独立目录下，赋于create_tgz.sh执行权限(chmod +x)并执行，
   打包需要一定时间，之后会生成tgz包；


安装：
* 目前支持el6 el7
1. 执行./eCloudCLI-DAMG-stable01.bin
2. 配置文件/etc/damg.conf
[public]
start_time =        # 开始时间，如果不修改默认是第一次安装时间
cycle_time =        # 采集周期，单位是天
if_wmconcat = yes   # 是否安装wmconcat工具，初次安装后可以设置为no
limit_cpu = 80      # CPU阈值，超过则不采集
limit_iops = 50000  # IO阈值，超过则不采集
listen_host =       # 旁挂机器ip   注意：开通旁挂需配ssh免密，并在旁挂服务器也安装bin包

[oracle]
health_time =       # 采集健康度参考天数
sys_password =      # sys用户密码
users =             # 采集用户


使用：
1.启动服务
dam_collect start

2.暂停收集
dam_collect pause

3.中断收集(停止并清空信息)
dam_collect abort

4.立即收集一次
dam_collect run
注意：采集信息不完整时无法启动立即收集动作

5.收集结束
dam_collect finish

6.查看采集进度
dam_collect status

7.守护进程
dam_daemon  #开启，杀进程关闭


采集：
采集周期到期或者执行dam_collect_run可以在/root下生成加密采集数据DAMG_INFO.enc和原始数据DAMG_INFO.zip
