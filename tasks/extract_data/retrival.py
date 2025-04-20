# -*- encoding: utf-8 -*-
"""
@Time    :   2025-04-20 23:17:51
@desc    :
@Author  :   ticoAg
@Contact :   1627635056@qq.com
"""


import jieba
from extract_data.main import Extractor
from fuzzywuzzy import fuzz


def recall_recipes(query: str, recipes: Extractor) -> dict:
    def update_matched_recipes(rel_recipes: list, matched_recipes: dict, score: int | float) -> dict:
        """更新匹配到的菜谱及其权重分数
        Args:
            rel_recipes (list): 相关菜谱列表
            matched_recipes (dict): 已匹配的菜谱及其权重分数
            score (int | float): 当前菜谱的权重分数
        Returns:
            dict: 更新后的已匹配的菜谱及其权重分数
        """
        for recipe in rel_recipes:
            matched_recipes[recipe] = matched_recipes.get(recipe, 0) + round(score, 2)
        return matched_recipes

    matched_recipes = {}

    tags = [tag.strip() for tag in query.replace("，", ",").replace("|", ",").split(",")]
    for tag in tags:
        # 优先完全匹配（权重5）
        _rel_recipes = recipes.materials.get(tag)
        if _rel_recipes:
            matched_recipes = update_matched_recipes(_rel_recipes, matched_recipes, 5)
            # continue  # 完全匹配后跳过后续处理

        # 未完全匹配时进行分词处理
        words = jieba.lcut(tag)
        for word in words:
            flag = 0
            # 部分匹配（权重2）
            for material in recipes.materials:
                if word in material or material in word:
                    _rel_recipes = recipes.materials[material]
                    matched_recipes = update_matched_recipes(_rel_recipes, matched_recipes, 1)
                    flag = 1
            if flag:
                continue

            # 模糊匹配（权重1）
            gate = 30
            for material in recipes.materials:
                sim_ratio = fuzz.token_sort_ratio(word, material)
                if sim_ratio >= gate:
                    _rel_recipes = recipes.materials[material]
                    matched_recipes = update_matched_recipes(_rel_recipes, matched_recipes, sim_ratio / (100 - gate))

    # 按权重分数降序排序
    sorted_recipes = sorted(matched_recipes.items(), key=lambda x: (-x[1], x[0]))
    return sorted_recipes


def recall_by_whole_markdown(query: str, recipes: Extractor):
    """先分词, 如果分出的词出现在文章中就添加"""
    matched_recipes = {}

    tags = [tag.strip() for tag in query.replace("，", ",").replace("|", ",").split(",")]

    for tag in tags:
        words = jieba.lcut(tag)
        for word in words:
            for recipe_name, path in recipes.all_dishes_map.items():
                markdown_content = open(path, "r", encoding="utf-8").read()
                if word in markdown_content:
                    matched_recipes[recipe_name] = matched_recipes.get(recipe_name, 0) + 1
    sorted_recipes = sorted(matched_recipes.items(), key=lambda x: (-x[1], x[0]))
    return sorted_recipes
