#!/usr/bin/env python
# coding: utf-8

# # 🎬 Netflix Content Analysis
# ### End-to-End Data Analytics Project
# **Tools Used:** Python &nbsp;|&nbsp; PostgreSQL &nbsp;|&nbsp; Power BI
# 
# ---

# ## 📦 Step 1 — Import Libraries

# In[1]:


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# ── Display settings ──────────────────────────────────
pd.set_option('display.max_columns',  20)
pd.set_option('display.width',        120)
pd.set_option('display.max_colwidth', 28)

# ── Netflix chart theme ───────────────────────────────
NETFLIX_RED  = '#E50914'
NETFLIX_DARK = '#221F1F'
NETFLIX_GRAY = '#6D6D6E'

plt.rcParams.update({
    'figure.facecolor'  : 'white',
    'axes.facecolor'    : '#FAFAFA',
    'axes.edgecolor'    : '#DDDDDD',
    'axes.grid'         : True,
    'grid.color'        : '#EEEEEE',
    'grid.linewidth'    : 0.8,
    'axes.spines.top'   : False,
    'axes.spines.right' : False,
    'font.family'       : 'DejaVu Sans',
    'axes.titlesize'    : 14,
    'axes.titleweight'  : 'bold',
    'axes.titlepad'     : 14,
    'axes.labelsize'    : 11,
    'xtick.labelsize'   : 10,
    'ytick.labelsize'   : 10,
    'figure.dpi'        : 110,
})

get_ipython().run_line_magic('matplotlib', 'inline')
print("✅ Libraries imported successfully!")


# ## 📂 Step 2 — Load Dataset

# In[2]:


df = pd.read_excel(r"C:\Users\Bhavyansh Nandwana\Desktop\Funnel Analysis Project\netflix_titles.xlsx")
print(f"✅ Dataset loaded  →  {df.shape[0]:,} rows  ×  {df.shape[1]} columns")


# ## 🔍 Step 3 — Initial Exploration

# ### 3.1 — First 5 Rows

# In[3]:


df[["show_id","type","title","director","country","release_year","rating","duration"]].head()


# ### 3.2 — Dataset Info

# In[4]:


df.info()


# ### 3.3 — Statistical Summary

# In[5]:


df.describe()


# ### 3.4 — Missing Values

# In[6]:


null_df = df.isnull().sum().reset_index()
null_df.columns = ['Column', 'Null Count']
null_df['% Missing'] = (null_df['Null Count'] / len(df) * 100).round(2)
null_df.style.background_gradient(subset=['Null Count'], cmap='Reds').format({'% Missing': '{:.2f}%'})


# ## 🧹 Step 4 — Data Cleaning

# In[7]:


# Fill missing director & cast with 'Unknown'
df['director'] = df['director'].fillna('Unknown')
df['cast']     = df['cast'].fillna('Unknown')

# Fill missing country & rating with mode
df['country'] = df['country'].fillna(df['country'].mode()[0])
df['rating']  = df['rating'].fillna(df['rating'].mode()[0])

# Drop rows where date_added or duration is null (only ~13 rows)
df = df.dropna(subset=['date_added', 'duration'])

# Strip whitespace
df['date_added'] = df['date_added'].str.strip()
df['country']    = df['country'].str.strip()

print("✅ Cleaning complete!")
print(f"   Null values remaining : {df.isnull().sum().sum()}")
print(f"   Rows after cleaning   : {len(df):,}")


# ## ⚙️ Step 5 — Feature Engineering

# In[8]:


df['date_added']      = pd.to_datetime(df['date_added'], format='%B %d, %Y', errors='coerce')
df['year_added']      = df['date_added'].dt.year
df['month_added']     = df['date_added'].dt.month
df['month_name']      = df['date_added'].dt.strftime('%b')
df['primary_country'] = df['country'].apply(lambda x: x.split(',')[0].strip())
df['primary_genre']   = df['listed_in'].apply(lambda x: x.split(',')[0].strip())
df['duration_value']  = df['duration'].str.extract(r'(\d+)').astype(float)
df['duration_unit']   = df['duration'].str.extract(r'([a-zA-Z ]+)').iloc[:, 0].str.strip()

print("✅ Feature Engineering complete!")
new_cols = ['year_added','month_added','month_name','primary_country',
            'primary_genre','duration_value','duration_unit']
df[new_cols].head(8)


# ## 📊 Step 6 — Exploratory Data Analysis (Visualizations)

# ### 6.1 — Movies vs TV Shows

# In[9]:


fig, ax = plt.subplots(figsize=(6, 6))
type_counts = df['type'].value_counts()
wedges, texts, autotexts = ax.pie(
    type_counts,
    labels=type_counts.index,
    autopct='%1.1f%%',
    colors=[NETFLIX_RED, NETFLIX_GRAY],
    startangle=90,
    wedgeprops={'edgecolor': 'white', 'linewidth': 3},
    textprops={'fontsize': 13, 'fontweight': 'bold'},
    pctdistance=0.75,
)
for at in autotexts:
    at.set_color('white')
    at.set_fontsize(13)
centre = plt.Circle((0, 0), 0.55, fc='white')
ax.add_patch(centre)
ax.text(0, 0, f"{len(df):,}\nTitles", ha='center', va='center',
        fontsize=13, fontweight='bold', color=NETFLIX_DARK)
ax.set_title('🎬  Movies vs TV Shows on Netflix', fontsize=15, fontweight='bold', pad=18)
plt.tight_layout()
plt.show()


# ### 6.2 — Top 10 Countries by Content

# In[10]:


fig, ax = plt.subplots(figsize=(10, 5))
top_countries = df['primary_country'].value_counts().head(10)
colors = [NETFLIX_RED] + [NETFLIX_GRAY] * 9
bars = ax.barh(top_countries.index[::-1], top_countries.values[::-1],
               color=colors[::-1], edgecolor='white', height=0.65)
for bar in bars:
    ax.text(bar.get_width() + 25, bar.get_y() + bar.get_height()/2,
            f'{int(bar.get_width()):,}', va='center', fontsize=9, color='#333333')
ax.set_title('🌍  Top 10 Countries by Number of Titles', pad=14)
ax.set_xlabel('Number of Titles')
ax.set_xlim(0, top_countries.max() * 1.18)
plt.tight_layout()
plt.show()


# ### 6.3 — Content Added Per Year

# In[11]:


fig, ax = plt.subplots(figsize=(11, 5))
yearly = (df[df['year_added'] >= 2010]
          .groupby(['year_added', 'type']).size().unstack(fill_value=0))
yearly.plot(kind='bar', ax=ax, color=[NETFLIX_RED, NETFLIX_GRAY],
            edgecolor='white', width=0.72)
ax.set_title('📅  Content Added to Netflix Per Year (2010–2021)', pad=14)
ax.set_xlabel('Year')
ax.set_ylabel('Number of Titles')
ax.legend(title='Type', fontsize=10, framealpha=0.6, loc='upper left')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.show()


# ### 6.4 — Top 10 Genres

# In[12]:


fig, ax = plt.subplots(figsize=(10, 5))
top_genres = df['primary_genre'].value_counts().head(10)
bar_colors = [NETFLIX_RED if i == 0 else '#C0392B' if i < 3 else NETFLIX_GRAY for i in range(10)]
bars = ax.bar(top_genres.index, top_genres.values, color=bar_colors, edgecolor='white', width=0.7)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f'{int(bar.get_height()):,}', ha='center', fontsize=9, color='#333333')
ax.set_title('🎭  Top 10 Content Genres on Netflix', pad=14)
ax.set_ylabel('Number of Titles')
ax.set_xlabel('Genre')
plt.xticks(rotation=30, ha='right')
plt.tight_layout()
plt.show()


# ### 6.5 — Rating Distribution

# In[13]:


fig, ax = plt.subplots(figsize=(10, 5))
rating_counts = df['rating'].value_counts().head(10)
bar_colors = [NETFLIX_RED if i == 0 else '#C0392B' if i < 3 else NETFLIX_GRAY for i in range(len(rating_counts))]
bars = ax.bar(rating_counts.index, rating_counts.values, color=bar_colors, edgecolor='white', width=0.65)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 10,
            f'{int(bar.get_height()):,}', ha='center', fontsize=9, color='#333333')
ax.set_title('🔞  Content Rating Distribution', pad=14)
ax.set_ylabel('Number of Titles')
ax.set_xlabel('Rating')
plt.tight_layout()
plt.show()


# ### 6.6 — Content Added by Month

# In[14]:


month_order = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
monthly = df.groupby('month_name').size().reindex(month_order, fill_value=0)
fig, ax = plt.subplots(figsize=(11, 4.5))
bars = ax.bar(monthly.index, monthly.values,
              color=[NETFLIX_RED if v == monthly.max() else NETFLIX_GRAY for v in monthly.values],
              edgecolor='white', width=0.7)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f'{int(bar.get_height()):,}', ha='center', fontsize=8.5, color='#333333')
ax.set_title('📆  Content Added by Month  (Peak month in red)', pad=14)
ax.set_ylabel('Number of Titles')
ax.set_xlabel('Month')
plt.tight_layout()
plt.show()


# ### 6.7 — Movie Duration Distribution

# In[15]:


movies_df = df[df['type'] == 'Movie']
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.hist(movies_df['duration_value'].dropna(), bins=35, color=NETFLIX_RED, edgecolor='white', alpha=0.92)
avg = movies_df['duration_value'].mean()
ax.axvline(avg, color=NETFLIX_DARK, linewidth=2, linestyle='--', label=f'Avg: {avg:.0f} min')
ax.legend(fontsize=11)
ax.set_title('⏱️  Movie Duration Distribution (Minutes)', pad=14)
ax.set_xlabel('Duration (Minutes)')
ax.set_ylabel('Number of Movies')
plt.tight_layout()
plt.show()


# ### 6.8 — TV Show Seasons Distribution

# In[16]:


tvshows_df = df[df['type'] == 'TV Show']
season_counts = tvshows_df['duration_value'].value_counts().sort_index().head(10)
fig, ax = plt.subplots(figsize=(9, 4.5))
bars = ax.bar(season_counts.index.astype(int).astype(str), season_counts.values,
              color=[NETFLIX_RED if i == 0 else NETFLIX_GRAY for i in range(len(season_counts))],
              edgecolor='white', width=0.65)
for bar in bars:
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 8,
            f'{int(bar.get_height()):,}', ha='center', fontsize=9, color='#333333')
ax.set_title('📺  TV Show — Seasons Distribution', pad=14)
ax.set_xlabel('Number of Seasons')
ax.set_ylabel('Number of Shows')
plt.tight_layout()
plt.show()


# ### 6.9 — Top 10 Directors

# In[17]:


fig, ax = plt.subplots(figsize=(10, 5))
top_dirs = df[df['director'] != 'Unknown']['director'].value_counts().head(10)
bars = ax.barh(top_dirs.index[::-1], top_dirs.values[::-1],
               color=[NETFLIX_RED] + [NETFLIX_GRAY] * 9, edgecolor='white', height=0.65)
for bar in bars:
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            f'{int(bar.get_width())}', va='center', fontsize=9, color='#333333')
ax.set_title('🎥  Top 10 Directors by Number of Titles', pad=14)
ax.set_xlabel('Number of Titles')
ax.set_xlim(0, top_dirs.max() * 1.2)
plt.tight_layout()
plt.show()


# ### 6.10 — Cumulative Content Growth

# In[18]:


cumulative = df[df['year_added'] >= 2010].groupby('year_added').size().cumsum()
fig, ax = plt.subplots(figsize=(10, 4.5))
ax.fill_between(cumulative.index, cumulative.values, alpha=0.15, color=NETFLIX_RED)
ax.plot(cumulative.index, cumulative.values,
        color=NETFLIX_RED, linewidth=3,
        marker='o', markersize=8,
        markerfacecolor='white', markeredgecolor=NETFLIX_RED, markeredgewidth=2.5)
for x, y in zip(cumulative.index, cumulative.values):
    ax.text(x, y + 100, f'{y:,}', ha='center', fontsize=8.5, color=NETFLIX_DARK)
ax.set_title('📈  Cumulative Content Growth on Netflix (2010–2021)', pad=14)
ax.set_xlabel('Year')
ax.set_ylabel('Total Titles')
ax.set_xticks(cumulative.index)
plt.tight_layout()
plt.show()


# ## 📋 Step 7 — Final Dataset Summary

# In[19]:


summary = {
    'Metric': ['Total Titles','Movies','TV Shows','Countries','Genres','Year Range','Total Columns'],
    'Value' : [f"{len(df):,}",
               f"{len(df[df['type']=='Movie']):,}",
               f"{len(df[df['type']=='TV Show']):,}",
               str(df['primary_country'].nunique()),
               str(df['primary_genre'].nunique()),
               f"{int(df['release_year'].min())} – {int(df['release_year'].max())}",
               str(len(df.columns))]
}
pd.DataFrame(summary).style.set_properties(**{
    'text-align': 'left',
    'font-size' : '13px',
}).hide(axis='index')


# ## 🗄️ Step 8 — Load Data into PostgreSQL

# In[20]:


df.to_csv("netflix_cleaned.csv", index=False)
print("✅ Cleaned file saved!")


# In[21]:


# pip install psycopg2-binary sqlalchemy openpyxl
from sqlalchemy import create_engine

username = "postgres"
password = "Bhavya_2004"    # 🔁 Replace with your PostgreSQL password
host     = "localhost"
port     = "5432"
database = "netflix_analysis" # Make sure this DB exists in pgAdmin

engine = create_engine(f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}")
df.to_sql("netflix", engine, if_exists="replace", index=False)

print("✅ Data loaded into table 'netflix' in database 'netflix_analysis'.")
print(f"   Total rows loaded : {len(df):,}")

