"""Write a finished figure to a PNG or PDF file.

The UI owns the file dialog, the format choice, cancelling and the overwrite
confirmation; this module only writes. It never creates a directory, never
calls a global pyplot function, and reports a write failure to the caller
rather than returning quietly.

`figure.savefig` selects the right backend for the extension and restores
`figure.canvas` afterwards, so exporting a figure that is currently shown in
the Qt window does not detach it from its widget.
"""

from __future__ import annotations

import os
from pathlib import Path

from matplotlib.figure import Figure

#: The shared contract supports exactly these two formats.
SUPPORTED_SUFFIXES = (".png", ".pdf")

#: Raster exports are meant for a report page, where the on-screen 100 dpi
#: looks soft. PDF is vector, so this only affects PNG in practice.
EXPORT_DPI = 200


def _validated_path(path) -> Path:
    if isinstance(path, Figure):
        raise ValueError("export_figure takes the figure first and the path second")
    if not isinstance(path, (str, os.PathLike)):
        raise ValueError("path must be a filesystem path")
    destination = Path(path)
    if not destination.name:
        raise ValueError("path must name a file, not a directory")

    suffix = destination.suffix.lower()
    if suffix not in SUPPORTED_SUFFIXES:
        supported = " or ".join(SUPPORTED_SUFFIXES)
        raise ValueError(f"Export supports {supported}; received '{destination.suffix}'")
    if destination.is_dir():
        raise ValueError(f"'{destination}' is a directory, not a file")
    # The contract keeps directory creation with the UI, so that a typed path
    # cannot quietly scatter new folders across the user's disk.
    if not destination.parent.exists():
        raise ValueError(f"Folder '{destination.parent}' does not exist")
    if not destination.parent.is_dir():
        raise ValueError(f"'{destination.parent}' is not a folder")
    return destination


def export_figure(figure: Figure, path: Path, *, dpi: int = EXPORT_DPI) -> None:
    """Write `figure` to `path`, choosing the format from the extension.

    Raises ValueError for an unusable figure or path and lets a genuine write
    failure propagate, so the UI can only report success once this returns.
    A file this call created but could not finish is removed again, so a failed
    export never leaves an empty file behind for someone to mistake for output.
    """
    if isinstance(path, Figure) and not isinstance(figure, Figure):
        # Swapped arguments are easy to write and confusing to diagnose from
        # "figure must be a matplotlib Figure" alone.
        raise ValueError("export_figure takes the figure first and the path second")
    if not isinstance(figure, Figure):
        raise ValueError("figure must be a matplotlib Figure")
    if not isinstance(dpi, int) or isinstance(dpi, bool) or dpi <= 0:
        raise ValueError("dpi must be a positive integer")
    destination = _validated_path(path)

    existed = destination.exists()
    try:
        figure.savefig(
            destination,
            format=destination.suffix.lower().lstrip("."),
            dpi=dpi,
            # Keep the theme's background instead of Matplotlib's default white,
            # which would put a dark-theme figure on a white page.
            facecolor=figure.get_facecolor(),
            edgecolor=figure.get_edgecolor(),
        )
    except BaseException:
        if not existed:
            # Remove our own half-written file; never touch a pre-existing one.
            destination.unlink(missing_ok=True)
        raise

    if not destination.exists() or destination.stat().st_size == 0:
        if not existed:
            destination.unlink(missing_ok=True)
        raise OSError(f"Export produced no data at '{destination}'")
