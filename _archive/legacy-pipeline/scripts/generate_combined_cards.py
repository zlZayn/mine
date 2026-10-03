# 用于处理文章卡片模板的脚本
# 将github和zhihu的文章信息填充到模板中
import re

# 读取模板文件
with open(r'd:\PythonDirectory\知乎\dynamic_article_card_template.txt', 'r', encoding='utf-8') as f:
    template = f.read()

# 使用正则表达式去除HTML注释和CSS注释
# 去除HTML注释: <!-- 注释内容 -->
template = re.sub(r'<!--[\s\S]*?-->', '', template)
# 去除CSS注释: /* 注释内容 */
template = re.sub(r'\/\*[\s\S]*?\*\/', '', template)
# 去除多余的空行
template = re.sub(r'\n\s*\n', '\n', template).strip()

# 定义替换映射
replacements = {
    '{{ article_english_title_1 }}': '【R Language】Anonymous Functions',
    '{{ article_chinese_title_1 }}': '【R 语言】匿名函数',
    '{{ article_english_link_1 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91Anonymous%20Functions.md',
    '{{ article_chinese_link_1 }}': 'https://zhuanlan.zhihu.com/p/1944083434071917665',
    
    '{{ article_english_title_2 }}': '【R Language】A Workflow Based on Nested Data Frames',
    '{{ article_chinese_title_2 }}': '【R 语言】一种基于嵌套数据框的工作流',
    '{{ article_english_link_2 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91A%20Workflow%20Based%20on%20Nested%20Data%20Frames.md',
    '{{ article_chinese_link_2 }}': 'https://zhuanlan.zhihu.com/p/1944921736941384138',
    
    '{{ article_english_title_3 }}': '【R Language】All-Subsets Regression Based on broom Package',
    '{{ article_chinese_title_3 }}': '【R 语言】基于 broom 包的模型全子集回归',
    '{{ article_english_link_3 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91All-Subsets%20Regression%20Based%20on%20broom%20Package.md',
    '{{ article_chinese_link_3 }}': 'https://zhuanlan.zhihu.com/p/1957450684447323826',
    
    '{{ article_english_title_4 }}': '【R Language】Plotting Known Functions with ggplot2',
    '{{ article_chinese_title_4 }}': '【R 语言】ggplot2 绘制已知函数图像',
    '{{ article_english_link_4 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91Plotting%20Known%20Functions%20with%20ggplot2.md',
    '{{ article_chinese_link_4 }}': 'https://zhuanlan.zhihu.com/p/1948532373101713365',
    
    '{{ article_english_title_5 }}': '【R Language】mice Package for Multiple Imputation and Batch Modeling',
    '{{ article_chinese_title_5 }}': '【R 语言】mice 包进行缺失值多重插补与批量建模',
    '{{ article_english_link_5 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91mice%20Package%20for%20Multiple%20Imputation%20and%20Batch%20Modeling.md',
    '{{ article_chinese_link_5 }}': 'https://zhuanlan.zhihu.com/p/1946672841723454894',
    
    '{{ article_english_title_6 }}': '【R Language】Nonlinear Least Squares and Linear Models',
    '{{ article_chinese_title_6 }}': '【R 语言】非线性最小二乘法与线性模型',
    '{{ article_english_link_6 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91Nonlinear%20Least%20Squares%20and%20Linear%20Models.md',
    '{{ article_chinese_link_6 }}': 'https://zhuanlan.zhihu.com/p/1954307887825414074',
    
    '{{ article_english_title_7 }}': '【R Language】Chi-square Distribution and Convolution Effect',
    '{{ article_chinese_title_7 }}': '【R 语言】卡方分布与卷积效应',
    '{{ article_english_link_7 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91Chi-square%20Distribution%20and%20Convolution%20Effect.md',
    '{{ article_chinese_link_7 }}': 'https://zhuanlan.zhihu.com/p/1961396245617685701',
    
    '{{ article_english_title_8 }}': '【R Language】Lorenz Curve and Gini Index',
    '{{ article_chinese_title_8 }}': '【R 语言】洛伦兹曲线与基尼指数',
    '{{ article_english_link_8 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91Lorenz%20Curve%20and%20Gini%20Index.md',
    '{{ article_chinese_link_8 }}': 'https://zhuanlan.zhihu.com/p/1951089194756703939',
    
    '{{ article_english_title_9 }}': '【R Language】broom Package for Tidy Modeling',
    '{{ article_chinese_title_9 }}': '【R 语言】broom 包进行整洁建模',
    '{{ article_english_link_9 }}': 'https://github.com/zlZayn/mine/blob/main/R%20Language/%E3%80%90R%20Language%E3%80%91broom%20Package%20for%20Tidy%20Modeling.md',
    '{{ article_chinese_link_9 }}': 'https://zhuanlan.zhihu.com/p/1949603330578953873'
}

# 执行替换
result = template
for placeholder, value in replacements.items():
    result = result.replace(placeholder, value)

# 写入结果文件
with open(r'd:\PythonDirectory\知乎\combined_article_cards.html', 'w', encoding='utf-8') as f:
    f.write(result)

print("最终组合卡片已生成，已保存到: d:\\PythonDirectory\\知乎\\combined_article_cards.html")