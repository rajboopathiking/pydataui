from pydataui import App, State
from pydataui.components import Container, Card, Flex, Button, Heading, Divider

class CounterState(State):
    count: int = 0
    
    def increment(self):
        self.count += 1
    
    def decrement(self):
        self.count -= 1
    
    def reset(self):
        self.count = 0

app = App(title='Counter')

@app.page('/')
def home():
    return Container(
        Card(
            title='Counter App',
            children=[
                Flex(
                    Button('-', on_click=CounterState.decrement, variant='danger'),
                    Heading(CounterState.count, level=2),
                    Button('+', on_click=CounterState.increment, variant='success'),
                    align='center', justify='center', gap='lg',
                ),
                Divider(),
                Button('Reset', on_click=CounterState.reset, variant='outline', full_width=True),
            ],
        ),
    )

if __name__ == '__main__':
    app.run()
