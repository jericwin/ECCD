import logging
import time
import os
import ssl
from config import Config

logger = logging.getLogger('db')

def get_db_connection():
    """
    Create a fresh MySQL connection each time.
    Prefers pure-Python PyMySQL for serverless/Vercel compatibility,
    falls back to mysql.connector.
    """
    # 1. Try PyMySQL (pure Python, recommended for Vercel/serverless)
    try:
        import pymysql
        import pymysql.cursors

        kwargs = {
            "host": Config.DB_HOST,
            "port": Config.DB_PORT,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DB_NAME,
            "connect_timeout": 10,
            "autocommit": False,
            "cursorclass": pymysql.cursors.DictCursor
        }

        if Config.DB_SSL:
            ctx = ssl.create_default_context()
            if Config.CA_PATH and os.path.exists(Config.CA_PATH):
                ctx.load_verify_locations(cafile=Config.CA_PATH)
            else:
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
            kwargs['ssl'] = ctx

        return pymysql.connect(**kwargs)

    except ImportError:
        pass
    except Exception as e:
        # If PyMySQL failed on connect, log and fallback
        logger.warning(f"PyMySQL connection failed ({e}), attempting mysql.connector fallback...")

    # 2. Fallback to mysql.connector
    try:
        import mysql.connector

        kwargs = {
            "host": Config.DB_HOST,
            "port": Config.DB_PORT,
            "user": Config.DB_USER,
            "password": Config.DB_PASSWORD,
            "database": Config.DB_NAME,
            "connection_timeout": 10,
            "autocommit": False
        }

        if Config.DB_SSL:
            if Config.CA_PATH and os.path.exists(Config.CA_PATH):
                kwargs['ssl_ca'] = Config.CA_PATH
            else:
                kwargs['ssl_disabled'] = False

        return mysql.connector.connect(**kwargs)

    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def execute_query(query, params=(), commit=False, fetch_all=False, fetch_one=False):
    conn = None
    cursor = None
    result = None
    start_time = time.time()
    try:
        logger.info(f"DB_SQL: executing: {query.strip().replace(chr(10), ' ')} with params: {params}")
        conn = get_db_connection()
        # Handle dictionary cursor across mysql.connector and PyMySQL
        try:
            cursor = conn.cursor(dictionary=True)
        except TypeError:
            cursor = conn.cursor()

        cursor.execute(query, params)
        
        if commit:
            conn.commit()
            result = {
                'lastrowid': cursor.lastrowid,
                'rowcount': cursor.rowcount
            }
        elif fetch_all:
            result = cursor.fetchall()
        elif fetch_one:
            result = cursor.fetchone()
            
        elapsed = time.time() - start_time
        logger.info(f"DB_SQL_SUCCESS: Query completed in {elapsed:.4f}s")
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"DB_SQL_ERROR: Query failed after {elapsed:.4f}s: {e}\nQuery: {query}\nParams: {params}")
        if conn and commit:
            try:
                conn.rollback()
            except Exception:
                pass
        raise e
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
        if conn:
            try:
                conn.close()
            except Exception:
                pass
            
    return result

