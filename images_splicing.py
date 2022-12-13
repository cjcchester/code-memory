import os
from PIL import Image
'''
'横向与纵向拼接，适用图片宽高差不多的图片
'''

# 读取图片文件并保存在一个列表中
def load_images(path,sort=False):
    # 读取目录中所有图片文件
    files = [f for f in os.listdir(path) if f.endswith('.png') or f.endswith('.jpg') or f.endswith('.jpeg')]
    if sort:
        files.sort() #升序
        # files.sort(reverse=True) #逆序
    images = []
    print("拼接图片：")
    for file in files:
        if "horizontal" not in os.path.basename(file) and "vertical" not in os.path.basename(file):
            print(os.path.basename(file))
            img = Image.open(os.path.join(path,file))
            images.append(img)
    return images

def get_max_dimensions(images):
    max_width = 0
    max_height = 0

    for image in images:
        width, height = image.size
        if width > max_width:
            max_width = width
        if height > max_height:
            max_height = height

    return (max_width, max_height)


# 将图片按照给定宽度等比例放大
def resize_image_w(img, width):
    # 计算等比例放大后图片的高度
    height = int(width * img.height / img.width)
    # 按照给定高度等比例放大图片
    img = img.resize((width, height), resample=Image.Resampling.LANCZOS)
    return img

# 将图片按照给定高度等比例放大
def resize_image_h(img, height):
    width = int(height * img.width / img.height)
    img = img.resize((width, height), resample=Image.Resampling.LANCZOS)
    return img

# 将多张图片拼接在一起
# direction: 拼接方向，可选值为 "horizontal"、"vertical"
# height: 长图的高度
def combine_images(images, direction):

    # 找出原始图片中，最大的宽高
    max_width,max_height = get_max_dimensions(images)
    a,b=[],[]
    # 原始图片经过放大后，宽高发生变化，从而最大宽高也可能发生变化
    for img in images:
        t1 = resize_image_h(img,max_height)
        t2 = resize_image_w(img, max_width)
        a.append(t1.width)
        a.append(t2.width)
        b.append(t1.height)
        b.append(t2.height)

    if direction == "vertical":
        # 计算拼接后图片的宽度和高度
        width = max_width
        # 这里为简便，直接取了所有值的最大值，会导致长图的最后将有空白画布，在后面进行去除
        height = max(b)*len(images)
        # 创建一张新图片
        combined = Image.new('RGB', (width, height))
        # 将每张图片拼接到新图片上
        y_offset = 0
        for img in images:
            img = resize_image_w(img,width)
            combined.paste(img, (0, y_offset))
            y_offset += img.height

    elif direction == "horizontal":
        # 计算拼接后图片的宽度和高度
        width = max(a)*len(images)
        height = max_height
        # 创建一张新图片
        combined = Image.new('RGB', (width, height))
        # 将每张图片拼接到新图片上
        x_offset = 0
        for img in images:
            img = resize_image_h(img, height)
            combined.paste(img, (x_offset, 0))
            x_offset += img.width
    # 去除空白画布
    combined = combined.crop(combined.getbbox())
    return combined

# 保存拼接好的长图
def save_image(image, path):
    # 无损保存
    image.save(path,quality=100)
    print("图片拼接成功！")

# 测试代码
if __name__ == '__main__':
    path = r"D:\音视频图\图片\图片拼接"
    images = load_images(path)
    vertical = combine_images(images, "vertical")
    save_image(vertical, os.path.join(path, 'vertical.jpg'))
    horizontal = combine_images(images, "horizontal")
    save_image(horizontal, os.path.join(path, 'horizontal.jpg'))
