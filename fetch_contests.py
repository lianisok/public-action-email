#coding=utf-8
import requests
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
from datetime import datetime, timezone

# 获取比赛信息
response = requests.get('https://codeforces.com/api/contest.list')
contests = response.json()['result'][:10]

# 解析 JSON 数据
contest_details = []
nearest_contest_index = -1
nearest_start_time = None

for index, contest in enumerate(contests):
    if contest['phase'] == 'BEFORE':
        start_time = datetime.fromtimestamp(contest['startTimeSeconds'], timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
        contest_info = (
            f"ID: {contest['id']}\n"
            f"Name: {contest['name']}\n"
            f"Type: {contest['type']}\n"
            f"Phase: {contest['phase']}\n"
            f"Frozen: {contest['frozen']}\n"
            f"Duration: {contest['durationSeconds'] // 3600} hours {contest['durationSeconds'] % 3600 // 60} minutes\n"
            f"Start Time: {start_time}\n"
            f"Relative Time: {contest['relativeTimeSeconds']} seconds\n"
        )
        contest_details.append(contest_info)
        
        # 找到距离现在最近的比赛
        if nearest_start_time is None or contest['startTimeSeconds'] < nearest_start_time:
            nearest_start_time = contest['startTimeSeconds']
            nearest_contest_index = len(contest_details) - 1

# 检查是否有符合条件的比赛
if contest_details:
    if nearest_contest_index != -1:
        contest_details[nearest_contest_index] += "记得报名！！！\n"
    
    # 在每个比赛信息后面添加分割线
    contest_details = [f"{detail}----------------------\n" for detail in contest_details]
else:
    contest_details.append("没有可以报名的比赛")

# 准备邮件内容
email_content = "\n".join(contest_details)

# 发送邮件
email_address = os.environ['EMAIL_ADDRESS']
email_password = os.environ['EMAIL_PASSWORD']
recipient = email_address

msg = MIMEMultipart()
msg['From'] = email_address
msg['To'] = recipient
msg['Subject'] = '请查看 CF 比赛列表'
msg.attach(MIMEText(email_content, 'plain'))

# 使用 163 邮件服务器发送邮件
server = smtplib.SMTP_SSL('smtp.163.com', 465)
server.login(email_address, email_password)
server.send_message(msg)
server.quit()