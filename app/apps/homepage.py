import sys
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_trich_components as dtc
from dash.dependencies import Input, Output, State

from app import app

card_documentation = dtc.Card(
    title='Documentation',
    # link='https://sam.nrel.gov/images/web_page_files/sam-help-2020-2-29-r1.pdf',
    link='/assets/docs/documentation.pdf',
    image='assets/images/documentation.png',
    description="The Solar Desalination Analysis Tool User Manual.",
    #badges=['Badge 1', 'Badge 2', 'Badge 3'],
    style={'padding':16}
)

card_geospatial_resources = dtc.Card(
    title='Geospatial Resources',
    link='https://resources-for-solar-desalination-columbia.hub.arcgis.com/',
    image='assets/images/geospatial_resources.png',
    description="Interactive maps and data layers.",
    #badges=['Badge 1', 'Badge 2', 'Badge 3'],
    style={'padding':16}
)

card_select_model = html.A(dtc.Card(
    title='Select Model',
    image='/assets/images/model_selection.png',
    description="Choose solar thermal, desalination and financial models.",
    #badges=['Badge 1', 'Badge 2', 'Badge 3'],
    git='https://github.com/adam-a-a/DOE_CSP_PROJECT',
    style={'padding':16}
),href='/model-selection',style={'text-decoration': 'none'})

card_select_site = html.A(dtc.Card(
    title='Select Site',
    image='/assets/images/site_selection.png',
    description="Interactive map to aid in choosing a suitable site location.",
    #badges=['Badge 1', 'Badge 2', 'Badge 3'],
    git='https://github.com/adam-a-a/DOE_CSP_PROJECT',
    style={'padding':16}
),href='/site-selection',style={'text-decoration': 'none'})

card_quick_analysis = dtc.Card(
    title='Quick Analysis',
    link='http://ec2-18-223-238-182.us-east-2.compute.amazonaws.com/calculate_lcow.html',
    image='/assets/images/quick_analysis.png',
    description="Calculate LCOW using a simple model.",
    #badges=['Badge 1', 'Badge 2', 'Badge 3'],
    style={'padding':16}
)

cards = dbc.Row([
    card_select_model,
    card_select_site,
    card_quick_analysis,
    card_geospatial_resources,
    card_documentation
],style={'padding':16})

chart_navbar = dbc.NavbarSimple(
    brand="WHAT|WHO",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60},  
    id='home-title'
)

homepage_layout = html.Div([
    chart_navbar,
    html.H3("Solar Desalination Analysis Tool", className='text-success', style={'text-align':'center'}),
    dbc.Container([
        cards,
        dbc.Row(dbc.Col(([dbc.Card("Contact Us Goes Here...", color='dark', outline=True, className='glyphicon glyphicon-cloud', style={'text-align':'center'})])))
    ],style={'margin-top':45} ),
    
])