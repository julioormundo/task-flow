import hashlib
from datetime import datetime
from typing import Optional

from data.translations import t

class AuthManager:
    """Gerencia autenticação, cadastro, criptografia de senha e sessões."""

    def __init__(self, storage):
        self.storage = storage

    def _hash_password(self, password: str) -> str:
        """Gera um hash SHA-256 seguro da senha."""
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register(self, username: str, password: str) -> dict:
        """Cadastra um novo usuário no sistema."""
        username = username.strip()
        password = password.strip()
        normalized_username = username.lower()

        if not username or not password:
            raise ValueError(t("auth_required_fields"))

        if len(username) < 3:
            raise ValueError(t("auth_username_min_length"))

        if len(password) < 4:
            raise ValueError(t("auth_password_min_length"))

        if self.storage.get_user_by_username(normalized_username):
            raise ValueError(t("auth_username_taken"))

        pwd_hash = self._hash_password(password)
        created_at = datetime.now().strftime("%d/%m/%Y %H:%M")
        user_id = self.storage.create_user(username, pwd_hash, created_at)

        # Inicia a sessão automaticamente
        self.storage.set_active_session(user_id)
        return self.storage.get_user_by_id(user_id)

    def login(self, username: str, password: str) -> dict:
        """Autentica o usuário."""
        username = username.strip()
        password = password.strip()

        if not username or not password:
            raise ValueError(t("auth_required_login"))

        user = self.storage.get_user_by_username(username.lower())
        if not user or user["password_hash"] != self._hash_password(password):
            raise ValueError(t("auth_login_error"))

        self.storage.set_active_session(user["id"])
        return user

    def get_current_user(self) -> Optional[dict]:
        """Verifica se existe um usuário lembrado na sessão."""
        user_id = self.storage.get_active_session_user_id()
        if user_id:
            return self.storage.get_user_by_id(user_id)
        return None

    def logout(self):
        """Encerra a sessão ativa do usuário."""
        self.storage.clear_active_session()