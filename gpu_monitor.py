#!/usr/bin/env python3
import subprocess
import time
import logging

from datetime import datetime
from sub_utils.smtp_sender import SMTPSender


# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('gpu_monitor.log'),
        logging.StreamHandler()
    ]
)


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

    # to modify
    SERVER_NAME = "222.200.185.9"
    receiver_email = "1341887814@qq.com"

    smtp_sender = SMTPSender()

    while True:
        try:
            current_time = time.time()
            gpu_status = get_gpu_status()
                
            if gpu_status:
                idel_list = is_gpu_idle(gpu_status)

                if len(idel_list) > 0:
                    if current_time - last_notification_time >= notification_interval:
                        subject = "GPU 空闲通知"
                        body = f"{SERVER_NAME} 服务器上的 GPU 空闲，当前状态如下：\n\n"

                        for i in idel_list:
                            body += f"GPU {i} 空闲，当前状态：\n{gpu_status[i]}\n"

                        body += f"\n当前时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

                        smtp_sender.send_email(subject, body, receiver_email)

                        last_notification_time = current_time

                        logging.info("检测到 GPU 空闲，已发送通知")
                else:
                    last_notification_time = 0
            
            time.sleep(60)  # 每分钟检查一次
            
        except Exception as e:
            logging.error(f"监控过程中出错: {str(e)}")
            time.sleep(60)  # 发生错误时等待一分钟后继续


if __name__ == "__main__":
    main()