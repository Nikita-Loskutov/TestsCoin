from sqlalchemy import create_engine, Table, Column, Integer, MetaData, update
from sqlalchemy.exc import SQLAlchemyError


def update_coins(database_url, user_id, new_coins):
    # Создание подключения к базе данных
    engine = create_engine(database_url, echo=True)  # echo=True для логов SQL-запросов
    metadata = MetaData()

    try:
        # Отражение структуры таблицы из базы данных
        metadata.reflect(bind=engine)
        users = metadata.tables['users']  # Динамическая загрузка таблицы

        # Подключение и выполнение обновления
        with engine.connect() as connection:
            stmt = (
                update(users)
                .where(users.c.user_id == user_id)
                .values(coins=new_coins)
            )
            result = connection.execute(stmt)
            connection.commit()  # Фиксация транзакции для SQLite

            # Проверка количества обновленных строк
            if result.rowcount > 0:
                print(f"Successfully updated coins for user {user_id} to {new_coins}.")
            else:
                print(f"No user found with id {user_id}.")

    except SQLAlchemyError as e:
        print(f"An error occurred: {e}")


# Пример вызова функции
update_coins("sqlite:///users.db", 1420231559, 100000000000)
