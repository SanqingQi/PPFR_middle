#!/usr/bin/env python 
# -*- coding:utf-8 -*-
from share_util import *
import pickle
import socket
import queue
from threading import Thread
import numpy


backIPaddress="127.0.0.1"
backport=9090
middleIPaddress1="127.0.0.1"
middleport1=9090
middleIPaddress2="127.0.0.1"
middleport2=9090

img_path="Your Path"
Q = 23740629843760239486723
BASE = 2
PRECISION_INTEGRAL = 16
PRECISION_FRACTIONAL = 32

database_path="facevec2.db"

def send_difference(data,client):
    differences=compute_dif(data,database_path)
    data=[0,differences]
    client.sendall(pickle.dumps(data))


#foreground process sends ID and corresponding seperated embedding vector
def save_vector(data):
    """
    保存用户的人脸分发向量
    :param data:
    :return:
    """
    embedding=numpy.array(float(data[1:]))
    embedding.astype('float64')
    embedding_path='server2/embeddings/'+str(data[0])+'_embedding.bin'
    np2file(embedding,embedding_path)
    insert(db_name=database_path,ID=data[0],Embedding=embedding_path)


def deal_listerner(client_socket,clientAddr,que):
    while(True):
        try:
            recv_data=client_socket.recv(8192)
            if not recv_data:
                client_socket.close()
            data=pickle.loads(recv_data)
            print('接收到的数据为:', data)
            assert len(data[1]) == 128
            if data[0]==0:
                que.put(data[1])
            else:
                save_vector(data[1])
        except:
            break

# listen to foreground process
def listener(que):
    """
    监听树莓派发送的信息
    data:[flag,[ID,embedding]]
    flag==1 注册人脸向量
    flag==0 识别人脸向量
    :param que:
    :return:
    """
    tcp_server_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_server_socket.bind((middleIPaddress1,middleport1))
    tcp_server_socket.listen(128)
    while(True):
        client_socket,clientAddr= tcp_server_socket.accept()
        print(client_socket)
        x=Thread(target=deal_listerner,args=[client_socket,clientAddr,que])
        x.start()


def speaker(que):
    """
    检查队列是否为空，若不为空，则计算所有的人脸向量欧氏距离并发送给后端服务器
    :param que:
    :return:
    """
    tcp_client_socket=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    tcp_client_socket.connect((backIPaddress,backport))
    while True:
        data=que.get(block=True,timeout=1e20)
        send_difference(data,tcp_client_socket)


#send calculation result to background process
def main():
    create_table(database_path)
    q=queue.Queue()
    t1=Thread(target=listener,args=[q])
    t2=Thread(target=speaker,args=[q])
    t1.start()
    t2.start()
    t1.join()
    t2.join()


if __name__=="__main__":
    main()
