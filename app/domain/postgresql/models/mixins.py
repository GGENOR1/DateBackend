from datetime import datetime
from sqlalchemy import ForeignKey, Integer, func
from sqlalchemy.orm import Mapped, mapped_column

class CreatedAtOnlyMixin:
    registered_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        server_default=func.now(),
        comment="Дата создания записи",
    )


# class UpdatedAtMixin(CreatedAtOnlyMixin):
#     updated_at: Mapped[datetime] = mapped_column(
#         default=func.now(),
#         server_default=func.now(),
#         onupdate=func.now(),
#         server_onupdate=func.now(),
#         comment="Дата обновления записи",
#     )

    @property
    def created_date(self) -> datetime:
        return self.registered_at.replace(microsecond=0, tzinfo=None)

    # @property
    # def updated_date(self) -> datetime:
    #     return self.updated_at.replace(microsecond=0, tzinfo=None)


class UUIDOidMixin:
    pass
#     oid: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4)
# oid: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4)
class IdMixin:
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
class CreatedRoleMixin:
    role_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False, default=1
    )