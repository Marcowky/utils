#!/usr/bin/env python3
import subprocess
import time
import smtplib
import os
import json
import logging

from email.mime.text import MIMEText
from email.header import Header
from datetime import datetime


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gpu_monitor.log'),
        logging.StreamHandler()
    ]
)


# 邮件配置
config_path = os.path.join(os.path.dirname(__file__), 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)
SMTP_SERVER = config['smtp_server']  # 根据你的邮箱服务商修改
SMTP_PORT = config['smtp_port']
SENDER_EMAIL = config['sender_email']  # 替换为你的邮箱
SENDER_PASSWORD = config['sender_password']  # 替换为你的应用专用密码
RECEIVER_EMAIL = config['receiver_email']  # 替换为接收通知的邮箱


def get_gpu_status():
    """获取 GPU 状态"""
    try:
        # 获取 GPU 使用率
        gpu_utils = subprocess.check_output(['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits']).decode('utf-8').strip()
        # 获取内存使用情况
        mem_infos = subprocess.check_output(['nvidia-smi', '--query-gpu=memory.used,memory.total', '--format=csv,noheader,nounits']).decode('utf-8').strip()

        final_status = [f"{gpu_util}, {mem_info}" for gpu_util, mem_info in zip(gpu_utils.split('\n'), mem_infos.split('\n'))]

        return final_status
    except Exception as e:
        logging.error(f"获取 GPU 状态时出错: {str(e)}")
        return None


def send_email(subject, body):
    """发送邮件通知"""
    try:
        msg = MIMEText(body, 'plain', 'utf-8')
        msg['Subject'] = Header(subject, 'utf-8')
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECEIVER_EMAIL

        with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
            server.connect(SMTP_SERVER, SMTP_PORT)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
            server.quit()
        
        logging.info("邮件发送成功")
    except Exception as e:
        logging.error(f"发送邮件时出错: {str(e)}")


def is_gpu_idle(gpu_status):
    """判断 GPU 是否空闲"""
    if not gpu_status:
        return False
    try:
        idel_list = []
        for i, gpu_statu in enumerate(gpu_status):
            # 解析 GPU 状态
            gpu_util, mem_used, mem_total = map(float, gpu_statu.split(', '))
            # 如果 GPU 利用率低于 5% 且内存使用率低于 10%，则认为空闲
            if gpu_util < 5 and (mem_used / mem_total) < 0.1:
                idel_list.append(i)
        return idel_list
    except Exception as e:
        logging.error(f"解析 GPU 状态时出错: {str(e)}")
        return False


def main():
    logging.info("GPU 监控程序启动")
    last_notification_time = 0
    notification_interval = 3600  # 通知间隔（秒）

    while True:
        try:
            current_time = time.time()
            gpu_status = get_gpu_status()
                
            if gpu_status:
                idel_list = is_gpu_idle(gpu_status)

                if len(idel_list) > 0:
                    if current_time - last_notification_time >= notification_interval:
                        subject = "GPU 空闲通知"
                        for i in idel_list:
                            body = f"GPU {i} 空闲，当前状态：\n{gpu_status[i]}\n\n时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                        send_email(subject, body)
                        last_notification_time = current_time
                        logging.info("检测到 GPU 空闲，已发送通知")
            
            time.sleep(60)  # 每分钟检查一次
            
        except Exception as e:
            logging.error(f"监控过程中出错: {str(e)}")
            time.sleep(60)  # 发生错误时等待一分钟后继续


if __name__ == "__main__":
    main()