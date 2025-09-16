import streamlit as st
import json
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from matplotlib.colors import LinearSegmentedColormap
import arabic_reshaper
from bidi.algorithm import get_display
from app import data
# ----------------------------------------------------------------------------------------

fig, ax = plt.subplots(figsize=(14, 6))
plot = data.pivot_table(values='id', index='fclass', columns='label', aggfunc='count')

print(plot)
plot.plot(kind='bar', ax=ax, stacked=True)
ax.grid(linestyle='--', alpha=0.5)
ax.set_title("Type of road vs number of each crack type")
ax.set_xlabel("Road type")
ax.set_ylabel("Number of cracks")
st.pyplot(fig)
# ---------------------------------------------------------------------------------------
time_cracks = (
    data.groupby([pd.Grouper(key="timestamp", freq="h"), "label"])
    .size()
    .reset_index(name="count")
)

pivot_df = time_cracks.pivot(index="timestamp", columns="label", values="count").fillna(0)

fig1, ax1 = plt.subplots(figsize=(14, 6))
pivot_df.plot(
    kind="area",
    stacked=True,
    alpha=0.6,
    figsize=(14,6),
    ax=ax1
)
ax1.set_title("Number of Cracks Over Time (by Category)")
ax1.set_xlabel("Time")
ax1.set_ylabel("Number of Cracks")
ax1.grid(True, linestyle="--", alpha=0.7)
st.pyplot(fig1)
# -----------------------------------------------------------------------------------------------
colors = {'Alligator Crack': '#e74c3c', 'Potholes': '#f39c12', 'Transverse Crack': '#3498db', 'Longitudinal Crack': '#2ecc71'}
def format_arabic(text):
    if isinstance(text, str) and any('\u0600' <= c <= '\u06FF' for c in text):
        reshaped_text = arabic_reshaper.reshape(text)
        return get_display(reshaped_text)
    return text

road_data = []
df = data.to_dict(orient='records')
for feature in df:
    name = feature.get('name', 'Unnamed Road')
    label = feature.get('label', 'none')
    confidence = feature.get('confidence', 0.5)
    
   # damage calculator
    if label == 'Alligator Crack':
        damage_weight = 1.0
    elif label == 'Potholes':
        damage_weight = 1.5
    elif label == 'Transverse Crack':
        damage_weight = 0.7
    elif label == 'Longitudinal Crack':
        damage_weight = 0.8
    else:  #none
        damage_weight = 0
        
    damage_score = damage_weight * confidence
    road_data.append({'name': name, 'label': label, 'confidence': confidence, 'damage_score': damage_score})

df = pd.DataFrame(road_data)

road_damage = df.groupby('name').agg({
    'damage_score': 'sum',
    'label': 'count'  
}).rename(columns={'label': 'segment_count'}).reset_index()

top_10_damaged = road_damage.nlargest(10, 'damage_score')


top_10_damaged['display_name'] = top_10_damaged['name'].apply(format_arabic)


fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 8))  # Increased figure size
fig.suptitle('Top 10 Most Damaged Road' , fontsize=16, fontweight='bold')

#bar char for those top 10 
bars = ax1.barh(range(len(top_10_damaged)), top_10_damaged['damage_score'], 
                color=plt.cm.Reds(np.linspace(0.9,0.4, len(top_10_damaged))))
ax1.set_yticks(range(len(top_10_damaged)))
ax1.set_yticklabels(top_10_damaged['display_name'], fontname='Arial', fontsize=12)
ax1.set_xlabel('Damage Score' , fontsize=10)
ax1.set_title('Damage Score by Road' , fontsize=12, fontweight='bold')
ax1.grid(axis='x', linestyle='--', alpha=0.7)



for i, (score, count) in enumerate(zip(top_10_damaged['damage_score'], top_10_damaged['segment_count'])):
    ax1.text(score + 0.1, i, f'{score:.2f}\n({count} segments)', 
             va='center', fontsize=9, fontname='Arial')


damage_types = df[df['name'].isin(top_10_damaged['name'])]
damage_breakdown = pd.crosstab(damage_types['name'], damage_types['label'])


damage_breakdown = damage_breakdown.reindex(top_10_damaged['name'])


damage_breakdown_display = damage_breakdown.copy()
damage_breakdown_display.index = top_10_damaged['display_name']

bottom = np.zeros(len(damage_breakdown))


for damage_type in damage_breakdown.columns:
    counts = damage_breakdown[damage_type].values
    ax2.barh(range(len(damage_breakdown)), counts, left=bottom, 
             label=damage_type, color=colors.get(damage_type, 'gray'))
    bottom += counts

ax2.set_yticks(range(len(damage_breakdown_display)))
ax2.set_yticklabels(damage_breakdown_display.index, fontname='Arial', fontsize=10)
ax2.set_xlabel('Number of Segments', fontname='Arial', fontsize=10)
ax2.set_title('Damage Type Breakdown', fontname='Arial', fontsize=12, fontweight='bold')

ax2.legend(loc='upper right')
ax2.grid(axis='x', linestyle='--', alpha=0.7)

plt.tight_layout(rect=[0, 0, 1, 0.96])
st.pyplot(fig)