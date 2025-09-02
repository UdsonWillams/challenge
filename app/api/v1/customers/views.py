from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.v1.auth.dependencies import get_current_user, require_admin
from app.database.unit_of_work import UnitOfWorkConnection, get_uow
from app.exceptions.exceptions import UnauthorizedError
from app.schemas.auth import AuthenticatedUser
from app.schemas.domain.customers import input, output
from app.schemas.domain.favorites import FavoriteCreate, FavoriteProductResponse
from app.services.domain.customer import CustomerService

router = APIRouter(prefix="/customers", tags=["Customers"])


@router.post(
    "",
    response_model=output.CreateCustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_customer(
    payload: input.CreateCustomer, uow: UnitOfWorkConnection = Depends(get_uow)
):
    service = CustomerService(uow)
    response = await service.create_customer(payload)
    return response


@router.get("", response_model=output.CustomerList, status_code=status.HTTP_200_OK)
async def list_customers(
    page_size: int = 100,
    page: int = 1,
    sort_by: str | None = "-updated_at",
    admin: AuthenticatedUser = Depends(require_admin),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    service = CustomerService(uow)
    response = await service.list_all(
        sort_by=sort_by, filters={}, page=page, page_size=page_size
    )
    return response


@router.get(
    "/{customer_id}",
    response_model=output.CustomerResponse,
    status_code=status.HTTP_200_OK,
)
async def get_customer(
    customer_id: UUID,
    get_current_user: AuthenticatedUser = Depends(get_current_user),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    service = CustomerService(uow, get_current_user)
    customer = await service.get_by_id(customer_id)
    return customer


@router.get(
    "/email/{customer_email}",
    response_model=output.CustomerResponse,
    status_code=status.HTTP_200_OK,
)
async def get_customer_by_email(
    email: str,
    get_current_user: AuthenticatedUser = Depends(get_current_user),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    service = CustomerService(uow, get_current_user)
    customer = await service.get_by_email(email)
    return customer


@router.put(
    "/{customer_id}",
    response_model=output.CustomerResponse,
    status_code=status.HTTP_200_OK,
)
async def update_customer(
    customer_id: UUID,
    payload: input.UpdateCustomer,
    current_user: AuthenticatedUser = Depends(get_current_user),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    service = CustomerService(uow, current_user)
    updated = await service.update(customer_id, payload.model_dump(exclude_unset=True))
    return updated


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: UUID,
    admin: AuthenticatedUser = Depends(require_admin),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    service = CustomerService(uow, admin)
    await service.delete(customer_id)
    return None


@router.post(
    "/{customer_id}/favorites",
    response_model=FavoriteProductResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_favorite(
    customer_id: UUID,
    payload: FavoriteCreate,
    current_user: AuthenticatedUser = Depends(get_current_user),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    if not (current_user.role == "admin" or str(current_user.id) == str(customer_id)):
        raise UnauthorizedError
    service = CustomerService(uow, current_user)
    product = await service.add_favorite(customer_id, payload)
    return product


@router.delete(
    "/{customer_id}/favorites/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def remove_favorite(
    customer_id: UUID,
    product_id: str,
    current_user: AuthenticatedUser = Depends(get_current_user),
    uow: UnitOfWorkConnection = Depends(get_uow),
):
    if not (current_user.role == "admin" or str(current_user.id) == str(customer_id)):
        raise UnauthorizedError
    service = CustomerService(uow, current_user)
    removed = await service.remove_favorite(customer_id, product_id)
    if not removed:
        raise HTTPException(status_code=404, detail="Favorite not found")
    return None
