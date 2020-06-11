import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_table
from dash.dependencies import Input, Output, State


layout =  html.Div("Title Here",id=f'collapse-title-{i}')

@app.callback([Output(f"collapse-title-{i}", 'children') for i in models],
            [Input('tabs-card','children')])
def title_collapse_buttons(x):
    '''Titles the collapse buttons based on values stored in JSON file'''
    app_vals = helpers.json_load(cfg.app_json)
    d = f"{cfg.Desal[app_vals['desal']].rstrip()} Desalination System"
    s = cfg.Solar[app_vals['solar']].rstrip()
    f = cfg.Financial[app_vals['finance']].rstrip()
    print(f"Title should be {d}")
    return d,s,f