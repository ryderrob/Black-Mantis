# bot/models.py
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
# For PickleType or JSON, uncomment the one you prefer. JSON is generally better for cross-platform/language compatibility.
# from sqlalchemy.types import PickleType
from sqlalchemy.types import JSON
from .db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # Telegram User ID
    username = Column(String, nullable=True)  # Telegram username

    # Relationship to Character: one-to-many (a user might have characters in different games/servers)
    # Or one-to-one if a user has one character globally. For this RPG, let's assume one character per user for simplicity to start.
    # If multiple characters per user are needed later, this relationship would change.
    character = relationship("Character", back_populates="user", uselist=False, cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Character(Base):
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True) # Link to the Telegram user

    name = Column(String, nullable=False)
    race = Column(String, nullable=False)
    _class = Column("class", String, nullable=False)  # Column name in DB is "class"

    health = Column(Integer, default=100)
    max_health = Column(Integer, default=100)
    mana = Column(Integer, default=50)
    max_mana = Column(Integer, default=50)

    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)

    # inventory = Column(PickleType, nullable=True) # For storing list of items, etc.
    inventory = Column(JSON, nullable=True, default=lambda: []) # Store as JSON list/dict

    location = Column(String, default="Starting Area") # Current location of the character

    user = relationship("User", back_populates="character")
    # game_session_id = Column(Integer, ForeignKey("game_sessions.id"), nullable=True) # If character is tied to a specific session
    # game_session = relationship("GameSession", back_populates="characters")


    def __repr__(self):
        return f"<Character(id={self.id}, name='{self.name}', race='{self.race}', class='{self._class}')>"


class GameSession(Base):
    __tablename__ = "game_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    chat_id = Column(Integer, unique=True, nullable=False)  # Telegram Group Chat ID

    current_scene = Column(Text, nullable=True, default="The adventure begins...")
    is_active = Column(Boolean, default=False)
    gm_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Optional Game Master

    # characters = relationship("Character", back_populates="game_session") # If characters are part of a session

    def __repr__(self):
        return f"<GameSession(id={self.id}, chat_id={self.chat_id}, is_active={self.is_active})>"

# To create tables:
# from .db import engine
# Base.metadata.create_all(bind=engine)
# This should be called once, e.g., in main.py or a setup script.
