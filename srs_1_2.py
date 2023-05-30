# Импортируем необходимые библиотеки
import dash
from dash import dash_table
from dash import dcc
from dash import html
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import json
from urllib.request import urlopen

us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}

periodicity = {"Smoke everyday": "Курят ежедневно", "Smoke some days": "Курят иногда",
               "Former smoker": "Курили в прошлом", "Never smoked": "Никогда не курили", "once": "Курили/курят",
               "now": "Курят сейчас"}

# Считываем данные из .csv файла
df = pd.read_csv('smoke.csv', dtype={"State": "str"})
df["codes"] = df['State'].map(us_state_abbrev)
df["once"] = df["Smoke everyday"] + df["Smoke some days"] + df["Former smoker"]
df["now"] = df["Smoke everyday"] + df["Smoke some days"]

# Определяем значения для отображения на карте
fig = px.choropleth(df,
                    locations='codes',
                    locationmode='USA-states',
                    scope='usa',
                    color="Smoke everyday",
                    color_continuous_scale='YlOrRd',
                    range_color=(0, 100),
                    labels={'Smoke everyday': 'Курят ежедневно'}
                    )

# Обновляем макет карты, добавляя заголовок и определяя размер
fig.update_layout(title_text='Частота курения жителей США',
                  geo_scope='usa',
                  margin=dict(l=10, r=10, b=10, t=50, pad=0),
                  height=512,
                  )
# Зададим описание и графические элементы нашего дашборда
app = dash.Dash(__name__)

# Задаем основной макет дашборда
app.layout = html.Div(
    [

        html.H1("Дашборд. Как часто курят жители США"),
        html.Div(id="output-clientside"),

        html.Br(), 

        html.Label([
            "Выберите частоту: ",
            dcc.Dropdown(
                id='period',
                options=[{'value': s, 'label': periodicity[s]} for s in periodicity.keys()],
                value='Smoke everyday',
                clearable=False
            )
        ]),

        html.Br(),

        dcc.Graph(
            id="choropleth",
            figure=fig
        ),

        html.Br(),

        # Добавляем элементы управления
        html.Label([
            "Выберите состояние: ",
            dcc.Dropdown(
                id='state-dropdown',
                options=[{'value': s, 'label': s} for s in df['State'].unique()],
                value='Alabama',
                clearable=False
            )
        ]),

        html.Br(),

        html.Div([
            dcc.Graph(
                id='daily-smoker',
            )
        ]),
    ]
)


# Обработка выбора в выпадающем списке
@app.callback(
    dash.dependencies.Output('daily-smoker', 'figure'),
    [dash.dependencies.Input('state-dropdown', 'value')])
def update_graph(selected_state):
    # Определяем данные для создания графика
    filtered_df = df[df.State == selected_state]
    data = [
        go.Bar(x=filtered_df['Year'], y=filtered_df['Smoke everyday'], name='Ежедневно'),
        go.Bar(x=filtered_df['Year'], y=filtered_df['Smoke some days'], name='Иногда'),
        go.Bar(x=filtered_df['Year'], y=filtered_df['Former smoker'], name='В прошлом'),
        go.Bar(x=filtered_df['Year'], y=filtered_df['Never smoked'], name='Никогда'),
    ]
    layout_bar = go.Layout(
        barmode='stack',
        title=f"Частота курения в штате {selected_state} по годам"
    )
    return {'data': data, 'layout': layout_bar}


@app.callback(
    dash.dependencies.Output('choropleth', 'figure'),
    [dash.dependencies.Input('period', 'value')])
def update_map(per):
    return px.choropleth(df,
                         locations='codes',
                         locationmode='USA-states',
                         scope='usa',
                         color=per,
                         color_continuous_scale='YlOrRd',
                         range_color=(0, 100),
                         labels=periodicity
                         )


if __name__ == '__main__':
    app.run_server(debug=True)
