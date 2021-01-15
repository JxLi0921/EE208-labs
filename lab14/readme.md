## File Structure

```powershell
D:\Desktop\homeworks\EE208\lab14-SearchByCNNFeatures
```

```powershell
├──code                                    # 代码
│  ├──extract_feature.py                   # 提取特征
│  ├──LSH_CNN.py                           # 用CNN提取特征的LSH
│  ├──similarityComputation.py             # 计算数据集中图片互相之间的相似度
│  ├──similarityDraw.py                    # 绘制两个相似矩阵对应点构成的散点图(a.png)
│  ├──testMatch.py                         # 测试用提取的特征进行匹配
│  ├──torchTest.py                         # 查看resnet50的参数
│  └──utilities.py                         # 一些本次实验常用到的函数写在一起
├──dataset                                 # 本次实验数据集
│  ├──0.jpg
│  ├──...(omitted)
├──dataset_12                              # 用于LSH的数据集
│  ├──1.jpg
│  ├──...(omitted)
├──testdata                                # 匹配用的测试数据
│  ├──earphone.jpg
│  └──phone.jpg
├──a.png                                   # 前面所说的画的图
├──angleMatrix.npy                         # 用角度表示的相似度矩阵
├──distMatrix.npy                          # 用欧氏距离表示的相似度矩阵
├──Dockerfile      
├──features_final.npy                      # 提取的特征
├──readme.md                               # 本文件
├──report.md                               # 报告(markdown version)
├──report.pdf                              # 报告(pdf version)
└──target.jpg                              # LSH target
```

