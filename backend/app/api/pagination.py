from fastapi import Query

from app.schemas.common import Page, PageParams


def get_page_params(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> PageParams:
    return PageParams(page=page, page_size=page_size)


def page_offset(params: PageParams) -> int:
    return (params.page - 1) * params.page_size


def to_page(items: list, total: int, params: PageParams) -> Page:
    return Page(items=items, total=total, page=params.page, page_size=params.page_size)
