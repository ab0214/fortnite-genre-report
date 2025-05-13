# -*- coding: utf-8 -*-
"""
Created on Wed Apr  2 14:42:03 2025

@author: Mikko
"""

import os
import time
from selenium import webdriver
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
import csv

html_file = "genres.html"                       # Local cache of the webpage
url = 'https://fortnite.gg/player-count?genres' # URL of the actual webpage
output_dir = "output"                           # Where outputs will be saved

# Download and save web page.
# Unless: If already downloaded and file is <1hr old, then use existing file.
if (os.path.exists(html_file) and
        (time.time() - os.path.getmtime(html_file) < 3600)):
    with open(html_file, "r", encoding="utf-8") as f:
        page_source = f.read()
# Else actually download and save the web page.
else:
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(5)
    page_source = driver.page_source
    driver.quit()
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(page_source)

# Create timestamp for filenames and plot title.
modified_time = time.localtime(os.path.getmtime(html_file))
timestamp = time.strftime("%d.%m.%Y %H.%M", modified_time)

# Extract data from saved html file.
data = []
soup = BeautifulSoup(page_source, 'html.parser')
for row in soup.find_all('a', class_='row'):
    genre_div = row.find('div', class_='column-1')
    genre_div.find('div', class_='rank').extract()
    genre = genre_div.text.strip()
    maps = row.find('div', class_='peak').text.strip().split()[0]
    players = row.find('div', class_='ccu').text.strip().split()[0]
    data.append([
        genre,
        int(maps.replace(',', '')),
        int(players.replace(',', ''))
    ])

# Keep only top 50 categories for the plot.
filtered_data = data[:50]

# Separate into lists for plotting.
genres = [row[0] for row in filtered_data]
maps = [row[1] for row in filtered_data]
players = [row[2] for row in filtered_data]

# Create figure, subplots, axes.
fig, ax1 = plt.subplots(figsize=(12, 6))

# Create bar plot for maps.
ax1.bar(genres, maps, color='navy', label='Maps')

# Create a second y-axis for the line plot.
ax2 = ax1.twinx()

# Create a line plot for players.
ax2.plot(genres, players, color='red', label='Players Now')

# Labels and title.
ax1.set_xlabel('Genre')
ax1.set_ylabel('Maps')
ax2.set_ylabel('Players Now')

# Rotate x-axis labels so they fit.
for tick in ax1.get_xticklabels():
    tick.set_rotation(90)

# Title and layout adjustments.
plt.title(f'Map Count vs Player Count, Top 50 Genres, {timestamp}')
plt.tight_layout()

# Show and save plot as PNG.
os.makedirs(output_dir, exist_ok=True)
plot_filename = os.path.join(output_dir,
                             f'fortnite_player_count_{timestamp}.png')
plt.savefig(plot_filename, bbox_inches='tight', dpi=300)
plt.show()

# Save the raw data as CSV.
csv_filename = os.path.join(output_dir,
                            f'fortnite_player_count_{timestamp}.csv')
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Genre', 'Maps', 'Players Now'])
    for row in data:
        writer.writerow([row[0], row[1], row[2]])
