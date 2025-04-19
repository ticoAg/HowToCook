# -*- encoding: utf-8 -*-
"""
@Time    :   2025-04-19 16:39:45
@desc    :   提取项目中原文件数据入口
@Author  :   ticoAg
@Contact :   1627635056@qq.com
"""

import sys
from pathlib import Path

from loguru import logger
from collections import defaultdict

sys.path.append(str(Path(__file__).parents[1].as_posix()))
from extract_data.parser import parse_recipe

# 设定控制台日志等级
logger.remove()
logger.add(sys.stderr, level="INFO")

class Extractor:
    def __init__(self) -> None:
        self.dishes_dir = dishes_dir
        self.all_dishes_map = self.get_file_path()
        self.char_count_map = {}

    def get_file_path(self) -> dict:
        """从目录下定位所有.md文件的路径"""
        all_dishes = [md_file for md_file in self.dishes_dir.rglob("*.md")]
        name_dishes_map = {i.stem: i for i in all_dishes}
        return name_dishes_map

    def submit_data(self, name: str, content: str):
        """提交数据"""
        # 统计每篇字数
        self.char_count_map[name] = len(content)
        

    def extract_data(self):
        for dish_name, dish_path in self.all_dishes_map.items():
            try:
                with open(dish_path, "r", encoding="utf-8") as f:
                    markdown_content = f.read()
                    self.submit_data(dish_name, markdown_content)
                    recipe = parse_recipe(markdown_content)
                    logger.info(f"{dish_name} 数据提取完成")
            except Exception as e:
                logger.error(f"{dish_path.as_posix()} 数据提取失败: {e}")
                continue
        logger.info(f"数据提取完成, 共计 {len(self.char_count_map)} 个菜谱")

    def view(self):
        """按每百字区间统计每篇字数分布"""
        counted_intervals = defaultdict(list)
        for dish_name, char_count in self.char_count_map.items():
            interval = char_count // 100
            counted_intervals[interval].append(dish_name)
        for interval, dishes in counted_intervals.items():
            if len(dishes) <=5:
                logger.info(f"{interval * 100}-{interval * 100 + 100}字: {len(dishes)}篇, {",".join(dishes)}")
            else:
                logger.info(f"{interval * 100}-{interval * 100 + 100}字: {len(dishes)}篇")
        

def main():
    extractor = Extractor()
    extractor.extract_data()
    extractor.view()


if __name__ == "__main__":
    dishes_dir = Path(__file__).parents[2] / "dishes"
    main()
