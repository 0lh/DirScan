from pathlib import Path

COROS_NUM = 400
BASE_DIR = Path.cwd()

# 定义输出日志路径
LOG_PATH = f'logs\\DirScan.log'
ERROR_LOG_PATH = f'logs\\DirScan 异常处理.txt'

# 定义导入的urls
URLS_FILE = f'data\\small.txt'

# 定义保存结果的路径
SAVE_FILE_01 = f'results\\01 - 应该存在路径.txt'
SAVE_FILE_02 = f'results\\02 - 大概率存在的路径.txt'
SAVE_FILE_03 = f'results\\03 - 小概率存在网站.txt'
SAVE_FILE_04 = f'results\\04 - 异常路径.txt'
SAVE_FILE_05 = f'results\\05 - 少见响应码路径.txt'

# sqlite相关
DB_PATH = 'data\\all_type_dict.db'
TABLE_NAME = 'php_dir'
export_dict = 'data\\php_dir 2020-02-06.txt'
