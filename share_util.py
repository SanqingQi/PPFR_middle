#!/usr/bin/env python
# -*- coding:utf-8 -*-
import numpy as np
from PIL import Image
import random

img_path="Your Path"
Q = 23740629843760239486723
BASE = 2
PRECISION_INTEGRAL = 16
PRECISION_FRACTIONAL = 32

import sqlite3


def insert(db_name,ID,Embedding):
    """
    :param db_name: str name of db
    :param ID: int
    :param U_NAME: str
    :param Embedding: str The embedding bin file path
    :param ImagePath: str The image bin file path
    :return: void
    test_info: Success
    Attention Please: It's better if the path is absolute path!!!!
    """
    conn = sqlite3.connect(db_name)
    print("Opened database successfully")
    c = conn.cursor()
    c.execute("INSERT INTO PrivacyData (ID,Embedding) \
          VALUES (?, ?)",(int(ID),Embedding))
    print("Table inserted successfully")
    conn.commit()
    conn.close()

def create_table(db_name):
    """
    :param db_name: str name of db
    :return: void
    test_info: Success
    """
    conn = sqlite3.connect(db_name)
    print("Opened database successfully")

    c = conn.cursor()
    c.execute('''CREATE TABLE PrivacyData
           (ID INT PRIMARY KEY     NOT NULL,
           Embedding            CHAR(200)     NOT NULL
           );''')
    print("Table created successfully")
    conn.commit()
    conn.close()

def select(db_name, attr):
    """
    :param db_name: str
    :param attr: str name of selected attribute
    :return:
    test_info: Success
    """
    conn = sqlite3.connect(db_name)
    print("Opened database successfully")
    c = conn.cursor()
    cursor = c.execute("SELECT ? from PrivacyData", (attr,))
    conn.commit()
    conn.close()
    return cursor

def delete_by_id(db_name, id):
    """
    :param db_name: str name of database
    :param id: int
    :return: Null
    test_info: Success
    """
    conn = sqlite3.connect(db_name)
    print("Opened database successfully")

    c = conn.cursor()
    c.execute('''Delete From PrivacyData Where ID = ?''', (id,))
    print("Delete successfully")
    conn.commit()
    conn.close()

def share(secret):
    secret=secret * BASE ** PRECISION_FRACTIONAL #把小数转换为整数
    a1=Q*random.random()
    share_1=(secret+a1*1)%Q
    share_2=(secret+a1*2)%Q
    share_1=share_1.astype('float64')
    share_2=share_2.astype('float64')
    return share_1,share_2

def decode(share_1,share_2):
    result=share_1*2-share_2
    map_negative_range = np.vectorize(lambda element: element if element <= Q / 2 else element - Q)
    return map_negative_range(result) / BASE ** PRECISION_FRACTIONAL


def img2np(img_path):
    """
    将图片转换为矩阵
    test_info: Success
    """
    img = Image.open(img_path)
    result = np.asarray(img)
    result = result.astype('int32')
    return result


def np2img(array):
    """
    把矩阵转换为图片
    test_info: Success
    """
    array = np.array(array, dtype='uint8')
    image = Image.fromarray(array)
    image.show()


def np2file(array, fileName):
    """
    numpy转换为二进制文件
    test_info: Success
    """
    array.tofile(fileName)


def file2np(fileName, d_type='float64', shape=None):
    """
    字符串转换为numpy数组
    array_str: str
    array_size: numpy array
    test_info: Success
    """
    if shape is None:
        array = np.fromfile(fileName, dtype=d_type)
    else:
        array = np.fromfile(fileName, dtype=d_type).reshape(shape)
    return array

def compute_dif(target, db_name):
    """
    :param target: 128*1 embedding of person
    :param db_name: name of database which contains many embeddings
    :return: difference of embeddings n*128
    test_info: Success
    """
    assert len(target) == 128
    target = target.astype('float64')
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    path_lists = c.execute("SELECT Embedding from PrivacyData")
    differences = []
    for path in path_lists:
        p=''.join(path) # type(path) is tuple, convert it to str
        differences.append(target-file2np(p))
    conn.commit()
    conn.close()
    return differences


