from pydantic import BaseModel, field_validator, model_validator, Field
from enum import Enum
import os


migration_path = os.path.abspath(os.path.join(__file__, "..", "..", "..", "migration"))
NAME_CONFIG = "config.yaml"

class DbType(str, Enum):
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    SQLITE = "sqlite"

class BaseDatabaseConfig(BaseModel):
    """Базовая конфигурация для всех баз данных"""
    db_type: DbType = Field(
        ..., description="Тип СУБД: mysql, postgresql или sqlite"
    )
    database: str = Field(
        default="", description="Имя базы данных или путь к файлу (для SQLite)"
    )
    host: str = "localhost"
    port: int = Field(default=5432, ge=1, le=65535, description="Порт подключения")
    username: str = Field(default="", description="Имя пользователя")
    password: str = Field(default="", description="Пароль") # Changed from password to db_password
    db_min_size_users: int = 1 # Changed from db_min_size_users to db_min_size
    db_max_size_users: int = 10
    max_queries: int = 50000
    max_inactive_connection_lifetime: int = 60
    timeout: int = 30
    @field_validator("port")
    def validate_port(cls, v: int, info):
        db_type = info.data.get("db_type")
        if db_type == DbType.MYSQL and v != 3306:
            print("Предупреждение: стандартный порт для MySQL - 3306")
        elif db_type == DbType.POSTGRESQL and v != 5432:
            print("Предупреждение: стандартный порт для PostgreSQL - 5432")
        return v

    @model_validator(mode="after")
    def validate_sqlite(self):
        if self.db_type == DbType.SQLITE:
            self.host = "localhost"
            self.port = 0
            self.db_min_size_users = 0
            self.db_max_size_users = 0
            # Для SQLite database - это путь к файлу
            if self.database and not self.database.endswith(".db"):
                self.database = rf"{migration_path}\{self.database}.db"
        return self


class UsersDatabaseConfig(BaseDatabaseConfig):
    """Конфигурация для базы данных пользователей"""
    db_type: DbType = DbType.SQLITE
    database: str = Field(default="users.db", description="Имя базы данных или путь к файлу (для SQLite)")

class DataDatabaseConfig(BaseDatabaseConfig):
    """Конфигурация для базы данных приложения"""
    db_type: DbType = DbType.SQLITE
    database: str = Field(default="data.db", description="Имя базы данных или путь к файлу (для SQLite)")


def create_config_file(migration_path, NAME_CONFIG):


    class AppConfig(BaseModel):
        """Общая конфигурация приложения"""

        debug: bool = True
        host: str | int = "localhost"
        port: int = 8000
        reload: bool = True
        allowed_hosts: list[str] = ["localhost"]

    class Config(BaseModel):
        users_db: UsersDatabaseConfig
        data_db: DataDatabaseConfig
        app: AppConfig
        features: dict[str, bool] | None = None

    config = Config(
        users_db=UsersDatabaseConfig(
            db_type=DbType.SQLITE, database=os.path.join(migration_path, "users.db")
        ),
        data_db=DataDatabaseConfig(
            db_type=DbType.SQLITE, database=os.path.join(migration_path, "data.db")
        ),
        app=AppConfig(
            debug=True,
            host="0.0.0.0",
            port=8000,
            reload=True,
        ),
    )

    config_dict = config.model_dump()

    yaml_content = """\
#|=============================|
#|    by ShipovnikAAA(iba)     |
#|=============================|


# Server settings your wiki application
app-setings:
    host: {host}
    port: {port}
    reload: {reload}
    debug: {debug}


# This conficuration block is responsible for data storage.
databases:
  # How should the application storage data
  # possible option : MYSQL, SQLITE, POSTGRESQL, ~soon: MARIADB
  type:
    users: {users_db_type}
    data: {data_db_type}
  # if you use databse such as: MYSQL, POSTGRESQL, ~soon: MARIADB, you must configurate this fields
  settings:
    users:
      database: '' # If you use SQLITE, you can type there path to db file
      host: ''
      port: ''
      username: ''
      password: ''
      db-min-size: ''
      db-max-size: ''
      max-queries: ''
      max-inactive-connection-lifetime: ''
      timeout:
    data:
      database: '' # If you use SQLITE, you can type there path to db file
      host: ''
      port: ''
      username: ''
      password: ''
      db-min-size: ''
      db-max-size: ''
      max-queries: ''
      max-inactive-connection-lifetime: ''
      timeout: ''""".format(
        host=config_dict["app"]["host"],
        port=config_dict["app"]["port"],
        reload=config_dict["app"]["reload"],
        debug=config_dict["app"]["debug"], # Changed from debug to debug
        users_db_type=config_dict["users_db"]["db_type"].value, # Changed from users_db_type to users_db_type
        data_db_type=config_dict["data_db"]["db_type"].value,
    )

    if os.path.exists(os.path.join(migration_path, NAME_CONFIG)):
        with open(os.path.join(migration_path, NAME_CONFIG), "w", encoding="utf-8") as f:
            f.write(yaml_content)


def read_config_file(migration_path, NAME_CONFIG):
    import yaml
    if not os.path.exists(os.path.join(migration_path, NAME_CONFIG)):
        create_config_file(migration_path, NAME_CONFIG)
    with open(os.path.join(migration_path, NAME_CONFIG), 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    return config

create_config_file(migration_path, NAME_CONFIG)


# raw_config = read_config_file(migration_path, NAME_CONFIG)

# class Config(BaseModel):
#     class AppSettings(BaseModel):
#         host: str
#         port: int
#         reload: bool
#         debug: bool

#     class DatabaseSettings(BaseModel):
#         class DbTypeConfig(BaseModel):
#             users: DbType
#             data: DbType

#         type: DbTypeConfig
#         settings: dict[str, BaseDatabaseConfig]

#         @model_validator(mode='after')
#         def validate_db_settings(self):
#             for db_name, db_config_data in self.settings.items():
#                 db_type = self.type.model_dump()[db_name]
#                 # Ensure db_config_data is a dict with string keys
#                 if isinstance(db_config_data, BaseModel):
#                     db_config_data = db_config_data.model_dump()
#                 elif not isinstance(db_config_data, dict):
#                     db_config_data = dict(db_config_data)
#                 db_config_data = {str(k): v for k, v in db_config_data.items()}
#                 self.settings[db_name] = BaseDatabaseConfig(db_type=db_type, **db_config_data)
#             return self

#     app_setings: AppSettings
#     databases: DatabaseSettings

# parsed_config = Config.model_validate(raw_config)

# DATABASE_DATA = parsed_config.databases.settings['data']
# DATABASE_USERS = parsed_config.databases.settings['users']
# APP_CONFIG = parsed_config.app_setings