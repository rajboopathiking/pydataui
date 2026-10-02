from pydataui import App, State
from pydataui.components import Container, Heading, Input, Button, Flex, List, ListItem, Text, Alert, Badge, Card
from pydantic import BaseModel
import uuid

class TodoItem(BaseModel):
    id: str
    text: str
    done: bool = False

class TodoState(State):
    todos: list[TodoItem] = []
    current_input: str = ""
    
    def add_todo(self):
        if self.current_input.strip():
            self.todos.append(TodoItem(id=uuid.uuid4().hex, text=self.current_input))
            self.current_input = ""
            
    def toggle_todo(self, item_id: str):
        for todo in self.todos:
            if todo.id == item_id:
                todo.done = not todo.done
                
    def remove_todo(self, item_id: str):
        self.todos = [t for t in self.todos if t.id != item_id]

app = App(title='Todo App')

@app.page('/')
def home():
    # Empty state handling
    todo_list_view = Alert("No todos yet! Add one below.", variant="info")
    if TodoState.todos:
        items = []
        for todo in TodoState.todos:
            status_badge = Badge("Done", variant="success") if todo.done else Badge("Pending", variant="warning")
            items.append(
                ListItem(
                    Flex(
                        Text(todo.text, strike=todo.done),
                        status_badge,
                        Button("Toggle", on_click=lambda id=todo.id: TodoState.toggle_todo(id), size="sm"),
                        Button("Delete", on_click=lambda id=todo.id: TodoState.remove_todo(id), variant="danger", size="sm"),
                        justify="space-between",
                        align="center",
                        gap="md"
                    )
                )
            )
        todo_list_view = List(*items)

    return Container(
        Card(
            title="Todo List",
            children=[
                todo_list_view,
                Flex(
                    Input(
                        placeholder="Add a new task...", 
                        bind=TodoState.current_input,
                        full_width=True
                    ),
                    Button("Add", on_click=TodoState.add_todo, variant="primary"),
                    gap="sm",
                    margin_top="lg"
                )
            ]
        )
    )

if __name__ == '__main__':
    app.run()
