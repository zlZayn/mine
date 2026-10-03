import re
import os

# 设置文件路径
html_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mine_R Language at main · zlZayn_mine.txt')
output_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extracted_github_links.txt')

# 定义要匹配的链接模式
link_pattern = r'href="(https://github\.com/zlZayn/mine/blob/main/R%20Language/[^" ]*?)"'

# 读取HTML文件内容
try:
    with open(html_file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # 提取符合模式的链接
    extracted_links = re.findall(link_pattern, html_content)
    
    # 去重
    unique_links = list(set(extracted_links))
    
    # 将链接写入输出文件
    with open(output_file_path, 'w', encoding='utf-8') as out:
        for link in unique_links:
            out.write(f"{link}\n")
    
    print(f"成功提取了 {len(unique_links)} 个链接")
    print(f"链接已保存到: {output_file_path}")
    
except Exception as e:
    print(f"处理文件时出错: {e}")