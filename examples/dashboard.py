from pydataui import App, State
from pydataui.components import Container, Grid, Card, Heading, Text, Flex, Table, Navbar, Sidebar, BarChart

class DashboardState(State):
    metrics = {
        "users": 1520,
        "revenue": "$12,400",
        "conversion": "4.2%"
    }
    recent_signups = [
        {"id": 1, "name": "Alice Smith", "plan": "Pro"},
        {"id": 2, "name": "Bob Jones", "plan": "Free"},
        {"id": 3, "name": "Charlie Brown", "plan": "Enterprise"},
    ]
    chart_data = {
        "labels": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "values": [120, 200, 150, 80, 220, 300, 250]
    }

app = App(title='Dashboard')

@app.page('/')
def dashboard():
    return Flex(
        Sidebar(
            links=[
                {"label": "Overview", "href": "/"},
                {"label": "Analytics", "href": "/analytics"},
                {"label": "Settings", "href": "/settings"}
            ]
        ),
        Container(
            Navbar(title="Admin Dashboard"),
            Grid(
                Card(title="Total Users", children=[Heading(DashboardState.metrics["users"], level=2)]),
                Card(title="Revenue", children=[Heading(DashboardState.metrics["revenue"], level=2)]),
                Card(title="Conversion Rate", children=[Heading(DashboardState.metrics["conversion"], level=2)]),
                columns=3,
                gap="md",
                margin_bottom="lg"
            ),
            Grid(
                Card(
                    title="Traffic Overview", 
                    children=[
                        BarChart(
                            labels=DashboardState.chart_data["labels"],
                            data=DashboardState.chart_data["values"]
                        )
                    ]
                ),
                Card(
                    title="Recent Signups",
                    children=[
                        Table(
                            columns=["ID", "Name", "Plan"],
                            data=[[s["id"], s["name"], s["plan"]] for s in DashboardState.recent_signups]
                        )
                    ]
                ),
                columns=2,
                gap="lg"
            ),
            full_width=True
        ),
        direction="row",
        full_height=True
    )

if __name__ == '__main__':
    app.run()
