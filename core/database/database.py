from sqlalchemy import create_engine, update
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func

from core.database.models import Base, Accounts


class MainDB():
    def __init__(self):
        self.__engine = create_engine('sqlite:///data/database/accounts.db')
        self.__Session = sessionmaker(bind=self.__engine, expire_on_commit=True)
        self.__session = self.__Session()

        Base.metadata.create_all(self.__engine, checkfirst=True)

    def get_accounts(self) -> list[Accounts]:
        accounts = self.__session.query(Accounts).all()
        for account in accounts:
            self.__session.refresh(account)
        return accounts
    
    def get_account_by_key(self, key: str, value: str) -> Accounts | None:
        account = self.__session.query(Accounts).filter(getattr(Accounts, key) == value).one_or_none()
        if account is not None:
            self.__session.refresh(account)
        return account

    def get_accounts_filtered(self, checkin: bool = True, todaytx: bool = True) -> list[Accounts]:
        query = self.__session.query(Accounts)
        
        if checkin and todaytx:
            accounts = query.filter(
                (Accounts.check_in == False) | (Accounts.today_tx != 100)
            ).all()
        elif checkin:
            accounts = query.filter(Accounts.check_in == False).all()
        elif todaytx:
            accounts = query.filter(Accounts.today_tx != 100).all()
        else:
            accounts = []
        return accounts

    def add_account(self, account: Accounts) -> Accounts:
        self.__session.add(account)
        self.__session.commit()
        return account

    def update_account(self, account_id: int, new_values: dict) -> None:
        stmt = update(Accounts).where(Accounts.id == account_id).values(new_values)
        self.__session.execute(stmt)
        self.__session.commit()

    # def count_accounts(self) -> int:
    #     return self.__session.query(func.count(Accounts.id)).scalar()

