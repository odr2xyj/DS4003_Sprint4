# %% [markdown]
# ### Sprint 4

# %%
# import dependencies
from dash import Dash, dcc, html, Input, Output, callback
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objs as go
import textwrap

# %%
# read in data
df = pd.read_csv('data.csv')
df.head()

# %%
# make small updates to data for graphs
columns_to_replace = ['depression', 'anxiety_disorder', 'lung_disease', 'high_blood_pressure', 'think_sleep_problem', 'otc_meds_aid', 'prescribed_meds_aid', 'alcohol_aid', 'eyemask_earplugs_aid', 'melatonin_aid' ]
df[columns_to_replace] = df[columns_to_replace].replace(["Don't Know", 'Refused'], np.nan)

# %%

# import stylesheet
stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# set up app and use stylesheet and colors
app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])
server = app.server
sunset_colors = ['#ffbf69', '#cbf3f0', '#2ec4b6']


# Define layout
app.layout = html.Div([

    # range slider for weight
    html.Div([
        html.Label('Weight Range:'),
        dcc.RangeSlider(
            id='weight-slider',
            min=int(df['weight'].min()),
            max=int(df['weight'].max()),
            step=1,
            value=[int(df['weight'].min()), int(df['weight'].max())],  
            marks={i: str(i) for i in range(int(df['weight'].min()), int(df['weight'].max()) + 1, 25)}
        )
    ], style={'width': '25%', 'display': 'inline-block'}),

    # range slider for age
    html.Div([
        html.Label('Age Range:'),
        dcc.RangeSlider(
            id='age-slider',
            min=int(df['age'].min()),
            max=int(df['age'].max()),
            step=1,
            value=[int(df['age'].min()), int(df['age'].max())],
            marks={i: str(i) for i in range(int(df['age'].min()), int(df['age'].max()) + 1, 10)}
        )
    ], style={'width': '25%', 'display': 'inline-block'}),

    # checkbox for gender
   html.Div([
        html.Label('Gender:'),
        dcc.Checklist(
            id='gender-checkbox',
            options=[{'label': gender, 'value': gender} for gender in df['gender'].unique()],
            value=df['gender'].unique(),
            inline=True
        )
    ], style={'width': '25%', 'display': 'inline-block'}),

    # range slider for sleep hours
    html.Div([
        html.Label('Sleep Hours Range:'),
        dcc.RangeSlider(
            id='sleep-slider',
            min=df['work_sleep_hours'].min(),
            max=df['work_sleep_hours'].max(),
            step=0.1,  # Adjust step to allow fractional values
            value=[df['work_sleep_hours'].min(), df['work_sleep_hours'].max()],
            marks={i: str(i) for i in range(int(df['work_sleep_hours'].min()), int(df['work_sleep_hours'].max()) + 1, 1)}
        )
    ], style={'width': '25%', 'display': 'inline-block'}),

    # line for text above charts
    html.Div([
        html.Div(id='characteristics-info'),
        html.Div(id='total-people-info')
    ], style={'width': '100%', 'text-align': 'center'}),
    
    # bar and pie graph
    html.Div([
        # bar graph (takes up 75% width)
        html.Div([
            dcc.Graph(id='health-graph', style={'height': '100vh', 'width': '100%', 'display': 'inline-block'})
        ], style={'width': '75%', 'display': 'inline-block'}),

        # pie chart (takes up 25% width)
        html.Div([
            dcc.Graph(id='sleep-disorder-pie', style={'height': '100vh', 'width': '100%', 'display': 'inline-block'})
        ], style={'width': '25%', 'display': 'inline-block'})

    ], style={'display': 'flex', 'flex-direction': 'row'})

]) 

# define callback
@app.callback(
    [Output('characteristics-info', 'children'),
     Output('total-people-info', 'children'),
     Output('health-graph', 'figure'),
     Output('sleep-disorder-pie', 'figure')],  
    [Input('weight-slider', 'value'),
     Input('age-slider', 'value'),
     Input('gender-checkbox', 'value'),
     Input('sleep-slider', 'value')]
)
def update_graph(weight, age, gender, sleep_hours):
    # make a filtered database that takes in user entries from sliders and drop downs
    df_filtered = df[(df['weight'] >= weight[0]) & (df['weight'] <= weight[1]) & 
                     (df['age'] >= age[0]) & (df['age'] <= age[1]) & 
                     (df['gender'].isin(gender)) & 
                     (df['work_sleep_hours'] >= sleep_hours[0]) & (df['work_sleep_hours'] <= sleep_hours[1])]
    
    # find total number of people in filtered data
    total_individuals = len(df_filtered)
    
    # calculate total percentage of "Yes" respondents to disorders in filtered data
    percentages_filtered = df_filtered[['depression', 'anxiety_disorder', 'lung_disease', 'high_blood_pressure']].apply(lambda col: col.value_counts(normalize=True).get('Yes', 0) * 100)
    
    # calculate total percentage of "Yes" respondents to disorders in filtered data
    percentages_total = df[['depression', 'anxiety_disorder', 'lung_disease', 'high_blood_pressure']].apply(lambda col: col.value_counts(normalize=True).get('Yes', 0) * 100)
    
    # create bar graph
    health_graph = go.Figure(data=[
        go.Bar(name='Filtered', 
               x=percentages_filtered.index, 
               y=percentages_filtered, 
               marker_color= '#B18FCF'),
        go.Bar(name='Total', 
               x=percentages_total.index, 
               y=percentages_total, 
               marker_color='#8AB6D6')
    ])
    
    # update layout for the bar graph
    health_graph.update_layout(
        title='Percentage of People with Health Disorders',
        xaxis_title='Condition',
        yaxis_title='Percentage of People (%)',
        barmode='group',
        width=900,
        height=600
    )

    # create pie chart with percentages of people who think they have a sleep problem 
    sleep_disorder_pie = px.pie(
        names=['Yes', 'No', 'Maybe'],
        values=[
            (df_filtered['think_sleep_problem'].value_counts(normalize=True).get('Yes', 0)) * 100,
            (df_filtered['think_sleep_problem'].value_counts(normalize=True).get('No', 0)) * 100,
            (df_filtered['think_sleep_problem'].value_counts(normalize=True).get('Maybe', 0)) * 100
        ],
        color_discrete_sequence=sunset_colors,
        width=300,
        height=300
    )

    # wrap title bc was too big before
    wrapped_pie_title = "<br>".join(textwrap.wrap('Percentage of People Who Think They Have a Sleep Disorder', width=30))
    sleep_disorder_pie.update_layout(
        title=wrapped_pie_title,  
        title_font=dict(size=12)  # set title font size
    )

    characteristics_info = f"Number of people with your characteristics: {total_individuals}"
    total_people_info = f"Total number of people: {len(df)}"
    
    # retuns parts
    return characteristics_info, total_people_info, health_graph, sleep_disorder_pie


# run the app
if __name__ == "__main__":
    app.run_server(debug=True)

# %%
