import mplsoccer
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.patches as patches

import numpy as np

mpl.rcParams['font.family']= 'Century Gothic'
mpl.rcParams['font.size'] = 12
mpl.rcParams['font.weight'] = 'bold'
mpl.rcParams['legend.title_fontsize'] = 20
mpl.rcParams['legend.fontsize'] = 17

font_dirs = ['Century Gothic']
font_files = mpl.font_manager.findSystemFonts(fontpaths=font_dirs)
for font_file in font_files:
    mpl.font_manager.fontManager.addfont(font_file)

def dark_theme():
    mpl.rcParams['text.color'] = 'white'
    return 'white', 'black'

def light_theme():
    mpl.rcParams['text.color'] = 'black'
    return 'black', 'white'


def plot_pitch(df, theme = 'light', player_col='red'):
    if theme == 'light':
        point_color, bg_color = light_theme()
    elif theme == 'dark':
        point_color, bg_color = dark_theme()
    gold_col = '#ad993c'
    in_col = '#868686'


    fig, ax = plt.subplots()
    fig.set_facecolor(bg_color)
    pitch = mplsoccer.VerticalPitch(pitch_type='opta', pitch_color=bg_color,
                        linewidth=1.5, line_alpha=0.5, goal_alpha=0.5, half=True)
    pitch.draw(ax=ax)

    if len(df) == 0:
        return fig, ax

    # SCATTER POINTS
    goal_cond = df['Shot Result']=='Goal'
    pitch.scatter(df[~goal_cond]['x']*100, df[~goal_cond]['y']*100, c='none', ec=point_color, alpha=0.15, ax=ax)
    pitch.scatter(df[goal_cond]['x']*100, df[goal_cond]['y']*100, c='none', ec=player_col, hatch='////////', alpha=0.5, ax=ax)

    # INTERNAL DATA
    player = df['Player'].unique()[0]
    start_year = df['Season'].min()
    end_year = df['Season'].max()
    avg_x, avg_y = df['x'].mean()*100, df['y'].mean()*100
    total_goals = sum(goal_cond)
    total_shots = len(df)
    total_xg = df['Shot xG'].sum()
    avg_distance_to_goal = np.sqrt(np.sum(np.square(np.array([100, 50])-
                                                    np.array([avg_x, avg_y]))))
    
    # DISTANCE
    circle = patches.Circle((50, 100), avg_distance_to_goal, ec=point_color, fc='None', alpha=0.5, ls=':', lw=1.5)
    ax.add_patch(circle)
    ax.annotate("", xy=(50-avg_distance_to_goal, 102.5), xycoords='data', 
                xytext=(50, 102.5), textcoords='data',
                size=10, arrowprops=dict(arrowstyle="-|>",fc='none', ls='--', ec=player_col))
    ax.text(49-avg_distance_to_goal, 102.5, "{:.2f}m".format(avg_distance_to_goal), size=11.5, 
            ha='left', va='center',c=in_col)
    ax.text(51, 102.5, "Avg distance", size=8, ha='right', va='center')

    # TEXT
    ax.scatter(np.linspace(90,10,5), [56]*5, c=bg_color, ec=point_color, marker='h', s=2000, ls='--', alpha=0.5)
    
    ax.text(90, 56,'{}'.format(total_shots), size=13, color=player_col, ha='center', va='center', family='Century Gothic')
    ax.text(70, 56,'{}'.format(total_goals), size=13, color=player_col, ha='center', va='center', family='Century Gothic')
    ax.text(50, 56,'{:.2f}'.format((total_goals-total_xg)/total_shots), size=13, color=player_col, 
        ha='center', va='center', family='Century Gothic')
    ax.text(30, 56,'{:.2f}'.format(total_xg/total_shots), size=13, color=player_col, 
        ha='center', va='center', family='Century Gothic')
    ax.text(10, 56,'{}'.format(sum(df['Changed Game State']==True)), size=13, color=player_col, 
        ha='center', va='center', family='Century Gothic')
    
    
    ax.text(90, 50,'Total\nShots', size=8, color=in_col, ha='center', va='top')
    ax.text(70, 50,'Total\nGoals', size=8, color=in_col, ha='center', va='top')
    ax.text(50, 50,'Finishing\nOverperformance\nper Shot', size=8, color=in_col, ha='center', va='top')
    ax.text(30, 50,'xG\nper Shot', size=8, color=in_col, ha='center', va='top')
    ax.text(10, 50,'Number of\nGame-State\nAltering Goals', size=8, color=in_col, ha='center', va='top')

    # ADD TITLES
    ax.set_title(f'{player.upper()}', color=gold_col, loc='left', 
        pad=25, weight='heavy', size=22)
    ax.text(103, 104.5,  f'{start_year}-{end_year+1} | League games only', size=13)
    fig.text(0.15, 0.05, 'Made using All About GameStates App. By @khatri_shreyas.', size=7)

    return fig, ax