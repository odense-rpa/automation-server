import bcrypt

from app.database.repository import ClientCredentialRepository
from app.database.models import ClientCredential

from app.config import settings


class ClientCredentialService:
    def __init__(self, client_credential_repository: ClientCredentialRepository):
        self.repository = client_credential_repository

    def get_by_client_id(self, client_id: str) -> ClientCredential:
        return self.repository.get_by_client_id(client_id)

    def create_client(self, client_id: str, client_secret: str) -> ClientCredential:
        salt = bcrypt.gensalt()
        hash = bcrypt.hashpw(
            client_secret.encode("utf-8"), salt + settings.password_salt.encode("utf-8")
        )

        return self.repository.create(
            {
                "client_id": client_id,
                "client_secret": hash.decode("utf-8"),
                "salt": salt.decode("utf-8"),
            }
        )

    def validate_client(self, client_id: str, client_secret: str) -> bool:
        client = self.repository.get_by_client_id(client_id)

        if client is None:
            return False

        # Salted hash comparison
        hash = bcrypt.hashpw(
            client_secret.encode("utf-8"),
            client.salt.encode("utf-8") + settings.password_salt.encode("utf-8"),
        )

        return hash == client.client_secret.encode("utf-8")
