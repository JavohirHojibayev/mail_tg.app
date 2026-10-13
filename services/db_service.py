import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import config

logger = logging.getLogger(__name__)

class DBService:
    def __init__(self):
        self.host = config.DB_HOST
        self.port = config.DB_PORT
        self.dbname = config.DB_NAME
        self.user = config.DB_USER
        self.password = config.DB_PASSWORD

    def _get_connection(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            dbname=self.dbname,
            user=self.user,
            password=self.password,
            connect_timeout=3,
            cursor_factory=RealDictCursor
        )

    def is_available(self) -> bool:
        """PostgreSQL bazasiga ulanish mumkinligini tekshiradi"""
        try:
            conn = self._get_connection()
            conn.close()
            return True
        except Exception as e:
            logger.debug(f"DB mavjud emas: {e}")
            return False

    def get_users(self, search: str = None, department: str = None) -> list:
        """Barcha faol xodimlarni bazadan oladi"""
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            query = """
                SELECT 
                    m.username as email,
                    COALESCE(mp.display_name, m.name, split_part(m.username, '@', 1)) as name,
                    COALESCE(mp.position, '') as position,
                    COALESCE(mp.department, '') as department,
                    COALESCE(mp.phone, '') as phone,
                    COALESCE(mp.is_online, false) as is_online,
                    mp.last_seen
                FROM mailbox m
                LEFT JOIN messenger_profiles mp ON mp.email = m.username
                WHERE m.active = 1 AND m.domain = %s
            """
            params = [config.MAIL_DOMAIN]

            if search:
                query += """ AND (
                    m.username ILIKE %s OR
                    m.name ILIKE %s OR
                    mp.display_name ILIKE %s OR
                    mp.department ILIKE %s OR
                    mp.position ILIKE %s
                )"""
                term = f"%{search}%"
                params.extend([term, term, term, term, term])

            if department:
                query += " AND mp.department = %s"
                params.append(department)

            query += " ORDER BY name ASC LIMIT 300"
            cur.execute(query, params)
            rows = cur.fetchall()
            return [dict(r) for r in rows]
        except Exception as e:
            logger.error(f"DB get_users xatosi: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def get_departments(self) -> list:
        """Mavjud bo'limlar ro'yxatini oladi"""
        conn = None
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT DISTINCT department 
                FROM messenger_profiles 
                WHERE department IS NOT NULL AND department != ''
                ORDER BY department
            """)
            rows = cur.fetchall()
            return [r['department'] for r in rows if r['department']]
        except Exception as e:
            logger.error(f"DB get_departments xatosi: {e}")
            return []
        finally:
            if conn:
                conn.close()
