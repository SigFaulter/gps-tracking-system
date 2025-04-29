from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import paginate, LimitOffsetPage

from core.dependencies import (
    admin_only,
    authentication_required,
    decode_jwt_token,
    oauth2_scheme,
    verify_license_plate_history_access,
)
from crud.license_plate_history import (
    delete_license_plate_history,
    get_license_plate_history,
    get_license_plate_history_by_device,
    get_license_plate_history_by_id,
    get_license_plate_history_by_user_id,
)
from db.database import Session, get_session
from db.models import LicensePlateHistory
from schemas.license_plate_history import (
    LicensePlateHistoryCreate,
    LicensePlateHistoryRead,
)

router = APIRouter(
    prefix="/license-plate-history",
    tags=["License Plate History"],
    dependencies=[Depends(authentication_required)],
)


@router.get("/{device_id}", response_model=list[LicensePlateHistoryRead])
def list_license_plate_history_by_device_id(
    device_id: int,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    return get_license_plate_history_by_device(session, device_id)


@router.get(
    "/{history_id}",
    response_model=LicensePlateHistoryRead,
    dependencies=[Depends(verify_license_plate_history_access)],
)
def read_license_plate_histories_by_history_id(
    history_id: int,
    session: Session = Depends(get_session),
):
    license_plate_history = get_license_plate_history_by_id(session, history_id)
    if not license_plate_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="license plate history not found",
        )
    return license_plate_history


@router.get(
    "",
    response_model=LimitOffsetPage[LicensePlateHistoryRead],
    dependencies=[Depends(verify_license_plate_history_access)],
)
def read_license_plate_histories(
    token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)
):
    token = decode_jwt_token(token)

    if token.get("is_admin"):
        license_plate_history = get_license_plate_history(session)
    else:
        license_plate_history = get_license_plate_history_by_user_id(
            session, token["id"]
        )

    if not license_plate_history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No license plate history found",
        )

    return paginate(license_plate_history)


@router.post(
    "",
    response_model=LicensePlateHistoryRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(admin_only)],
)
def create_license_plate_history(
    history_data: LicensePlateHistoryCreate,
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(get_session),
):
    return verify_license_plate_history_access(
        session, LicensePlateHistory(**history_data.dict())
    )


@router.delete(
    "/{history_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(admin_only)],
)
def remove_license_plate_history(
    history_id: int,
    session: Session = Depends(get_session),
):
    history = get_license_plate_history_by_id(session, history_id)
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="License plate history not found",
        )

    delete_license_plate_history(session, history)
