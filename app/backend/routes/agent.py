from fastapi import APIRouter
from pydantic import BaseModel
from db import get_connection
import json

router = APIRouter(prefix="/api/v1", tags=["agent"])


class ChatRequest(BaseModel):
    message: str


@router.post("/agent/chat")
def agent_chat(req: ChatRequest):
    conn = get_connection()
    try:
        cur = conn.cursor()
        sql = """
            SELECT SNOWFLAKE.CORTEX.DATA_AGENT_RUN(
                'MTA_DEMO.ANALYTICS.MTA_AGENT',
                %s
            )
        """
        cur.execute(sql, (req.message,))
        row = cur.fetchone()
        if row and row[0]:
            result = json.loads(row[0]) if isinstance(row[0], str) else row[0]
            return result
        return {"message": "No response from agent"}
    finally:
        conn.close()
