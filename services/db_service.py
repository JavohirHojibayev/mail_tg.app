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
            connect_timeout=1,
            cursor_factory=RealDictCursor
        )

    def _is_direct_available(self) -> bool:
        if not self.password:
            return False
        try:
            conn = self._get_connection()
            conn.close()
            return True
        except Exception:
            return False

    def is_available(self) -> bool:
        """Server bazasiga (to'g'ridan-to'g'ri yoki SSH orqali) ulanish mumkinligini tekshiradi"""
        if self._is_direct_available():
            return True
        return bool(config.SSH_HOST and config.SSH_PASSWORD)

    def _get_users_from_ssh(self) -> list:
        if not config.SSH_HOST or not config.SSH_PASSWORD:
            return []
        try:
            import paramiko
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            client.connect(
                config.SSH_HOST,
                username=config.SSH_USER,
                password=config.SSH_PASSWORD,
                timeout=5
            )
            sql = """
                SELECT 
                    m.username as email,
                    COALESCE(NULLIF(mp.display_name, ''), NULLIF(m.name, ''), split_part(m.username, '@', 1)) as name
                FROM mailbox m
                LEFT JOIN messenger_profiles mp ON mp.email = m.username
                WHERE m.active = 1
                ORDER BY name ASC;
            """
            cmd = f"PGPASSWORD='{self.password}' psql -h 127.0.0.1 -U {self.user} -d {self.dbname} -t -A -F'|' -c \"{sql}\""
            stdin, stdout, stderr = client.exec_command(cmd)
            raw = stdout.read().decode('utf-8').strip()
            client.close()

            if not raw:
                return []

            users = []
            for line in raw.split('\n'):
                if not line.strip():
                    continue
                parts = line.split('|')
                if len(parts) >= 2:
                    email = parts[0].strip().lower()
                    name = parts[1].strip() or email.split('@')[0]
                    users.append({"name": name, "email": email})
            return users
        except Exception as e:
            logger.error(f"SSH get_users xatosi: {e}")
            return []

    def get_users(self) -> list:
        """Serverdan (to'g'ridan-to'g'ri DB yoki SSH orqali) eng so'nggi xodimlar ro'yxatini oladi"""
        # 1. To'g'ridan-to'g'ri PostgreSQL orqali urinib ko'rish
        if self._is_direct_available():
            conn = None
            try:
                conn = self._get_connection()
                cur = conn.cursor()
                query = """
                    SELECT 
                        m.username as email,
                        COALESCE(NULLIF(mp.display_name, ''), NULLIF(m.name, ''), split_part(m.username, '@', 1)) as name
                    FROM mailbox m
                    LEFT JOIN messenger_profiles mp ON mp.email = m.username
                    WHERE m.active = 1
                    ORDER BY name ASC
                """
                cur.execute(query)
                rows = cur.fetchall()
                return [dict(r) for r in rows]
            except Exception as e:
                logger.error(f"DB get_users xatosi: {e}")
            finally:
                if conn:
                    conn.close()

        # 2. Agar port 5432 tashqaridan yopiq bo'lsa, xavfsiz SSH orqali olish
        return self._get_users_from_ssh()
