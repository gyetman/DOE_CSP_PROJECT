import sys
import dash_bootstrap_components as dbc
# import dash_core_components as dcc
from dash import dcc
# import dash_html_components as html
from dash import html
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

contact = dbc.Card([
    dbc.Card(
        dbc.CardBody([
            html.H4("Contact Us", className="card-title"),
            html.P([html.A("Vasilis Fthenakis", href="https://www.eee.columbia.edu/faculty/vasilis-fthenakis"), ", ", html.A("Center for Life Cycle Analysis", href="http://www.clca.columbia.edu/"), html.Br(), "Columbia University. Principal Investigator"]),
            html.P([html.A("Greg Yetman", href="http://ciesin.columbia.edu/yetman.html"), ", ", html.A("Center for International Earth Science Information Network", href="https://www.ciesin.columbia.edu/"), html.Br(), "Columbia University. Co-investigator"]),
        ])),
    dbc.Card(
        dbc.CardBody([
            html.P(html.I("Copyright 2021. The Trustees of Columbia University in the City of New York.")),
            html.P(html.I("This material is based upon work supported by the U.S. Department of Energy’s Office of Energy Efficiency and Renewable Energy (DOE-EERE) under the Solar Energy Technologies Office (SETO) Award Number DE00008401.  This software was prepared as an account of work sponsored by an agency of the United States Government. Neither the United States Government nor any agency thereof, nor any of their employees, makes any warranty, express or implied, or assumes any legal liability or responsibility for the accuracy, completeness, or usefulness of any information, apparatus, product, or process disclosed, or represents that its use would not infringe privately owned rights. Any opinions, findings, and conclusions or recommendations expressed in this material are those of the authors and do not necessarily reflect the views of the Department of Energy.")),
            html.P("The resources collected here are made available for use in solar facility development under the license of the original data authors as noted in each item.")   
        ]))],
    outline=True, 
    className='card border-info mb-3', 
)

cards = dbc.Row([
    card_select_model,
    card_select_site,
    card_quick_analysis,
    card_geospatial_resources,
    card_documentation
],style={'padding':16})

chart_navbar = dbc.NavbarSimple(
    brand="COLUMBIA UNIVERSITY | SOLAR ENERGY DESALINATION ANALYSIS TOOL (SEDAT)",
    color="primary",
    dark=True,
    sticky='top',
    style={'margin-bottom':60},  
    id='home-title'
)

homepage_layout = html.Div([
    chart_navbar,
    html.H3("Solar Energy Desalination Analysis Tool (SEDAT)", className='text-success', style={'text-align':'center'}),
    dbc.Container([
        cards,
        dbc.Row(dbc.Col(([contact])))
    ],style={'margin-top':45} ),
    
])