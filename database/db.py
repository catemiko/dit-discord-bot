import copy
import logging
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError

from database.model import Base, Guild, Role, User

logger = logging.getLogger(__name__)

class DatabaseClient():
    def __init__(self, url: str, echo: bool = False) -> None:
        logger.debug("Created database client")
        self.engine = create_engine(url, echo=echo)
        self.Session = sessionmaker(bind=self.engine)
    
    # Init database
    def init_db(self) -> None:
        logger.debug("Initialized database")
        Base.metadata.create_all(self.engine)

    # Create role
    def create_role(self, guild: Guild, name: str) -> Role:
        role = Role(name=name, guild_id=guild.id)
        logger.info(f"Prepare to create role '{role}' in guild {guild}")
        with self.Session() as session:
            try:
                session.add(role)
                session.commit()
                session.refresh(role)
                logger.info(f"Created role '{role}' in guild {guild}")
            except IntegrityError:
                role = self.get_role(guild, name)
                logger.info(f"Role '{role}' already exists in guild {guild}")
            return role

    # Update role
    def update_role(self, guild: Guild, role: Role, name: str) -> Role:
        logger.info(f"Prepare to update role '{role}' in guild {guild}")
        with self.Session() as session:
            try:
                role.name = name
                session.add(role)
                session.commit()
                session.refresh(role)
                logger.info(f"Updated role '{role}' in guild {guild}")
            except IntegrityError:
                role = self.get_role(guild, name=name)       
                logger.info(f"No updates for role '{role}' in guild {guild}")
            return role

    # Delete role
    def delete_role(self, role: Role) -> None:
        with self.Session() as session:
            session.delete(role)
            session.commit()
            logger.info(f"Deleted role '{role}'")

    # Assign role to user
    def assign_role(self, user: User, role: Role) -> User:
        logger.info(f"Prepare to assign role '{role}' to user '{user}'")
        with self.Session() as session:
            session.add(user)
            if role not in user.roles:
                user.roles.append(role)
            session.commit()
            session.refresh(user)
            logger.info(f"Assigned role '{role}' to user '{user}'")
            return user
        
    # Unassign role from user
    def unassign_role(self, user: User, role: Role) -> User:
        logger.info(f"Prepare to unassign role '{role}' from user '{user}'")
        with self.Session() as session:
            session.add(user)
            if role in user.roles:
                user.roles.remove(role)
            session.commit()
            session.refresh(user)
            logger.info(f"Unassigned role '{role}' from user '{user}'")
            return user

    # Get role
    def get_role(self, guild: Guild, name: str) -> Role:
        logger.info(f"Prepare to get role by name '{name}' in guild '{guild}'")
        with self.Session() as session:
            role = session.query(Role).filter_by(guild_id=guild.id, name=name).first()
            logger.info(f"Got role '{role}' in guild '{guild}'")
            return role

    # List all roles
    def list_all_roles(self, guild: Guild) -> List[Role]:
        logger.info(f"Prepare to list all roles in guild '{guild}'")
        with self.Session() as session:
            roles = session.query(Role).all()
            logger.info(f"Listed all roles in guild '{guild}'")
            return roles

    # Create user
    def create_user(self, id: int) -> User:
        user = User(id=id)
        logger.info(f"Prepare to create user '{user}'")
        with self.Session() as session:
            try:
                session.add(user)
                session.commit()
                session.refresh(user)
                logger.info(f"Created user '{user}'")
            except IntegrityError:
                user = self.get_user(id)
                logger.info(f"User '{user}' already exists")
            return user

    # Get user
    def get_user(self, id: int) -> User:
        logger.info(f"Prepare to get user by ID '{id}'")
        with self.Session() as session:
            user = session.query(User).filter_by(id=id).first()
            logger.info(f"Got user '{user}'")
            return user

    # List roles for user
    def list_user_roles(self, guild: Guild, user: User) -> List[Role]:
        logger.info(f"Prepare to list all roles for '{user}' in '{guild}'")
        with self.Session() as session:
            roles = session.query(Role).filter_by(guild_id=guild.id).join(Role.users).filter_by(id=user.id).all()
            logger.info(f"Listed all roles for '{user}' in '{guild}'")
            return roles

    # Create guild
    def create_guild(self, id: int) -> Guild:    
        guild = Guild(id=id)
        logger.info(f"Prepare to create guild '{guild}'")
        with self.Session() as session:
            try:
                session.add(guild)
                session.commit()
                session.refresh(guild)
                logger.info(f"Created guild '{guild}'")
            except IntegrityError:
                guild = self.get_guild(id)
                logger.info(f"Guild '{guild}' already exists")
            return guild
        
    # Get guild
    def get_guild(self, id: int) -> Guild:
        logger.info(f"Prepare to get guild by ID '{id}'")
        with self.Session() as session:
            guild = session.query(Guild).filter_by(id=id).first()
            logger.info(f"Got guild '{guild}'")
            return guild