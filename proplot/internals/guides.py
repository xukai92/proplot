#!/usr/bin/env python3
"""
Utilties related to legends and colorbars.
"""
import matplotlib.artist as martist
import matplotlib.axes as maxes
import matplotlib.colorbar as mcolorbar
import matplotlib.offsetbox as moffsetbox
import matplotlib.projections as mprojections  # noqa: F401
import matplotlib.ticker as mticker
import matplotlib.transforms as mtransforms
import numpy as np

from . import ic  # noqa: F401
from . import warnings


def _fill_guide_kw(kwargs, overwrite=False, **pairs):
    """
    Add the keyword arguments to the dictionary if not already present.
    """
    aliases = (
        ('title', 'label'),
        ('locator', 'ticks'),
        ('format', 'formatter', 'ticklabels')
    )
    for key, value in pairs.items():
        if value is None:
            continue
        keys = tuple(k for opts in aliases for k in opts if key in opts)
        keys = keys or (key,)  # e.g. 'extend' or something
        keys_found = tuple(key for key in keys if kwargs.get(key) is not None)
        if not keys_found:
            kwargs[key] = value
        elif overwrite:  # overwrite existing key
            kwargs[keys_found[0]] = value


def _guide_kw_to_arg(name, kwargs, **pairs):
    """
    Add to the `colorbar_kw` or `legend_kw` dict if there are no conflicts.
    """
    # WARNING: Here we *do not* want to overwrite properties in the dictionary.
    # Indicates e.g. calling colorbar(extend='both') after pcolor(extend='neither').
    kw = kwargs.setdefault(f'{name}_kw', {})
    _fill_guide_kw(kw, overwrite=True, **pairs)


def _guide_kw_to_obj(obj, name, kwargs):
    """
    Store settings on the object from the input dict.
    """
    pairs = getattr(obj, f'_{name}_kw', None)
    pairs = pairs or {}
    _fill_guide_kw(pairs, overwrite=True, **kwargs)  # update with current input
    try:
        setattr(obj, f'_{name}_kw', kwargs)
    except AttributeError:
        pass
    if isinstance(obj, (tuple, list, np.ndarray)):
        for member in obj:
            _guide_kw_to_obj(member, name, kwargs)


def _guide_obj_to_kw(obj, name, kwargs):
    """
    Add to the dict from settings stored on the object if there are no conflicts.
    """
    # WARNING: Here we *do* want to overwrite properties in dictionary. Indicates
    # updating kwargs during parsing (probably only relevant for ax.parametric).
    pairs = getattr(obj, f'_{name}_kw', None)
    pairs = pairs or {}  # needed for some reason
    _fill_guide_kw(kwargs, overwrite=False, **pairs)
    if isinstance(obj, (tuple, list, np.ndarray)):
        for member in obj:  # possibly iterate over matplotlib tuple/list subclasses
            _guide_obj_to_kw(member, name, kwargs)
    return kwargs


def _iter_children(*args):
    """
    Iterate through `_children` of `HPacker`, `VPacker`, and `DrawingArea`.
    This is used to update legend handle properties.
    """
    for arg in args:
        if hasattr(arg, '_children'):
            yield from _iter_children(*arg._children)
        elif arg is not None:
            yield arg


def _iter_iterables(*args):
    """
    Iterate over arbitrary nested lists of iterables. Used for deciphering legend input.
    Things can get complicated with e.g. bar colunns plus negative-positive colors.
    """
    for arg in args:
        if np.iterable(arg):
            yield from _iter_iterables(*arg)
        elif arg is not None:
            yield arg


def _update_ticks(self, manual_only=False):
    """
    Refined colorbar tick updater without subclassing.
    """
    # TODO: Add this to generalized colorbar subclass?
    # NOTE: Matplotlib 3.5+ does not define _use_auto_colorbar_locator since
    # ticks are always automatically adjusted by its colorbar subclass. This
    # override is thus backwards and forwards compatible.
    use_auto = getattr(self, '_use_auto_colorbar_locator', lambda: True)
    if use_auto():
        if manual_only:
            pass
        else:
            mcolorbar.Colorbar.update_ticks(self)  # here AutoMinorLocator auto updates
    else:
        mcolorbar.Colorbar.update_ticks(self)  # update necessary
        minorlocator = getattr(self, 'minorlocator', None)
        if minorlocator is None:
            pass
        elif hasattr(self, '_ticker'):
            ticks, *_ = self._ticker(self.minorlocator, mticker.NullFormatter())
            axis = self.ax.yaxis if self.orientation == 'vertical' else self.ax.xaxis
            axis.set_ticks(ticks, minor=True)
            axis.set_ticklabels([], minor=True)
        else:
            warnings._warn_proplot(f'Cannot use user-input colorbar minor locator {minorlocator!r} (older matplotlib version). Turning on minor ticks instead.')  # noqa: E501
            self.minorlocator = None
            self.minorticks_on()  # at least turn them on


class _AnchoredAxes(moffsetbox.AnchoredOffsetbox):
    """
    An anchored child axes whose background patch and offset position is determined
    by the tight bounding box. Analogous to `~matplotlib.offsetbox.AnchoredText`.
    """
    def __init__(self, ax, width, height, **kwargs):
        # Note the default bbox_to_anchor will be
        # the axes bounding box.
        bounds = [0, 0, 1, 1]  # arbitrary initial bounds
        child = maxes.Axes(ax.figure, bounds, zorder=self.zorder)
        # cls = mprojections.get_projection_class('proplot_cartesian')  # TODO
        # child = cls(ax.figure, bounds, zorder=self.zorder)
        super().__init__(child=child, bbox_to_anchor=ax.bbox, **kwargs)
        ax.add_artist(self)  # sets self.axes to ax and bbox_to_anchor to ax.bbox
        self._child = child  # ensure private attribute exists
        self._width = width
        self._height = height

    def draw(self, renderer):
        # Just draw the patch (not the axes)
        if not self.get_visible():
            return
        if hasattr(self, '_update_offset_func'):
            self._update_offset_func(renderer)
        else:
            warnings._warn_proplot(
                'Failed to update _AnchoredAxes offset function due to matplotlib '
                'private API change. The resulting axes position may be incorrect.'
            )
        bbox = self.get_window_extent(renderer)
        self._update_patch(renderer, bbox=bbox)
        bbox = self.get_child_extent(renderer, offset=True)
        self._update_child(bbox)
        self.patch.draw(renderer)
        self._child.draw(renderer)

    def _update_child(self, bbox):
        # Update the child bounding box
        trans = getattr(self.figure, 'transSubfigure', self.figure.transFigure)
        bbox = mtransforms.TransformedBbox(bbox, trans.inverted())
        getattr(self._child, '_set_position', self._child.set_position)(bbox)

    def _update_patch(self, renderer, bbox):
        # Update the patch position
        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())
        self.patch.set_bounds(bbox.x0, bbox.y0, bbox.width, bbox.height)
        self.patch.set_mutation_scale(fontsize)

    def get_extent(self, renderer, offset=False):
        # Return the extent of the child plus padding
        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())
        pad = self.pad * fontsize
        bbox = self._child._tight_bbox = self._child.get_tightbbox(renderer)
        # bbox = self._child.get_tightbbox(renderer, use_cache=True)  # TODO
        width = bbox.width + 2 * pad
        height = bbox.height + 2 * pad
        xd = yd = pad
        if offset:
            xd += self._child.bbox.x0 - bbox.x0
            yd += self._child.bbox.y0 - bbox.y0
        return width, height, xd, yd

    def get_child_extent(self, renderer, offset=False):
        # Update the child position
        fontsize = renderer.points_to_pixels(self.prop.get_size_in_points())
        x0, y0 = self._child.bbox.x0, self._child.bbox.y0
        if offset:  # find offset position
            self._update_child(self.get_child_extent(renderer))
            width, height, xd, yd = self.get_extent(renderer, offset=True)
            x0, y0 = self.get_offset(width, height, xd, yd, renderer)
            # bbox = self._child.get_tightbbox(use_cache=True)  # TODO
            xd += self._child.bbox.x0 - self._child._tight_bbox.x0
            yd += self._child.bbox.y0 - self._child._tight_bbox.y0
        width, height = self._width * fontsize, self._height * fontsize
        return mtransforms.Bbox.from_bounds(x0, y0, width, height)

    def get_window_extent(self, renderer):
        # Return the window bounding box
        self._child.get_tightbbox(renderer)  # reset the cache
        self._update_child(self.get_child_extent(renderer))
        xi, yi, xd, yd = self.get_extent(renderer, offset=False)
        ox, oy = self.get_offset(xi, yi, xd, yd, renderer)
        return mtransforms.Bbox.from_bounds(ox - xd, oy - yd, xi, yi)


class _CenteredLegend(martist.Artist):
    """
    A legend-like subclass whose handles are grouped into centered rows of
    `~matplotlib.offsetbox.HPacker` rather than `~matplotlib.offsetbox.VPacker` columns.
    """
