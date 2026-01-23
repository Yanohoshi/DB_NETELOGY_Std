import psycopg2
from psycopg2 import sql


def create_database(db_name, user, password):
    """
    Создает базу данных если она не существует
    Использует контекстные менеджеры (with) для автоматического управления ресурсами
    """
    try:
        print(f"Попытка создания базы данных '{db_name}'...")

        # Используем контекстный менеджер для подключения к postgres
        with psycopg2.connect(
                dbname="postgres",  # подключаемся к стандартной базе данных
                user=user,
                password=password,
                host="localhost",
                port="5432"
        ) as conn:
            # Устанавливаем autocommit для создания базы данных
            conn.autocommit = True

            # Используем контекстный менеджер для курсора
            with conn.cursor() as cur:
                # Проверяем существует ли база данных
                cur.execute(
                    "SELECT 1 FROM pg_database WHERE datname = %s",
                    (db_name,)
                )
                exists = cur.fetchone()

                if not exists:
                    # Создаем базу данных с использованием sql.Identifier для безопасности
                    cur.execute(
                        sql.SQL("CREATE DATABASE {}").format(
                            sql.Identifier(db_name)
                        )
                    )
                    print(f"✅ База данных '{db_name}' создана успешно")
                else:
                    print(f"ℹ️ База данных '{db_name}' уже существует")

        return True

    except psycopg2.OperationalError as e:
        print(f"❌ Ошибка подключения: {e}")
        print("\nУбедитесь, что:")
        print("1. PostgreSQL установлен и запущен")
        print("2. Используются правильные учетные данные")
        print("3. Сервер PostgreSQL доступен по указанному адресу")
        return False

    except Exception as e:
        print(f"❌ Ошибка при создании базы данных: {e}")
        return False


def connect_to_db(db_name, user, password):
    """
    Подключение к базе данных с использованием контекстного менеджера
    Возвращает соединение, которое нужно закрыть вручную
    """
    try:
        conn = psycopg2.connect(
            dbname=db_name,
            user=user,
            password=password,
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"❌ Ошибка подключения к базе данных: {e}")
        return None


def create_db(conn):
    """
    1. Функция, создающая структуру БД (таблицы)
    """
    try:
        # Используем контекстные менеджеры для курсора
        with conn.cursor() as cur:
            # Создаем таблицу клиентов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    id SERIAL PRIMARY KEY,
                    first_name VARCHAR(50) NOT NULL,
                    last_name VARCHAR(50) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Создаем таблицу телефонов
            cur.execute("""
                CREATE TABLE IF NOT EXISTS phones (
                    id SERIAL PRIMARY KEY,
                    client_id INTEGER NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
                    phone_number VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Создаем индексы для ускорения поиска
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_name 
                ON clients(first_name, last_name)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_clients_email 
                ON clients(email)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_phones_client 
                ON phones(client_id)
            """)

            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_phones_number 
                ON phones(phone_number)
            """)

        conn.commit()
        print("✅ Структура базы данных создана успешно")
        return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при создании таблиц: {e}")
        return False


def add_client(conn, first_name, last_name, email, phones=None):
    """
    2. Функция, позволяющая добавить нового клиента
    """
    try:
        with conn.cursor() as cur:
            # Добавляем клиента
            cur.execute(
                """
                INSERT INTO clients (first_name, last_name, email)
                VALUES (%s, %s, %s)
                RETURNING id
                """,
                (first_name, last_name, email)
            )

            client_id = cur.fetchone()[0]

            # Добавляем телефоны, если они есть
            if phones:
                for phone in phones:
                    cur.execute(
                        """
                        INSERT INTO phones (client_id, phone_number)
                        VALUES (%s, %s)
                        """,
                        (client_id, phone)
                    )

            conn.commit()
            print(f"✅ Клиент {first_name} {last_name} добавлен (ID: {client_id})")
            return client_id

    except psycopg2.IntegrityError as e:
        conn.rollback()
        if "unique constraint" in str(e).lower() and "email" in str(e).lower():
            print(f"❌ Ошибка: клиент с email '{email}' уже существует")
        else:
            print(f"❌ Ошибка при добавлении клиента: {e}")
        return None
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка: {e}")
        return None


def add_phone(conn, client_id, phone):
    """
    3. Функция, позволяющая добавить телефон для существующего клиента
    """
    try:
        # Проверяем существует ли клиент
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            if not cur.fetchone():
                print(f"❌ Ошибка: клиент с ID {client_id} не найден")
                return False

        with conn.cursor() as cur:
            # Добавляем телефон
            cur.execute(
                """
                INSERT INTO phones (client_id, phone_number)
                VALUES (%s, %s)
                """,
                (client_id, phone)
            )

            conn.commit()
            print(f"✅ Телефон {phone} добавлен клиенту с ID: {client_id}")
            return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при добавлении телефона: {e}")
        return False


def change_client(conn, client_id, first_name=None, last_name=None, email=None, phones=None):
    """
    4. Функция, позволяющая изменить данные о клиенте
    """
    try:
        # Проверяем существует ли клиент
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            if not cur.fetchone():
                print(f"❌ Ошибка: клиент с ID {client_id} не найден")
                return False

        # Формируем запрос на обновление данных клиента
        updates = []
        params = []

        if first_name is not None:
            updates.append("first_name = %s")
            params.append(first_name)

        if last_name is not None:
            updates.append("last_name = %s")
            params.append(last_name)

        if email is not None:
            updates.append("email = %s")
            params.append(email)

        if updates:
            params.append(client_id)
            query = f"UPDATE clients SET {', '.join(updates)} WHERE id = %s"

            with conn.cursor() as cur:
                cur.execute(query, tuple(params))

        # Обновляем телефоны, если они предоставлены
        if phones is not None:
            with conn.cursor() as cur:
                # Удаляем все существующие телефоны
                cur.execute("DELETE FROM phones WHERE client_id = %s", (client_id,))

                # Добавляем новые телефоны
                for phone in phones:
                    cur.execute(
                        "INSERT INTO phones (client_id, phone_number) VALUES (%s, %s)",
                        (client_id, phone)
                    )

        conn.commit()
        print(f"✅ Данные клиента с ID {client_id} обновлены")
        return True

    except psycopg2.IntegrityError:
        conn.rollback()
        print(f"❌ Ошибка: email '{email}' уже используется другим клиентом")
        return False
    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при обновлении клиента: {e}")
        return False


def delete_phone(conn, client_id, phone):
    """
    5. Функция, позволяющая удалить телефон для существующего клиента
    """
    try:
        # Проверяем существует ли клиент
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM clients WHERE id = %s", (client_id,))
            if not cur.fetchone():
                print(f"❌ Ошибка: клиент с ID {client_id} не найден")
                return False

        with conn.cursor() as cur:
            # Удаляем телефон
            cur.execute(
                """
                DELETE FROM phones 
                WHERE client_id = %s AND phone_number = %s
                """,
                (client_id, phone)
            )

            conn.commit()

            if cur.rowcount > 0:
                print(f"✅ Телефон {phone} удален у клиента с ID: {client_id}")
                return True
            else:
                print(f"❌ Телефон {phone} не найден у клиента с ID: {client_id}")
                return False

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при удалении телефона: {e}")
        return False


def delete_client(conn, client_id):
    """
    6. Функция, позволяющая удалить существующего клиента
    """
    try:
        # Проверяем существует ли клиент
        with conn.cursor() as cur:
            cur.execute("SELECT id, first_name, last_name FROM clients WHERE id = %s", (client_id,))
            client = cur.fetchone()

            if not client:
                print(f"❌ Ошибка: клиент с ID {client_id} не найден")
                return False

            client_name = f"{client[1]} {client[2]}"

        with conn.cursor() as cur:
            # Удаляем клиента (телефоны удалятся каскадно)
            cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            conn.commit()

            print(f"✅ Клиент '{client_name}' (ID: {client_id}) удален")
            return True

    except Exception as e:
        conn.rollback()
        print(f"❌ Ошибка при удалении клиента: {e}")
        return False


def find_client(conn, first_name=None, last_name=None, email=None, phone=None):
    """
    7. Функция, позволяющая найти клиента по его данным
    """
    try:
        with conn.cursor() as cur:
            # Начинаем формировать запрос
            query = """
                SELECT DISTINCT c.id, c.first_name, c.last_name, c.email, 
                       COALESCE(
                           STRING_AGG(p.phone_number, ', ' ORDER BY p.created_at),
                           'нет телефона'
                       ) as phones
                FROM clients c
                LEFT JOIN phones p ON c.id = p.client_id
                WHERE 1=1
            """

            params = []

            # Добавляем условия поиска
            if first_name:
                query += " AND c.first_name ILIKE %s"
                params.append(f'%{first_name}%')

            if last_name:
                query += " AND c.last_name ILIKE %s"
                params.append(f'%{last_name}%')

            if email:
                query += " AND c.email ILIKE %s"
                params.append(f'%{email}%')

            if phone:
                query += " AND p.phone_number ILIKE %s"
                params.append(f'%{phone}%')

            query += " GROUP BY c.id ORDER BY c.id"

            cur.execute(query, params)
            results = cur.fetchall()

            if results:
                print(f"\n🔍 Найдено {len(results)} клиент(ов):")
                print("-" * 70)
                for row in results:
                    client_id, first_name, last_name, email, phones = row
                    print(f"  ID: {client_id}")
                    print(f"    Имя: {first_name} {last_name}")
                    print(f"    Email: {email}")
                    print(f"    Телефоны: {phones}")
                    print("    " + "-" * 40)
                return results
            else:
                print("\n🔍 Клиенты не найдены")
                return []

    except Exception as e:
        print(f"❌ Ошибка при поиске клиентов: {e}")
        return []


def display_all_clients(conn):
    """
    Вспомогательная функция: отображение всех клиентов
    """
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT c.id, c.first_name, c.last_name, c.email, c.created_at,
                       COALESCE(
                           STRING_AGG(p.phone_number, ', ' ORDER BY p.created_at),
                           'нет телефона'
                       ) as phones,
                       COUNT(p.id) as phone_count
                FROM clients c
                LEFT JOIN phones p ON c.id = p.client_id
                GROUP BY c.id, c.created_at
                ORDER BY c.id
            """)

            clients = cur.fetchall()

            if not clients:
                print("\n📭 В базе данных нет клиентов")
                return

            print("\n" + "=" * 70)
            print("📋 СПИСОК ВСЕХ КЛИЕНТОВ")
            print("=" * 70)

            total_clients = 0
            total_phones = 0

            for client in clients:
                client_id, first_name, last_name, email, created_at, phones, phone_count = client
                total_clients += 1
                total_phones += phone_count if phone_count else 0

                print(f"\n👤 ID: {client_id}")
                print(f"   Имя: {first_name} {last_name}")
                print(f"   Email: {email}")
                print(f"   Телефоны: {phones}")
                print(f"   Количество телефонов: {phone_count}")
                print(f"   Дата регистрации: {created_at.strftime('%Y-%m-%d %H:%M')}")

            print("\n" + "=" * 70)
            print(f"📊 ИТОГО: {total_clients} клиент(ов), {total_phones} телефон(ов)")
            print("=" * 70)

    except Exception as e:
        print(f"❌ Ошибка при получении клиентов: {e}")

def interactive_mode():
    """
    Интерактивный режим работы с базой данных
    """
    print("\n" + "=" * 70)
    print("💼 СИСТЕМА УПРАВЛЕНИЯ КЛИЕНТАМИ")
    print("=" * 70)

    # Запрашиваем параметры подключения
    print("\n📝 Введите параметры подключения к PostgreSQL:")
    db_name = input("   Имя базы данных: ").strip()
    user = input("   Имя пользователя: ").strip()
    password = input("   Пароль: ").strip()

    # Создаем базу данных если её нет
    if not create_database(db_name, user, password):
        print("\n❌ Не удалось создать базу данных. Завершение работы.")
        return

    # Подключаемся к базе данных
    conn = connect_to_db(db_name, user, password)
    if not conn:
        print("❌ Не удалось подключиться к базе данных. Завершение работы.")
        return

    # Создаем таблицы
    create_db(conn)

    print(f"\n✅ Подключение к базе данных '{db_name}' успешно!")

    # Главное меню
    while True:
        print("\n" + "=" * 70)
        print("🏠 ГЛАВНОЕ МЕНЮ")
        print("=" * 70)
        print("1. 📋 Показать всех клиентов")
        print("2. ➕ Добавить нового клиента")
        print("3. 📞 Добавить телефон клиенту")
        print("4. ✏️  Изменить данные клиента")
        print("5. 🗑️  Удалить телефон клиента")
        print("6. ❌ Удалить клиента")
        print("7. 🔍 Найти клиента")
        print("8. 🎬 Демонстрация всех функций")
        print("0. 🚪 Выход")
        print("=" * 70)

        choice = input("   Выберите действие: ").strip()

        if choice == "0":
            print("\n👋 Выход из программы")
            break

        elif choice == "1":
            display_all_clients(conn)

        elif choice == "2":
            print("\n➕ ДОБАВЛЕНИЕ НОВОГО КЛИЕНТА")

            first_name = input("   Имя: ").strip()
            last_name = input("   Фамилия: ").strip()
            email = input("   Email: ").strip()

            phones = []
            print("\n   Введите телефоны клиента (по одному, пустая строка для завершения):")
            counter = 1
            while True:
                phone = input(f"   Телефон {counter}: ").strip()
                if not phone:
                    break
                phones.append(phone)
                counter += 1

            if phones:
                add_client(conn, first_name, last_name, email, phones)
            else:
                add_client(conn, first_name, last_name, email)

        elif choice == "3":
            print("\n📞 ДОБАВЛЕНИЕ ТЕЛЕФОНА КЛИЕНТУ")
            display_all_clients(conn)

            try:
                client_id = int(input("\n   ID клиента: ").strip())
                phone = input("   Номер телефона: ").strip()
                add_phone(conn, client_id, phone)
            except ValueError:
                print("   ❌ Ошибка: введите числовой ID клиента")

        elif choice == "4":
            print("\n✏️  ИЗМЕНЕНИЕ ДАННЫХ КЛИЕНТА")
            display_all_clients(conn)

            try:
                client_id = int(input("\n   ID клиента: ").strip())

                print("   Введите новые данные (оставьте пустым, если не нужно изменять):")
                first_name = input("   Новое имя: ").strip() or None
                last_name = input("   Новая фамилия: ").strip() or None
                email = input("   Новый email: ").strip() or None

                # Для изменения телефонов
                change_phones = input("   Изменить телефоны? (y/n): ").strip().lower()
                phones = None
                if change_phones == 'y':
                    phones = []
                    print("   Введите новые телефоны (по одному, пустая строка для завершения):")
                    while True:
                        phone = input(f"   Телефон {len(phones) + 1}: ").strip()
                        if not phone:
                            break
                        phones.append(phone)

                change_client(conn, client_id, first_name, last_name, email, phones)
            except ValueError:
                print("   ❌ Ошибка: введите числовой ID клиента")

        elif choice == "5":
            print("\n🗑️  УДАЛЕНИЕ ТЕЛЕФОНА КЛИЕНТА")
            display_all_clients(conn)

            try:
                client_id = int(input("\n   ID клиента: ").strip())
                phone = input("   Номер телефона для удаления: ").strip()
                delete_phone(conn, client_id, phone)
            except ValueError:
                print("   ❌ Ошибка: введите числовой ID клиента")

        elif choice == "6":
            print("\n❌ УДАЛЕНИЕ КЛИЕНТА")
            display_all_clients(conn)

            try:
                client_id = int(input("\n   ID клиента для удаления: ").strip())

                confirm = input(f"   Вы уверены, что хотите удалить клиента ID {client_id}? (y/n): ").strip().lower()
                if confirm == 'y':
                    delete_client(conn, client_id)
                else:
                    print("   Удаление отменено")
            except ValueError:
                print("   ❌ Ошибка: введите числовой ID клиента")

        elif choice == "7":
            print("\n🔍 ПОИСК КЛИЕНТА")
            print("   Введите данные для поиска (оставьте пустым, если не нужно искать по этому полю):")
            first_name = input("   Имя: ").strip() or None
            last_name = input("   Фамилия: ").strip() or None
            email = input("   Email: ").strip() or None
            phone = input("   Телефон: ").strip() or None

            find_client(conn, first_name, last_name, email, phone)

        elif choice == "8":
            # Закрываем текущее соединение перед запуском демо
            conn.close()
            demo_functions()
            # После демо нужно снова подключиться
            conn = connect_to_db(db_name, user, password)
            if not conn:
                print("❌ Не удалось восстановить подключение после демо")
                break

        else:
            print("   ❌ Неверный выбор. Попробуйте снова.")

    # Закрываем соединение
    conn.close()
    print("\n🔌 Соединение с базой данных закрыто")


def main():
    """
    Основная функция программы
    """
    print("=" * 70)
    print("💻 СИСТЕМА УПРАВЛЕНИЯ КЛИЕНТАМИ НА POSTGRESQL")
    print("=" * 70)
    print("📚 Использует только библиотеку psycopg2")
    print("=" * 70)

    # Запускаем интерактивный режим
    interactive_mode()


if __name__ == "__main__":
    main()