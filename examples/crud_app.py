from pydataui import App, State
from pydataui.components import Container, Heading, Table, Button, Flex, Modal, Input, Card, Alert
from pydantic import BaseModel
import uuid

class User(BaseModel):
    id: str
    name: str
    email: str

class CRUDState(State):
    users: list[User] = [
        User(id="1", name="Admin", email="admin@example.com")
    ]
    show_modal: bool = False
    current_name: str = ""
    current_email: str = ""
    editing_id: str = ""
    message: str = ""
    
    def open_create(self):
        self.current_name = ""
        self.current_email = ""
        self.editing_id = ""
        self.show_modal = True
        
    def open_edit(self, user_id: str):
        user = next((u for u in self.users if u.id == user_id), None)
        if user:
            self.current_name = user.name
            self.current_email = user.email
            self.editing_id = user.id
            self.show_modal = True
            
    def close_modal(self):
        self.show_modal = False
        
    def save_user(self):
        if self.editing_id:
            for u in self.users:
                if u.id == self.editing_id:
                    u.name = self.current_name
                    u.email = self.current_email
            self.message = "User updated successfully."
        else:
            self.users.append(User(id=uuid.uuid4().hex, name=self.current_name, email=self.current_email))
            self.message = "User created successfully."
        self.show_modal = False
        
    def delete_user(self, user_id: str):
        self.users = [u for u in self.users if u.id != user_id]
        self.message = "User deleted successfully."

app = App(title='CRUD App')

@app.page('/')
def home():
    alert = Alert(CRUDState.message, variant="success", margin_bottom="md") if CRUDState.message else None
    
    # Action buttons for table
    table_data = []
    for user in CRUDState.users:
        edit_btn = Button("Edit", size="sm", on_click=lambda id=user.id: CRUDState.open_edit(id))
        del_btn = Button("Delete", size="sm", variant="danger", on_click=lambda id=user.id: CRUDState.delete_user(id))
        actions = Flex(edit_btn, del_btn, gap="sm")
        table_data.append([user.id, user.name, user.email, actions])

    modal = None
    if CRUDState.show_modal:
        title = "Edit User" if CRUDState.editing_id else "Create User"
        modal = Modal(
            title=title,
            is_open=True,
            on_close=CRUDState.close_modal,
            children=[
                Flex(
                    Input("Name", bind=CRUDState.current_name, full_width=True),
                    Input("Email", bind=CRUDState.current_email, full_width=True),
                    direction="column",
                    gap="md"
                ),
                Flex(
                    Button("Cancel", variant="outline", on_click=CRUDState.close_modal),
                    Button("Save", variant="primary", on_click=CRUDState.save_user),
                    justify="flex-end",
                    gap="sm",
                    margin_top="lg"
                )
            ]
        )

    return Container(
        Heading("User Management", level=1),
        alert,
        Card(
            children=[
                Flex(
                    Heading("Users", level=2),
                    Button("Add User", variant="primary", on_click=CRUDState.open_create),
                    justify="space-between",
                    align="center",
                    margin_bottom="md"
                ),
                Table(
                    columns=["ID", "Name", "Email", "Actions"],
                    data=table_data
                )
            ]
        ),
        modal
    )

if __name__ == '__main__':
    app.run()
