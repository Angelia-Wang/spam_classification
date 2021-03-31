# coding=utf-8
import base64
import quopri

import numpy as np
import os


def read_index_file(file_path):  # trec06c/full/index
    """读取索引文件，返回索引字典，key为文件相对地址，value为类别"""
    type = {'spam': '1', 'ham': '0'}
    index_dict = {}
    with open(file_path) as f:
        for line in f:
            mail = line.split(' ')  # spam ../data/000/000
            if len(mail) == 2:
                key, value = mail
            value = value.replace('../data/', '').replace('\n', '')
            index_dict[value] = type[key.lower()]  # 000/000:1
    return index_dict


def decode_text(text):
    """邮件部分字段采用gb2312编码，base64存储，返回解码后的字符串"""
    if text.startswith("=?"):
        temp = text.split('?')
        if temp[2].lower() == 'b':
            data = base64.b64decode(temp[3])
            return data.decode(encoding='gbk', errors='replace')
        elif temp[2].lower() == 'q':
            data = quopri.decodestring(temp[3])
            return data.decode(encoding='gbk', errors='replace')
    else:
        return text


def read_email(file_path):
    """读取邮件内容，返回内容字符串"""
    content_dict = {}
    is_content = False
    with open(file_path, encoding='gb2312', errors='ignore') as f:
        for line in f:
            line = line.strip()
            if line.startswith("From:"):  # 发送地址
                content_dict['from'] = line[5:].strip()
            elif line.startswith("To:"):  # 接收地址
                content_dict['to'] = line[3:].strip()
            elif line.startswith("Subject:"):  # 邮件标题
                content_dict['subject'] = decode_text(line[8:].strip())
            elif not line:  # 为空，证明下一行是正文部分
                is_content = True

            # 正文部分
            if is_content:
                if 'content' in content_dict:
                    content_dict['content'] += line
                else:
                    content_dict['content'] = line

        content_dict['content'] = decode_text(content_dict['content'].strip())

    # 将上述得到的字典转换为字符串
    mail = content_dict.get('from', 'None').replace(',', '').strip() + ","  # 没有from字段就填充None
    mail += content_dict.get('to', 'None').replace(',', '').strip() + ","
    mail += content_dict.get('subject', 'None').replace(',', '').strip() + ","
    mail += content_dict.get('content', 'None').replace(',', '').strip()
    return mail


index_dict = read_index_file('data/trec06c/full/index')  # 得到文件与类别的索引字典
write_file_path = 'data/mail_process01'
folder_list = sorted(os.listdir('data/trec06c/data'))  # list[000,001,002....215] 文件夹列表
folder_list.pop(0)  # 删除mac系统自带文件夹 .DS_Store

# 将所有处理后的邮件内容写入一个文件
with open(write_file_path, 'w', encoding='utf=8') as w:
    for folder in folder_list:
        folder_path = 'data/trec06c/data/' + folder
        print(f'开始处理文件夹 {folder_path} 中的邮件')
        files = sorted(os.listdir(folder_path))  # list[000,001,002....215] 文件列表
        for file in files:
            file_path = f'{folder_path}/{file}'
            # print(file_path)
            index_key = f'{folder}/{file}'  # 此文件对应的索引
            if index_key in index_dict:
                mail = read_email(file_path)  # from字符串,to字符串,subject字符串,content字符串
                mail += f',{index_dict[index_key]}\n'  # 加上标签特征 from字符串,to字符串,subject字符串,content字符串,0/1
                w.writelines(mail)
