from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.database import db_manager

router = APIRouter(prefix="/api/db", tags=["Database Management"])

class MySQLConnectionRequest(BaseModel):
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "root"
    password: str = ""
    database: str = "tubeflow_db"
    migrate_data: bool = True

class RawQueryRequest(BaseModel):
    sql: str

@router.get("/status")
def get_status():
    return db_manager.get_status()

@router.post("/test-connection")
def test_connection(req: MySQLConnectionRequest):
    return db_manager.test_connection_params(
        host=req.host,
        port=req.port,
        user=req.user,
        password=req.password,
        database=req.database
    )

@router.post("/switch-mysql")
def switch_mysql(req: MySQLConnectionRequest):
    result = db_manager.switch_to_mysql(
        host=req.host,
        port=req.port,
        user=req.user,
        password=req.password,
        database=req.database,
        migrate_data=req.migrate_data
    )
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Switch failed"))
    return result

@router.post("/query")
def run_query(req: RawQueryRequest):
    query = req.sql.strip()
    if not query:
        raise HTTPException(status_code=400, detail="SQL query cannot be empty")
    return db_manager.execute_raw_sql(query)

@router.get("/schema-info")
def get_schema_info():
    if not db_manager.engine:
        return {"tables": {}}
    from sqlalchemy import inspect
    inspector = inspect(db_manager.engine)
    table_names = inspector.get_table_names()
    info = {}
    for t in table_names:
        cols = inspector.get_columns(t)
        info[t] = [
            {
                "name": c["name"],
                "type": str(c["type"]),
                "nullable": c.get("nullable", True),
                "default": str(c.get("default", "")) if c.get("default") else None
            }
            for c in cols
        ]
    return {"engine": db_manager.active_engine_type, "tables": info}
