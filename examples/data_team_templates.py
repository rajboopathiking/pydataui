from pydataui import App

try:
    from data_team_samples import analyst_page, models_page, pipelines_page, quality_page
except ImportError:
    from examples.data_team_samples import (
        analyst_page,
        models_page,
        pipelines_page,
        quality_page,
    )

app = App(title="Data Team Workspace")


@app.page("/")
def analyst():
    return analyst_page()


@app.page("/quality")
def quality():
    return quality_page()


@app.page("/pipelines")
def pipelines():
    return pipelines_page()


@app.page("/models")
def models():
    return models_page()


if __name__ == "__main__":
    app.run()
