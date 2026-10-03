# 提取GitHub链接并生成HTML卡片
# 使用CSS选择器来定义卡片样式
import os
import re
import urllib.parse


def create_html_card(title, url, index, total_cards):
    gradient_class = generate_gradient(index, total_cards)
    # 只保留需要动态生成的颜色类，其他样式通过CSS选择器定义
    return f'''    <a href="{url}" target="_blank" class="article-card-link">
        <div class="article-card">
            <div class="article-card-gradient {gradient_class}"></div>
            <div class="article-card-content">
                <h3 class="article-card-title">{title}</h3>
            </div>
        </div>
    </a>
'''


def generate_gradient(index, total_cards):
    # 定义基础色调名称（使用彩虹色顺序：红、橙、黄、绿、蓝、靛、紫）
    color_names = ['red', 'orange', 'amber', 'yellow', 'emerald', 'teal', 'blue', 'indigo', 'violet', 'purple', 'pink', 'rose']
    
    # 计算线性均匀分布的颜色索引
    color_index = int((index / total_cards) * len(color_names))
    color_name = color_names[color_index % len(color_names)]
    
    # 使用Tailwind CSS标准色阶值（100-900）
    light_shade = 300  # 浅色
    dark_shade = 600   # 深色
    
    return f'bg-gradient-to-r from-{color_name}-{light_shade} to-{color_name}-{dark_shade}'


def extract_title_from_url(url):
    """
    从GitHub URL中提取标题
    例如：从"https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91broom%20Package%20for%20Tidy%20Modeling.md" 
    提取出 "【R Language】broom Package for Tidy Modeling"
    """
    # 提取URL中的文件名部分
    path_parts = url.split('/')
    file_name = path_parts[-1]
    
    # 解码URL编码的字符
    decoded_name = urllib.parse.unquote(file_name)
    
    # 移除文件扩展名
    title = decoded_name.replace('.md', '')
    
    return title


def main():
    # 读取原始HTML文件
    # 获取脚本所在目录的绝对路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 在脚本所在目录下构建文件路径
    html_file_path = os.path.join(script_dir, 'mine_R Language at main · zlZayn_mine.txt')
    
    # 检查文件是否存在
    if not os.path.exists(html_file_path):
        print(f"错误：找不到文件 {html_file_path}")
        return
    
    # 读取HTML文件内容
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # 提取符合模式的链接
        link_pattern = r'href="(https://github\.com/zlZayn/mine/blob/main/R%20Language/[^" ]*?)"'
        extracted_links = re.findall(link_pattern, html_content)
        
        # 去重
        urls = list(set(extracted_links))
        
        print(f"成功提取了 {len(urls)} 个链接")
        
        # 提取标题和URL
        cards_data = []
        for url in urls:
            title = extract_title_from_url(url)
            cards_data.append((title.strip(), url.strip()))
            
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return
    
    # 生成HTML，添加CSS样式定义
    html_content = '''<!DOCTYPE html>
<html lang="zh-CN">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>R Language</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 使用CSS选择器定义卡片样式 */
        .article-card-link { display: block; }
        .article-card {
            background-color: white;
            border-radius: 0.5rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            overflow: hidden;
            transition: all 300ms ease;
            height: 8rem;
            display: flex;
            flex-direction: column;
        }
        .article-card:hover {
            transform: translateY(-0.5rem);
            box-shadow: 0 10px 18px -3px rgba(0, 0, 0, 0.1), 0 4px 8px -2px rgba(0, 0, 0, 0.06);
        }
        .article-card-gradient {
            height: 0.5rem;
            transition: all 300ms ease;
        }
        .article-card:hover .article-card-gradient { height: 0.75rem; }
        .article-card-content {
            padding: 1rem;
            flex: 1;
            display: flex;
            align-items: center;
        }
        .article-card-title {
            font-size: 1.125rem;
            font-weight: 600;
            color: #1f2937;
            line-height: 1.5;
        }
    </style>
</head>
<body class="bg-gray-50 p-6 pt-16 min-h-screen">
     <div class="max-w-7xl mx-auto">
         <!-- 标题 -->
         <div class="text-center mb-10">
             <h1 class="text-4xl font-bold text-gray-800 mb-2">R Language</h1>
             <p class="text-gray-600">Github Column</p>
         </div>
         
         <!-- 卡片网格布局 -->
         <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-2 lg:grid-cols-2 gap-6">
'''
    
    total_cards = len(cards_data)
    for i, (title, url) in enumerate(cards_data):
        html_content += create_html_card(title, url, i, total_cards)
        
        # 每3个卡片后添加换行（保持代码格式）
        if (i + 1) % 3 == 0:
            html_content += '\n'
    
    html_content += '''        </div>
     </div>
 </body>
 </html>'''
    
    # 保存HTML文件
    output_file = os.path.join(script_dir, 'article_cards_github.html')
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    print(f'HTML卡片生成完成，已保存到: {os.path.abspath(output_file)}')


if __name__ == "__main__":
    main()