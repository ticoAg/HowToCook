import re
from enum import StrEnum
from typing import Dict, List, Optional

from loguru import logger
from pydantic import BaseModel, Field


class Recipe(BaseModel):
    """菜谱数据结构"""

    title: str = Field(None, description="菜谱标题")
    difficulty: str = Field(None, description="烹饪难度")
    materials: List[str] = Field([], description="必备材料")
    materials_darty: List[str] = Field([], description="必备材料(未处理)")
    estimation: str = Field("", description="份量计算")
    steps: List[Dict] = Field([], description="操作步骤")
    additional_info: List[str] = Field([], description="附加信息")


class EnumHeadings(StrEnum):
    """菜谱标题"""

    MATERIALS = "## 必备原料和工具"
    ESTIMATION = "## 计算"
    STEPS = "## 操作"
    ADDITIONAL_INFO = "## 附加内容"


def compare_diff(l1):
    """校验all_headings是否与EnumHeadings一致"""
    return set(l1).difference(set(EnumHeadings.__members__.values()))


def is_all_chinese(text):
    """判断字符串是否全是中文字符"""
    return all(re.match(r"^[\u4e00-\u9fff]+$", item) for item in text)


def clean_str(text: str) -> str:
    """清理字符串"""

    # 使用正则表达式过滤掉中英文括号内的内容
    result = re.sub(r"[（\(][^）\)]*[）\)]", "", text)
    return result.strip().strip(":").strip("：").strip("。").strip(".")


def clean_material_str(text: str) -> list:
    """处理材料字符串"""
    materials_darty = []
    for line in text.split("\n"):
        if line.strip():
            items = [
                item.strip()
                for item in re.split(r"[()（）,，。、”“:：+-/!！<>\[\]]+", line.replace("-", "").replace("*", "").replace(">", ""))
                if item.strip()
            ]
            materials_darty.extend(items)

    materials = [clean_str(i) for i in materials_darty]
    # 判断rep 是否全是中文字符
    if not is_all_chinese(materials):
        logger.warning(materials)
    return materials, materials_darty


def parse_recipe(markdown_content):
    # 解析所有级别的markdown标题
    # all_headings = re.findall(r'^#{1,6} .+$', markdown_content, re.MULTILINE)
    all_headings = re.findall(r"^#{1,2} .+$", markdown_content, re.MULTILINE)
    logger.debug(f"markdown标题: {all_headings}")
    # 基于EnumHeadings校验all_headings
    for idx, heading in enumerate(all_headings):
        if idx == 0:
            continue
        if heading not in EnumHeadings.__members__.values():
            diff_set = compare_diff(all_headings)
            raise ValueError(f"Diff heading: {diff_set}")

    item_collection = {}

    # 解析标题
    item_collection["title"] = markdown_content.split("\n")[0].strip("# ")

    # 解析难度
    difficulty_match = re.search(r"预估烹饪难度：(★+)", markdown_content)
    if difficulty_match:
        item_collection["difficulty"] = difficulty_match.group(1)

    # 解析必备原料和工具
    ingredients_section = re.search(r"## 必备原料和工具\n(.*?)\n##", markdown_content, re.DOTALL)
    if ingredients_section:
        item_collection["materials"], item_collection["materials_darty"] = clean_material_str(ingredients_section.group(1))

    # 提取计算部分
    quantities_section = re.search(r"## 计算\n(.*?)\n##", markdown_content, re.DOTALL)
    if quantities_section:
        item_collection["estimation"] = quantities_section.group(1).strip()

    # 解析操作步骤
    steps_section = re.search(r"## 操作\n(.*?)\n##", markdown_content, re.DOTALL)
    if steps_section:
        item_collection["steps"] = []
        step_stack = []

        for line in steps_section.group(1).split("\n"):
            if line.strip() and not line.startswith("注："):
                # 计算缩进级别
                indent = len(line) - len(line.lstrip())
                level = indent // 2  # 假设每级缩进2个空格

                # 处理多级列表
                while level < len(step_stack):
                    step_stack.pop()

                step_text = line.strip("- ")
                step_obj = {"text": step_text, "sub_steps": []}

                if level == 0:
                    item_collection["steps"].append(step_obj)
                else:
                    # 将子步骤附加到父步骤
                    parent_step = step_stack[-1]
                    parent_step["sub_steps"].append(step_obj)

                step_stack.append(step_obj)

    # 解析附加内容
    additional_section = re.search(r"## 附加内容\n(.*?)(?:\n##|$)", markdown_content, re.DOTALL)
    if additional_section:
        item_collection["additional_info"] = []
        for line in additional_section.group(1).split("\n"):
            if line.strip():
                item_collection["additional_info"].append(line.strip("- "))
    recipe = Recipe(**item_collection)
    return recipe


# 使用示例
if __name__ == "__main__":
    with open("/Users/ticoag/Documents/myws/HowToCook/dishes/aquatic/红烧鲤鱼.md", "r", encoding="utf-8") as f:
        content = f.read()
        recipe = parse_recipe(content)
