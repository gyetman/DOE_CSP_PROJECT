import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import model_selection_test, wc

layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])
app.layout = layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/ms':
        return model_selection_test.model_selection_layout
    elif pathname == '/wc':
        return wc.wc_layout
    else:
        return html.H5('404 URL not found')

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)