from sqlmodel import SQLModel, Session, select

from app.database import UserBase, UserPermission, UserLogin, create_user, engine


def get_username() -> str:
    with Session(engine) as session:
        while True:
            username = input("Unique username: ")

            existing_user = session.exec(
                select(UserBase).where(UserBase.username == username)
            ).one_or_none()
            if existing_user is None:
                break

            print("Error: Username already exist!")
    return username


def create_admin_user() -> None:
    print("Press Ctrl+c for cancelling.")
    SQLModel.metadata.create_all(engine)

    username = get_username()
    password = input("Secure password: ")

    user_login = UserLogin(username=username, password=password)
    create_user(
        user_login=user_login, permission=UserPermission.admin,
    )


if __name__ == "__main__":
    create_admin_user()