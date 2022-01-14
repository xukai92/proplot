#!/usr/bin/env python3
"""
Test 2D plotting overrides.
"""
import numpy as np
import xarray as xr

import proplot as pplt


def test_ignore_message():
    """
    Test various ignored argument warnings.
    """
    fig, ax = pplt.subplots()
    ax.contour(np.random.rand(5, 5) * 10, levels=pplt.arange(10), symmetric=True)

    fig, ax = pplt.subplots()
    ax.contourf(np.random.rand(10, 10), levels=np.linspace(0, 1, 10), locator=5, locator_kw={})  # noqa: E501

    fig, ax = pplt.subplots()
    ax.contourf(
        np.random.rand(10, 10),
        levels=pplt.arange(0, 1, 0.2),
        vmin=0,
        vmax=2,
        locator=3,
        colorbar='b'
    )

    fig, ax = pplt.subplots()
    ax.hexbin(
        np.random.rand(1000),
        np.random.rand(1000),
        levels=pplt.arange(0, 20),
        gridsize=10,
        locator=2, cmap='blues', colorbar='b'
    )


def test_edge_fix():
    """
    Test edge fix applied to 1D plotting utilities.
    """
    pplt.rc.inlinefmt = 'svg'
    pplt.rc.edgefix = 1
    fig, axs = pplt.subplots(ncols=2, share=False)
    axs.format(grid=False)
    axs[0].bar(np.random.rand(10,) * 10 - 5, width=1, negpos=True)
    axs[1].area(np.random.rand(5, 3), stack=True)

    #
    # Make sure `edgefix` is not applied wherever transparent colorbars appear.

    pplt.rc.inlinefmt = 'svg'
    data = np.random.rand(10, 10)
    cmap = 'magma'
    fig, axs = pplt.subplots(nrows=3, ncols=2, refwidth=2.5, share=False)
    for i, iaxs in enumerate((axs[:2], axs[2:4])):
        if i == 0:
            cmap = pplt.Colormap('magma', alpha=0.5)
            alpha = None
            iaxs.format(title='Colormap alpha')
        else:
            cmap = 'magma'
            alpha = 0.5
            iaxs.format(title='Single alpha')
        iaxs[0].contourf(data, cmap=cmap, colorbar='b', alpha=alpha)
        iaxs[1].pcolormesh(data, cmap=cmap, colorbar='b', alpha=alpha)
    axs[4].bar(data[:3, :3], alpha=0.5)
    axs[5].area(data[:3, :3], alpha=0.5, stack=True)


def test_levels_with_vmin_vmax():
    """
    Make sure `vmin` and `vmax` go into level generation algorithm.
    """
    # Sample data
    state = np.random.RandomState(51423)
    x = y = np.array([-10, -5, 0, 5, 10])
    data = state.rand(y.size, x.size)

    # Figure
    fig = pplt.figure(refwidth=2.3, share=False)
    axs = fig.subplots()

    m = axs.pcolormesh(x, y, data, vmax=1.35123)
    axs.colorbar([m], loc='r')


def test_level_restriction():
    """
    Test `negative`, `positive`, and `symmetric` with and without discrete.
    """
    fig, axs = pplt.subplots(ncols=3, nrows=2)
    data = 20 * np.random.rand(10, 10) - 5
    keys = ('negative', 'positive', 'symmetric')
    for i, grp in enumerate((axs[:3], axs[3:])):
        for j, ax in enumerate(grp):
            kw = {keys[j]: True, 'discrete': bool(1 - i)}
            ax.pcolor(data, **kw, colorbar='b')


def test_colormap_mode():
    """
    Test auto extending, auto discrete. Should issue warnings.
    """
    fig, axs = pplt.subplots(ncols=2, nrows=2, share=False)
    axs[0].pcolor(np.random.rand(5, 5) % 0.3, extend='both', cyclic=True, colorbar='b')
    axs[1].pcolor(np.random.rand(5, 5), sequential=True, diverging=True, colorbar='b')
    axs[2].pcolor(np.random.rand(5, 5), discrete=False, qualitative=True, colorbar='b')
    pplt.rc['cmap.discrete'] = False  # should be ignored below
    axs[3].contourf(np.random.rand(5, 5), colorbar='b')


def test_segmented_norm():
    """
    Test segmented norm with non-discrete levels.
    """
    fig, ax = pplt.subplots()
    ax.pcolor(
        np.random.rand(5, 5) * 10,
        discrete=False,
        norm='segmented',
        norm_kw={'levels': [0, 2, 10]},
        colorbar='b'
    )


def test_negative_contours():
    """
    Ensure `cmap.monochrome` properly assigned.
    """
    fig = pplt.figure(share=False)
    ax = fig.subplot(131)
    data = np.random.rand(10, 10) * 10 - 5
    ax.contour(data, color='k')
    ax = fig.subplot(132)
    ax.tricontour(*(np.random.rand(3, 20) * 10 - 5), color='k')
    ax = fig.subplot(133)
    ax.contour(data, cmap=['black'])  # fails but that's ok


def test_auto_diverging():
    """
    Test that auto diverging works.
    """
    fig = pplt.figure()
    # fig.format(collabels=('Auto sequential', 'Auto diverging'), suptitle='Default')
    ax = fig.subplot(121)
    ax.pcolor(np.random.rand(10, 10) * 5, colorbar='b')
    ax = fig.subplot(122)
    ax.pcolor(np.random.rand(10, 10) * 5 - 3.5, colorbar='b')
    fig.format(toplabels=('Sequential', 'Diverging'))

    # Test when cmap input disables auto diverging.
    # %%
    fig, axs = pplt.subplots(ncols=2, nrows=2, refwidth=2)
    cmap = pplt.Colormap(('red7', 'red3', 'red1', 'blue1', 'blue3', 'blue7'), listmode='discrete')  # noqa: E501
    data1 = 10 * np.random.rand(10, 10)
    data2 = data1 - 2
    for i, cmap in enumerate(('RdBu_r', cmap)):
        for j, data in enumerate((data1, data2)):
            cmap = pplt.Colormap(pplt.Colormap(cmap))
            axs[i, j].pcolormesh(data, cmap=cmap, colorbar='b')

    fig, axs = pplt.subplots(ncols=3)
    data = np.random.rand(5, 5) * 10 - 5
    for i, ax in enumerate(axs[:2]):
        ax.pcolor(data, sequential=bool(i), colorbar='b')
    axs[2].pcolor(data, diverging=False, colorbar='b')  # should have same effect

    fig, axs = pplt.subplots(ncols=2)
    data = np.random.rand(5, 5) * 10 + 2
    for ax, norm in zip(axs, (None, 'div')):
        ax.pcolor(data, norm=norm, colorbar='b')


def test_single_contour():
    """
    Test whether single contour works.
    """
    da = xr.DataArray(
        np.array(
            [
                [0, 1, 2],
                [3, 4, 5],
                [6, 7, 8],
                [9, 10, 11]
            ]
        ),
        dims=['y', 'x']
    )
    fig, ax = pplt.subplots()
    ax.contour(da, levels=[5.0], color='r')


def test_contour_labels():
    """
    Test contour labels. We use a separate `contour` object when adding labels to
    filled contours or else weird stuff happens (see below). We could just modify
    filled contour edges when not adding labels but that would be inconsistent with
    behavior when labels are active.
    """
    data = np.random.rand(5, 5) * 10 - 5
    fig, axs = pplt.subplots(ncols=2)
    ax = axs[0]
    ax.contourf(
        data, edgecolor='k', linewidth=1.5,
        labels=True, labels_kw={'color': 'k', 'size': 'large'}
    )
    ax = axs[1]
    m = ax.contourf(data)
    ax.clabel(m, colors='black', fontsize='large')  # looks fine without this
    for o in m.collections:
        o.set_linewidth(1.5)
        o.set_edgecolor('k')


def test_flow_functions():
    """
    These are seldom used and missing from documentation. Be careful
    not to break anything basic.
    """
    fig, ax = pplt.subplots()
    for _ in range(2):
        ax.streamplot(np.random.rand(10, 10), 5 * np.random.rand(10, 10), label='label')

    fig, axs = pplt.subplots(ncols=2)
    ax = axs[0]
    ax.quiver(
        np.random.rand(10, 10), 5 * np.random.rand(10, 10), c=np.random.rand(10, 10),
        label='label'
    )
    ax = axs[1]
    ax.quiver(np.random.rand(10), np.random.rand(10), label='single')


def test_gray_adjustment():
    """
    Test gray adjustments.
    """
    fig, ax = pplt.subplots()
    data = np.random.rand(5, 5) * 10 - 5
    cmap = pplt.Colormap(['blue', 'grey3', 'red'])
    ax.pcolor(data, cmap=cmap, colorbar='b')


def test_qualitative_colormaps():
    """
    Test both `colors` and `cmap` input and ensure extend setting is used for
    extreme only if unset.
    """
    fig, axs = pplt.subplots(ncols=2)
    data = np.random.rand(5, 5)
    colors = pplt.get_colors('set3')
    for ax, extend in zip(axs, ('both', 'neither')):
        ax.pcolor(
            data, extend=extend,
            colors=colors, colorbar='b'
        )

    fig, axs = pplt.subplots(ncols=2)
    data = np.random.rand(5, 5)
    cmap = pplt.Colormap('set3')
    cmap.set_under('black')  # does not overwrite
    for ax, extend in zip(axs, ('both', 'neither')):
        ax.pcolor(
            data, extend=extend, cmap=cmap, colorbar='b'
        )
