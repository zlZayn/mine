import os
import re

# 设置目录路径
dir_path = r"d:\ObsidianDirectory\zhihu"
# 设置输出子文件夹路径
output_dir = os.path.join(dir_path, "processed_files")

# 确保输出文件夹存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# 获取目录下所有.md文件
all_files = [f for f in os.listdir(dir_path) if f.endswith('.md')]

# 遍历每个文件
for filename in all_files:
    # 检查文件名是否包含"-落日阳红的文章"
    if "-落日阳红的文章" in filename:
        # 创建新文件名（删除"-落日阳红的文章"部分）
        new_filename = filename.replace("-落日阳红的文章", "")
        
        # 构建完整的文件路径
        old_filepath = os.path.join(dir_path, filename)
        new_filepath = os.path.join(output_dir, new_filename)
        
        try:
            # 读取文件内容
            with open(old_filepath, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 删除YAML头（从---开始到下一个---结束的部分）
            modified_content = re.sub(r'^---\s*[\s\S]*?\s*---\s*', '', content, count=1)
            
            # 将代码块语言标注改为R
            # 只匹配并修改代码块的开始标记（```后面有字符），不修改结束标记（只有```）
            modified_content = re.sub(r'(```)\s*[a-zA-Z0-9]+\s*$', '```R', modified_content, flags=re.MULTILINE)
            
            # 保存修改后的内容到新文件
            with open(new_filepath, 'w', encoding='utf-8') as file:
                file.write(modified_content)
            
            print(f"Processed: {filename} -> {os.path.join('processed_files', new_filename)}")
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")

print("All files processed!")