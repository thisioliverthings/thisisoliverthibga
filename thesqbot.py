import sqlite3

DATABASE_FILE = "user_data.db"

def update_db():
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        try:
            # إضافة عمود account_number
            cursor.execute("ALTER TABLE users ADD COLUMN account_number TEXT")
            print("تم إضافة العمود 'account_number' بنجاح.")
        except sqlite3.OperationalError as e:
            print(f"حدث خطأ: {e}")

if __name__ == '__main__':
    update_db()