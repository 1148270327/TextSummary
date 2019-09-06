#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
@File    :   jieba_seg.py
@Desciption    :   分词器封装；以单例模式实现，每次调用示例： segK, PR = Sentence2terms().wordSegment_tag('对于资金收入的问题，此次人工评价为：非常满意', HMM=True)
@notice        :   jieba自定义词典的在单个词重复的情况下，和词频无关，取决于词最后加载的那个词性
@Author    :   LensonYuan
@Contact :   15000959076@163.com
@License :   (C)Copyright 2019-2021, HQ-33Lab

@Modify Time         @Version
------------         --------
2019/8/28 16:38         1.0
"""
import jieba
import jieba.posseg as pseg
from jieba import analyse
import re
from common.utils import log_exp, project_path


def singleton(cls, *args, **kwargs):
    '''
    static singleton mode wraper
    :param cls:
    :param args:
    :param kwargs:
    :return:
    '''
    instances = {}
    def get_instance (*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
            return instances[cls]
        else :
            return instances[cls]
    return get_instance

@singleton
class Sentence2terms(object):
    # def __new__(cls, *args, **kwargs):
    #     # singleton mode
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super().__new__(cls, *args, **kwargs)
    #     return cls._instance

    def __init__(self):
        self.jieba_initialize()
    '''
    initialize jieba Segment
    '''
    def jieba_initialize(self):
        #结巴可以添加两个词典，是add过程
        log_exp.debug('initialize jieba vocab...')
        jieba.load_userdict(project_path() + '/resource/segDic/others.txt')
        jieba.load_userdict(project_path() + '/resource/segDic/THUOCL_caijing.txt')
        # jieba.load_userdict(utils.project_path() + '/resource/segDic/vocab.txt') # 当前词典很多和其他词典覆盖的地方，不能直接用
        self.stopwords = {line.strip() for line in open(project_path()+'/resource/segDic/stop_words.txt', 'r').readlines()}
        jieba.initialize()

    '''
    Segment words by jieba，自定义词典有效
    '''
    def wordSegment(self, text, cut_all=False, HMM=True):
        '''

        :param text:
        :param cut_all: 精准模式、全模式；精确模式，试图将句子最精确地切开，适合文本分析；
                全模式，把句子中所有的可以成词的词语都扫描出来, 速度非常快，但是不能解决歧义；
        :param HMM:是否启用马尔科夫模型
        :return:
        '''
        seg_list = jieba.lcut(text,cut_all=cut_all,HMM=HMM)
        result = " ".join(seg_list)
        return seg_list, result

    '''
    POS Tagging，自定义词典可能无效，会被内部hmm给替换掉
    '''
    def wordSegment_tag(self, text, HMM=True):
        words = pseg.lcut(text, HMM)
        p_t =''
        for term, pos in words:
            p_t+=term+'/'+pos+' '
        return words, p_t

    '''
     Segment words by jieba
     '''

    def wordSegment_search(self, text, HMM=True, isFilter =True):
        '''

        :param text:
        :param isFilter: true
        :param HMM:是否启用马尔科夫模型
        :return:
        '''
        seg_list = jieba.lcut_for_search(text, HMM=HMM)
        seg_filter = []
        if isFilter:
            for per in seg_list:
                per = per.strip()
                if per == '' or re.match('^(。|\.|\?|？|，|,|:|：|；|;|\'|"|!|！)$', per):
                    continue
                else:
                    seg_filter.append(per)
        result = " ".join(seg_filter)
        return seg_filter, result
    '''
    stopwords filter
    '''
    def is_stop_words(self, term):
        if term in self.stopwords: return True
        else: return False


    # '''
    # singal instance
    # '''
    # @staticmethod
    # def instance():
    #     return Sentence2terms()


    def top_words_extract(self, text, topK=800, withWeight=False, allowPOS=[]):
        """
        对文本进行主题词提取
        :param text:
        :return:
        """
        word_lst = analyse.extract_tags(text, topK=topK, withWeight=withWeight, allowPOS=allowPOS)
        result = " ".join(word_lst)
        return word_lst, result


'''
去除带tag的words中重复的pair
'''
def tag_words_unique(wordSegWithTagLst):
    tmp =[]
    for word, flag in wordSegWithTagLst:
        newPair = pseg.pair(word,flag)
        if newPair in tmp:
            log_exp.debug('duplicate word:%s',word+'/'+flag)
        else:
            tmp.append(newPair)
    return tmp



if __name__=='__main__':
    #jieba.load_userdict(utils.project_path() + '/resource/segDic/student_teacher_filter.txt')
    segK, PR = Sentence2terms().wordSegment_tag('对于资金收入的问题，此次人工评价为：非常满意', HMM=True)
    print(PR)
    xx = Sentence2terms().top_words_extract("老板私人车，在公司报销车辆维修费，过路费，燃油税这些，计入哪里？\n你好\n计入管理费用-办公费\n全部吗？\n都记入办公费里面？\n只要是老板车产生的费用，都记入办公费？\n是的\n不算福利费\n不算\n好的，谢谢老师\n不客气\n麻烦点击结束评价一下\n此次评价为：非常满意此次评价为：很满意", topK=20)
    print(xx)
    exit()
    # tag_words_unique(segK)
    # segK, PR = Sentence2terms().wordSegment_search('我来到北京清华大学')
    # print(PR)
    #
    # print(Sentence2terms().is_stop_words('什么'))
    with open('/Users/lensonyuan/gitLocal/IntelligentAnswer/result/question_filter.txt', mode='r') as f:
        lines = f.readlines()
        for line in lines:
            segK, PR = Sentence2terms().wordSegment_tag(line)
            print(PR)

