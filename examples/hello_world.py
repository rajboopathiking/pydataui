from pydataui import App
from pydataui.components import Container, Heading, Text

app = App(title='Hello World')

@app.page('/')
def home():
    return Container(
        Heading('Hello, World!', level=1),
        Text('Welcome to PyDataUI — Build full-stack Python apps.'),
    )

if __name__ == '__main__':
    app.run()
