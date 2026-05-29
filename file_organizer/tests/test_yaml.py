import yaml

# ==========================================
# 准备 4 种不同格式的 YAML 文本数据
# ==========================================

# 1. 键值对格式（会解析为 dict）
yaml_mapping = """
.jpg: images
.txt: notes
.py: scripts
"""

# 2. 列表格式（会解析为 list）
yaml_sequence = """
- .jpg
- .png
- .gif
"""

# 3. 纯量格式（会解析为基础类型，如 str, int, bool）
yaml_scalar_str = "hello"
yaml_scalar_int = "123"
yaml_scalar_bool = "true"

# 4. 空文本（会解析为 None）
yaml_empty = """
# 这里只有注释，没有实际内容
"""


# ==========================================
# 统一测试与打印结果
# ==========================================
print("--- 开始测试 yaml.safe_load() ---\n")

# 测试 1：键值对 -> 字典
data1 = yaml.safe_load(yaml_mapping)
print(f"【场景 1 键值对】解析后的类型: {type(data1)}")
print(f"解析后的值: {data1}\n")

# 测试 2：列表 -> 列表
data2 = yaml.safe_load(yaml_sequence)
print(f"【场景 2 列表】  解析后的类型: {type(data2)}")
print(f"解析后的值: {data2}\n")

# 测试 3：纯量 -> 基础类型
data3_str = yaml.safe_load(yaml_scalar_str)
data3_int = yaml.safe_load(yaml_scalar_int)
data3_bool = yaml.safe_load(yaml_scalar_bool)
print(f"【场景 3 纯量】  字符串类型: {type(data3_str)}, 值: {data3_str}")
print(f"                 整数类型: {type(data3_int)}, 值: {data3_int}")
print(f"                 布尔类型: {type(data3_bool)}, 值: {data3_bool}\n")

# 测试 4：空文本 -> None
data4 = yaml.safe_load(yaml_empty)
print(f"【场景 4 空文本】解析后的类型: {type(data4)}")
print(f"解析后的值: {data4}\n")

print("--- 测试结束 ---")