#!/usr/bin/env python3
"""
Test 1D plotting overrides.
"""
import numpy as np
import numpy.ma as ma
import pandas as pd

import proplot as pplt


def test_cmap_cycles():
    """
    Test sampling of multiple continuous colormaps.
    """
    cycle = pplt.Cycle(
        'Boreal', 'Grays', 'Fire', 'Glacial', 'yellow',
        left=[0.4] * 5, right=[0.6] * 5,
        samples=[3, 4, 5, 2, 1],
    )
    fig, ax = pplt.subplots()
    data = np.random.rand(10, len(cycle)).cumsum(axis=1)
    data = pd.DataFrame(data, columns=list('abcdefghijklmno'))
    ax.plot(data, cycle=cycle, linewidth=2, legend='b')


def test_auto_reverse():
    """
    Test enabled and disabled auto reverse.
    """
    x = np.arange(10)[::-1]
    y = np.arange(10)
    z = np.random.rand(10, 10)
    fig, axs = pplt.subplots(ncols=2, nrows=2, share=False)
    # axs[0].format(xreverse=False)  # should fail
    axs[0].plot(x, y)
    axs[1].format(xlim=(0, 9))  # manual override
    axs[1].plot(x, y)
    axs[2].pcolor(x, y[::-1], z)
    axs[3].format(xlim=(0, 9), ylim=(0, 9))  # manual override!
    axs[3].pcolor(x, y[::-1], z)


def test_invalid_values():
    """
    Test distributions with missing or invalid values.
    """
    fig, axs = pplt.subplots(ncols=2)
    data = np.random.normal(size=(100, 5))
    for j in range(5):
        data[:, j] = np.sort(data[:, j])
        data[:19 * (j + 1), j] = np.nan
        # data[:20, :] = np.nan
    data_masked = ma.masked_invalid(data)  # should be same result
    for ax, dat in zip(axs, (data, data_masked)):
        ax.plot(dat, means=True, shade=True)

    fig, axs = pplt.subplots(ncols=2, nrows=2)
    data = np.random.normal(size=(100, 5))
    for i in range(5):  # test uneven numbers of invalid values
        data[:10 * (i + 1), :] = np.nan
    data_masked = ma.masked_invalid(data)  # should be same result
    for ax, dat in zip(axs[:2], (data, data_masked)):
        ax.violin(dat, means=True)
    for ax, dat in zip(axs[2:], (data, data_masked)):
        ax.box(dat, fill=True, means=True)


def test_histogram_types():
    """
    Test the different histogram types using basic keywords.
    """
    fig, axs = pplt.subplots(ncols=2, nrows=2, share=False)
    data = np.random.normal(size=(100, 5))
    data += np.arange(5)
    kws = ({'stack': 0}, {'stack': 1}, {'fill': 0}, {'fill': 1, 'alpha': 0.5})
    for ax, kw in zip(axs, kws):
        ax.hist(data, ec='k', **kw)


def test_scatter_inbounds():
    """
    Test in-bounds scatter plots.
    """
    fig, axs = pplt.subplots(ncols=2, share=False)
    N = 100
    fig.format(xlim=(0, 20))
    for i, ax in enumerate(axs):
        c = ax.scatter(np.arange(N), np.arange(N), c=np.arange(N), inbounds=i)
        ax.colorbar(c, loc='b')


def test_scatter_columns():
    """
    Test scatter column iteration and property cycling. Note we cannot
    retrieve metadata from `s` and `c`.
    """
    fig, ax = pplt.subplots()
    cycle = pplt.Cycle(
        '538', marker=['X', 'o', 's', 'd'], sizes=[50, 100], edgecolors=['r', 'k']
    )
    ax.scatter(np.random.rand(10, 4), np.random.rand(10, 4), cycle=cycle)

    fig, axs = pplt.subplots(ncols=2)
    axs[0].plot(np.random.rand(5, 5), np.random.rand(5, 5), lw=5)
    axs[1].scatter(
        np.random.rand(5, 5), np.random.rand(5, 5), s=np.random.rand(5, 5) * 300
    )


def test_scatter_colors():
    """
    Test diverse scatter keyword parsing and RGB scaling.
    """
    # Test sizes and face or edge colors
    x = np.random.randn(60)
    y = np.random.randn(60)

    fig, axs = pplt.subplots()
    axs.scatter(x, y, s=80, fc='none', edgecolors='r')

    # Test RGB color scaling.
    fig, axs = pplt.subplots(ncols=3)
    data = np.random.rand(50, 3)
    ax = axs[0]
    ax.scatter(data, c=data, cmap='reds')
    ax = axs[1]
    ax.scatter(data[:, 0], c=data, cmap='reds', )  # cycle='foo')  # should warn
    ax = axs[2]
    ax.scatter(data, mean=True, shadestd=1, barstd=0.5)
    ax.format(xlim=(-0.1, 2.1))


def test_scatter_sizes():
    """
    Test marker size scaling.
    """
    fig = pplt.figure()
    ax = fig.subplot(margin=0.15)
    data = np.random.rand(5) * 500
    ax.scatter(
        np.arange(5),
        [0.25] * 5,
        c='blue7',
        sizes=['5pt', '10pt', '15pt', '20pt', '25pt']
    )
    ax.scatter(
        np.arange(5),
        [0.50] * 5,
        c='red7',
        sizes=data,
        absolute_size=True
    )
    ax.scatter(
        np.arange(5),
        [0.75] * 5,
        c='red7',
        sizes=data,
        absolute_size=True
    )
    for i, d in enumerate(data):
        ax.text(i, 0.5, format(d, '.0f'), va='center', ha='center')

    fig, axs = pplt.subplots(ncols=3)
    pplt.rc.reset()
    pplt.rc['lines.markersize'] = 20
    N = 50
    x = np.random.rand(N)
    y = np.random.rand(N)
    for i, ax in enumerate(axs):
        kw = {'absolute_size': i == 2}
        if i == 1:
            kw['smax'] = 20 ** 2  # should be same as relying on lines.markersize
        ax.scatter(x, y, x * y, **kw)


def test_bar_width():
    """
    Test relative and absolute widths.
    """
    fig, axs = pplt.subplots(ncols=3)
    x = np.arange(10)
    y = np.random.rand(10, 2)
    for i, ax in enumerate(axs):
        ax.bar(x * (2 * i + 1), y, width=0.8, absolute_width=i == 1)


def test_pie_charts():
    """
    Test basic pie plots. No examples in user guide right now.
    """
    pplt.rc.inlinefmt = 'svg'
    labels = ['foo', 'bar', 'baz', 'biff', 'buzz']
    array = np.arange(1, 6)
    data = pd.Series(array, index=labels)
    fig = pplt.figure()
    ax = fig.subplot(121)
    ax.pie(array, edgefix=True, labels=labels, ec='k', cycle='reds')
    ax = fig.subplot(122)
    ax.pie(data, ec='k', cycle='blues')


def test_box_violin_plots():
    """
    Test new default behavior of passing cycles to box/violin commands.
    """
    fig = pplt.figure()
    ax = fig.subplot(121)
    ax.box(
        np.random.uniform(-3, 3, size=(1000, 5)),
        # cycle='blues_r',
        fillcolor=['red', 'blue', 'green', 'orange', 'yellow'],
        # ec='face',
    )
    ax = fig.subplot(122)
    ax.violin(
        np.random.normal(0, 1, size=(1000, 5)),
        # cycle='greys',
        fillcolor=['gray1', 'gray7'],
        means=True,
        barstds=2,
    )

    # Sample data
    N = 500
    state = np.random.RandomState(51423)
    data1 = state.normal(size=(N, 5)) + 2 * (state.rand(N, 5) - 0.5) * np.arange(5)
    data1 = pd.DataFrame(data1, columns=pd.Index(list('abcde'), name='label'))
    data2 = state.rand(100, 7)
    data2 = pd.DataFrame(data2, columns=pd.Index(list('abcdefg'), name='label'))

    # Figure
    fig, axs = pplt.subplots([[1, 1, 2, 2], [0, 3, 3, 0]], span=False)
    axs.format(
        abc='A.', titleloc='l', grid=False,
        suptitle='Boxes and violins demo'
    )

    # Box plots
    ax = axs[0]
    obj1 = ax.box(data1, means=True, marker='x', meancolor='r', fillcolor='gray4')
    print(obj1)
    ax.format(title='Box plots')

    # Violin plots
    ax = axs[1]
    obj2 = ax.violin(data1, fillcolor='gray6', means=True, points=100)
    print(obj2)
    ax.format(title='Violin plots')

    # Boxes with different colors
    ax = axs[2]
    ax.format(title='Multiple colors', ymargin=0.15)
    ax.boxh(data2, cycle='pastel2')


def test_parametric_labels():
    """
    Test passing strings as parametric 'color values'. Likely a common use case.
    """
    pplt.rc.inlinefmt = 'svg'
    fig, ax = pplt.subplots()
    ax.parametric(
        np.random.rand(5), c=list('abcde'), lw=20, colorbar='b', cmap_kw={'left': 0.2}
    )


def test_parametric_color_input():
    """
    Test color input arguments. Should be able to make monochromatic
    plots for case where we want `line` without sticky x/y edges.
    """
    fig, axs = pplt.subplots(ncols=2, nrows=2)
    colors = (
        [(0, 1, 1), (0, 1, 0), (1, 0, 0), (0, 0, 1), (1, 1, 0)],
        ['b', 'r', 'g', 'm', 'c', 'y'],
        'black',
        (0.5, 0.5, 0.5),
        # [(0.5, 0.5, 0.5)],
    )
    for ax, color in zip(axs, colors):
        ax.parametric(
            np.random.rand(5), np.random.rand(5),
            linewidth=2, label='label', color=color, colorbar='b', legend='b'
        )
