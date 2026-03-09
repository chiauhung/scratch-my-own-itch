"""Slack bot — Socket Mode entrypoint.

Mirrors the production Cloud Function (agent_entrypoint/core.py) but simplified:
- Socket Mode instead of Events API (no public URL, no signature verification needed)
- SQLite instead of Firestore for session mapping
- Buffered response instead of chat_stream() (no real-time streaming)
- Plain logging instead of Langfuse + GCP Cloud Logging

Production gaps (see README for details):
1. Switch to Events API + public HTTPS endpoint (Cloud Run / Cloud Function)
2. Add Slack signature verification (SignatureVerifier)
3. Handle X-Slack-Retry-Num header for idempotency
4. Replace SQLite session store with Firestore
5. Add Langfuse for LLM observability and prompt management
6. Replace buffered reply with chat_stream() for real-time streaming
"""

import logging
import os
import sys

import httpx
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

sys.path.insert(0, str(__file__.replace("slack_bot/app.py", "")))
from slack_bot.session import get_session_id, init_db, upsert_session

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

ADK_URL = os.getenv("ADK_URL", "http://adk-agent:8002")
ADK_APP_NAME = "substack_search_agent"

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def create_adk_session(user_id: str) -> str:
    with httpx.Client(timeout=30) as client:
        resp = client.post(
            f"{ADK_URL}/apps/{ADK_APP_NAME}/users/{user_id}/sessions",
            json={},
        )
        resp.raise_for_status()
        return resp.json()["id"]


def query_adk_agent(user_id: str, session_id: str, message: str) -> str:
    with httpx.Client(timeout=60) as client:
        resp = client.post(
            f"{ADK_URL}/run",
            json={
                "app_name": ADK_APP_NAME,
                "user_id": user_id,
                "session_id": session_id,
                "new_message": {
                    "parts": [{"text": message}],
                    "role": "user",
                },
            },
        )
        resp.raise_for_status()
        events = resp.json()

    # Extract final text from the last agent event
    for event in reversed(events):
        content = event.get("content", {})
        for part in content.get("parts", []):
            if text := part.get("text"):
                return text

    return "I couldn't find a relevant answer. Try rephrasing your question."


@app.event("app_mention")
def handle_mention(event, client):
    channel = event["channel"]
    user_id = event.get("user", "unknown")
    thread_ts = event.get("thread_ts", event["ts"])
    message = event["text"]

    # adk_user_id mirrors production: thread_ts without dots (Agent Engine constraint)
    adk_user_id = thread_ts.replace(".", "")

    # Acknowledge immediately — mirrors production's 200 OK before async processing
    client.chat_postMessage(
        channel=channel,
        thread_ts=thread_ts,
        text=f"<@{user_id}> Thinking...",
    )

    try:
        # Session lookup / creation — mirrors Firestore lookup in production
        session_id = get_session_id(thread_ts)
        if not session_id:
            session_id = create_adk_session(user_id=adk_user_id)
            upsert_session(thread_ts, session_id)
            logging.info(f"Created new session: {session_id}")
        else:
            logging.info(f"Reusing session: {session_id}")

        response_text = query_adk_agent(adk_user_id, session_id, message)

        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"<@{user_id}> {response_text}",
        )

    except Exception:
        logging.exception("Error handling Slack mention")
        client.chat_postMessage(
            channel=channel,
            thread_ts=thread_ts,
            text=f"<@{user_id}> Sorry, something went wrong. Please try again.",
        )


if __name__ == "__main__":
    init_db()
    logging.info("Starting Slack bot in Socket Mode...")
    handler = SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"])
    handler.start()
