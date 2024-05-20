from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class Accounts(Base):
    __tablename__ = 'accounts'

    id                 : Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    address            : Mapped[str]
    private_key        : Mapped[str]

    twitter_token      : Mapped[str]
    discord_token      : Mapped[str]
    proxy              : Mapped[str]

    device_id          : Mapped[str]
    refcode            : Mapped[str]

    address_particle   : Mapped[str] = mapped_column(nullable=True)
    invite_code        : Mapped[str] = mapped_column(nullable=True)
    referrer_address   : Mapped[str] = mapped_column(nullable=True)

    check_in           : Mapped[bool] = mapped_column(default=False)
    today_tx           : Mapped[int] = mapped_column(default=0)
    total_tx           : Mapped[int] = mapped_column(default=0)
    
    referral_points    : Mapped[int] = mapped_column(nullable=True)
    checkin_points     : Mapped[int] = mapped_column(nullable=True)
    deposit_points     : Mapped[int] = mapped_column(nullable=True)
    transactions_points    : Mapped[int] = mapped_column(nullable=True)
    total_points       : Mapped[int] = mapped_column(nullable=True)

    ethereum_main      : Mapped[float] = mapped_column(nullable=True)
    arbitrum_main      : Mapped[float] = mapped_column(nullable=True)
    optimism_main      : Mapped[float] = mapped_column(nullable=True)
    base_main          : Mapped[float] = mapped_column(nullable=True)
    linea_main         : Mapped[float] = mapped_column(nullable=True)
    blast_main         : Mapped[float] = mapped_column(nullable=True)
    polygon_main       : Mapped[float] = mapped_column(nullable=True)
    bnb_main           : Mapped[float] = mapped_column(nullable=True)
    avalanche_main     : Mapped[float] = mapped_column(nullable=True)
    b2network_main     : Mapped[float] = mapped_column(nullable=True)

    ethereum_particle  : Mapped[float] = mapped_column(nullable=True)
    arbitrum_particle  : Mapped[float] = mapped_column(nullable=True)
    optimism_particle  : Mapped[float] = mapped_column(nullable=True)
    base_particle      : Mapped[float] = mapped_column(nullable=True)
    linea_particle     : Mapped[float] = mapped_column(nullable=True)
    blast_particle    : Mapped[float] = mapped_column(nullable=True)
    polygon_particle   : Mapped[float] = mapped_column(nullable=True)
    bnb_particle       : Mapped[float] = mapped_column(nullable=True)
    avalanche_particle : Mapped[float] = mapped_column(nullable=True)
    b2network_particle : Mapped[float] = mapped_column(nullable=True)

