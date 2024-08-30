import seaborn as sns

# Define a custom colour palette with #f2634c as the primary colour
palette = [
    '#f2634c', # Primary colour
    '#3a3a3a', # Dark grey
    '#b0b0b0', # Light grey
    '#e0e0e0', # Very light grey
    '#0091d5', # Complementary blue
    '#7a7a7a', # Medium grey
    '#6dbd45', # Complementary green
    '#f5c6cb', # Soft pink
    '#c9d6e3', # Pale blue
    '#a9b7c6', # Soft steel blue
    '#f4f4f4'  # Near white
]

red_palette15 = sns.color_palette("Reds", n_colors=15).as_hex()[::-1]
red_palette5 = sns.color_palette("Reds", n_colors=5).as_hex()[::-1]
red_palette3 = sns.color_palette("Reds", n_colors=3).as_hex()[::-1]


# Set the Seaborn theme with a sleek and professional style
sns.set_theme(style="whitegrid", palette=palette, rc={
    'axes.facecolor': 'white',
    'axes.edgecolor': 'black',
    'axes.labelsize': 'large',
    'xtick.labelsize': 'medium',
    'ytick.labelsize': 'medium',
    'grid.alpha': 0.3, # Less intrusive gridlines
    'grid.linestyle': '--',
    'legend.frameon': True,
    'legend.loc': 'upper left', # Legend outside the plot
    'legend.borderpad': 1,
    'legend.labelspacing': 1,
    'legend.handlelength': 2.5,
    'legend.handletextpad': 1,
    'figure.figsize': (10, 6) # Wider figure size
})