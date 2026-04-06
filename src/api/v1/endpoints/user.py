from fastapi import APIRouter, Request


router = APIRouter()


@router.get("/me")
async def current_user(request: Request):
    token = request.session.get("token")
    print(token)
    user = token.get("userinfo")
    return user
