"""
Κοινό helper για κλήση agents (token-efficient).
Το backend καλεί ΑΠΕΥΘΕΙΑΣ τον σωστό agent — όχι μέσω runtime coordinator.
"""

import anthropic
from . import config as cfg

client = anthropic.Anthropic(api_key=cfg.ANTHROPIC_API_KEY)


def run_agent(agent_id: str, message: str, vault_ids: list[str] | None = None,
              title: str = "task") -> str:
    """
    Ανοίγει session, στέλνει 1 μήνυμα, επιστρέφει το τελικό κείμενο του agent.
    Stream-first: ανοίγει stream ΠΡΙΝ στείλει (αλλιώς χάνει πρώτα events).
    """
    session = client.beta.sessions.create(
        agent=agent_id,                       # string shorthand → latest version
        environment_id=cfg.ENV_ID,
        vault_ids=vault_ids or [],
        title=title,
    )
    out: list[str] = []
    with client.beta.sessions.events.stream(session_id=session.id) as stream:
        client.beta.sessions.events.send(
            session_id=session.id,
            events=[{"type": "user.message",
                     "content": [{"type": "text", "text": message}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                for b in event.content:
                    if b.type == "text":
                        out.append(b.text)
            elif event.type == "session.status_terminated":
                break
            elif event.type == "session.status_idle":
                # σπάσε μόνο σε terminal stop_reason (όχι requires_action)
                if getattr(event.stop_reason, "type", None) != "requires_action":
                    break
    return "".join(out)


def continue_session(session_id: str, message: str) -> str:
    """Για το interactive refinement loop (συνέχεια ίδιου session)."""
    out: list[str] = []
    with client.beta.sessions.events.stream(session_id=session_id) as stream:
        client.beta.sessions.events.send(
            session_id=session_id,
            events=[{"type": "user.message",
                     "content": [{"type": "text", "text": message}]}],
        )
        for event in stream:
            if event.type == "agent.message":
                for b in event.content:
                    if b.type == "text":
                        out.append(b.text)
            elif event.type == "session.status_terminated":
                break
            elif event.type == "session.status_idle":
                if getattr(event.stop_reason, "type", None) != "requires_action":
                    break
    return "".join(out)
