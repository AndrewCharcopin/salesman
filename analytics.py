import pandas as pd
import seaborn as sns

sns.set(style='darkgrid')
# df_total = pd.read_csv("./total_distance.csv", header=1, names=['generation', 'total'])
df_shortest = pd.read_csv("./shortest.csv", header=1, names=['generation', 'shortest'])

shortest_plot = sns.lineplot(x="generation", y="shortest", data=df_shortest)
# total_plot = sns.lineplot(x="generation", y="total", data=df_total)
shortest_fig = shortest_plot.get_figure()
# total_fig = total_plot.get_figure()
shortest_fig.savefig("shortest_plot.png", bbox_inches='tight')
# total_fig.savefig("total_plot.png", bbox_inches='tight')
