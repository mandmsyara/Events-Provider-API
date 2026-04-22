from enum import StrEnum


class EventStatus(StrEnum):
    NEW = "mew"
    PUBLISHED = "published"
    REGISTRATION_CLOSED = "registration_closed"
    FINISHED = "finished"
