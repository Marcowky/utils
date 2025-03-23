import paramiko
import json
import time

from sub_utils.smtp_sender import SMTPSender


def check_ssh_connection(hostname, port, username, password, wait_seconds):
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname, port, username, password, timeout=wait_seconds)
        client.close()
        return True
    except Exception as e:
        print(f"Failed to connect to {hostname}:{port} - {e}")
        return False


if __name__ == "__main__":
    # to modify
    hostname = "222.200.185.67"
    port = 22
    username = "kaiyu"
    password = "kaiyu@123"
    receiver_email = "1341887814@qq.com"

    smtp_sender = SMTPSender()

    ssh_wait_seconds = 10
    last_notification_time = 0
    notification_interval = 3600  # 通知间隔（秒）

    while True:
        current_time = time.time()
            
        if check_ssh_connection(hostname, port, username, password, ssh_wait_seconds):
            if current_time - last_notification_time >= notification_interval:

                subject = "SSH Connection Successful"
                body = f"Successfully connected to SSH server {hostname}:{port}"

                smtp_sender.send_email(subject, body, receiver_email)
                last_notification_time = current_time

                print("SSH connection successful")

        else:
            print("SSH connection failed")
            last_notification_time = 0

        time.sleep(60)