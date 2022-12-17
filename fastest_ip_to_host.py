import os
import time
import re
import threading
import datetime
import subprocess
import requests
from lxml import etree  # 解析库

'''
输入网址，从ip138和ipaddress获取ping最快的ip写入HOSTS
'''

def get_ip(ori_url):
    '''
    获取网址对应ip
    :param ori_url: 网址链接
    :return: ip列表
    '''
    # 输入网址去http或https和www以及页内地址

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
    }

    # 访问网站并获取 HTML 文档
    response1 = requests.get("https://site.ip138.com/" + url, headers=headers)
    response2 = requests.get("https://www.ipaddress.com/site/" + url, headers=headers)

    # 解析
    response1.encoding = 'utf-8'
    response2.encoding = 'utf-8'
    html_dt1 = etree.HTML(response1.text)
    html_dt2 = etree.HTML(response2.text)

    # xpath提取值
    # 注，做了反爬措施，要根据response.text生成的html获取xpath，不要直接在网站获取
    values1 = html_dt1.xpath(f'//*[@id="J_ip_history"]/p[*]/a')
    en_times = html_dt1.xpath(f'//*[@id="J_ip_history"]/p[*]/span')
    values2 = html_dt2.xpath(f'//*[@id="dns"]/tbody/tr[*]/td[2]/a')
    # ipv4
    pattern = re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')

    ip_list = []
    # 获取当前日期
    now = datetime.datetime.now()
    for i in range(len(values1)):
        #   ipv4模式匹配，重复的不在加进iplist，解析时间最后10位是当前时间说明ip还在使用
        if pattern.match(values1[i].text) and values1[i].text not in ip_list and en_times[i].text[-10:] == now.strftime(
                '%Y-%m-%d'):
            ip_list.append(values1[i].text)
    for value in values2:
        if pattern.match(value.text) and value.text not in ip_list:
            ip_list.append(value.text)

    return ip_list



def ping(ip):
    '''
    ping指定ip
    :param ip: ip地址
    :return: 平均时间
    '''
    # 调用ping 命令,获取ping结果
    # -w 检查延迟的超时时间，单位是秒。指的是整个ping的超时时间，即等待接收第一个响应之前的最长等待时间
    cmd = ["ping", ip, "-w", "0.5"]
    # subprocess.Popen()打开一个子进程，执行命令cmd
    # stdin、stdout、stderr参数分别表示子进程的标准输入、标准输出、标准错误输出，shell参数表示是否以shell模式运行
    ping_result = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
    # 读取ping结果
    out = ping_result.stdout.read().decode('gbk')
    # 获取平均时间
    # 注，此处正则表达式可能会因为不同操作系统而变化，需要根据ping结果再次修改
    time_result = re.findall(r'平均 = (.*?)ms', out, re.M)
    # 没有ping通
    if not time_result:
        return False, 0
    else:
        return True, float(time_result[0])
    print("-",end="")


def get_fast_ip(ip_list):
    '''
    获取最快的ip和平均时间
    :param ip_list: ip列表
    :return: 最快的ip和平均时间
    '''
    # 存放ip和ping平均时间的元组
    ip_time_list = []
    # 存放ping线程
    threads = []

    # 初始化最快ip
    fast_ip = ip_list[0]
    fast_time = -1

    # 开启多线程ping
    for ip in ip_list:
        t = threading.Thread(target=ping, args=(ip,))
        threads.append(t)
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # 生成ip_time_list
    for ip in ip_list:
        is_ping, time = ping(ip)
        if is_ping:
            ip_time_list.append((ip, time))
            # 更新最快ip
            if time < fast_time or fast_time == -1:
                fast_ip = ip
                fast_time = time

    return fast_ip, fast_time, ip_time_list

def write_hosts(fastest_ip,url):
    if fastest_ip:
        # 打开文件
        with open(r"C:\Windows\System32\drivers\etc\HOSTS", 'r+') as f:
            # 读取文件
            lines = f.readlines()
            # 判断hostname是否存在
            exist = False
            # 循环遍历检查
            for line in lines:
                # 判断hostname是否存在
                if url in line:
                    exist = True
                    line = fastest_ip + ' ' + url
                    break
            # 如果hostname存在，则替换
            if exist:
                lines[lines.index(line)] = line
            # 如果hostname不存在，则添加
            else:
                lines.append(fastest_ip + ' ' + url)
            # 重新写入文件
            f.seek(0)
            f.writelines(lines)


if __name__ == '__main__':
    ori_url = input("请输入待查询ip的网址：")
    url = re.sub(r'https?://(www\.)?(.*?)/.*', r'\2', ori_url)
    ip_list = get_ip(url)
    print("有", len(ip_list), "个ip待查询: ", ip_list)

    fast_ip, fast_time, ip_time_list = get_fast_ip(ip_list)

    print("ip和ping平均时间列表：", ip_time_list)
    print("最快的ip：", fast_ip, "，ping平均时间：", fast_time)

    write_hosts(fast_ip,url)
    print("写入hosts成功")
