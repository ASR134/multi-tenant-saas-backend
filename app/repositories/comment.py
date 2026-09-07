from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.comment import Comment


class CommentRepository:

    def __init__(self,db : AsyncSession):
        self.db = db


    async def create(
            self,
            content : str,
            user_id : int,
            task_id : int,
    ):

        comment = Comment(
            content = content,
            task_id = task_id,
            user_id = user_id,
        )

        self.db.add(comment)# sqlalchemy starts tracking the object

        await self.db.flush() # sends insert command

        return comment


    async def get_by_task_id( # gives all comments
            self,
            task_id : int,
            page : int,
            limit : int,
    ):

        offset = (page -1 )*limit

        result = await self.db.execute(
                select(Comment).where(
                    Comment.task_id == task_id
                )
                .order_by(Comment.id)
                .offset(offset)
                .limit(limit)
            )

        return result.scalars().all()


    async def get_by_task_and_comment_id(
            self,
            task_id : int,
            comment_id : int,
    ):
        result = await self.db.execute(
                    select(Comment).where(
                        Comment.task_id == task_id,
                        Comment.id == comment_id,
                    ).order_by(
                        Comment.id
                    )
                )

        return result.scalar_one_or_none()


    async def delete(
            self,
            comment : Comment,
    ):

        await self.db.delete(comment)
        await self.db.flush() # write db operation (sends delete command to postgresql)

