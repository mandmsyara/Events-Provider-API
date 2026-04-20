from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ticket import Ticket


class TicketRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, data: dict):
        ticket = Ticket(**data)
        self.session.add(ticket)
        await self.session.flush()
        return ticket
