"""Module 13.5 - custom session persistence backed by Firestore.

Implements the BaseSessionService contract so agent memory survives process
restarts. Document layout:

    apps/{app_name}/users/{user_id}/sessions/{session_id}
        state, created_at, last_update_time
        events/{event_id}   (sub-collection, one doc per event)

The Runner never knows Firestore exists - swap this for Redis/Postgres by
writing another BaseSessionService subclass; the agent code is untouched.
"""

import time
import uuid
from typing import Any, Optional

from google.cloud import firestore
from google.adk.events.event import Event
from google.adk.sessions.base_session_service import (
    BaseSessionService,
    GetSessionConfig,
    ListSessionsResponse,
)
from google.adk.sessions.session import Session


class FirestoreSessionService(BaseSessionService):

    def __init__(self, project_id: str, database: str = "(default)"):
        self._client = firestore.AsyncClient(project=project_id, database=database)

    def _session_ref(self, app_name: str, user_id: str, session_id: str):
        return (
            self._client.collection("apps").document(app_name)
            .collection("users").document(user_id)
            .collection("sessions").document(session_id)
        )

    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: Optional[dict[str, Any]] = None,
        session_id: Optional[str] = None,
    ) -> Session:
        session_id = session_id or uuid.uuid4().hex
        now = time.time()
        await self._session_ref(app_name, user_id, session_id).set(
            {"state": state or {}, "created_at": now, "last_update_time": now}
        )
        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=state or {},
            last_update_time=now,
        )

    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: Optional[GetSessionConfig] = None,
    ) -> Optional[Session]:
        ref = self._session_ref(app_name, user_id, session_id)
        doc = await ref.get()
        if not doc.exists:
            return None
        data = doc.to_dict()

        query = ref.collection("events").order_by("timestamp")
        if config and config.after_timestamp:
            query = query.where("timestamp", ">=", config.after_timestamp)
        events = [Event.model_validate(d.to_dict()) async for d in query.stream()]
        if config and config.num_recent_events is not None:
            events = events[-config.num_recent_events:] if config.num_recent_events else []

        return Session(
            id=session_id,
            app_name=app_name,
            user_id=user_id,
            state=data.get("state", {}),
            events=events,
            last_update_time=data.get("last_update_time", 0.0),
        )

    async def list_sessions(
        self, *, app_name: str, user_id: Optional[str] = None
    ) -> ListSessionsResponse:
        if user_id is None:
            return ListSessionsResponse()
        sessions_ref = (
            self._client.collection("apps").document(app_name)
            .collection("users").document(user_id)
            .collection("sessions").order_by("last_update_time")
        )
        sessions = [
            Session(
                id=doc.id,
                app_name=app_name,
                user_id=user_id,
                last_update_time=doc.to_dict().get("last_update_time", 0.0),
            )
            async for doc in sessions_ref.stream()
        ]
        return ListSessionsResponse(sessions=sessions)

    async def delete_session(
        self, *, app_name: str, user_id: str, session_id: str
    ) -> None:
        ref = self._session_ref(app_name, user_id, session_id)
        async for event_doc in ref.collection("events").stream():
            await event_doc.reference.delete()
        await ref.delete()

    async def append_event(self, session: Session, event: Event) -> Event:
        # Base class applies the state delta to the in-memory session and
        # appends the event; we then mirror both to Firestore.
        event = await super().append_event(session, event)
        if event.partial:
            return event

        ref = self._session_ref(session.app_name, session.user_id, session.id)
        await ref.collection("events").document(event.id).set(
            event.model_dump(mode="json")
        )
        session.last_update_time = time.time()
        await ref.update(
            {"state": session.state, "last_update_time": session.last_update_time}
        )
        return event
