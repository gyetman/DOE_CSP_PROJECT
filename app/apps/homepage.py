import sys
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import dash_trich_components as dtc
from dash.dependencies import Input, Output, State

# import app_config as cfg
# sys.path.insert(0,str(cfg.base_path))

# import helpers
from app import app

#TODO LIST
# remove app.titles from each page except index
# Card Hover to change colors (see end):
#https://www.ordinarycoders.com/blog/article/codepen-bootstrap-card-hovers
#Link to Arc Resources: https://resources-for-solar-desalination-columbia.hub.arcgis.com/

card_documentation = dtc.Card(
    link='https://sam.nrel.gov/images/web_page_files/sam-help-2020-2-29-r1.pdf',
    image='assets/images/documentation.png',
    title='Documentation',
    description="SAM documenation until we add our own.",
    badges=['Badge 1', 'Badge 2', 'Badge 3'],
    style={'padding':16}
)

card_geospatial_resources = dtc.Card(
    link='https://resources-for-solar-desalination-columbia.hub.arcgis.com/',
    image='assets/images/geospatial_resources.png',
    title='Geospatial Resources',
    description="About our resources HERE",
    badges=['Badge 1', 'Badge 2', 'Badge 3'],
    style={'padding':16}
)

card_select_model = html.A(dtc.Card(
    image='/assets/images/model_selection.png',
    title='Select Model',
    description="Some quick example text to build on the card title and make up the bulk of the card's content.",
    badges=['Badge 1', 'Badge 2', 'Badge 3'],
    git='https://github.com/adam-a-a/DOE_CSP_PROJECT',
    style={'padding':16}
),href='/model-selection',style={'text-decoration': 'none'})

card_select_site = html.A(dtc.Card(
    image='/assets/images/site_selection.png',
    title='Select Site',
    description="Some quick example text to build on the card title and make up the bulk of the card's content.",
    badges=['Badge 1', 'Badge 2', 'Badge 3'],
    git='https://github.com/adam-a-a/DOE_CSP_PROJECT',
    style={'padding':16}
),href='/dynamic-map',style={'text-decoration': 'none'})

card_quick_analysis = dtc.Card(
    link='https://columbia.maps.arcgis.com/home/item.html?id=719c769587604bb9a2e098fa052ef1b9#overview',
    image='/assets/images/quick_analysis.png',
    title='Quick Analysis',
    description="Describe Quick Analysis here...",
    badges=['Badge 1', 'Badge 2', 'Badge 3'],
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
    # children=[dbc.NavItem(dbc.NavLink("Charts", href='/chart-results')),
    #           dbc.NavItem(dbc.NavLink("Report"), active=True),
    #           dbc.NavItem(dbc.NavLink("Results Map", href='/results-map')),
    #           html.P(id='data-initialize')],
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
        # card_select_model,
        # card_select_site,
        # card_quick_analysis,
        # card_geospatial_resources,
        # card_documentation,
        dbc.Button(
            html.Span(["Button  ", html.I(className="fas fa-plus-circle ml-2")])
        ),
        dbc.Row(dbc.Col(([dbc.Card("Contact Us Goes Here...", color='dark', outline=True, className='glyphicon glyphicon-cloud', style={'text-align':'center'})])))
    ],style={'margin-top':45} ),
    
])