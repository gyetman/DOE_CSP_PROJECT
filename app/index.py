# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
from dash.dependencies import Input, Output

from app import app
from apps import analysis_report, chart_results, homepage, model_selection, model_parameters, parametric_charts, results_map, site_selection

layout = html.Div([
    dcc.Location(id='url', refresh=True),
    html.Div(id='page-content'),
    dcc.Store(id='session',storage_type='session',
              data=[]),
])
app.layout = layout
app.title = 'Solar Desalination Analysis Tool'

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/' or pathname == '/home':
        return homepage.homepage_layout
    elif pathname == '/site-selection':
        return site_selection.render_map()
    elif pathname == '/model-selection':
        return model_selection.model_selection_layout
    elif pathname == '/model-variables':
        return model_parameters.model_tables_layout
    elif pathname == '/chart-results':
        return chart_results.real_time_layout()
    elif pathname == '/parametric-charts':
        return parametric_charts.real_time_layout()
    elif pathname == '/analysis-report':
        return analysis_report.analysis_report_layout
    elif pathname == '/results-map':
        return results_map.render_results_map()
    else:
        return html.Div([
            html.H5("404 URL Not Found"), 
            html.A("To Home Page", href='/home')])

if __name__ == '__main__':
    app.run_server(debug=True, port=8077)