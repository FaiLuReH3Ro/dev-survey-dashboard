# Import libraries
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash_bootstrap_templates import load_figure_template
from dash import Dash, html, dcc, Input, Output, State

# Loading the figure themes
load_figure_template("minty_dark")

# Read the data
data = pd.read_csv('clean_survey_data.csv')

# Create the app 
dbc_css = "https://cdn.jsdelivr.net/gh/AnnMarieW/dash-bootstrap-templates/dbc.min.css"
app = Dash(__name__, external_stylesheets=[dbc.themes.MINTY, dbc_css, dbc.icons.BOOTSTRAP])
server = app.server
app.title = "Dev Survey Dashboard"

# Create list of age ranges
ages = list(data['Age'].sort_values().unique())
under18 = ages[-1]
ages.insert(0, under18)
ages.pop()

# Create a list of education level
ed_levels = list(data['EdLevel'].sort_values().unique())

# Create a list of employments
employ = data['Employment'].dropna().str.split(";")
employ = employ.explode('Employment')
employments = list(employ.sort_values().unique())

# Create a list of Developer Status
dev_status = list(data['MainBranch'].unique())

# Create a range of Years coding 
years_code = list(range(0, 51))


# Make a copy of the original data
df = data.copy()

# Explode the employment column
df['Employment'] = df['Employment'].str.split(";")
df = df.explode('Employment')

# Define the layout
app.layout = dbc.Container(children=[
    
    # Heading
    html.H1("2024 Stack Overflow Developer Survey Results", className='mb-4'),

    # Toggle Filters Button
    dbc.Button([html.I(className='bi bi-filter me-2'),"Filters"], 
               id='filters-button', 
               n_clicks=0, 
               size='lg',
               className = 'mb-4'),

    # Collapse component
    dbc.Collapse(id = 'collapse-filters', is_open=False, children=[

        # Filters
        html.Div([

            # Age Group Filter (Age)
            html.Div([
                html.Label('Age', htmlFor='age', className = 'mb-2 fs-5'),
                dcc.Dropdown(id='age',
                            options=[{'label': i, 'value': i} for i in ages],
                            value= [i for i in ages],
                            placeholder='Select Age Groups',
                            multi=True)
            ], className = 'mb-4'),

            # Education Level Filter (EdLevel)
            html.Div([
                html.Label('Education Level', htmlFor='ed-level', className = 'mb-2 fs-5'),
                dcc.Dropdown(id='ed-level',
                            options=[{'label': i, 'value': i} for i in ed_levels],
                            value = [i for i in ed_levels],
                            placeholder='Select Education Levels',
                            multi=True)
            ], className = 'mb-4'),

            # Employment Status Filter (Employment)
            html.Div([
                html.Label("Employment Status", htmlFor='employment-status', className = 'mb-2 fs-5'),
                dcc.Dropdown(id = 'employment-status',
                            options = [{'label': i, 'value': i} for i in employments],
                            value = [i for i in employments],
                            placeholder = 'Select Employment Status',
                            multi=True)
            ] , className = 'mb-4'  
            ),

            # Developer Status Filter (MainBranch)
            html.Div([
                html.Label("Developer Status", htmlFor = 'dev-status', className = 'mb-2 fs-5'),
                dcc.Dropdown(id = 'dev-status',
                            options = [{'label': i, 'value': i} for i in dev_status],
                            value = [i for i in dev_status],
                            placeholder = "Select Developer Status",
                            multi=True
                )
            ], className = 'mb-4'),

            # Years Code Filter (YearsCode)
            html.Div([
                html.Label("Years Coding", htmlFor = 'years-code', className = 'mb-2 fs-5'),
                dcc.RangeSlider(id = 'years-code',
                                min=0,
                                max=50,
                                tooltip={'placement': 'bottom', 'always_visible': True},
                                value=[0,50],
                                marks={0 : '0', 50: '50'}
                )
            ])

        ], id='filters', className = 'mb-4')

    ]),

    # Main body
    html.Main([

        # Tabs
        dcc.Tabs(children = [
            dcc.Tab(value = 'tech-used', label = 'Technologies Used', className='fs-4 fw-bold'),
            dcc.Tab(value = 'tech-want', label = 'Technologies Desired', className='fs-4 fw-bold'),
            dcc.Tab(value = 'demographics', label = 'Survey Demographics', className='fs-4 fw-bold')],
            value = 'tech-used',
            id = 'tabs',
            className = 'mb-4'
        ),
        
        # Output visualizations
        html.Div(id='output-container') 
    ], id='main'),

], fluid=True, className='dbc p-4')

# Callback for toggling filter button
@app.callback(Output(component_id='collapse-filters', component_property='is_open'),
              [Input(component_id='filters-button', component_property='n_clicks'),
               State(component_id='collapse-filters', component_property='is_open')])

def toggle_filters(n, is_open):
    if n:
        return not is_open
    return is_open


# Callback decorator for applying filters
@app.callback(Output(component_id='output-container', component_property='children'),
              Input(component_id='tabs', component_property='value'),
              Input(component_id='age', component_property='value'),
              Input(component_id='ed-level', component_property='value'),
              Input(component_id='employment-status', component_property='value'),
              Input(component_id='dev-status', component_property='value'),
              Input(component_id='years-code', component_property='value'))

# Callback function that gets executed 
def get_plots(tab, age, ed_level, employ_status, dev_status, years_code):

    df_filer = df.copy()

    ## Technologies Used 
    if tab == 'tech-used':
        
        # Filters the data
        df_filer = df_filer[
            (df_filer['Age'].isin(age)) &
            (df_filer['EdLevel'].isin(ed_level)) &
            (df_filer['Employment'].isin(employ_status)) &
            (df_filer['MainBranch'].isin(dev_status)) &
            (df_filer['YearsCode'] >= years_code[0]) &
            (df_filer['YearsCode'] <= years_code[1])
        ]
        
        ## Languages Used
        ## LanguageHaveWorkedWith
        lang_worked = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'LanguageHaveWorkedWith']].copy()

        # Since values are separated by a semicolon, it needs to be exploded
        lang_worked['LanguageHaveWorkedWith'] = lang_worked['LanguageHaveWorkedWith'].str.split(";")
        lang_worked = lang_worked.explode('LanguageHaveWorkedWith')

        # Finding the top 10 languages
        top10_lang_worked = lang_worked['LanguageHaveWorkedWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot a bar chart
        top10_lang_worked_plot = dcc.Graph(figure=px.bar(top10_lang_worked,
                                                    x= 'LanguageHaveWorkedWith', 
                                                    y='count',
                                                    labels= {'LanguageHaveWorkedWith' : 'Languages',
                                                            'count': 'Count'}
                                                            ), className='plot w-100')
        
        ## Databases Used
        ## DatabaseHaveWorkedWith
        db_worked = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'DatabaseHaveWorkedWith']].dropna().copy()

        # Since values are separated by a semicolon, it needs to be exploded
        db_worked['DatabaseHaveWorkedWith'] = db_worked['DatabaseHaveWorkedWith'].str.split(";")
        db_worked = db_worked.explode('DatabaseHaveWorkedWith')

        # Finding the top 10 databases
        top10_db_worked = db_worked['DatabaseHaveWorkedWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot a bar chart
        top10_db_worked_plot = dcc.Graph(figure=px.bar(top10_db_worked,
                                                    x= 'DatabaseHaveWorkedWith', 
                                                    y='count',
                                                    labels= {'DatabaseHaveWorkedWith' : 'Databases',
                                                            'count': 'Count'}), className='plot w-100')
        
        ## Web Frameworks Used
        ## WebframeHaveWorkedWith
        web_worked = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'WebframeHaveWorkedWith']].dropna().copy()

        # Explode the column
        web_worked['WebframeHaveWorkedWith'] = web_worked['WebframeHaveWorkedWith'].str.split(";")
        web_worked = web_worked.explode('WebframeHaveWorkedWith')

        # Finding the top 10 web frameworks
        top10_web_worked = web_worked['WebframeHaveWorkedWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot the horizontal bar chart
        top10_web_worked_fig = px.bar(top10_web_worked,
                                    x = 'count',
                                    y = 'WebframeHaveWorkedWith',
                                    labels={'WebframeHaveWorkedWith': 'Web Frameworks',
                                            'count': 'Count'},
                                    orientation='h')
        
        top10_web_worked_fig.update_layout(yaxis=dict(autorange="reversed"))
        
        top10_web_worked_plot = dcc.Graph(figure=top10_web_worked_fig, className='plot w-100')

        ## Collaboration Tools Used
        ## NEWCollabToolsHaveWorkedWith	
        collab_worked = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'NEWCollabToolsHaveWorkedWith']].dropna().copy()

        # Explode the column
        collab_worked['NEWCollabToolsHaveWorkedWith'] = collab_worked['NEWCollabToolsHaveWorkedWith'].str.split(";")
        collab_worked = collab_worked.explode('NEWCollabToolsHaveWorkedWith')

        # Finding the top 10 collaboration tools
        top10_collab_worked = collab_worked['NEWCollabToolsHaveWorkedWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot the horizontal bar chart
        top10_collab_worked_fig = px.bar(top10_collab_worked,
                                        x = 'count',
                                        y = 'NEWCollabToolsHaveWorkedWith',
                                        labels={'NEWCollabToolsHaveWorkedWith': 'Collaboration Tools',
                                                'count': 'Count'},
                                        orientation='h')
        
        top10_collab_worked_fig.update_layout(yaxis=dict(autorange="reversed"))
        
        top10_collab_worked_plot = dcc.Graph(figure=top10_collab_worked_fig, className='plot w-100')

        # Return the plots
        return [ 
            dbc.Row([
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Programming Languages"),
                            dbc.CardBody([html.H2("Top 10 Languages Used", className='plot-title'), top10_lang_worked_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4'),
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Databases"),
                            dbc.CardBody([html.H2("Top 10 Databases Used", className='plot-title'), top10_db_worked_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4')
                         ], align='center', justify='center'),
            dbc.Row([
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Web Frameworks"),
                            dbc.CardBody([html.H2("Top 10 Web Frameworks Used", className='plot-title'), top10_web_worked_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4'),
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Collaboration Tools"),
                            dbc.CardBody([html.H2("Top 10 Collaboration Tools Used", className='plot-title'), top10_collab_worked_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4')
                        ],align='center', justify='center')
                ]
    
    ##################################
    
    ## Technologies Desired
    elif tab == 'tech-want':

        # Filters the data
        df_filer = df_filer[
            (df_filer['Age'].isin(age)) &
            (df_filer['EdLevel'].isin(ed_level)) &
            (df_filer['Employment'].isin(employ_status)) &
            (df_filer['MainBranch'].isin(dev_status)) &
            (df_filer['YearsCode'] >= years_code[0]) &
            (df_filer['YearsCode'] <= years_code[1])
        ]

        ## Languages Desired
        ## LanguageWantToWorkWith
        lang_want = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'LanguageWantToWorkWith']].dropna().copy()

        # Since values are separated by a semicolon, it needs to be exploded
        lang_want['LanguageWantToWorkWith'] = lang_want['LanguageWantToWorkWith'].str.split(";")
        lang_want = lang_want.explode('LanguageWantToWorkWith')

        # Finding the top 10 languages
        top10_lang_want = lang_want['LanguageWantToWorkWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot the bar graph
        top10_lang_want_plot = dcc.Graph(figure=px.bar(top10_lang_want,
                                                    x= 'LanguageWantToWorkWith', 
                                                    y='count',
                                                    labels= {'LanguageWantToWorkWith' : 'Language',
                                                                'count': 'Count'}), className='plot w-100')
        
        ## Databases Desired
        ## DatabaseWantToWorkWith
        db_want = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'DatabaseWantToWorkWith']].dropna().copy()

        # Since values are separated by a semicolon, it needs to be exploded
        db_want['DatabaseWantToWorkWith'] = db_want['DatabaseWantToWorkWith'].str.split(";")
        db_want = db_want.explode('DatabaseWantToWorkWith')

        # Finding the top 10 languages
        top10_db_want = db_want['DatabaseWantToWorkWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot the bar graph
        top10_db_want_plot = dcc.Graph(figure=px.bar(top10_db_want,
                                                    x= 'DatabaseWantToWorkWith', 
                                                    y='count',
                                                    labels= {'DatabaseWantToWorkWith' : 'Database',
                                                                'count': 'Count'}), className='plot w-100')
        
        ## Web Frameworks Desired
        ## WebframeWantToWorkWith
        web_want = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'WebframeWantToWorkWith']].dropna().copy()

        # Explode the column
        web_want['WebframeWantToWorkWith'] = web_want['WebframeWantToWorkWith'].str.split(";")
        web_want = web_want.explode('WebframeWantToWorkWith')

        # Finding the top 10 web frameworks
        top10_web_want = web_want['WebframeWantToWorkWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot the horizontal bar chart
        top10_web_want_fig =px.bar(top10_web_want,
                                    x = 'count',
                                    y = 'WebframeWantToWorkWith',
                                    labels={'WebframeWantToWorkWith': 'Web Frameworks',
                                            'count': 'Count'},
                                    orientation='h')
        
        top10_web_want_fig.update_layout(yaxis=dict(autorange="reversed"))
        
        top10_web_want_plot = dcc.Graph(figure=top10_web_want_fig, className='plot w-100')

        ## Collaboration Tools Desired
        ## NEWCollabToolsWantToWorkWith	
        collab_want = df_filer[['Age', 'EdLevel', 'Employment', 'MainBranch', 'YearsCode', 'NEWCollabToolsWantToWorkWith']].dropna().copy()

        # Explode the column
        collab_want['NEWCollabToolsWantToWorkWith'] = collab_want['NEWCollabToolsWantToWorkWith'].str.split(";")
        collab_want = collab_want.explode('NEWCollabToolsWantToWorkWith')

        # Finding the top 10 collaboration tools
        top10_collab_want = collab_want['NEWCollabToolsWantToWorkWith'].value_counts().sort_values(ascending=False).head(10).reset_index()

        # Plot the horizontal bar chart
        top10_collab_want_fig = px.bar(top10_collab_want,
                                        x = 'count',
                                        y = 'NEWCollabToolsWantToWorkWith',
                                        labels={'NEWCollabToolsWantToWorkWith': 'Collaboration Tools',
                                                'count': 'Count'},
                                        orientation='h')
        
        top10_collab_want_fig.update_layout(yaxis=dict(autorange="reversed"))
        
        top10_collab_want_plot = dcc.Graph(figure=top10_collab_want_fig, className='plot w-100')

        # Return the plots
        return [ 
            dbc.Row([
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Programming Languages"),
                            dbc.CardBody([html.H2("Top 10 Languages Desired", className='plot-title'), top10_lang_want_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4'),
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Databases"),
                            dbc.CardBody([html.H2("Top 10 Databases Desired", className='plot-title'),top10_db_want_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4')
                         ], align='center', justify='center'),
            dbc.Row([
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Web Frameworks"),
                            dbc.CardBody([html.H2("Top 10 Web Frameworks Desired", className='plot-title'),top10_web_want_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4'),
                dbc.Col(dbc.Card([
                            dbc.CardHeader("Collaboration Tools"),
                            dbc.CardBody([html.H2("Top 10 Collaboration Tools Desired", className='plot-title'), top10_collab_want_plot], className='p-4')
                            ]), 
                        lg=12, xl=6, className='mb-4')
                        ],align='center', justify='center')
                ]
    ###################################

    # Demographics
    elif tab == 'demographics':

        # Filters the data
        df_filer = df_filer[
            (df_filer['Age'].isin(age)) &
            (df_filer['EdLevel'].isin(ed_level)) &
            (df_filer['Employment'].isin(employ_status)) &
            (df_filer['MainBranch'].isin(dev_status)) &
            (df_filer['YearsCode'] >= years_code[0]) &
            (df_filer['YearsCode'] <= years_code[1])
        ]

        ## Country Distribution
        country_counts = df_filer['Country'].dropna().value_counts().reset_index()
        country_counts.rename(columns={'count': 'Count'}, inplace = True)

        # Plot the map
        country_plot = dcc.Graph(figure=px.choropleth(country_counts,
                                                      locations='Country',
                                                      locationmode='country names',
                                                      color='Count'
                                                      ), 
                                                      className='plot w-100',
                                                      )
    
        ## Top 10 Countries
        top10_countries = country_counts.sort_values(by='Count', ascending = False).head(10)
        top10_countries['Country'].replace({'United States of America': 'USA', 'United Kingdom of Great Britain and Northern Ireland': 'UK'}, inplace=True)

        # Plot the bar chart
        top10_countries_plot = dcc.Graph(figure=px.bar(top10_countries,
                                                       x='Country',
                                                       y='Count'), className='plot')
        
        ## Education level Distribution
        ed_level_counts = df_filer['EdLevel'].value_counts().reset_index()

        ed_level_fig = px.pie(ed_level_counts,
                                names='EdLevel',
                                values='count',
                                labels={'EdLevel': 'Education Level', 'count': 'Count'}
                                )
        
        ed_level_fig.update_layout(
            showlegend=False
        )

        ed_level_plot = dcc.Graph(figure=ed_level_fig, className='plot w-100')

        ## Developer Status Distribution
        dev_status_counts = df_filer['MainBranch'].value_counts().reset_index()

        dev_status_fig = px.pie(dev_status_counts,
                                names='MainBranch',
                                values='count',
                                labels={'MainBranch': 'Dev Type', 'count': 'Count'})
        
        dev_status_fig.update_layout(showlegend = False)

        dev_status_plot = dcc.Graph(figure=dev_status_fig, className='plot w-100')

        ## Employment Distribution
        employ_counts = df_filer['Employment'].value_counts().reset_index()

        employ_counts_fig = px.pie(employ_counts,
                                    names='Employment',
                                    values='count',
                                    labels={'Employment': 'Employment Type', 'count': 'Count'})
        
        employ_counts_fig.update_layout(showlegend = False)            
    
        employ_counts_plot = dcc.Graph(figure=employ_counts_fig, className='plot w-100')
        
        # Return the plots
        return [
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("World Map"),
                        dbc.CardBody([
                            html.H2("Country Distribution", className='plot-title'),
                            country_plot
                        ], className='p-4')
                    ]), lg=12, xl=8, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Countries"),
                        dbc.CardBody([
                            html.H2("Top 10 Participating Countries"),
                            top10_countries_plot
                        ], className='p-4')
                    ]), lg=12, xl=4, className='mb-4'
                )
            ], align='center', justify='center'),
            dbc.Row([
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Education Level"),
                        dbc.CardBody([
                            html.H2("Education Level Distribution"),
                            ed_level_plot
                        ], className='p-4')
                    ]), lg=12, xl=4, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Developer Status"),
                        dbc.CardBody([
                            html.H2("Developer Status Distribution"),
                            dev_status_plot
                        ], className='p-4')
                    ]), lg=12, xl=4, className='mb-4'
                ),
                dbc.Col(
                    dbc.Card([
                        dbc.CardHeader("Employment Type"),
                        dbc.CardBody([
                            html.H2("Employment Type Distribution"),
                            employ_counts_plot
                        ], className='p-4')
                    ]), lg=12, xl=4, className='mb-4'
                )
            ], align='center', justify='center')
        ]
        

# Run the app
if __name__ == '__main__':
    app.run()




