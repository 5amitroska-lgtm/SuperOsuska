from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, Response, Request, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

# --- Konfigurácia ---
SECRET_KEY = "tu-by-mal-byt-velmi-silny-tajny-kluc-zabezpeceny-v-env"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI(title="FastAPI Auth Demo")

# CORS nastavenie pre komunikáciu s React frontendom
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Predvolená adresa Vite/Reactu
    allow_credentials=True,  # Kľúčové pre cookies!
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Hashovanie hesiel ---
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> str:
    return pwd_context.verify(plain_password, hashed_password)


# --- Simulovaná databáza ---
# V reálnej aplikácii tu budete volať PostgreSQL cez SQLAlchemy
fake_users_db = {
    "admin@example.com": {
        "email": "admin@example.com",
        "hashed_password": hash_password("tajneheslo123"),
        "full_name": "Ján Novák"
    }
}


# --- Pydantic schémy ---
class LoginRequest(BaseModel):
    email: str
    password: str


# --- JWT helper funkcie ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# --- Dependencia na overenie používateľa cez Cookie ---
def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nie ste prihlásený (chybajúci token)"
        )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Neplatný token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Neplatný alebo exspirovaný token")

    user = fake_users_db.get(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Používateľ neexistuje")
    return user


# --- Endpointy ---

@app.post("/api/login")
def login(body: LoginRequest, response: Response):
    # 1. Kontrola používateľa
    user = fake_users_db.get(body.email)
    if not user or not verify_password(body.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nesprávny email alebo heslo"
        )

    # 2. Vytvorenie JWT tokenu
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )

    # 3. Uloženie do HttpOnly cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # V produkcii (HTTPS) zmeňte na True!
        samesite="lax",  # Ochrana proti CSRF
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    return {"message": "Prihlásenie úspešné", "email": user["email"]}


@app.get("/api/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    # Tento endpoint je chránený - vyžaduje platnú cookie s JWT
    return {
        "email": current_user["email"],
        "full_name": current_user["full_name"]
    }


@app.post("/api/logout")
def logout(response: Response):
    # Vymazanie cookie nastavením prázdnej hodnoty a okamžitej exspirácie
    response.delete_cookie(key="access_token", httponly=True, secure=False, samesite="lax")
    return {"message": "Úspešne odhlásený"}