# -*- coding: utf-8 -*-
# 修复 app.py 中的重复路由问题

# 读取 app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到第二个 @app.route('/customer_lead_management') 的位置
# 第一个在前面，第二个在后面（重复的部分）
first_occurrence = content.find("@app.route('/customer_lead_management')\n")
if first_occurrence != -1:
    # 找到第二个出现的位置
    second_occurrence = content.find("@app.route('/customer_lead_management')\n", first_occurrence + 1)
    
    if second_occurrence != -1:
        # 找到第二个 occurrences 的结束位置（下一个 @app.route 或 if __name__）
        # 我们找从第二个 occurrences 开始到文件末尾，然后找到 if __name__ == '__main__':
        remaining = content[second_occurrence:]
        main_block = remaining.find("\n\nif __name__ == '__main__':")
        
        if main_block != -1:
            # 计算实际位置
            end_of_duplicates = second_occurrence + main_block
            
            # 保留第二部分之前的逗号换行，去掉重复内容
            # 实际上我们需要保留从 second_occurrence 到 end_of_duplicates 之外的内容
            new_content = content[:second_occurrence] + content[end_of_duplicates:]
            
            # 写回
            with open('app.py', 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("成功删除重复的路由代码")
        else:
            print("未找到 if __name__ == '__main__':，无法定位重复代码结束位置")
    else:
        print("未找到重复的路由代码")
else:
    print("未找到路由代码")
