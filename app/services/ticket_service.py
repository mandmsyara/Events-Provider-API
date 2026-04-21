import uuid

from fastapi import HTTPException


class TicketService:
    def __init__(self, client, event_repo, ticket_repo):
        self.client = client
        self.event_repo = event_repo
        self.ticket_repo = ticket_repo

    async def create_ticket(self, data):
        event = await self.event_repo.get_events_by_id(data.event_id)

        if not event:
            raise HTTPException(status_code=404, detail="Event not found")

        if event.status != "published":
            raise HTTPException(status_code=400, detail="Event not avaliable")

        seats = await self.client.get_seats(str(data.event_id))

        if data.seat not in seats:
            raise HTTPException(status_code=400, detail="seats not avaliable")

        ticket_id = await self.client.register(
            str(data.event_id),
            data.first_name,
            data.last_name,
            data.email,
            data.seat,
        )

        ticket = await self.ticket_repo.create(
            {
                "id": uuid.UUID(ticket_id),
                "event_id": data.event_id,
                "first_name": data.first_name,
                "last_name": data.last_name,
                "seat": data.seat,
                "email": data.email,
            }
        )

        await self.ticket_repo.session.commit()

        return {"ticket_id": ticket.id}

    async def delete_ticket(self, ticket_id):
        ticket = await self.ticket_repo.get_by_id(uuid.UUID(ticket_id))

        if not ticket:
            raise HTTPException(status_code=404, detail="Ticket is not found")

        await self.client.unregister(str(ticket.event_id), str(ticket.id))

        await self.ticket_repo.delete(ticket)
        await self.ticket_repo.session.commit()

        return {"success": True}
