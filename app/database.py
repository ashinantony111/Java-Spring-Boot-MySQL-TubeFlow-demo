import os
import time
import logging
from typing import Dict, Any, List, Optional
import pymysql
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app import config

logger = logging.getLogger("tubeflow.db")
logging.basicConfig(level=logging.INFO)

Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.active_engine_type = "sqlite"
        self.engine = None
        self.SessionLocal = None
        self.is_connected = False
        self.error_message: Optional[str] = None
        self.mysql_config = {
            "host": config.MYSQL_HOST,
            "port": config.MYSQL_PORT,
            "user": config.MYSQL_USER,
            "password": config.MYSQL_PASSWORD,
            "database": config.MYSQL_DB
        }
        self.initialize()

    def get_mysql_url(self, conf: Optional[Dict[str, Any]] = None, with_db: bool = True) -> str:
        c = conf or self.mysql_config
        pwd = f":{c['password']}" if c['password'] else ""
        db_part = f"/{c['database']}?charset=utf8mb4" if with_db else "?charset=utf8mb4"
        return f"mysql+pymysql://{c['user']}{pwd}@{c['host']}:{c['port']}{db_part}"

    def try_connect_mysql(self, conf: Optional[Dict[str, Any]] = None) -> bool:
        c = conf or self.mysql_config
        try:
            # 1. Connect without DB first to ensure DB exists
            conn = pymysql.connect(
                host=c["host"],
                port=int(c["port"]),
                user=c["user"],
                password=c["password"],
                connect_timeout=3
            )
            with conn.cursor() as cursor:
                cursor.execute(
                    f"CREATE DATABASE IF NOT EXISTS `{c['database']}` "
                    f"CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
                )
            conn.close()

            # 2. Test SQLAlchemy engine with DB
            mysql_url = self.get_mysql_url(c, with_db=True)
            engine = create_engine(
                mysql_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))

            self.engine = engine
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            self.active_engine_type = "mysql"
            self.is_connected = True
            self.error_message = None
            if conf:
                self.mysql_config = conf
            logger.info("Successfully connected to MySQL database: %s", c["database"])
            return True
        except Exception as e:
            self.error_message = str(e)
            logger.warning("Could not connect to MySQL (%s:%s): %s", c["host"], c["port"], e)
            return False

    def init_sqlite_fallback(self):
        sqlite_url = f"sqlite:///{config.SQLITE_DB_PATH}"
        self.engine = create_engine(
            sqlite_url,
            connect_args={"check_same_thread": False},
            echo=False
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.active_engine_type = "sqlite"
        self.is_connected = True
        logger.info("Using SQLite fallback storage at %s", config.SQLITE_DB_PATH)
        self.ensure_schema_and_seed()

    def ensure_schema_and_seed(self):
        try:
            from app.models import Base
            Base.metadata.create_all(bind=self.engine)
            from app.seed_data import seed_database
            with self.SessionLocal() as session:
                seed_database(session, engine=self.engine)
        except Exception as e:
            logger.error("Error creating schema or seeding: %s", e)

    def initialize(self):
        connected = self.try_connect_mysql()
        if connected:
            self.ensure_schema_and_seed()
        else:
            if config.USE_SQLITE_FALLBACK:
                logger.info("MySQL unavailable on startup. Falling back to local SQLite mirror.")
                self.init_sqlite_fallback()
            else:
                self.is_connected = False

    def get_status(self) -> Dict[str, Any]:
        table_counts = {}
        try:
            if self.engine:
                inspector = inspect(self.engine)
                table_names = inspector.get_table_names()
                with self.engine.connect() as conn:
                    for t in table_names:
                        try:
                            res = conn.execute(text(f"SELECT COUNT(*) FROM `{t}`")).scalar()
                            table_counts[t] = res
                        except Exception:
                            table_counts[t] = 0
            else:
                table_names = []
        except Exception as e:
            table_names = []

        return {
            "active_engine": self.active_engine_type,
            "is_connected": self.is_connected,
            "mysql_host": self.mysql_config["host"],
            "mysql_port": self.mysql_config["port"],
            "mysql_user": self.mysql_config["user"],
            "mysql_database": self.mysql_config["database"],
            "has_password": bool(self.mysql_config["password"]),
            "error_message": self.error_message,
            "tables": table_names,
            "table_counts": table_counts,
            "sqlite_file": str(config.SQLITE_DB_PATH)
        }

    def test_connection_params(self, host: str, port: int, user: str, password: str, database: str) -> Dict[str, Any]:
        try:
            conn = pymysql.connect(
                host=host,
                port=int(port),
                user=user,
                password=password,
                connect_timeout=4
            )
            server_version = conn.get_server_info()
            with conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES;")
                dbs = [row[0] for row in cursor.fetchall()]
            conn.close()
            return {
                "success": True,
                "message": f"Connection successful! Server: MySQL {server_version}",
                "databases": dbs,
                "target_db_exists": database in dbs
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Connection failed: {str(e)}"
            }

    def switch_to_mysql(self, host: str, port: int, user: str, password: str, database: str, migrate_data: bool = True) -> Dict[str, Any]:
        conf = {
            "host": host,
            "port": int(port),
            "user": user,
            "password": password,
            "database": database
        }
        test_res = self.test_connection_params(host, port, user, password, database)
        if not test_res["success"]:
            return test_res

        old_engine = self.engine
        old_engine_type = self.active_engine_type

        success = self.try_connect_mysql(conf)
        if not success:
            return {"success": False, "message": f"Failed to switch to MySQL: {self.error_message}"}

        # Create schema in MySQL
        from app.models import Base as ModelsBase
        ModelsBase.metadata.create_all(bind=self.engine)

        migrated_tables = []
        # If migrate_data is requested and previously had SQLite data
        if migrate_data and old_engine and old_engine_type == "sqlite":
            try:
                from sqlalchemy import MetaData, Table
                metadata_source = MetaData()
                metadata_source.reflect(bind=old_engine)
                
                with old_engine.connect() as src_conn, self.engine.connect() as dst_conn:
                    for table_name in [
                        "categories", "users", "channels", "videos", "comments",
                        "video_reactions", "comment_reactions", "subscriptions",
                        "playlists", "playlist_items", "watch_history", "watch_later"
                    ]:
                        if table_name in metadata_source.tables:
                            src_table = metadata_source.tables[table_name]
                            rows = src_conn.execute(src_table.select()).fetchall()
                            if rows:
                                dst_table = Table(table_name, ModelsBase.metadata, autoload_with=self.engine)
                                # Clean existing in dest first
                                dst_conn.execute(text(f"SET FOREIGN_KEY_CHECKS=0;"))
                                dst_conn.execute(dst_table.delete())
                                insert_data = [dict(row._mapping) for row in rows]
                                dst_conn.execute(dst_table.insert(), insert_data)
                                dst_conn.execute(text(f"SET FOREIGN_KEY_CHECKS=1;"))
                                dst_conn.commit()
                                migrated_tables.append(f"{table_name} ({len(rows)} rows)")
            except Exception as mig_err:
                logger.error("Migration error: %s", mig_err)

        return {
            "success": True,
            "message": f"Successfully connected to MySQL database '{database}'!",
            "migrated_tables": migrated_tables
        }

    def execute_raw_sql(self, sql_query: str) -> Dict[str, Any]:
        start = time.time()
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text(sql_query))
                duration_ms = round((time.time() - start) * 1000, 2)
                
                if result.returns_rows:
                    columns = list(result.keys())
                    rows = [list(r) for r in result.fetchmany(100)]
                    return {
                        "success": True,
                        "columns": columns,
                        "rows": rows,
                        "row_count": len(rows),
                        "duration_ms": duration_ms
                    }
                else:
                    conn.commit()
                    return {
                        "success": True,
                        "columns": [],
                        "rows": [],
                        "row_count": result.rowcount,
                        "duration_ms": duration_ms,
                        "message": f"Query executed. {result.rowcount} rows affected."
                    }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_ms": round((time.time() - start) * 1000, 2)
            }

db_manager = DatabaseManager()

def get_db():
    db: Session = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()
