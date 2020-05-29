import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

from app import app
from apps import analysis_report, chart_results, model_selection, model_parameters

layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content')
])
app.layout = layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/model-selection':
        return model_selection.model_selection_layout
    elif pathname == '/model-variables':
        return model_parameters.model_tables_layout
    elif pathname == '/chart-results':
        return chart_results.chart_results_layout
    elif pathname == '/analysis-report':
        return analysis_report.analysis_report_layout
    else:
        return html.H5('404 URL not found')

if __name__ == '__main__':
    app.run_server(debug=True, port=8077)