import psycopg2


def get_connection():
    return psycopg2.connect(
        host="127.0.0.1",
        port=5432,
        database="utility_intelligence_db",
        user="postgres",
    )


def create_admin_config_table():
    """
    Create the admin_config table if it does not already exist.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin_config (
            id SERIAL PRIMARY KEY,
            config_key VARCHAR(100) UNIQUE NOT NULL,
            config_value TEXT,
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

    cursor.close()
    conn.close()


def set_config(config_key, config_value, description=""):
    """
    Insert or update an admin configuration value.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO admin_config
            (config_key, config_value, description)
        VALUES (%s, %s, %s)
        ON CONFLICT (config_key)
        DO UPDATE SET
            config_value = EXCLUDED.config_value,
            description = EXCLUDED.description,
            updated_at = CURRENT_TIMESTAMP;
    """, (
        config_key,
        str(config_value),
        description
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_config(config_key, default=None):
    """
    Get one configuration value.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT config_value
        FROM admin_config
        WHERE config_key = %s;
    """, (config_key,))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is None:
        return default

    return result[0]


def get_all_config():
    """
    Get all admin configuration settings.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            config_key,
            config_value,
            description,
            updated_at
        FROM admin_config
        ORDER BY config_key;
    """)

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def create_question_history_table():
    """
    Create the AI question history table.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS question_history (
            id SERIAL PRIMARY KEY,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            data_signature TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    conn.commit()

    cursor.close()
    conn.close()


def save_question_history(question, answer, data_signature=""):
    """
    Save an AI question and its answer.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO question_history
            (question, answer, data_signature)
        VALUES (%s, %s, %s);
    """, (
        question,
        answer,
        data_signature
    ))

    conn.commit()

    cursor.close()
    conn.close()


def get_question_history(limit=20):
    """
    Get recent AI question history.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            id,
            question,
            answer,
            data_signature,
            created_at
        FROM question_history
        ORDER BY created_at DESC
        LIMIT %s;
    """, (limit,))

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    return rows

def clear_question_history():
    """
    Delete all saved AI question history.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        DELETE FROM question_history;
    """)

    conn.commit()

    cursor.close()
    conn.close()

def get_previous_answer(question, data_signature=""):
    """
    Return the previous answer for the same question
    and the same data version.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT answer
        FROM question_history
        WHERE LOWER(TRIM(question)) = LOWER(TRIM(%s))
        AND data_signature = %s
        ORDER BY created_at DESC
        LIMIT 1;
    """, (
        question,
        data_signature
    ))

    result = cursor.fetchone()

    cursor.close()
    conn.close()

    if result is None:
        return None

    return result[0]
if __name__ == "__main__":

    try:

        conn = get_connection()

        print("DATABASE CONNECTION SUCCESSFUL")

        conn.close()

        create_admin_config_table()
        create_question_history_table()

        print("ADMIN CONFIG TABLE READY")
        print("QUESTION HISTORY TABLE READY")

    except Exception as e:

        print("DATABASE ERROR")
        print(e)

    