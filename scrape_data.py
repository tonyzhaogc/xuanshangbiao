#!/usr/bin/env python3
import requests
import re
import json
from pathlib import Path

def fetch_trademark_data():
    """获取并解析商标分类数据"""
    print("正在获取商标分类数据...")
    
    # 获取数据
    response = requests.get('https://www.zcw.com.cn/assets/tm-classes.js')
    content = response.text
    
    # 提取并解析数组
    start = content.find('[')
    end = content.rfind(']') + 1
    array_str = content[start:end]
    
    # 解析数据
    pattern = r'\["([^"]+)",\s*"([^"]*)",\s*"([^"]*)"(?:,\s*"([^"]*)")?\]'
    matches = re.findall(pattern, array_str)
    
    print(f"共获取 {len(matches)} 条数据")
    
    # 商标大类简短名称映射
    class_name_map = {
        '01': '化工原料',
        '02': '颜料油漆',
        '03': '日化用品',
        '04': '燃料油脂',
        '05': '医药制剂',
        '06': '金属制品',
        '07': '机械设备',
        '08': '手工器具',
        '09': '科学仪器',
        '10': '医疗器械',
        '11': '家用电器',
        '12': '运输工具',
        '13': '火花火药',
        '14': '珠宝首饰',
        '15': '乐器',
        '16': '办公用品',
        '17': '橡胶制品',
        '18': '皮革皮具',
        '19': '建筑材料',
        '20': '家具',
        '21': '厨房洁具',
        '22': '绳网篷布',
        '23': '纺织纱线',
        '24': '织物',
        '25': '服装鞋帽',
        '26': '花边装饰',
        '27': '地毯席垫',
        '28': '健身器材',
        '29': '食品',
        '30': '调味品',
        '31': '饲料种籽',
        '32': '啤酒饮料',
        '33': '酒类',
        '34': '烟草',
        '35': '广告销售',
        '36': '金融物管',
        '37': '建筑修理',
        '38': '通讯服务',
        '39': '运输贮藏',
        '40': '材料加工',
        '41': '教育娱乐',
        '42': '技术服务',
        '43': '餐饮住宿',
        '44': '医疗园艺',
        '45': '社会法律'
    }
    
    # 构建层级结构
    classes_data = []
    groups_data = {}
    items_data = {}
    
    for match in matches:
        item_id, parent_id, name, remark = match
        item = {
            'id': item_id,
            'parent_id': parent_id,
            'name': name,
            'remark': remark
        }
        
        if len(item_id) == 2:  # 大类
            # 使用简短名称
            short_name = class_name_map.get(item_id, name.split('；')[0].split('，')[0])
            item['name'] = short_name
            item['full_name'] = name  # 保留完整名称
            classes_data.append(item)
        elif len(item_id) == 4:  # 类似群
            if parent_id not in groups_data:
                groups_data[parent_id] = []
            groups_data[parent_id].append(item)
        elif len(item_id) == 6:  # 商品
            if parent_id not in items_data:
                items_data[parent_id] = []
            items_data[parent_id].append(item)
    
    # 构建完整树状结构
    tree = []
    for cls in classes_data:
        cls_node = {
            'id': cls['id'],
            'name': cls['name'],  # 使用简短名称
            'type': 'class',
            'remark': cls['remark'],
            'children': []
        }
        
        if cls['id'] in groups_data:
            for group in groups_data[cls['id']]:
                group_node = {
                    'id': group['id'],
                    'name': group['name'],
                    'type': 'group',
                    'remark': group['remark'],
                    'children': []
                }
                
                if group['id'] in items_data:
                    for item in items_data[group['id']]:
                        item_node = {
                            'id': item['id'],
                            'name': item['name'],
                            'type': 'item',
                            'remark': item['remark']
                        }
                        group_node['children'].append(item_node)
                
                cls_node['children'].append(group_node)
        
        tree.append(cls_node)
    
    return tree

def save_data(tree, output_file='trademark_data.json'):
    """保存数据到JSON文件"""
    output_path = Path(output_file)
    output_path.write_text(json.dumps(tree, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"数据已保存到 {output_file}")

if __name__ == '__main__':
    tree = fetch_trademark_data()
    save_data(tree)
    print(f"共 {len(tree)} 个大类")
    print(f"总计 {sum(len(cls['children']) for cls in tree)} 个类似群")
    print(f"总计 {sum(len(group['children']) for cls in tree for group in cls['children'])} 个商品")
    
    # 显示前5个大类的名称
    print("\n前5个大类名称:")
    for cls in tree[:5]:
        print(f"  {cls['id']}: {cls['name']}")
