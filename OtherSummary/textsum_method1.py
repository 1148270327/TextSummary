#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   textsummary.py
@Desciption    :   针对会答数据提供策略生成摘要缩略图, 返回字符串，空串为默认值
@Author    :   LensonYuan
@Contact :   15000959076@163.com
@License :   (C)Copyright 2019-2021, HQ-33Lab

@Modify Time         @Version
------------         --------
2019/8/28 16:38         1.0
"""

from Common.jieba_seg import Sentence2terms
import logging as log_exp
import re

seg =Sentence2terms()

class TextSummary:
    text = ""
    title = ""
    pos_point = list()
    keywords = set()
    sentences = list()
    summary = list()

    def SetText(self, title, text):
        self.title = title
        self.pos_point = ['fa', 'ca',  'n', 'nt', 'nz', 'ns', 'ng', 'nr', 'nl', 'nsf', 'v', 'vn', 'adj', 'vd', 'l', 'd']
        self.text = text

    def __SplitSentence(self):
        # 通过换行符对文档进行分段
        sections = self.text.split("\n")
        for section in sections:
            if section.strip() == "":
                sections.remove(section)

        # 通过分割符对每个段落进行分句
        for i in range(len(sections)):
            section = sections[i]
            text = ""
            k = 0
            for j in range(len(section)):
                char = section[j]
                text = text + char
                if char in ["!",  "。", "？", '；', ';'] or j == len(section)-1:
                    sentence = dict()
                    sentence["text"] = text.strip()
                    sentence["pos"] = dict()
                    sentence["pos"]["x"] = i
                    sentence["pos"]["y"] = k
                    # 将处理结果加入self.sentences
                    if sentence['text'] != '':
                        self.sentences.append(sentence)
                    text = ""
                    k = k + 1

        # 对文章位置进行标注，通过mark列表，标注出是否是第一段、尾段、第一句、最后一句
        for sentence in self.sentences:
            pos = sentence["pos"]
            pos["mark"] = list()
            if pos["x"] == 0:
                pos["mark"].append("FIRSTSECTION")
            if pos["y"] == 0:
                pos["mark"].append("FIRSTSENTENCE")
            if pos["x"] == self.sentences[len(self.sentences)-1]["pos"]["x"]:
                pos["mark"].append("LASTSECTION")

    def __CalcKeywords(self):
        # 计算tf-idfs，取出排名靠前的20个词
        words_best = list()
        words_best = words_best + seg.top_words_extract(self.text, topK=20,allowPOS=self.pos_point)[0]

        # 提取第一段的关键词
        parts = self.text.lstrip().split("\n")
        first_part = ""
        if len(parts) >= 1:
            first_part = parts[0]
        words_best = words_best + seg.top_words_extract(first_part, topK=5, allowPOS=self.pos_point)[0]
        # 提取title中的关键词
        words_best = words_best + seg.top_words_extract(self.title, topK=3,allowPOS=self.pos_point)[0]
        # 去除单一的词以及停用词
        keywords = set(filter(lambda x: len(x) > 1 and not seg.is_stop_words(x), words_best))
        self.keywords = keywords

    def __CalcSentenceWeightByKeywords(self):
        # 计算句子的关键词权重
        for sentence in self.sentences:
            sentence["weightKeywords"] = 0
        for keyword in self.keywords:
            for sentence in self.sentences:
                if sentence["text"].find(keyword) >= 0:
                    sentence["weightKeywords"] = sentence["weightKeywords"] + 1

    def __CalcSentenceWeightByPos(self):
        # 计算句子的位置权重
        for sentence in self.sentences:
            mark = sentence["pos"]["mark"]
            weightPos = 0
            if "FIRSTSECTION" in mark:
                weightPos = weightPos + 2
            if "FIRSTSENTENCE" in mark:
                weightPos = weightPos + 2
            if "LASTSENTENCE" in mark:
                weightPos = weightPos + 1
            if "LASTSECTION" in mark:
                weightPos = weightPos + 1
            sentence["weightPos"] = weightPos

    def __CalcSentenceWeightByCueWords(self):
        # 计算句子的线索词权重
        index = ["点击", "右上角", "老师", "同学", "你好", '您好', '为您解答', '是不是', '结束', '明白', '疑问', '关注', '评价', '请问', '对吗', '红包', '抢答', '谢谢', '满意', '客气']
        for sentence in self.sentences:
            sentence["weightCueWords"] = 0
            sentence["weightLength"] = 0
        for i in index:
            for sentence in self.sentences:
                sentence['text'] = sentence['text'].strip()
                if len(sentence["text"]) > 4:
                    sentence["weightLength"] = 1
                if sentence["text"].find(i) != 0:
                    sentence["weightCueWords"] = 1

    def __CalcSentenceWeight(self):
        self.__CalcSentenceWeightByPos()
        self.__CalcSentenceWeightByCueWords()
        self.__CalcSentenceWeightByKeywords()
        for sentence in self.sentences:
            sentence["weight"] = sentence["weightPos"] + 2 * sentence["weightCueWords"] + sentence["weightKeywords"]+sentence['weightLength']

    def CalcSummary(self, ratio=0.1):
        # 清空变量
        self.keywords = set()
        self.sentences = list()
        self.summary = list()
        try:
            # 调用方法，分别计算关键词、分句，计算权重
            self.__SplitSentence()
            self.__CalcKeywords()
            self.__CalcSentenceWeight()
            # 对句子的权重值进行排序
            self.sentences = sorted(self.sentences, key=lambda k: k['weight'], reverse=True)
        except Exception as e:
            log_exp.error('summary text error: %s', repr(e))
            return ''

        # 根据排序结果，取排名占前X%的句子作为摘要
        # print(len(self.sentences))
        for i in range(len(self.sentences)):
            if i < ratio * len(self.sentences):
                sentence = self.sentences[i]
                self.summary.append(sentence["text"])

        if self.summary.__len__() == 0:
            return ''
        else:
            rs = self.summary[0]
            if len(rs) > 60:
                return ''
            return rs


def kuaida_sentence_core(sentence):
    xx = re.split('[^\w\u4e00-\u9fff]+', sentence)

    pass

if __name__ =='__main__':
    sf = kuaida_sentence_core('keynote:对方公司在我方账里是应付账款，收到退货款时，借银行，贷应付账款－xx公司，贷方金额用负号吗？')
    exit()
    ts = TextSummary()
    ts.SetText(title='财产补税的基本特征是橼嚟，租金收入是指租房产生的费用', text='老板私人车，在公司报销车辆维修费，过路费，燃油税这些，计入哪里？\n你好\n计入管理费用-办公费\n全部吗？\n都记入办公费里面？\n只要是老板车产生的费用，都记入办公费？\n是的\n不算福利费\n不算\n好的，谢谢老师\n不客气\n麻烦点击结束评价一下\n此次评价为：非常满意此次评价为：很满意')
    summ = ts.CalcSummary()
    print(summ)