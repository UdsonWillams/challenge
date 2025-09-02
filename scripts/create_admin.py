import asyncio
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.settings import get_settings
from app.database.models.base import Customer
from app.database.repositories.customer import CustomerRepository
from app.database.unit_of_work import get_uow
from app.services.auth.authentication import AuthService


async def create_admin():
    s = get_settings()
    email, password, role = (
        s.ADMIN_DEFAULT_EMAIL,
        s.ADMIN_DEFAULT_PASSWORD,
        s.ADMIN_DEFAULT_ROLE,
    )
    async for uow in get_uow():
        async with uow:
            repo = CustomerRepository(uow)
            try:
                existing = await repo.get_user_by_email(email)
            except TypeError:
                existing = repo.get_user_by_email(email)
            if existing:
                print(f"[INFO] Admin already exists: {email}")
                break
            auth = AuthService()
            try:
                hashed = await auth.get_password_hash(password)
            except AttributeError as e:
                print(f"[ERROR] Bcrypt backend failure: {e}")
                break
            pwd_field = (
                "hashed_password"
                if hasattr(Customer, "hashed_password")
                else "password"
            )
            customer = Customer(
                email=email,
                **{pwd_field: hashed},
                name="Administrator",
                role=role,
                is_active=True,
            )
            created = await repo.create(customer)
            try:
                await uow.commit()
            except Exception as error:
                print(f"error - {str(error)}")
            print(f"[OK] Admin created: {created.email}")
            break


def main():
    asyncio.run(create_admin())


if __name__ == "__main__":
    main()
