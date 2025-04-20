# -*- encoding: utf-8 -*-
"""
@Time    :   2025-04-20 21:45:46
@desc    :
@Author  :   ticoAg
@Contact :   1627635056@qq.com
"""

import asyncio
import sys
import time
from functools import wraps
from pathlib import Path
from typing import Callable, Coroutine, Union

import jieba
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, RedirectResponse
from loguru import logger

sys.path.append(str(Path(__file__).parents[1].as_posix()))
from extract_data.main import Extractor


def init_recipes() -> Extractor:
    """提取数据"""
    extractor = Extractor()
    extractor.extract_data()
    return extractor


def lifespan(app: FastAPI):

    global recipes
    recipes = init_recipes()
    yield
    del recipes


def timer_decorator(func: Callable) -> Callable:
    @wraps(func)
    def sync_wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute.")
        return result

    @wraps(func)
    async def async_wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Function {func.__name__} took {elapsed_time:.4f} seconds to execute.")
        return result

    return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    """重定向到/docs"""
    return RedirectResponse(url="/docs")


@app.get("/recipes/list_all")
async def list_all_recipes():
    """列出所有菜谱"""
    return JSONResponse(content={"recipes": list(recipes.dishes_map.keys())})


@app.get("/recipes/{recipe}")
async def get_recipe(recipe: str):
    """获取解析后的菜谱"""
    return JSONResponse(content=recipes.dishes_map.get(recipe).model_dump())


# 获取原始菜谱markdown
@app.get("/recipes/raw/{recipe}")
async def get_raw_recipe(recipe: str):
    """获取原始菜谱markdown"""
    _path = recipes.all_dishes_map.get(recipe)
    if not _path:
        return JSONResponse(content={"error": "菜谱不存在"})

    md_content = open(_path, "r", encoding="utf-8").read()
    return JSONResponse(content={"content": md_content})


from fuzzywuzzy import fuzz  # 需要安装 fuzzywuzzy 库


@app.get("/recipes/query/")
@timer_decorator
async def match_recipes(query: str = Query(..., description="输入多个标签，用逗号分隔", example="螃蟹,西瓜")):
    """
    根据输入的多个标签匹配菜谱
    - 完全匹配: 权重 + 5
    - 部分匹配: 权重 + 1
    - 模糊匹配: 权重 + 0-1
    """

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
            continue  # 完全匹配后跳过后续处理

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
    return JSONResponse(content={"matched_recipes": [{"recipe": k, "score": v} for k, v in sorted_recipes]})


if __name__ == "__main__":
    import uvicorn

    # uvicorn.run("tasks.server:app", host="localhost", port=8000)
    uvicorn.run(app, host="localhost", port=8000)
