import plotly.graph_objects as go

# Generate dataset
import numpy as np
np.random.seed(1)

x0 = np.random.normal(2, 0.4, 400)
y0 = np.random.normal(2, 0.4, 400)
x1 = np.random.normal(3, 0.6, 600)
y1 = np.random.normal(6, 0.4, 400)
x2 = np.random.normal(4, 0.2, 200)
y2 = np.random.normal(4, 0.4, 200)


df = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_usa_states.csv')

# Create figure
fig = go.Figure()

# Add traces
fig.add_trace(
    go.Table(
    header=dict(values=list(smoothened_lv_df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[smoothened_lv_df.Datums, smoothened_lv_df.ApstiprinataCOVID19InfekcijaSkaits, smoothened_lv_df.TestuSkaits, smoothened_lv_df.New_Cases_7_Day_Mean],
               fill_color='lavender',
               align='left'),
               visible=True
               )
)



#Cases per 100k 7days
fig.add_trace(
    go.Table(
    header=dict(values=list(sim_lv7_df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[sim_lv7_df.Date,sim_lv7_df.R0_8,sim_lv7_df.R0_85,sim_lv7_df.R0_9,sim_lv7_df.R0_95,sim_lv7_df.R1_05,sim_lv7_df.R1_1,sim_lv7_df.R1_15,sim_lv7_df.R1_2],
               fill_color='lavender',
               align='left'),
               visible=False,
               )

)

#Cases per 100k 14days
fig.add_trace(
    go.Table(
    header=dict(values=list(sim_lv14_df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[sim_lv14_df.Date,sim_lv14_df.R0_8,sim_lv14_df.R0_85,sim_lv14_df.R0_9,sim_lv14_df.R0_95,sim_lv14_df.R1_05,sim_lv14_df.R1_1,sim_lv14_df.R1_15,sim_lv14_df.R1_2],
               fill_color='lavender',
               align='left'),
               visible=False,
               )
)

#Only new cases
fig.add_trace(
    go.Table(
    header=dict(values=list(sim_lv_new_df.columns),
                fill_color='paleturquoise',
                align='left'),
    cells=dict(values=[sim_lv_new_df.Date,sim_lv_new_df.R0_8,sim_lv_new_df.R0_85,sim_lv_new_df.R0_9,sim_lv_new_df.R0_95,sim_lv_new_df.R1_05,sim_lv_new_df.R1_1,sim_lv_new_df.R1_15,sim_lv_new_df.R1_2],
               fill_color='lavender',
               align='left'),
               visible=False,
               )

)

fig.update_layout(
    updatemenus=[
         dict(
            type = "buttons",
            direction = "left",
            buttons=list([
            dict(label="Past Data",
                 method="update",
                 args=[{"visible": [True, False,False,False]}]),
            dict(label="Simulated Data",
                 method="update",
                 args=[{"visible": [False, True, True, True]}])
            ]),
#            pad={"r": 10, "t": 10},
            showactive=True,
            x=0.01,
            xanchor="left",
            y=1.2,
            yanchor="top"
        ),
        dict(
            active=0,
            buttons=list([
                dict(
                    label='Cases per 100k 7days',
                    method='update',
                    args=[{"visible":[False,True,False,False]}]
                ),
                dict(
                    label='Cases per 100k 14days',
                    method="update",
                    args=[{"visible":[False,False,True,False]}]
                ),
                dict(
                    label='New cases (daily)',
                    method="update",
                    args=[{"visible":[False,False,False,True]}]
                )
            ]),
            x=1,
            xanchor="right",
            y=1.2,
            yanchor="top"
        )
    ]
)



fig.show()