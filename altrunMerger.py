import os
import sys

def get_available_backup_name(filepath, suffix):
    """获取可用的备份文件名，避免冲突"""
    backup_path = f"{filepath}.{suffix}"
    if not os.path.exists(backup_path):
        return backup_path
    idx = 0
    while True:
        backup_path = f"{filepath}.{suffix}_{idx}"
        if not os.path.exists(backup_path):
            return backup_path
        idx += 1

def rename_file(old_path, new_path):
    try:
        os.rename(old_path, new_path)
        print(f"已重命名: {old_path} -> {new_path}")
    except FileNotFoundError:
        print("文件未找到:", old_path)
    except Exception as e:
        print("重命名失败:", e)

def parse_file_gb2312(filepath) -> dict:
    """使用 GB2312 编码读取文件并逐行打印内容"""
    try:
        config = {}
        with open(filepath, 'r', encoding='gb2312') as f:
            for line in f:
                # print(line.rstrip('\n'))
                args = line.split('|')
                args = [arg.strip() for arg in args]
                if len(args) < 5:
                    # print(line)
                    continue
                # print(" | ".join(args))
                config[args[2]] = args
        return config
    except FileNotFoundError:
        print(f"文件未找到: {filepath}")
    except UnicodeDecodeError:
        print("文件编码不是 GB2312，解码失败")
    except Exception as e:
        print(f"读取文件时发生错误: {e}")
    return {}

def merge_config_by_field2(map1: dict, map2: dict) -> dict:
    """合并两个配置字典，map2 的值覆盖 map1 的值"""
    merged_map = map1.copy()  # 先复制 map1
    for key, value in map2.items():
        if key not in merged_map:
            merged_map[key] = value  # 添加 map2 的项
            print(f"添加新项: {key} -> {' | '.join(value)}")
        else:
            if value[4] == merged_map[key][4]:
                continue  # 相同则跳过
            # 值不同，发生冲突，修改 key
            print(f"冲突项{key} -> {' | '.join(merged_map[key])}")
            print(f"冲突项{key} -> {' | '.join(value)}")
            idx = 0
            key = key + f"_{idx}"
            while key in merged_map:
                idx += 1
                key = key + f"_{idx}"
            value[2] = key  # 更新 value 中的 key 字段 
            merged_map[key] = value # 添加修改后的项
            print(f"冲突项，修改后添加: {key} -> {' | '.join(value)}")
    return merged_map

def merge_strings(a: str, b: str) -> str:
    """
    合并两个字符串，使得结果尽可能短，并保证 a 和 b 都是子串。
    """
    # 若 a 已包含 b
    if b in a:
        return a
    # 若 b 已包含 a
    if a in b:
        return b

    # 计算 b 在 a 末尾的最大重叠
    max_overlap_ab = 0
    for i in range(1, min(len(a), len(b)) + 1):
        if a.endswith(b[:i]):
            max_overlap_ab = i

    # 计算 a 在 b 末尾的最大重叠
    max_overlap_ba = 0
    for i in range(1, min(len(a), len(b)) + 1):
        if b.endswith(a[:i]):
            max_overlap_ba = i

    # 选择更短的合并方式
    option1 = a + b[max_overlap_ab:]  # a 后接 b
    option2 = b + a[max_overlap_ba:]  # b 后接 a

    return option1 if len(option1) <= len(option2) else option2

def compress_config_by_field4(config_map: dict) -> dict:
    """根据字段4压缩配置字典，保留字段4相同的最后一项"""
    compressed_map = {}
    field4_to_key = {}
    for key, value in config_map.items():
        field4 = value[4]
        if field4 in field4_to_key:
            # 已存在相同字段4的项，删除旧项
            old_key = field4_to_key[field4]
            new_key = merge_strings(old_key, key)
            new_value = value
            new_value[2] = new_key  # 更新 value 中的 key 字段
            new_value[3] = merge_strings(compressed_map[old_key][3], value[3])  # 合并字段0
            print(f"{old_key} vs {key}")
            print(f"压缩-删除旧项: \n{old_key} -> {' | '.join(compressed_map[old_key])}")
            del compressed_map[old_key]
            print(f"压缩项-添加新项: \n{new_key} -> {' | '.join(new_value)}")    
            compressed_map[new_key] = new_value
            field4_to_key[field4] = new_key
        else:
            # 添加当前项
            compressed_map[key] = value
            field4_to_key[field4] = key
    return compressed_map


def merge_config_file(config_file1, config_file2=None, config_file_target='ShortCutList.txt'):
    map1 = parse_file_gb2312(config_file1)
    map2 = parse_file_gb2312(config_file2) if config_file2 else {}
    
    if config_file2:
        # 根据索引键进行合并
        map3 = merge_config_by_field2(map1, map2)
    else:
        # 单文件模式，直接使用 map1
        map3 = map1
    
    map3 = dict(sorted(map3.items(), key=lambda item: item[1][2]))
    # 根据索引键进行压缩
    map4 = compress_config_by_field4(map3)
    print(f"合并后共 {len(map4)} 项")
    # 输出合并后的结果到新文件
    with open(config_file_target, 'w', encoding='gb2312') as f:
        for key, value in map4.items():
            f.write(" |".join(value) + '\n')
    # 备份输入文件
    backup1 = get_available_backup_name(config_file1, 'ori1')
    rename_file(config_file1, backup1)
    if config_file2:
        backup2 = get_available_backup_name(config_file2, 'ori2')
        rename_file(config_file2, backup2)

def main():
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python altrunMerger.py <config_file1> [config_file2]")
        print("输出文件: ShortCutList.txt")
        print("说明: 可输入一个文件去重，或两个文件合并去重")
        sys.exit(1)

    config_file1 = sys.argv[1]
    config_file2 = sys.argv[2] if len(sys.argv) == 3 else None
    config_file_target = 'ShortCutList.txt'

    merge_config_file(config_file1, config_file2, config_file_target)


if __name__=="__main__":
    main()
    