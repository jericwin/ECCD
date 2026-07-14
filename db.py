import mysql.connector
import logging
import time
from config import Config

logger = logging.getLogger('db')

def get_db_connection():
    """
    Create a fresh MySQL connection each time.
    """
    try:
        conn = mysql.connector.connect(
            host=Config.DB_HOST,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME,
            connection_timeout=10,
            autocommit=False
        )
        return conn
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise

def execute_query(query, params=(), commit=False, fetch_all=False, fetch_one=False):
    conn = None
    cursor = None
    result = None
    start_time = time.time()
    try:
        logger.info(f"DB_SQL: executing: {query.strip().replace('\n', ' ')} with params: {params}")
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
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
