import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from plot import plot_pitch

df = pd.read_csv('data/AppData.gz', encoding='utf-8-sig')
df_fil = df.copy()
df_fil['isGoal'] = df_fil['isGoal'].apply(abs)

st.title("All About GameStates")

st.text("An app for finding Understat player by player shot data based on their shooting\nand finishing performance in different gamestates")
st.caption("Made by Shreyas Khatri. Twitter: @khatri_shreyas", unsafe_allow_html=False)

# WIDGETS SIDEBAR
st.sidebar.header("PLAYER INPUTS")
player_id = st.sidebar.number_input("Input Understat Player ID:", 
    format='%d',
    value = 2097
)
start_year, end_year = st.sidebar.select_slider(
     "Select Range of Seasons:",
     options=[x for x in range(2014, 2021)],
     value=(2014,2020)
)
filter_gs = st.sidebar.multiselect(
    "Filter for Game States:",
    options = df['Filter Game_State'].unique().tolist(),
    default = df['Filter Game_State'].unique().tolist()
)
player_col = st.sidebar.color_picker('Pick A Color', '#EA2304')
theme = st.sidebar.radio(
     "Visualisation Theme",
     ('dark', 'light')
)
only_goals = st.sidebar.checkbox('Show Only Goals')
add_pens = st.sidebar.checkbox('Keep Penalties')
only_changed_gs = st.sidebar.checkbox('Show Only Game State Altering Moments')

# FILTER DF
df_fil = df_fil[df_fil['Player ID']==player_id]
df_fil = df_fil[df_fil['Season'].between(start_year, end_year)]
df_fil = df_fil[df_fil['Filter Game_State'].isin(filter_gs)]
if only_goals:
    df_fil = df_fil[df_fil['Shot Result']=='Goal']
if not add_pens:
    df_fil = df_fil[df_fil['Situation']!='Penalty']
if only_changed_gs:
    df_fil = df_fil[df_fil['Changed Game State']==True]

def find_distance(x, y):
    return np.sqrt(np.sum(np.square(np.array([100, 50])-np.array([x*100, y*100]))))
# GROUPBY DF
def generate_gb_df():
    df_gb = df_fil[['Player ID','x','y', 'Shot xG','isGoal','Filter Game_State']].groupby("Filter Game_State").agg(['sum', 'count'])
    df_gb['Distance'] = df_gb.apply(lambda x: find_distance(x['x']['sum']/x['x']['count'], x['y']['sum']/x['y']['count']), axis=1)
    df_gb = df_gb.drop([('Player ID',   'sum'), (  'Shot xG', 'count'), (   'isGoal', 'count'),
                    (   'x', 'count'), (   'x', 'sum'), (   'y', 'count'), (   'y', 'sum')], axis=1)
    df_gb.columns = ['Total Shots', 'Total xG', 'Total Goals', 'Distance From Goal']
    df_gb['xG Overperformance'] = df_gb['Total Goals'] - df_gb['Total xG']
    df_gb['xG O/P per Shot'] = df_gb['xG Overperformance']/df_gb['Total Shots']
    return df_gb


def convert_df(df):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode('utf-8-sig')

# INTERFACE
if len(df_fil) > 0:
    st.header("\n\nPlayer: {}".format(df_fil['Player'].unique()[0]))
    st.subheader("\nPLAYER SHOT BY GAMESTATE COMPARISON")
    st.table(generate_gb_df())
else:
    st.error("Sorry no entries with these inputs, please change your inputs")
    
if st.button('Click For Visualisation Generation'):
    st.header("PLAYER SHOT DATAFRAME")
    st.dataframe(df_fil.drop(['x','y', 'h_a', 'isGoal', 'Filter Game_State'], axis=1).reset_index(drop=True), width = 2000, height=250)
    df_fil_save = convert_df(df_fil)
    
    st.download_button(
        label="Download Shot DataFrame as CSV",
        data=df_fil_save,
        file_name='PlayerShots.csv',
        mime='text/csv',
    )

    theme_dict = {'light':'white', 'dark':'black'}
    st.header("\nPLAYER SHOT MAP")
    fig, ax = plot_pitch(df_fil, theme=theme, player_col=player_col)
    plt.savefig('static/PlayerShots.png', dpi=300, facecolor=theme_dict[theme])
    st.pyplot(fig)
    with open("static/PlayerShots.png", "rb") as file:
        btn = st.download_button(
            label="Download image",
            data=file,
            file_name="PlayerShots.png",
            mime="image/png"
           )



# GUIDE AND CREDITS
st.markdown("""
    ### GUIDE TO THE WIDGET ELEMENTS

    1. Player ID - Player ID for player on Understat.com(https://www.understat.com)
    2. Range Of Season - Filter for seasons of relevance
    3. Filter Game State - Shots during a particular type (or types) of game state
    4. Show Only Goals - Filter for only goals
    5. Keep Penalties - Do you want to keep penalties or not?
    6. Game State Altering Moments - Show only those goals which altered the game state
    7. Pick A Colour - Choose colour for goal scatter points
    8. Visualisation Theme - Choose between light and dark themed templates
""")

hide_streamlit_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True) 