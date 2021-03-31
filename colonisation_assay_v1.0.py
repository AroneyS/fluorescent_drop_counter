# Import modules
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Settings
#plt.rcParams['patch.force_edgecolor'] = True

# Import data
input_directory = '/Users/aroney/OneDrive/PhD/Experiments/Colonisation Assay/2019-03-19 Z1 wildtype/'
df = pd.read_csv(input_directory + 'avg_counts.csv', index_col=0)
metadata = pd.read_csv(input_directory + 'metadata.csv')
#media_letters = pd.read_csv(input_directory + 'media_letters.csv', index_col=0)
#strain_letters = pd.read_csv(input_directory + 'strain_letters.csv', index_col=0)


# Functions
def box_plotting(data, method, plot_name, context, n):
    show = 1
    save = 1
    verbose = False

    data = data[data['type'] == method]
    if method == 'bulk':
        y_label = 'Bacteria (counts / tube)'
    else:
        y_label = 'Bacteria (counts / g root)'

    plt.figure(n)
    sns.set_style('ticks', {'legend.frameon': True, 'axes.grid': True})
    sns.set_context(context)
    # Paired: 01 blue, 23 green, 45 red, 67 orange, 89 purple, 10 yellow, 11 brown
    basecolours = sns.color_palette('Paired', n_colors=12)
    colours = [basecolours[10], basecolours[1]]
    order = ['sYFP', 'gusA']
    fig = sns.boxplot(x='dpi', y='count', hue='fluorescence', data=data,
                      hue_order=order, palette=colours, fliersize=0)
    fig = sns.swarmplot(x='dpi', y='count', hue='fluorescence', data=data,
                        hue_order=order, palette=colours, linewidth=1, edgecolor='gray', dodge=True)
    plt.setp(fig, xlabel='Days post inoculation', ylabel=y_label)
    fig.set(yscale="log")

    # Remove swarm legend entries from legend
    handles, labels = fig.get_legend_handles_labels()
    plt.legend(handles[0:2], labels[0:2])

    '''
    # Add significance letters to plot
    if verbose:
        print(letters)

    columns = list(pd.unique(data[[categories]].values.ravel('K')))
    rows = list(pd.unique(data[[types]].values.ravel('K')))
    splits = len(rows)

    # ws = 1.25 for 5 hues, 1 for 4 hues
    if splits == 5:
        ws = 1.25
    elif splits == 4:
        ws = 1
    else:
        ws = 1
        # ??? Even/Odd difference??

    # Find mean and sd for height calculation
    stats = (df.groupby([categories, types])['Diameter'].agg(['mean', 'std'])).reset_index()
    stats['comb'] = stats.fillna(0)['mean'] + stats.fillna(0)['std'] + 2
    stats = stats.pivot(index=types, columns=categories, values='comb')
    if verbose:
        print(stats)

    # Add letters
    for i, col in enumerate(columns):
        for j, row in enumerate(rows):
            position = i - (1/(splits+ws))*((splits - 1)/2-j)
            plt.text(position, stats.loc[row, col], letters.loc[row, col], ha='center', va='center', color='k')
    '''

    # Save/Show plots
    if save == 1:
        plt.savefig(plot_name + '.png')
    if show == 1:
        plt.show()
    return

def meta_plotting(data, plot_name, context, n):
    show = 1
    save = 1

    plt.figure(n)
    sns.set_context(context)
    colours = sns.color_palette('Greens', n_colors=4)
    fig = sns.boxplot(x='dpi', y='weight', palette=colours, data=data)
    fig = sns.swarmplot(x='dpi', y='weight', palette=colours, linewidth=1, edgecolor='gray', data=data)
    plt.setp(fig, xlabel='Days post inoculation', ylabel='Plant root weight (g)')

    # Save/Show plots
    if save == 1:
        plt.savefig(plot_name + '.png')
    if show == 1:
        plt.show()
    return

# Main
# box_plotting(df, type, plot_name, context, n)

box_plotting(df, 'bulk', 'plot_bulk_book', 'notebook', 0)
box_plotting(df, 'bulk', 'plot_bulk_talk', 'poster', 1)
box_plotting(df, 'grind', 'plot_grind_book', 'notebook', 2)
box_plotting(df, 'grind', 'plot_grind_talk', 'poster', 3)

weights = metadata[metadata['strain1'] != "water"]
meta_plotting(weights, 'plot_plant_weights_book', 'notebook', 4)
meta_plotting(weights, 'plot_plant_weights_talk', 'poster', 5)


print('Successfully completed')
