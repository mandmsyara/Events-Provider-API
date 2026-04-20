from pydantic import BaseModel, EmailStr
from uuid import UUID


class TicketCreate(BaseModel):
    event_id: UUID
    first_name: str
    last_name: str
    email: EmailStr
    seat: str


class TickerResponse(BaseModel):
    ticket_id: UUID
