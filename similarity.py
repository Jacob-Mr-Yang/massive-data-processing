import time
import csv
import os
from math import *
from multiprocessing import Pool, cpu_count, Manager

# 通过gbk解码方式打开该文本文件
filePath = "199801_clear(1).txt"
file = open(filePath, "r", encoding="gbk", errors = "ignore")
fileLines = file.readlines()
file.close()

# 打开停用词文件，并进行去除换行符的处理，为接下来的文章开头的比较做铺垫
stopWordsPath = "stop_words.txt"
stopWordsFile = open(stopWordsPath, "r", encoding="gbk", errors = "ignore")
stopWords = stopWordsFile.read()
stopWords = stopWords.split('\n')

# res = '[a-zA-Z0-9]'

# 进行文章开头的比较，通过比较文章开头来判断是否为同一篇文章
preBegin = fileLines[0][0:15]
essayContent = [] # 存储所有文章，每一个元素就是一篇文章
nowEssay = "" # 进行文章内每行文字的拼接

# 遍历文件中的每一行内容,去除空行
for content in fileLines:
    if content == '\n':
        continue
#     content = content[19:]
#     print(content)
    nowBegin = content[0:15]
    if nowBegin == preBegin:
        nowEssay += content
    else:
        essayContent.append(nowEssay)
        nowEssay = content
        preBegin = nowBegin
essayContent.append(nowEssay)

# 遍历去除空行之后的文章内容，取每行的前六个字节，通过比较来进行文章的分隔
wordsListByEssay = [] # 存储一维数组，该一维数组为将每篇文章的停用词去除后所形成的文章数组（存储所有文章）
for i in essayContent:
    words = i.split()
    wordsList = [] # 存储每篇文章中的非停用词
    for j in words:
        if j[0:6] == '199801':
            continue
        jNew = j.split('/')[0] #去除文章中的停用词
        if jNew in stopWords:
            continue
        wordsList.append(jNew)
    wordsListByEssay.append(wordsList) 

# 构建文本之间的文本向量
def vec_cos_sim(tfIdfA,tfIdfB):
    listA = []
    listB = []
    for wordA in tfIdfA:
        listA.append(tfIdfA[wordA])
        if wordA not in tfIdfB:
            listB.append(0)
        else:
            listB.append(tfIdfB[wordA])
    for wordB in tfIdfB:
        if wordB not in tfIdfA:
            listB.append(tfIdfB[wordB])
            listA.append(0)
    return listA,listB

# 余弦相似度的计算
def cos_sim(listA, listB):
    lenA = sum(a * a for a in listA) ** 0.5
    lenB = sum(b * b for b in listB) ** 0.5
    dot = sum(a * b for a, b in zip(listA, listB))
    cosine = dot / (lenA * lenB)
    return cosine

# 计算所有文本之间的相似度
sim = {}
startTime = time()
contentLength = len(wordsList)
for i in range(contentLength):
    for j in range(i+1, contentLength):
        listA, listB = vec_cos_sim(wordsList[i], wordsList[j])
        sim[(i, j)] = cos_sim(listA, listB)

def worker_with(lock, f):
    with lock:
        fs = open(f, 'a+')
        n = 10
        for i in range(start, end):
            simi = {}
            for j in range(0, N):
                if i == j:
                    continue
                commonWord = wordList[i].keys() & wordList[j].keys()
        fs.close()
        
def worker_no_with(lock, f):
    lock.acquire()
    try:
        fs = open(f, 'a+')
        n = 10
        for word in commonWord:
            if word not in wordList:
                wordList[word] = 0
                for k in range(0, N):
                    if word in wordList[k]:
                        count = wordList[word]
                        wordList[word] = count + 1
        fs.close()
    finally:
        lock.release()
    
if __name__ == "__main__":
    keywordCount = []
    with open('bag-of-words.csv')as f:
        fCsv = csv.reader(f)
        for row in fCsv:
            for i in range(len(row)):
                row[i] = int(row[i])
            keywordCount.append(row)       
    startTime = time.time()
    numCores = 3
    pool = Pool(numCores)
    similarityMatrix = Manager().list()
    for i in range(len(keywordCount)):
        pool.apply_async(cal_sim, args=(i, keywordCount, similarityMatrix))
    pool.close()
    pool.join()
    similarity_matrix = list(similarityMatrix)
    endTime = time.time()
    print("\nRunning time: ", endTime - startTime)
    print()

    startTime = time.time()
    resultFile = open("similarityMatrix.txt", 'w')
    for line in similarityMatrix:
        for i in line:
            resultFile.write(str(i) + ' ')
        resultFile.write('\n')
    resultFile.close()
    endTime = time.time()
    print("Running time: ", endTime - startTime)