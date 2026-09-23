from dataclasses import dataclass
from fastapi import Header, HTTPException

@dataclass(frozen=True)
class CurrentUser:
    id: str
    email: str
    role: str

async def current_user(
    x_user_id: str = Header(default="demo-user", alias="X-User-ID"),
    x_user_email: str = Header(default="finance.manager@example.com", alias="X-User-Email"),
    x_user_role: str = Header(default="FINANCE_MANAGER", alias="X-User-Role"),
) -> CurrentUser:
    return CurrentUser(x_user_id, x_user_email, x_user_role)

def require_role(*roles: str):
    async def dependency(user: CurrentUser = None):
        user = user or await current_user()
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user
    return dependency
