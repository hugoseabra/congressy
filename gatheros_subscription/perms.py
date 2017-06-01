from permission import add_permission_logic

from gatheros_event.perms import MemberPermissionLogic, member_is_member
from .models import Lot

# Lógicas de permissões
# Lot -> Event -> Organization -> Admin
logic = MemberPermissionLogic(
    member_is_member,
    ['change_lot', 'delete_lot'],
    'event__organization'
)
add_permission_logic(Lot, logic)
