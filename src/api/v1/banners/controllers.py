from api.v1.banners.serializers.get_banner_list import (
    GetBannersRequest,
    GetBannersResponse,
)
from api.v1.banners.serializers.get_user_banner import GetUserBannerRequest
from fastapi import APIRouter, Depends, Request, status
from services.banner_service import BannerService
from storages.banners.db.exceptions import (
    BannerNotFoundException,
    BannersConsistenceBrokenException,
)
from utils.generic_response import BadResponse, OkResponse

from src.api.v1.banners.dependencies import (
    User,
    get_banner_service,
    get_user_or_401,
)

banners = APIRouter(prefix="/banners", tags=["Banners"])


@banners.get(
    "/user_banner",
    summary="Получение баннера для пользователя",
    name="banners:user_banner",
)
async def user_banner(
    request: Request,
    params: GetUserBannerRequest = Depends(),
    banner_service: BannerService = Depends(get_banner_service),
    user: User = Depends(get_user_or_401),
):
    try:
        content: dict = await banner_service.get_banner_by_feature_and_tag_id(
            user=user,
            tag_id=params.tag_id,
            feature_id=params.feature_id,
            use_last_revision=params.use_last_revision,
        )
    except BannerNotFoundException:
        return BadResponse.new(
            status_code=status.HTTP_404_NOT_FOUND, error="Не найдено"
        )
    except BannersConsistenceBrokenException:
        return BadResponse.new(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Внутренняя ошибка сервера",
        )
    return OkResponse.new(status_code=status.HTTP_200_OK, payload=content)


@banners.get("/banner")
async def get_banners(
    request: Request,
    params: GetBannersRequest = Depends(),
    user: User = Depends(get_user_or_401),
    banner_service: BannerService = Depends(get_banner_service),
):
    banners_list: list[dict] = await banner_service.get_banner_list(
        user=user, params=params
    )
    data = [GetBannersResponse(**banner_map) for banner_map in banners_list]
    return OkResponse.new(status_code=status.HTTP_200_OK, payload=data)
