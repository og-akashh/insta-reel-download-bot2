# In-memory store of verified users (chat_id -> bool)
# For production, replace with Redis or database
verified_users = set()

def is_user_verified(chat_id: int) -> bool:
    return chat_id in verified_users

def set_user_verified(chat_id: int, verified: bool = True):
    if verified:
        verified_users.add(chat_id)
    else:
        verified_users.discard(chat_id)

def clear_verification(chat_id: int):
    verified_users.discard(chat_id)
