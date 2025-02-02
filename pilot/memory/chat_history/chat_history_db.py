from pilot.base_modules.meta_data.base_dao import BaseDao
from pilot.base_modules.meta_data.meta_data import Base, engine, session
from typing import List
from sqlalchemy import Column, Integer, String, Index, DateTime, func, Boolean, Text
from sqlalchemy import UniqueConstraint


class ChatHistoryEntity(Base):
    __tablename__ = "chat_history"
    id = Column(
        Integer, primary_key=True, autoincrement=True, comment="autoincrement id"
    )
    __table_args__ = {
        "mysql_charset": "utf8mb4",
        "mysql_collate": "utf8mb4_unicode_ci",
    }
    conv_uid = Column(
        String(255),
        unique=False,
        nullable=False,
        comment="Conversation record unique id",
    )
    chat_mode = Column(String(255), nullable=False, comment="Conversation scene mode")
    summary = Column(String(255), nullable=False, comment="Conversation record summary")
    user_name = Column(String(255), nullable=True, comment="interlocutor")
    messages = Column(Text, nullable=True, comment="Conversation details")

    UniqueConstraint("conv_uid", name="uk_conversation")
    Index("idx_q_user", "user_name")
    Index("idx_q_mode", "chat_mode")
    Index("idx_q_conv", "summary")


class ChatHistoryDao(BaseDao[ChatHistoryEntity]):
    def __init__(self):
        super().__init__(
            database="dbgpt", orm_base=Base, db_engine=engine, session=session
        )

    def list_last_20(self, user_name: str = None):
        session = self.get_session()
        chat_history = session.query(ChatHistoryEntity)
        if user_name:
            chat_history = chat_history.filter(ChatHistoryEntity.user_name == user_name)

        chat_history = chat_history.order_by(ChatHistoryEntity.id.desc())

        result = chat_history.limit(20).all()
        session.close()
        return result

    def update(self, entity: ChatHistoryEntity):
        session = self.get_session()
        try:
            updated = session.merge(entity)
            session.commit()
            return updated.id
        finally:
            session.close()

    def update_message_by_uid(self, message: str, conv_uid: str):
        session = self.get_session()
        try:
            chat_history = session.query(ChatHistoryEntity)
            chat_history = chat_history.filter(ChatHistoryEntity.conv_uid == conv_uid)
            updated = chat_history.update({ChatHistoryEntity.messages: message})
            session.commit()
            return updated.id
        finally:
            session.close()

    def delete(self, conv_uid: int):
        session = self.get_session()
        if conv_uid is None:
            raise Exception("conv_uid is None")

        chat_history = session.query(ChatHistoryEntity)
        chat_history = chat_history.filter(ChatHistoryEntity.conv_uid == conv_uid)
        chat_history.delete()
        session.commit()
        session.close()

    def get_by_uid(self, conv_uid: str) -> ChatHistoryEntity:
        session = self.get_session()
        chat_history = session.query(ChatHistoryEntity)
        chat_history = chat_history.filter(ChatHistoryEntity.conv_uid == conv_uid)
        result = chat_history.first()
        session.close()
        return result
