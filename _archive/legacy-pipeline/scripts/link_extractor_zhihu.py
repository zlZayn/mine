import re
import os

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))

# 在脚本所在目录下构建文件路径
file_path = os.path.join(script_dir, 'R 语言 - 知乎.txt')
output_file = os.path.join(script_dir, 'R 语言.txt')

# 正则表达式模式，用于匹配特定结构的链接
specific_link_pattern = re.compile(r'<a href="(http[^"]+)" target="_blank" rel="noopener noreferrer" data-za-detail-view-element_name="Title">(.*?)<\/a>')

# 读取整个文件内容并处理
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f, open(output_file, 'w', encoding='utf-8') as out:
    content = f.read()
    matches = specific_link_pattern.findall(content)
    for url, text in matches:
        #out.write(f"[{text}]({url})\n\n")
        out.write(f"{url}\n")

print(f"链接提取完成，已保存到: {output_file}")