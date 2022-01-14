#!/usr/bin/env python3
"""
Test xarray, pandas, pint, seaborn integration.
"""
import numpy as np
import pandas as pd
import pint
import seaborn as sns
import xarray as xr

# %%
import proplot as pplt

# ## Pint quantities
#
# Ensure auto-formatting and column iteration both work.

pplt.rc.unitformat = '~H'
ureg = pint.UnitRegistry()
fig, ax = pplt.subplots()
ax.plot(
    np.arange(10),
    np.random.rand(10) * ureg.km,
    'C0',
    np.arange(10),
    np.random.rand(10) * ureg.m * 1e2,
    'C1'
)

# ## Data keyword
#
# Make sure `data` keywords work properly.

N = 10
M = 20
ds = xr.Dataset(
    {'z': (('x', 'y'), np.random.rand(N, M))},
    coords={
        'x': ('x', np.arange(N) * 10, {'long_name': 'longitude'}),
        'y': ('y', np.arange(M) * 5, {'long_name': 'latitude'})
    }
)
fig, ax = pplt.subplots()
# ax.pcolor('z', data=ds, order='F')
ax.pcolor(z='z', data=ds, transpose=True)
ax.format(xformatter='deglat', yformatter='deglon')


# ## Remember guide labels
#
# Preserve metadata when passing mappables and handles to colorbar and legend
# subsequently.

fig, ax = pplt.subplots()
df = pd.DataFrame(np.random.rand(5, 5))
df.name = 'variable'
m = ax.pcolor(df)
ax.colorbar(m)

fig, ax = pplt.subplots()
for k in ('foo', 'bar', 'baz'):
    s = pd.Series(np.random.rand(5), index=list('abcde'), name=k)
    ax.plot(
        s, legend='ul',
        legend_kw={'lw': 5, 'ew': 2, 'ec': 'r', 'fc': 'w', 'handle_kw': {'marker': 'd'}}
    )


# ## Triangular functions
#
# Test triangular functions. Here there is no remotely sensible way to infer
# coordinates so we skip standardize function.

fig, ax = pplt.subplots()
N = 30
y = np.random.rand(N) * 20
x = np.random.rand(N) * 50
da = xr.DataArray(np.random.rand(N), dims=('x',), coords={'x': x, 'y': ('x', y)})
ax.tricontour(da.x, da.y, da, labels=True)


# ## Seaborn swarmplot
#
# Test swarm plots.

# %%

tips = sns.load_dataset('tips')
fig = pplt.figure(refwidth=3)
ax = fig.subplot()
sns.swarmplot(ax=ax, x='day', y='total_bill', data=tips, palette='cubehelix')

# %%

fig, ax = pplt.subplots()
sns.swarmplot(y=np.random.normal(size=100), ax=ax)


# ## Seaborn histograms
#
# Test histograms and kernels.

# %%

fig, ax = pplt.subplots()
sns.histplot(np.random.normal(size=100), ax=ax)

# %%
# %matplotlib inline

penguins = sns.load_dataset('penguins')
fig, axs = pplt.subplots()
sns.kdeplot(
    data=penguins, x='flipper_length_mm', hue='species', multiple='stack', ax=axs[0]
)
fig = pplt.figure()
ax = fig.subplot()
sns.histplot(
    data=penguins, x='flipper_length_mm', hue='species', multiple='stack', ax=ax
)

# %%
tips = sns.load_dataset('tips')
fig = pplt.figure()
ax = fig.subplot()
# sns.swarmplot(ax=ax, x="day", y="total_bill", data=tips)
sns.kdeplot(np.random.rand(100), np.random.rand(100), ax=ax)


# ## Seaborn relational
#
# Test scatter plots. Disabling seaborn detection creates mismatch between marker sizes
# and legend.

# %%
fig = pplt.figure()
ax = fig.subplot()
sns.set_theme(style='white')

# Load the example mpg dataset
mpg = sns.load_dataset('mpg')

# Plot miles per gallon against horsepower with other semantics
sns.scatterplot(
    x='horsepower', y='mpg', hue='origin', size='weight',
    sizes=(40, 400), alpha=.5, palette='muted',
    # legend='bottom',
    # height=6,
    data=mpg, ax=ax
)


# ## Seaborn heatmap
#
# This now works thanks to backwards compatibility support.

# %%
penguins = sns.load_dataset('penguins')

# %%
# %matplotlib inline

fig, ax = pplt.subplots()
sns.heatmap(np.random.normal(size=(50, 50)), ax=ax[0])
