###############################################################################
#                            RUN MAIN                                         #
###############################################################################

# setup
import warnings
warnings.filterwarnings("ignore")

import dash
from dash.dependencies import Input, Output, State
from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

import pandas as pd

from settings import config
from python.data import DB, download_file


# App Instance
app = dash.Dash(name=config.app_name, assets_folder="static", external_stylesheets=[dbc.themes.LUX, config.fontawesome])
app.title = config.app_name

cols_to_show = ["PROVINCIA_SIGLA","COMUNE_NOME","ADDRESS","CIVICO","ID_BUILDING","POP","ID_SCALA"]

geo = pd.read_excel("stored/comuni.xls", dtype=str)
regioni = {row[0]:row[1] for index,row in geo[["REGIONE_NOME","REGIONE"]].drop_duplicates().iterrows()}  #{'Piemonte':'01', ...}
province = {k:sorted(geo[geo["REGIONE_NOME"]==k]["PROVINCIA_NOME"].unique()) 
            for k in geo["REGIONE_NOME"].unique()}  #{'Piemonte':['Alessandria','Asti','Biella','Torino'], ...}

db = DB().run()



########################## Navbar ##########################
# Output
navbar = dbc.Nav(className="nav nav-pills", children=[
    ## logo/home
    dbc.NavItem(html.Img(src=app.get_asset_url("logo.PNG"), height="40px")),
    ## about
    dbc.NavItem(html.Div([
        dbc.NavLink("About", href="/", id="about-popover", active=False),
        dbc.Popover(id="about", is_open=False, target="about-popover", children=[
            dbc.PopoverHeader("How it works"), dbc.PopoverBody(config.about)
        ])
    ])),
    ## links
    dbc.DropdownMenu(label="Links", nav=True, children=[
        dbc.DropdownMenuItem([html.I(className="fa fa-linkedin"), "  Contacts"], href=config.contacts, target="_blank"), 
        dbc.DropdownMenuItem([html.I(className="fa fa-github"), "  Code"], href=config.code, target="_blank"),
        dbc.DropdownMenuItem([html.I(className="fa fa-medium"), "  Tutorial"], href=config.tutorial, target="_blank")
    ])
])


# Callbacks
@app.callback(output=[Output(component_id="about", component_property="is_open"), 
                      Output(component_id="about-popover", component_property="active")], 
              inputs=[Input(component_id="about-popover", component_property="n_clicks")], 
              state=[State("about","is_open"), State("about-popover","active")])
def about_popover(n, is_open, active):
    if n:
        return not is_open, active
    return is_open, active



########################## Body ##########################
# Input
inputs = dbc.FormGroup([
    dbc.Row([
        ## input dropdown
        dbc.Col(md=2, children=[
            dbc.Label("Seleziona Regione", style={"font-weight":"bold"}), 
            dcc.Dropdown(id="regione", options=[{"label":x,"value":x} for x in sorted(regioni.keys())], value="Abruzzo")
        ]),
        ## input dropdown
        dbc.Col(md=2, children=[
            dbc.Label("Seleziona Provincia", style={"font-weight":"bold"}), 
            dcc.Dropdown(id="provincia", value="L'Aquila")
        ]),
        ## input text
        dbc.Col(md=3, children=[
            dbc.Label("Inserisci Indirizzo", style={"font-weight":"bold"}), 
            dbc.Input(id="query", placeholder="esempio: Piazza Verdi 5", type="text")
        ]),
        ## run button
        dbc.Col(md=1, children=[
            dbc.Label("Clicca", style={"font-weight":"bold"}),
            dbc.Col(dbc.Button("Cerca", id="run", color="primary"))
        ])
    ])
])


# Output
body = html.Div([
        ## input
        inputs, 
        ## output
        dbc.Spinner([
            ### table
            dbc.Label("Risultato", style={"font-weight":"bold"}),
            dash_table.DataTable(id="table"),
            ### download
            html.Br(),html.Br(),
            dbc.Badge(html.A('Download', id='download-excel', download="data.xlsx", href="", target="_blank"), color="success", pill=True)
        ], color="primary", type="grow"),
], style={"padding-left":"1%"})


# Callbacks
@app.callback(output=Output(component_id='provincia', component_property='options'),
              inputs=[Input(component_id='regione', component_property='value')])
def update_dropdown(regione):
    return [{'label':i, 'value':i} for i in province[regione]]


@app.callback(output=[Output(component_id='table', component_property='columns'),
                      Output(component_id="table", component_property="data"),
                      Output(component_id='download-excel', component_property='href')],
              inputs=[Input(component_id="run", component_property="n_clicks")],
              state=[State("regione","value"), State("provincia","value"), State("query","value")])
def results(n_clicks, regione, provincia, query):
    dtf = db[db["REGIONE"] == regioni[regione]]
    dtf = dtf.merge(geo, how="left", on=["PROVINCIA","COMUNE"])
    dtf = dtf[dtf["PROVINCIA_NOME"]==provincia]
    dtf = dtf[dtf["ADDRESS"].str.contains(query.upper().strip())] if query is not None else dtf.head()
    out = dtf[cols_to_show]
    columns = [{'name':i, 'id':i} for i in out.columns]
    data = out.to_dict(orient='records')
    return columns, data, download_file(dtf)



########################## App Layout ##########################
app.layout = dbc.Container(fluid=True, children=[
    html.H1(config.app_name, id="nav-pills"),
    navbar,
    html.Br(),html.Br(),html.Br(),
    body
])



########################## Run ##########################
if __name__ == "__main__":
    debug = True if config.ENV == "DEV" else False
    app.run_server(debug=debug, host=config.host, port=config.port)
        