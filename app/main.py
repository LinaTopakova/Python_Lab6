from fastapi import FastAPI
from app.database import engine, Base
from app.routers import users_router, auth_router  

app = FastAPI(
    title="JWT Auth Lab",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_js_url="/static/swagger-ui-bundle.js",
    swagger_css_url="/static/swagger-ui.css",
)

app.include_router(users_router)
app.include_router(auth_router)   

@app.on_event("startup")
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def root():
    return {"message": "Hello, JWT!"}