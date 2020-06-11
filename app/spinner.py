import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State, ALL
import time

# loading_spinner = html.Div(
#     [
#         dbc.Button("Load", id="loading-button"),
#         dbc.Spinner(html.Div(id="loading-output")),
#     ]
# )

# butt=dbc.Button(
#     [dbc.Spinner(size="sm"), " Loading..."],
#     color="primary",
#     disabled=True,
# )

# integrated = html.Div([
#     dbc.Row([dbc.Col([dbc.Button([
#         dbc.Spinner([
#             html.Div(id="integrated-output"),
#         ],size="sm"),
#             "Run Model Simulation",  
#     ],id="integrated-button")
#     ],width=9)])
# ])

replace = html.Div([
    dbc.Button([
        " Run Model Simulation",  
    ],id="integrated-button")
],id='replace-button')

spinner = [dbc.Spinner(size="sm"), " Run Model Simulation"]


butt_output = html.Div("Done Processing")


# layout=html.Div(children=[loading_spinner,butt,integrated])
layout=html.Div(replace)
external_stylesheets = [dbc.themes.FLATLY]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.layout = layout

@app.callback(
    Output("replace-button", "children"), 
    [Input("integrated-button", "n_clicks")]
)
def load_output(n):
    if n:
        time.sleep(10)
        return butt_output

@app.callback(
    Output('integrated-button','children'),
    [Input('integrated-button', 'n_clicks')]
)
def replace_button(n):
    if n:
        return spinner


# @app.callback(
#     Output("loading-output", "children"), 
#     [Input("loading-button", "n_clicks")]
# )
# def load_output(n):
#     if n:
#         time.sleep(1)
#         return f"Output loaded {n} times"
#     return "Output not reloaded yet"




if __name__ == '__main__':
    app.run_server(debug=True, port=8051)