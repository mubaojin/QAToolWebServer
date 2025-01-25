# coding=utf-8
import hashlib
import os
import time
import uuid

import pandas as pd
import requests
from openai import OpenAI
import json

class AI:
    def __init__(self, system = '你是一个从业20多年的游戏QA组长，你负责的项目是一款UE5的MMORPG，你对组员的要求非常严苛，从不放过任何蛛丝马迹', ai_type = 'deepseek-chat'):
        self.client = OpenAI(
            # 若没有配置环境变量，请用百炼API Key将下行替换为：api_key="sk-xxx",
            api_key="sk-ccd08368dc434bef9dbd6ff9e114a47f",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        )
        self.ai_type = ai_type
        if self.ai_type == 'deepseek-chat':
            self.client = OpenAI(api_key="sk-4f559142960a44b0a5641502d46a3a9a", base_url="https://api.deepseek.com")
            # 设定AI的身份
        self.system = system
        # 设定模型类型
        self.ai_type = ai_type

    # 文字call ai，
    def call_ai(self, msg):
        if self.ai_type == 'deepseek-chat':
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": self.system},
                    {"role": "user", "content": msg},
                ],
                stream=False,
                max_tokens=8192,
            )
            return response.choices[0].message.content
        else:
            completion = self.client.chat.completions.create(
                model = self.ai_type,  # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
                messages = [
                    {'role': 'system', 'content': self.system},
                    {'role': 'user', 'content': msg}],
            )
            return json.loads(completion.model_dump_json())['choices'][0]['message']['content']

    # 分析当前路径下的excel表
    def call_ai_to_excel(self, extra_msg):
        """
        分析当前路径下的excel表
        Args:
            extra_msg: 额外的要分析的内容，传入字符串

        Returns:None
        """
        # 获取当前目录下的所有文件
        files_in_directory = os.listdir('.')

        # 过滤出Excel文件，支持以'.xlsx'或'.xls'结尾的文件
        excel_files = [file for file in files_in_directory if file.endswith(('.xlsx', '.xls'))]

        # 检查是否只有一个Excel文件
        if len(excel_files) == 1:
            excel_file = excel_files[0]
            print(f"读取Excel文件: {excel_file}")

            # 读取Excel文件
            df = pd.read_excel(excel_file)

            # 将DataFrame转换为JSON格式，确保输出为可读的Unicode字符
            data_json = df.to_json(orient='records', force_ascii=False)

            # 打印JSON格式的数据
            print(data_json)

            print(self.call_ai(f'{extra_msg}：{data_json}'))

            res = input('输入回车后关闭窗口===============>\n')
        else:
            print("错误：找到的Excel文件数不是1个，请确保目录中只有一个Excel文件。")

    # 获取当前路径下的excel表内容，返回dict
    def get_excel_data(self, file_name):
        """
        从指定文件名中获取Excel表内容，返回dict
        Args:
            file_name (str): 指定的Excel文件名（包括扩展名，如'data.xlsx'）
        Returns:
            dict: Excel文件内容转换后的字典
        """
        # 检查文件是否存在
        if not os.path.exists(file_name):
            print(f"文件 '{file_name}' 不存在")
            return None

        # 检查文件是否是Excel文件
        if not file_name.endswith(('.xlsx', '.xls')):
            print(f"文件 '{file_name}' 不是Excel文件（支持.xlsx或.xls）")
            return None

        print(f"读取Excel文件: {file_name}")

        try:
            # 读取Excel文件
            df = pd.read_excel(file_name)

            # 将DataFrame转换为字典（列表形式，每行一个字典）
            data_dict = df.to_dict(orient='records')

            # 返回字典数据
            return data_dict

        except Exception as e:
            print(f"读取文件 '{file_name}' 时发生错误: {e}")
            return None

class CompanyAI():
    def __init__(self, system = '' , uuid = '55018afa-c4b0-4c71-bcd7-82ade5ee41d8'):
        self.ai_url = 'http://39.105.101.103:8000/api/key/run'
        self.accessKey = '3f5a39d7-1e6b-40f5-b30f-e50c532f5b7b'
        self.secretKey = 'd25b514c-eff2-4779-9923-c63c0fcb09b2'
        # uuid是用于确定大模型种类的id，默认值是GPT4o的
        self.uuid = uuid
        # 用于设定AI的角色信息
        self.system = system

    def call_ai(self, msg, sessionId = ''):
        """
        调用AI接口

        Args:
            sessionId (str):会话id，指定当前请求属于哪次会话，第一次调用不用携带该参数，由服务器生成，返回给调用端，调用端下次发送请求可以携带该sessionId，表示和上次是同一策略的同一次会话
        """
        ts = self.get_timestamp()
        nonce = self.get_uuid()
        # 构造签名字符串
        tmp_str = f'POST|run|{ts}|{nonce}|{self.secretKey}'
        # 将tmp_str用md5处理，并转小写
        signature = self.to_lower_md5(tmp_str)
        # 构造post请求的headers
        headers = {
            'Authorization': f'{self.accessKey}:{ts}:{nonce}:{signature}',
            'Content-Type': 'application/json;UTF-8'
        }
        # 构造请求体
        data = {
            "uuid": self.uuid,
            # 用户输入的数组，支持不同类型，type： 1文本，2声音，3图片
            "inputs": [
                {
                    "type": 1,
                    "content": msg
                }
            ],
            "sessionId": sessionId,
            "params": [
                {"name": "UserAccount", "value": ""},
                {"name": "SystemMsg", "value": self.system},
                {"name": "MaxMessages", "value": "5"},
                {"name": "Temperature", "value": "0.8"},
                {"name": "TopP", "value": "0.9"},
                {"name": "MaxTokens", "value": "4096"},
                {"name": "Image", "value": ""},
                {"name": "Seed", "value": "0"},
                {"name": "PresencePenalty", "value": "0"},
                {"name": "FrequencyPenalty", "value": "0"},
                {"name": "Examples", "value": ""}
                # Examples对应的value为json格式的字符串，用于指导模型生成对话，必须为参数为“User”和“Assistant”的json数组，参考样式：[{\"User\":\"这是哪里？\",\"Assistant\":\"(开心)这是京城！\"},{\"User\":\"你是谁？\",\"Assistant\":\"(惊讶)你连我都不认识吗？！\"}]
            ]
        }
        res = requests.post(self.ai_url, headers = headers, json = data)
        res = res.json()
        print(res)
        return f"{res['outputs'][0]['content']}\n本次AI花费RMB：[{res['cost']}元]"

    def get_timestamp(self):
        """
        获取当前的秒级时间戳
        """
        return int(time.time())

    def get_uuid(self):
        """
        生成UUID
        """
        return uuid.uuid4()

    def to_lower_md5(self, string):
        """
        将传入的字符串转换为小写的md5值
        """
        # 创建 MD5 哈希对象
        md5_hash = hashlib.md5()

        # 更新哈希对象，确保编码为字节
        md5_hash.update(string.encode('utf-8'))

        # 返回MD5值的十六进制表示
        return md5_hash.hexdigest().lower()

    # 分析当前路径下的excel表
    def call_ai_to_excel(self, extra_msg):
        """
        分析当前路径下的excel表
        Args:
            extra_msg: 额外的要分析的内容，传入字符串

        Returns:None
        """
        # 获取当前目录下的所有文件
        files_in_directory = os.listdir('.')

        # 过滤出Excel文件，支持以'.xlsx'或'.xls'结尾的文件
        excel_files = [file for file in files_in_directory if file.endswith(('.xlsx', '.xls'))]

        # 检查是否只有一个Excel文件
        if len(excel_files) == 1:
            excel_file = excel_files[0]
            print(f"读取Excel文件: {excel_file}")

            # 读取Excel文件
            df = pd.read_excel(excel_file)

            # 将DataFrame转换为JSON格式，确保输出为可读的Unicode字符
            data_json = df.to_json(orient='records', force_ascii=False)

            # 打印JSON格式的数据
            print(data_json)

            print(self.call_ai(f'{extra_msg}：{data_json}'))

            res = input('输入回车后关闭窗口===============>\n')
        else:
            print("错误：找到的Excel文件数不是1个，请确保目录中只有一个Excel文件。")


if __name__ == '__main__':
    ai = AI()
    cai = CompanyAI()
    print(ai.get_excel_data('QA组常见问题Q&A.xlsx'))