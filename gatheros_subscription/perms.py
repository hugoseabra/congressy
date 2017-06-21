from permission import add_permission_logic

from gatheros_event.perms import MemberPermissionLogic, member_is_member
from .models import Field, Form, Lot

# Lógicas de permissões
# Lot -> Event -> Organization -> Member
logic = MemberPermissionLogic(
    member_is_member,
    ['change_lot', 'delete_lot'],
    'event__organization'
)
add_permission_logic(Lot, logic)

# Field -> Event -> Organization -> Member
logic = MemberPermissionLogic(
    member_is_member,
    ['can_add_field', 'change_form'],
    'event__organization'
)
add_permission_logic(Form, logic)

# Field -> Event -> Organization -> Member
logic = MemberPermissionLogic(
    member_is_member,
    ['change_field', 'delete_field'],
    'form__event__organization'
)
add_permission_logic(Field, logic)
