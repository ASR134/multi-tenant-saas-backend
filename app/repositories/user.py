from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.models.user import User


class UserRepository:

    def __init__(self,db : AsyncSession):
        self.db = db


    async def get_by_id(self,user_id : int):
        result = await self.db.execute(
            select(User).where(User.id == user_id) # read db operation
        )
        return result.scalar_one_or_none()


    async def get_by_email(self,email : str):
        result = await self.db.execute(
            select(User).where(User.email == email) # read db operation
        )
        return result.scalar_one_or_none() # returns User model class object or None


    async def get_by_verification_token_hash(
            self,
            token_hash : str,
    ):
        result = await self.db.execute(
            select(User).where(
                User.verification_token_hash == token_hash
            )
        )

        return result.scalar_one_or_none()


    async def create(
            self,
            email: str,
            hashed_password : str,
            full_name : str,
            verification_token_hash : str,
            verification_token_expiry_at : datetime,
    ):
        user = User(
            email = email,
            password_hash = hashed_password,
            full_name = full_name,
            verification_token_hash = verification_token_hash,
            verification_token_expires_at = verification_token_expiry_at,
        )

        self.db.add(user) # AsyncSession obj starts tracking this obj

        await self.db.flush() # sends the insert command.
        # now id,created_at could be generaed. (write db operation)
        return user


    async def update(
            self,
            full_name : str,
            user_data : User,
    ):

        if full_name is not None: # defensive check
            user_data.full_name = full_name

        await self.db.flush()

        return user_data


    async def delete(
            self,
            user : User,
    ):

        await self.db.delete(user)

        await self.db.flush()
