import os
import threading
from PIL import Image
import time


def compress_resize(file2):
    # 打开要压缩的图片
    im = Image.open(file2)
    width, height = im.size
    # 宽高调整为原来的0.5倍
    width = int(width * 0.5)
    height = int(height * 0.5)
    # 压缩图片分辨率
    im = im.resize((width, height), Image.Resampling.LANCZOS)
    # 保存压缩后的图片
    im.save(file2,quality=100)

def compress_one_png(file1,file2):
    #使用pngquant压缩图片，
    # --quality rgb的范围，整体范围数值越大，压缩后颜色越鲜艳图片大小越大，1-100基本上和原图的颜色一样
    # --speed控制压缩速度和质量的均衡，1最慢11最快，默认为4
    os.system("pngquant --quality=1-100 --speed=11 "+file1+" --force -o "+file2)
	compress_resize(file2)
    print(file1," --→ ",file2)

def compress_one_folder(path1,path2):
    #获取文件夹中所有png图片
    files = [f for f in os.listdir(path1) if f.endswith(".png")]

    # 创建压缩文件夹
    if not os.path.exists(path2):
        os.mkdir(path2)

    # 创建多线程
    threads = []
    for file in files:
        file1 = os.path.join(path1,file)
        file2 = os.path.join(path2,file)
        thread = threading.Thread(target=compress_one_png, args=(file1,file2))
        threads.append(thread)
        thread.start()
    # 等待所有线程结束
    for thread in threads:
        thread.join()

def Size(folder_path):
    # 计算文件夹中所有png图片的大小之和
    total_size = 0
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".png"):
            file_path = os.path.join(folder_path, file_name)
            file_size = os.path.getsize(file_path)
            total_size += file_size
    return total_size

def pngquant_resize_1():
    start_time = time.time()
    path = r"D:\多个图片文件夹的上级文件夹"
    for i in os.listdir(path):
        path1 = os.path.join(path,i)
        if os.path.isdir(path1):
            path2 = path1
            compress_one_folder(path1,path2)
            t1 = Size(path1)
            t2 = Size(path2)
            print(f"\n原大小：{round(t1/1024/1024,2)} MB"
                  f"\n压缩后大小：{round(t2/1024/1024,2)} MB"
                  f"\n压缩率为：{round(((t1-t2)/t1)*100,2)}%\n")
    end_time = time.time()
    print("用时：",int(end_time - start_time/60),"min",round((end_time - start_time)%60,2),"s")


def pngquant_resize_2():
    #path1是源文件夹，path2是目标文件夹，当path1=path2，将直接替换图片
    start_time = time.time()
    path1 = r"D:\源文件夹"
    path2 = r"D:\新文件夹"
    compress_one_folder(path1,path2)
    t1 = Size(path1)
    t2 = Size(path2)
    print(f"\n原大小：{round(t1/1024/1024,2)} MB"
          f"\n压缩后大小：{round(t2/1024/1024,2)} MB"
          f"\n压缩率为：{round(((t1-t2)/t1)*100,2)}%\n")
    end_time = time.time()
    print("用时：",round(end_time - start_time,2),"s")

if __name__ == '__main__':
    pngquant_resize_1() # 压缩一个文件夹里所有一级子文件夹里的图片
    # pngquant_resize_2() # 压缩一个文件夹里所有图片
