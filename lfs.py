import os
import shutil
import hashlib

import argparse

def split_function():
    # Iterate through all files
    for root, dirs, files in os.walk('.'):
        # Iterate through all files
        for file in files:
            # Get the full path of the file
            file_path = os.path.join(root, file)
            # If the file size is greater than 50MB, split the file
            if os.path.getsize(file_path) > 50 * 1024 * 1024:
                print(f'Splitting file: {file_path}')
                # Calculate the file signature
                hasher = hashlib.sha256()
                with open(file_path, 'rb') as f:
                    hasher.update(f.read())
                signature = hasher.digest()
                # Save the signature
                signature_file = f'{file_path}.sha'
                with open(signature_file, 'wb') as f:
                    f.write(signature)

                with open(file_path, 'rb') as f:
                    file_number = 1
                    chunk_size = 50 * 1024 * 1024

                    chunk = f.read(chunk_size)
                    while chunk:
                        chunk_file = f'{file_path}.lfs.{str(file_number).zfill(4)}'
                        with open(chunk_file, 'wb') as chunk_f:
                            chunk_f.write(chunk)
                        
                        chunk = f.read(chunk_size)
                        file_number += 1
                # Delete the original file
                #os.remove(file_path)

    print('File split complete!')

def merge_function():
    # 定义一个字典，用于保存文件名
    split_files = {}

    # 遍历所有文件
    for root, dirs, files in os.walk('.'):
        # 遍历所有文件
        for file in files:
            # 如果文件名称中包含 .lfs.，则表示为小文件
            if '.lfs.' in file:
                file_path = os.path.join(root, file)
                # 获取文件名称中的原文件名
                file_name = file_path.split('.lfs.')[0]
                # 如果文件名不存在于字典中，则添加新的键值对
                if file_name not in split_files:
                    split_files[file_name] = []
                # 将文件名添加到字典中
                split_files[file_name].append(file_path)

    for original_file in split_files.keys():
        print(f'Merging file: {original_file}')
        with open(original_file, 'wb') as f:
            for split_file in sorted(split_files[original_file]):
                with open(split_file, 'rb') as split_f:
                    chunk = split_f.read()
                    f.write(chunk)
            
            if check_signature(original_file):
                os.remove(f'{original_file}.sha')
                for split_file in sorted(split_files[original_file]):
                    os.remove(split_file)
            else:
                os.remove(original_file)
                print('Signature mismatch')

    print('文件合并完成！')

def check_signature(filename):
    # Check if signature file exists
    signature_file = f'{filename}.sha'
    if not os.path.exists(signature_file):
        return True
    
    # Read in the signature
    with open(signature_file, 'rb') as f:
        signature = f.read()

    # Calculate the hash of the file
    hasher = hashlib.sha256()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(4096)
            if not data:
                break
            hasher.update(data)

    file_hash = hasher.digest()

    # Compare the calculated hash to the signature
    return file_hash == signature

# 创建 ArgumentParser 对象
parser = argparse.ArgumentParser()
# 定义参数
parser.add_argument('--split', action='store_true', help='Split the file')
parser.add_argument('--merge', action='store_true', help='Merge the file')
# 解析参数
args = parser.parse_args()

# 根据参数调用函数
if args.split:
    split_function()
elif args.merge:
    merge_function()
else:
    print('No action specified')
