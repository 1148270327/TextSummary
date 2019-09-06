#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   web_textsummary.py 
@Desciption    :   生成摘要、标题生成、主旨识别, 可替换不同方法进行测试
@Author    :   LensonYuan   
@Contact :   15000959076@163.com
@License :   (C)Copyright 2019-2021, HQ-33Lab

@Modify Time         @Version   
------------         --------
2019/8/28 17:38         1.0  
"""

from sanic import Sanic
from sanic.response import json as sanic_json
import json
from sanic import response
from jinja2 import Template
from Common.utils import project_path
from OtherSummary.textsum_method1 import TextSummary # method_1


app = Sanic()
app.static(uri='/statics/sample.json', file_or_directory= project_path()+'/ui/statics/sample.json')

@app.route('/api/CalcSummary/', methods=['GET', 'POST'])
async def CalcSummary(request):
    content = request_para(request)
    text = content.get('text')
    title = content.get('title')
    textsummary = TextSummary()
    textsummary.SetText(title, text)
    summary = textsummary.CalcSummary()
    print(summary)
    return sanic_json(summary)


@app.route('/', methods=['GET'])
async def index(request):
    # 直接返回静态文件
    with open(project_path() + '/ui/templates/index.html') as html_file:
        template = Template(html_file.read())
        return response.html(template.render(name='index'))


@app.route('/page', methods=['GET'])
async def index(request):
    para = request_para(request)
    up = para.get('up')
    num = int(para.get('num'))
    txt = json.load(open(project_path() + '/ui/statics/pages.json', encoding='utf8')).get('pages')
    # 下一页
    if up == '1' and num < len(txt)-1:
        one = {'title':txt[num + 1]['title'],'text':txt[num + 1]['text'], 'num': str(num + 1)}
        pass
    elif up == '1' and num == len(txt)-1:
        one = {'title': txt[0]['title'], 'text': txt[0]['text'], 'num': '0'}
    # 上一页
    elif up == '0' and num > 0:
        one = {'title': txt[num - 1]['title'], 'text': txt[num - 1]['text'], 'num': str(num - 1)}
    elif up == '0' and num == 0:
        one = {'title': txt[len(txt)-1]['title'], 'text': txt[len(txt)-1]['text'], 'num': str(len(txt)-1)}
    return sanic_json(one)


def request_para(request):
    """
    依据get、post参数不同位置，进行解析出标准请求参数
    :param request: sanic 请求对象, 目前参数要求是str
    :return: dict
    """
    if request.method.lower() == 'get':
        data = request.args
        pass
    elif request.method .lower() == 'post':
        data = request.form
        pass
    else:
        raise EOFError
    # 被json化的数据是在单独的字段中
    if data is None or len(data) == 0:
        data = request.json
    return data

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=888)