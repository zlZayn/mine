import os
import subprocess
import sys
import webbrowser

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 要运行的脚本列表
scripts = [
    "html_card_generator_github.py",
    "html_card_generator_zhihu.py",
    "generate_dynamic_template.py",
    "generate_combined_cards.py"
]

# 按顺序运行每个脚本
for script in scripts:
    print(f"\n  正在运行：{script}...")
    script_path = os.path.join(current_dir, script)
    # 使用check_call简化错误处理
    subprocess.check_call([sys.executable, script_path])

# 用浏览器打开最后生成的HTML文件
final_html_path = os.path.join(current_dir, "combined_article_cards.html")
webbrowser.open(final_html_path)
print(f"\n  已打开生成的HTML文件：{final_html_path}")

print("\n\n  所有脚本运行完成！\n\n")
