from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession, 
    create_async_engine, 
    async_sessionmaker,
)


class AsyncDatabaseConnection:

    def __init__(
        self,
        driver: str,
        pool_size: int,
        max_overflow: int,
        echo: bool = True
    ):
        self._session = None
        self._engine = create_async_engine(
            driver,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
        )

    def __getattr__(self, name):
        return getattr(self._session, name)

    @asynccontextmanager
    async def session(self):
        try:
            async_sess = async_sessionmaker(
                self._engine, 
                class_=AsyncSession, 
                expire_on_commit=False
            )

            async with async_sess() as sess:
                yield sess
        except:
            await sess.rollback()
            raise
        finally:
            await sess.close()

    async def close(self):
        self._engine.dispose()

