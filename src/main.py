import sys

from PyQt6.QtWidgets import QApplication

from ui.ui import ShareSpace
from database.models import Base
from database.database import async_engine


async def init_models():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

if __name__ == '__main__':
    # asyncio.run(init_models())
    app = QApplication(sys.argv)
    window = ShareSpace()
    window.show()
    sys.exit(app.exec())
