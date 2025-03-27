from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String, unique=True, nullable=False)
    coins = Column(Integer, default=0)
    level = Column(Integer, default=1)
    ref_link = Column(String, unique=True)
    invited_friends = Column(Integer, default=0)
    friends_usernames = Column(String)  # Хранение ников друзей через запятую
    profit_per_hour = Column(Integer, default=0)
    profit_per_tap = Column(Integer, default=1)
    level_token = Column(Integer, default=0)
    level_staking = Column(Integer, default=0)
    level_genesis = Column(Integer, default=0)
    level_ledger = Column(Integer, default=0)
    level_echeleon = Column(Integer, default=0)
    level_quantum = Column(Integer, default=0)
    level_multitap = Column(Integer, default=1)

    def update_profit(self):
        from db_utils import CARD_DATA  # Импортируем CARD_DATA из db_utils

        # Обнуляем profit_per_hour перед пересчетом
        self.profit_per_hour = 0

        # Добавляем прибыль за все купленные уровни каждой карточки
        if self.level_token > 0:
            self.profit_per_hour += sum([CARD_DATA['token'][i]['profit'] for i in range(self.level_token)])
        if self.level_staking > 0:
            self.profit_per_hour += sum([CARD_DATA['staking'][i]['profit'] for i in range(self.level_staking)])
        if self.level_genesis > 0:
            self.profit_per_hour += sum([CARD_DATA['genesis'][i]['profit'] for i in range(self.level_genesis)])
        if self.level_echeleon > 0:
            self.profit_per_hour += sum([CARD_DATA['echeleon'][i]['profit'] for i in range(self.level_echeleon)])
        if self.level_ledger > 0:
            self.profit_per_hour += sum([CARD_DATA['ledger'][i]['profit'] for i in range(self.level_ledger)])
        if self.level_quantum > 0:
            self.profit_per_hour += sum([CARD_DATA['quantum'][i]['profit'] for i in range(self.level_quantum)])

        # Пересчитываем profit_per_tap
        self.profit_per_tap = CARD_DATA['multitap'][self.level_multitap - 1]['profit'] if self.level_multitap > 0 else 0

    def __repr__(self):
        return (f"<User(user_id={self.user_id}, username='{self.username}', coins={self.coins}, "
                f"level={self.level}, profit_per_hour={self.profit_per_hour}, "
                f"profit_per_tap={self.profit_per_tap})>")

# Настройка базы данных
DATABASE_URL = 'sqlite:///users.db'
engine = create_engine(DATABASE_URL, echo=True)  # Добавлен echo=True для логирования SQL-запросов
Base.metadata.create_all(engine)

# Создание сессии
Session = sessionmaker(bind=engine)
session = Session()

# Вспомогательная функция для отладки
if __name__ == "__main__":
    # Проверка базы данных
    print("Существующие пользователи:")
    users = session.query(User).all()
    for user in users:
        print(user)