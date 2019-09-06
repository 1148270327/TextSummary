import pickle
import os
import logging, time

def singleton (cls, *args, **kwargs):
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
class Debug_hangder(object):
    '''通过继承实现的单例模式是有点突出的。因为它跟其他方式有点不同，它是通过new方法的改造实现的。如果之前有就返回之前的实例；如果没有，就创建新的实例。'''
    # def __new__(cls, *args, **kwargs):
    #     # singleton mode
    #     if not hasattr(cls, '_instance'):
    #         cls._instance = super().__new__(cls)
    #     return cls._instance

    def __init__(self):
        print('init Debug_hangder...')
        self.log = self.make_hander('utils')


    def get_logger(self, name= None):
        if name is None:
            return self.log
        else:
            return self.make_hander(name)

    def make_hander(self,log_name):
        print('make new debug hander: ',log_name)
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.INFO)

        # 创建一个handler，用于写入日志文件
        log_path =os.path.abspath(os.path.join(os.path.dirname(__file__), "../loginfo"))
        name = log_path + '/' + time.strftime("%Y%m%d") + '.log'
        if not os.path.isdir(log_path):
            os.makedirs(log_path)
        fh = logging.FileHandler(filename=name, mode='w')
        fh.setLevel(logging.WARNING)

        # 再创建一个handler，用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)#服务器运行时改成info

        # 定义handler的输出格式
        formatter = logging.Formatter('%(asctime)-8s %(filename)-8s %(levelname)-8s %(name)-12s [line:%(lineno)d]  %(message)s')
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # 给logger添加handler
        logger.addHandler(fh)
        logger.addHandler(ch)
        return logger

log_exp = Debug_hangder().get_logger()

#获取项目路径
def project_path():
    return os.path.abspath(os.path.join(os.path.dirname(__file__),'../'))

#序列化到文件
def file_obj_convert(fileName='/data/k_df.pkl',obj = None):
    path = project_path()+fileName
    if obj is not None:
        print('开始写入文件：'+path)
        # 序列化
        with open(path, 'wb') as f:
            pickle.dump(obj, f)
            print('写入结束')
    else:
        print('开始读取数据：' + path)
        # 反序列化
        with open(path, 'rb') as f:
            Person = pickle.load(f)
        print('读取完毕')
        return Person

if __name__=='__main__':
    log_exp.error('run one')
    log_exp.error('run two')
    log_exp.error('run three')