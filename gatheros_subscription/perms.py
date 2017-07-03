from permission import add_permission_logic

from gatheros_event.perms import MemberPermissionLogic, member_is_member
from .models import Field, Form, Lot

# Lógicas de permissões
# Organization -> Member -> Lot
logic = MemberPermissionLogic(
    member_is_member,
    ['change_lot', 'delete_lot'],
    'event__organization'
)
add_permission_logic(Lot, logic)

# Organization -> Member -> Form
logic = MemberPermissionLogic(
    member_is_member,
    ['can_add_field', 'change_form'],
    'event__organization'
)
add_permission_logic(Form, logic)

# Organization -> Member -> Field
logic = MemberPermissionLogic(
    member_is_member,
    ['change_field', 'delete_field'],
    'organization'
)
add_permission_logic(Field, logic)
