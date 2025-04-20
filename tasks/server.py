# -*- encoding: utf-8 -*-
"""
@Time    :   2025-04-20 21:45:46
@desc    :
@Author  :   ticoAg
@Contact :   1627635056@qq.com
"""


import sys
from pathlib import Path

from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, RedirectResponse

sys.path.append(str(Path(__file__).parents[1].as_posix()))
from extract_data.main import Extractor
from extract_data.retrival import recall_recipes
from extract_data.util import get_git_commit_hash, get_git_commit_time, timer_decorator


def init_recipes() -> Extractor:
    """提取数据"""
    extractor = Extractor()
    extractor.extract_data()
    return extractor


def lifespan(app: FastAPI):

    global RECIPES
    RECIPES = init_recipes()
    yield
    del RECIPES


app = FastAPI(lifespan=lifespan, version="commit time:" + get_git_commit_time() + ", commit hash:" + get_git_commit_hash())


@app.get("/")
async def root():
    """重定向到/docs"""
    return RedirectResponse(url="/docs")


@app.get("/recipes/list_all", tags=["菜谱"], description="列出所有菜谱")
async def list_all_recipes():
    return JSONResponse(content={"recipes": list(RECIPES.dishes_map.keys())})


@app.get("/recipes/{recipe}", tags=["菜谱"], description="获取解析后的菜谱")
async def get_recipe(recipe: str):
    return JSONResponse(content=RECIPES.dishes_map.get(recipe).model_dump())


@app.get("/recipes/raw/{recipe}", tags=["菜谱"], description="获取原始菜谱markdown")
async def get_raw_recipe(recipe: str):
    _path = RECIPES.all_dishes_map.get(recipe)
    if not _path:
        return JSONResponse(content={"error": "菜谱不存在"})

    md_content = open(_path, "r", encoding="utf-8").read()
    return JSONResponse(content={"content": md_content})


@app.get("/recipes/query/", tags=["菜谱"], description="匹配菜谱")
@timer_decorator
async def match_recipes(query: str = Query(..., description="输入多个标签或者自然语言,用`,`或者`|`分隔", example="冬瓜,菠菜")):
    """
    根据输入的多个标签匹配菜谱
    - 完全匹配: 权重 + 5
    - 部分匹配: 权重 + 1
    - 模糊匹配: 权重 + 0-1
    """
    sorted_recipes = recall_recipes(query, RECIPES)

    return JSONResponse(content={"matched_recipes": [{"recipe": k, "score": v} for k, v in sorted_recipes]})


@app.get("/materials/list_all", tags=["材料"], description="列出所有材料,注:此处处理出的材料是很`脏`的,仅用于召回菜谱")
async def list_all_materials():
    return JSONResponse(content={"materials": list(RECIPES.materials.keys())})


@app.get("/materials/query/", tags=["材料"], description="查询材料相关的菜谱")
async def query_materials(query: str = Query(..., description="仅接受单一材料", example="冬瓜")):
    return JSONResponse(content={"recipes": RECIPES.materials.get(query, [])})


if __name__ == "__main__":
    import uvicorn

    # uvicorn.run("tasks.server:app", host="localhost", port=8000)
    uvicorn.run(app, host="localhost", port=8000)
