# coding=utf-8
from flask import Flask
from AIBaseClass import AI

app = Flask(__name__)

ai = AI('''
    你好，我是一个AI，我可以帮你分析当前路径下的output.xlsx文件
''')

@app.route('/')
def hello():
    return "Hello, Flask!"

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 22333, debug=True)