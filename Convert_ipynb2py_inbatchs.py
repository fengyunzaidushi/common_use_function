
import os
from nbconvert import PythonExporter
import json
import nbformat
# 要转换的文件夹路径
root_folder_path = '/mnt/sda/github/10yue/openai-cookbook/ceshi'
import re
# 创建一个导出器对象
exporter = PythonExporter()

# 使用 os.walk 遍历文件夹和子文件夹
for foldername, subfolders, filenames in os.walk(root_folder_path):
    for filename in filenames:
        # 检查是否为 ipynb 文件
        if filename.endswith('.ipynb'):
            notebook_path = os.path.join(foldername, filename)
            output_path = os.path.join(foldername, filename.replace('.ipynb', '.py'))

            # 使用 nbformat 读取 notebook
            notebook_content = nbformat.read(notebook_path, as_version=4)

            # 导出为 Python 格式
            python_script, _ = exporter.from_notebook_node(notebook_content)
            python_script = python_script.replace('get_ipython().system', '#')
            python_script = python_script.replace('display', '#display')
            rex = re.compile(r'# In.*')
            for item in rex.findall(python_script):
                python_script = python_script.replace(item, '')

            # print(repr(python_script))
            while '\n\n\n' in python_script:
                python_script = python_script.replace('\n\n\n', '\n\n')

            # 写入到新的 Python 文件
            with open(output_path, 'w', encoding='utf-8') as python_file:
                python_file.write(python_script)
