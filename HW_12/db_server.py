# from sqlalchemy import create_engine, Table, Column, Integer, String, MetaData, ForeignKey, DateTime
# from sqlalchemy.orm import declarative_base, sessionmaker, Session
# from sqlalchemy.sql import func
#
# Base = declarative_base()
# engine = create_engine('sqlite:///server_base.db3', echo=True, pool_recycle=7200, pool_pre_ping=True)
#
#
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     name = Column(String, unique=True, nullable=False)
#     info = Column(String)
#
#     def __init__(self, name, info):
#         self.name = name
#         self.info = info
#
#     def __repr__(self):
#         return "<User('%s', '%s')>" % (self.name, self.info)
#
#
# class UserHistory(Base):
#     __tablename__ = 'user_history'
#     id = Column(Integer, primary_key=True)
#     id_user = Column(Integer, ForeignKey('users.id'))
#     time_connect = Column(DateTime(timezone=True), server_default=func.now())
#     ip_addr = Column(String)
#
#     def __init__(self, id_user, time_connect, ip_addr):
#         self.id_user = id_user
#         self.time_connect = time_connect
#         self.ip_addr = ip_addr
#
#     def __repr__(self):
#         return "<UserHistory('%s', '%s')>" % (self.time_connect, self.ip_addr)
#
#
# class ContactList(Base):
#     __tablename__ = 'contact_list'
#     id = Column(Integer, primary_key=True)
#     id_user = Column(Integer, ForeignKey('users.id'))
#     id_client = Column(Integer, ForeignKey('users.id'))
#
#     def __init__(self, id_user, id_client):
#         self.id_user = id_user
#         self.id_client = id_client
#
#     def __repr__(self):
#         return "<ContactList('%s', '%s')>" % (self.id_user, self.id_client)
#
#
# class ServerStorage:
#
#     def __init__(self):
#         session = sessionmaker(bind=engine)
#         self.sess: Session = session()
#         Base.metadata.create_all(engine)
#
#     def add_user(self, name: str, info: str = None):
#         if self.sess.query(User).filter_by(name=name).first():
#             return
#         user_row = User(name=name, info=info)
#         self.sess.add(user_row)
#         self.sess.commit()
#
#     def get_contacts(self, user_login):
#         user = self.sess.query(User).filter_by(name=user_login).one()
#         print(f'Ready {user.id}')
#         query = self.sess.query(ContactList, User).filter_by(id_user=user.id).join(User,
#                                                                                    ContactList.id_user == User.id)
#         return [contact[1].name for contact in query.all()]
#
#     def add_contact(self, user, contact):
#         user = self.sess.query(User).filter_by(name=user).first()
#         contact = self.sess.query(User).filter_by(name=contact).first()
#         if not user or not contact or self.sess.query(ContactList).filter_by(id_user=user.id,
#                                                                              id_client=contact.id).count():
#             return
#         contact_string = ContactList(id_user=user.id, id_client=contact.id)
#         self.sess.add(contact_string)
#         self.sess.commit()
#
#     def del_contact(self, user, contact):
#         user = self.sess.query(User).filter_by(name=user).first()
#         contact = self.sess.query(User).filter_by(name=contact).first()
#         if not user or not contact:
#             return
#         self.sess.query(ContactList).filter(ContactList.id_user == user.id,
#                                             ContactList.id_client == contact.id).delete()
#         self.sess.commit()
#
#     def users_list(self):
#         query = self.sess.query(User.name)
#         return query.all()
#
#
# if __name__ == '__main__':
#     storage = ServerStorage()
#     storage.add_user('nick_1', 'info_1')
#     storage.add_user('nick_2', 'info_2')
#     storage.add_user('nick_3', 'info_3')
#     storage.add_user('nick_4', 'info_4')
#     print('test_1', list(storage.users_list()))
#     storage.add_contact('nick_1', 'nick_2')
#     storage.add_contact('nick_2', 'nick_1')
#     print('test_2', storage.get_contacts('nick_1'))
#     storage.del_contact('nick_2', 'nick_1')
#     print('test_3', storage.get_contacts('nick_1'))
#     print('finally', list(storage.users_list()))


from datetime import datetime
from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

engine = create_engine('sqlite:///server_base.db3', echo=True, pool_recycle=7200, pool_pre_ping=True)

Base = declarative_base()


class Client(Base):
    __tablename__ = 'clients'

    id = Column(Integer(), primary_key=True)
    login = Column(String(50), unique=True)
    information = Column(String(254))

    def __init__(self, login, information=None):
        self.login = login
        self.information = information


class ClientHistory(Base):
    __tablename__ = 'client_history'

    id = Column(Integer(), primary_key=True)
    id_client = Column(Integer(), ForeignKey('clients.id'))
    time_login = Column(DateTime(), default=datetime.now)
    ip_address = Column(String(50))

    def __init__(self, id_client, ip_address, time_login=None) -> None:
        self.id_client = id_client
        self.time_login = time_login or datetime.now()
        self.ip_address = ip_address


class ContactList(Base):
    __tablename__ = 'contact_list'

    id = Column(Integer(), primary_key=True)
    id_owner = Column(Integer(), ForeignKey('clients.id'))
    id_client = Column(Integer(), ForeignKey('clients.id'))

    def __init__(self, id_owner, id_client) -> None:
        self.id_owner = id_owner
        self.id_client = id_client


class ServerDataBase:

    def __init__(self):
        session = sessionmaker(bind=engine)
        self.sess: Session = session()
        Base.metadata.create_all(engine)

    def add_user(self, login: str, information: str = None):
        if self.sess.query(Client).filter_by(login=login).first():
            return
        user_row = Client(login=login, information=information)
        self.sess.add(user_row)
        self.sess.commit()

    def get_contacts(self, client_login):
        user = self.sess.query(Client).filter_by(login=client_login).one()
        print(f'HERE WE ARE {user.id}')
        query = self.sess.query(ContactList, Client).filter_by(id_owner=user.id).join(Client,
                                                                                      ContactList.id_client == Client.id)
        return [contact[1].login for contact in query.all()]

    def add_contact(self, client, contact):
        user = self.sess.query(Client).filter_by(login=client).first()
        contact = self.sess.query(Client).filter_by(login=contact).first()
        if not user or not contact or self.sess.query(ContactList).filter_by(id_owner=user.id,
                                                                             id_client=contact.id).count():
            return
        contact_string = ContactList(id_owner=user.id, id_client=contact.id)
        self.sess.add(contact_string)
        self.sess.commit()

    def del_contact(self, client, contact):
        user = self.sess.query(Client).filter_by(login=client).first()
        contact = self.sess.query(Client).filter_by(login=contact).first()
        if not user or not contact:
            return
        self.sess.query(ContactList).filter(ContactList.id_owner == user.id,
                                            ContactList.id_client == contact.id).delete()
        self.sess.commit()

    def users_list(self):
        query = self.sess.query(Client.login)
        return query.all()


if __name__ == '__main__':
    storage = ServerDataBase()
    storage.add_user('nick_1', 'info_1')
    storage.add_user('nick_2', 'info_2')
    storage.add_user('nick_3', 'info_3')
    print('test_1', list(storage.users_list()))
    storage.add_contact('nick_1', 'nick_2')
    storage.add_contact('nick_1', 'nick_3')
    print('test_2', storage.get_contacts('nick_1'))
    storage.del_contact('nick_1', 'nick_2')
    print('test_3', storage.get_contacts('nick_1'))
    print('finally_test', list(storage.users_list()))


