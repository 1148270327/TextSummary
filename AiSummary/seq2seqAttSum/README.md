目录
==================
* [中文教程](#中文教程)
    * [语料和参数](#语料和参数)
    * [预测结果](#预测结果)
    * [attention可视化](#attention可视化)
    * [训练模型](#训练模型)

中文教程
=================
textsum基于tensorflow (1.0.0) 实现的Seq2Seq-attention模型, 来解决中文新闻标题自动生成的任务。
Seq2Seq模型的例子从原来的法语英语翻译的例子 translate.py 修改得到，同时我们在eval.py 模块中还提供了评价这种序列模型的计算ROUGE和BLEU分的方法。

语料和参数
---------------
我们选择公开的“搜狐新闻数据(SogouCS)”的语料，2012年6月—7月期间的搜狐新闻数据，包含超过1M 一百多万条新闻语料数据，新闻标题和正文的信息。数据集可以从搜狗lab下载。
http://www.sogou.com/labs/resource/cs.php
语料需要做分词和标签替换的预处理。模型训练在一台8个CPU核的Linux机器上完成，速度慢需耐心等待。

我们选取下列Seq2Seq-attention 模型参数: 
Encoder的LSTM:
*   num_layers = 4  # 4层LSTM Layer
*   size = 256      # 每层256节点
*   num_samples = 4096  #负采样4096
*   batch_size = 64     # 64个样本
*   vocab_size = 50000  # 词典50000个词

Bucket桶:
新闻正文截至长度为120个词，不足补齐PAD, 标题长度限制30个词。
buckets = [(120, 30), ...]

预训练模型的解压:
我们基于1M的搜狐新闻的语料预训练好了一个模型，因为大小限制所以分卷压缩上传。
在使用前需要合并后解压缩, 模型名为: headline_large.ckpt-48000.data-00000-of-00001,
被压缩为3卷: *.tar.gz00, *.tar.gz01, *.tar.gz02

```shell
#解压缩后的预训练模型文件为: headline_large.ckpt-48000.data-00000-of-00001

cd ./ckpt
cat headline_large.ckpt-48000.* > headline_large.ckpt-48000.data-00000-of-00001.tar.gz
tar xzvf headline_large.ckpt-48000.data-00000-of-00001.tar.gz
```

预测结果
---------------
### 交互式运行
linux下运行命令行，交互式输入中文分好词的新闻正文语料，词之间空格分割，结果返回自动生成的新闻标题。

```shell
python predict.py
```
输出结果例子
```shell
新闻:      中央 气象台 TAG_DATE TAG_NUMBER 时 继续 发布 暴雨 蓝色 预警 TAG_NAME_EN 预计 TAG_DATE TAG_NUMBER 时至 TAG_DATE TAG_NUMBER 时 TAG_NAME_EN 内蒙古 东北部 、 山西 中 北部 、 河北 中部 和 东北部 、 京津 地区 、 辽宁 西南部 、 吉林 中部 、 黑龙江 中部 偏南 等 地 的 部分 地区 有 大雨 或 暴雨 。
生成标题:  中央 气象台 发布 暴雨 蓝色 预警 华北 等 地 持续 暴雨

新闻:      美国 科罗拉多州 山林 大火 持续 肆虐 TAG_NAME_EN 当地 时间 TAG_DATE 横扫 州 内 第二 大 城市 科罗拉多斯 普林斯 一 处 居民区 TAG_NAME_EN 迫使 超过 TAG_NUMBER TAG_NAME_EN TAG_NUMBER 万 人 紧急 撤离 。 美国 正 值 山火 多发 季 TAG_NAME_EN 现有 TAG_NUMBER 场 山火 处于 活跃 状态 。
生成标题:  美国 多地 山火 致 TAG_NUMBER 人 死亡
...
```

### 预测和评估ROUGE分
运行命令行: python predict.py arg1 arg2 arg3
arg1 参数1: 输入分好词的新闻正文，每行一篇新闻报道;
arg2 参数2: 输入原本的人工的新闻标题，每行一个标题作为评估的Reference;
arg2 参数3: 生成的标题的返回结果。

进入目录
```shell
folder_path=`pwd`
input_dir=${folder_path}/news/test/content-test.txt
reference_dir=${folder_path}/news/test/title-test.txt
summary_dir=${folder_path}/news/test/summary.txt

python predict.py $input_dir $reference_dir $summary_dir

```

attention可视化
---------------
为了获得Decoder阶段的Attention矩阵, 我们需要对Tensorflow的标准运算符tf.nn.seq2seq进行适当的修改, 保存在了seq2seq_attn.py文件中。

### 运行 predict_attn.py文件
保存attention的Heatmap
```shell
# 调用 eval.py的模块的方法 plot_attention(data, X_label=None, Y_label=None)
# 保存每个预测样本的attention的Heatmap图像在img目录下
python predict_attn.py

```
Example:

训练模型
---------------
### 语料格式
将自己的textsum的语料分好词，分训练集和测试集，准备下列四个文件: content-train.txt, title-train.txt, content-dev.txt, title-dev.txt
要将新闻正文content和其对应标题title存在两个文件内，一行一个样本，例如:

content-train.txt
```shell
世间 本 没有 歧视 TAG_NAME_EN 歧视 源自于 人 的 内心 活动 TAG_NAME_EN “ 以爱 之 名 ” TAG_DATE 中国 艾滋病 反歧视 主题 创意 大赛 开幕 TAG_NAME_EN 让 “ 爱 ” 在 高校 流动 。 TAG_NAME_EN 详细 TAG_NAME_EN 
济慈 之 家 小朋友 感受 爱心 椅子  TAG_DATE TAG_NAME_EN 思源 焦点 公益 基金 向 盲童 孤儿院 “ 济慈 之 家 ” 提供 了 首 笔 物资 捐赠 。 这 笔 价值 近 万 元 的 物资 为 曲 美 家具 向 思源 · 焦点 公益 基金 提供 的 儿童 休闲椅 TAG_NAME_EN 将 用于 济慈 之 家 的 小孩子们 日常 使用 。 
...
```

title-train.txt
```shell
艾滋病 反歧视 创意 大赛 
思源 焦点 公益 基金 联手 曲 美 家具 共 献 爱心 ...
```

### 运行脚本
运行下列脚本训练模型，模型会被保存在ckpt目录下。
```shell
python headline.py
```
