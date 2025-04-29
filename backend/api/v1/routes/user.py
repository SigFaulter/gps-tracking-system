from core.dependencies import (
    admin_only,
    authentication_required,
    verify_access,
    verify_self_delete_admin,
)
from crud.user import (
    create_user,
    delete_user,
    get_user_by_id,
    get_user_by_username,
    get_users,
    update_user,
)
from db.database import Session, get_session
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import paginate, LimitOffsetPage
from schemas.user import UserCreate, UserModify, UserRead

router = APIRouter(
    prefix="/users",
    tags=["User Management"],
    dependencies=[Depends(authentication_required)],
)


@router.get(
    "/{user_id}",
    dependencies=[Depends(verify_access)],
    response_model=UserRead,
)
def read_user(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return user


@router.get(
    "", response_model=LimitOffsetPage[UserRead], dependencies=[Depends(admin_only)]
)
def read_users(session: Session = Depends(get_session)):
    users = get_users(session)
    return paginate(users)


@router.post(
    "",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_only)],
)
def add_user(
    user: UserCreate,
    session: Session = Depends(get_session),
):
    existing_user = get_user_by_username(session, user.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )
    return create_user(session, user)


@router.patch(
    "/{user_id}",
    response_model=UserRead,
)
def modify_user(
    user_id: int,
    user_update: UserModify,
    session: Session = Depends(get_session),
):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return update_user(session, user, user_update)


@router.delete(
    "/{user_id}",
    response_model=dict,
    dependencies=[
        Depends(admin_only),
        Depends(verify_self_delete_admin),
    ],
)
def delete_user_by_id(
    user_id: int,
    session: Session = Depends(get_session),
):
    user = get_user_by_id(session, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    return delete_user(session, user)
