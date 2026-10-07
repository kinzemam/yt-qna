from db import get_conn

def create_chat(user_id, video_id):
    with get_conn() as conn:
        row = conn.execute("insert into chats (user_id, video_id) values(%s, %s) returning id", (user_id, video_id)).fetchone()
    return row[0]    
    
def add_message(chat_id, role, content):
    with get_conn() as conn:
        row = conn.execute("insert into messages (chat_id, role, content) values (%s, %s, %s)", (chat_id, role, content))
    
def get_messages(chat_id):
    with get_conn() as conn:
        rows = conn.execute("select id, role, content from messages where chat_id=%s order by created_at, id", (chat_id,)).fetchall()
    return [{"role":role, "content":content, "id":id} for id, role, content in rows]

def get_chat_owner(chat_id):
    with get_conn() as conn:
        row = conn.execute('select user_id from chats where id=%s', (chat_id,)).fetchone()
    return row[0] if row else None

def list_chats(user_id):
    with get_conn() as conn:
        rows = conn.execute("select id, video_id, created_at from chats where user_id=%s order by created_at desc", (user_id,)).fetchall()
        return [
            { "id": id_, "video_id": video_id, "created_at": created_at.isoformat()} for id_, video_id, created_at in rows  
        ]

if __name__=="__main__":
    chat_id = create_chat(2, "testvid123")
    add_message(chat_id, "Human", "Hello AI")
    add_message(chat_id, "AI", "Hello World")
    print(get_messages(chat_id))
    