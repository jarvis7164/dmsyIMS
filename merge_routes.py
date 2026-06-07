# -*- coding: utf-8 -*-
# 合并客资管理路由到 app.py

# 读取 add_customer_lead_routes.py 的内容（去掉第一行注释）
with open('add_customer_lead_routes.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
    # 去掉第一行注释
    routes_content = ''.join(lines[1:])

# 读取 app.py
with open('app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

# 找到 if __name__ == '__main__': 的位置
insert_pos = app_content.find("if __name__ == '__main__':")

if insert_pos != -1:
    # 在 if __name__ == '__main__': 之前插入路由
    new_content = app_content[:insert_pos] + '\n' + routes_content + '\n\n' + app_content[insert_pos:]
    
    # 写回 app.py
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("路由已成功合并到 app.py")
else:
    print("未找到 if __name__ == '__main__':，合并失败")
