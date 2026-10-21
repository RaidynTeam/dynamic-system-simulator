"""Export must produce a real file, or fail loudly without leaving a stub."""

import numpy as np
import pytest
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.colors import to_rgba

from dss.analytical import solve_analytical
from dss.contracts import ModelParams, SimulationConfig
from dss.numerical import make_time_grid, solve_euler, solve_rk4
from dss.visualization import (
    EXPORT_DPI,
    SUPPORTED_SUFFIXES,
    build_response_figure,
    export_figure,
    figure_theme,
    new_figure,
)

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
PDF_MAGIC = b"%PDF"


def real_figure(theme="light"):
    model = ModelParams(a1=1.0, a0=1.0, b0=1.0)
    t = make_time_grid(SimulationConfig(t0=0.0, t_end=6.0, dt=0.2))
    responses = [solve_analytical(model, t), solve_euler(model, t), solve_rk4(model, t)]
    return build_response_figure(responses, theme=theme)


# --- the file that comes out -------------------------------------------------


def test_png_export_writes_a_real_png(tmp_path):
    target = tmp_path / "response.png"
    export_figure(real_figure(), target)
    assert target.is_file()
    data = target.read_bytes()
    assert data.startswith(PNG_MAGIC)
    assert len(data) > 5000  # a real plot, not a blank canvas


def test_pdf_export_writes_a_real_pdf(tmp_path):
    target = tmp_path / "response.pdf"
    export_figure(real_figure(), target)
    assert target.is_file()
    data = target.read_bytes()
    assert data.startswith(PDF_MAGIC)
    assert b"%%EOF" in data[-2048:]  # the page was closed, not truncated
    assert len(data) > 3000


def test_both_contract_formats_are_supported(tmp_path):
    assert set(SUPPORTED_SUFFIXES) == {".png", ".pdf"}
    for suffix in SUPPORTED_SUFFIXES:
        target = tmp_path / f"out{suffix}"
        export_figure(real_figure(), target)
        assert target.stat().st_size > 0


def test_the_extension_decides_the_format_whatever_its_case(tmp_path):
    upper = tmp_path / "RESPONSE.PNG"
    export_figure(real_figure(), upper)
    assert upper.read_bytes().startswith(PNG_MAGIC)


def test_a_string_path_is_accepted_as_well_as_a_path_object(tmp_path):
    target = tmp_path / "from-string.png"
    export_figure(real_figure(), str(target))
    assert target.is_file()


def test_the_exported_pixel_size_follows_the_dpi(tmp_path):
    from PIL import Image

    figure = real_figure()
    width, height = figure.get_size_inches()
    target = tmp_path / "sized.png"
    export_figure(figure, target, dpi=100)
    with Image.open(target) as image:
        assert image.size == (round(width * 100), round(height * 100))

    bigger = tmp_path / "bigger.png"
    export_figure(figure, bigger)
    with Image.open(bigger) as image:
        assert image.size == (round(width * EXPORT_DPI), round(height * EXPORT_DPI))


def test_a_dark_figure_keeps_its_background_instead_of_turning_white(tmp_path):
    from PIL import Image

    target = tmp_path / "dark.png"
    export_figure(real_figure("dark"), target)
    expected = tuple(round(channel * 255) for channel in to_rgba(figure_theme("dark").surface))
    with Image.open(target) as image:
        assert image.convert("RGBA").getpixel((2, 2)) == expected


# --- the figure is not damaged by exporting it -------------------------------


def test_exporting_does_not_detach_the_canvas_the_ui_is_showing(tmp_path):
    # The UI keeps the figure on a FigureCanvasQTAgg while the user exports.
    figure = real_figure()
    canvas = FigureCanvasAgg(figure)
    export_figure(figure, tmp_path / "a.png")
    export_figure(figure, tmp_path / "a.pdf")
    assert figure.canvas is canvas


def test_exporting_does_not_change_what_the_figure_contains(tmp_path):
    figure = real_figure()
    before = [(line.get_xydata().copy(), line.get_label()) for line in figure.axes[0].get_lines()]
    export_figure(figure, tmp_path / "a.png")
    after = figure.axes[0].get_lines()
    assert len(after) == len(before)
    for line, (data, label) in zip(after, before):
        assert np.array_equal(line.get_xydata(), data)
        assert line.get_label() == label


def test_the_same_figure_can_be_exported_repeatedly(tmp_path):
    figure = real_figure()
    for index in range(3):
        target = tmp_path / f"repeat{index}.png"
        export_figure(figure, target)
        assert target.stat().st_size > 0


# --- rejected input ----------------------------------------------------------


@pytest.mark.parametrize("suffix", [".svg", ".jpg", ".jpeg", ".txt", ".eps", ""])
def test_an_unsupported_extension_is_rejected(tmp_path, suffix):
    target = tmp_path / f"out{suffix}"
    with pytest.raises(ValueError):
        export_figure(real_figure(), target)
    assert not target.exists()


def test_a_missing_folder_is_rejected_rather_than_created(tmp_path):
    target = tmp_path / "does-not-exist" / "out.png"
    with pytest.raises(ValueError, match="does not exist"):
        export_figure(real_figure(), target)
    assert not target.parent.exists()


def test_a_directory_target_is_rejected(tmp_path):
    folder = tmp_path / "folder.png"
    folder.mkdir()
    with pytest.raises(ValueError):
        export_figure(real_figure(), folder)
    assert folder.is_dir()


def test_a_parent_that_is_a_file_is_rejected(tmp_path):
    parent = tmp_path / "a-file"
    parent.write_text("not a folder", encoding="utf-8")
    with pytest.raises(ValueError):
        export_figure(real_figure(), parent / "out.png")


@pytest.mark.parametrize("bad", [None, "figure", 3, object()])
def test_anything_that_is_not_a_figure_is_rejected(tmp_path, bad):
    with pytest.raises(ValueError):
        export_figure(bad, tmp_path / "out.png")


@pytest.mark.parametrize("bad", [None, 3, object(), b"out.png"])
def test_anything_that_is_not_a_path_is_rejected(bad):
    with pytest.raises(ValueError):
        export_figure(real_figure(), bad)


def test_swapping_the_two_arguments_is_reported_clearly(tmp_path):
    with pytest.raises(ValueError, match="figure first"):
        export_figure(tmp_path / "out.png", real_figure())


@pytest.mark.parametrize("dpi", [0, -100, 1.5, True, None, "200"])
def test_an_unusable_dpi_is_rejected(tmp_path, dpi):
    with pytest.raises(ValueError):
        export_figure(real_figure(), tmp_path / "out.png", dpi=dpi)


# --- failures leave nothing misleading behind --------------------------------


def test_a_failed_export_removes_the_file_it_started(tmp_path, monkeypatch):
    target = tmp_path / "broken.png"
    figure = real_figure()

    def fail_after_creating(path, **kwargs):
        # Imitate a writer that opens the file and then dies part way through.
        target.write_bytes(b"")
        raise OSError("disk full")

    monkeypatch.setattr(figure, "savefig", fail_after_creating)
    with pytest.raises(OSError, match="disk full"):
        export_figure(figure, target)
    assert not target.exists()


def test_a_failed_overwrite_keeps_the_previous_file(tmp_path, monkeypatch):
    target = tmp_path / "existing.png"
    target.write_bytes(b"original contents")
    figure = real_figure()

    def fail(path, **kwargs):
        raise OSError("disk full")

    monkeypatch.setattr(figure, "savefig", fail)
    with pytest.raises(OSError):
        export_figure(figure, target)
    assert target.read_bytes() == b"original contents"


def test_an_empty_result_is_reported_as_a_failure_not_a_success(tmp_path, monkeypatch):
    target = tmp_path / "empty.png"
    figure = real_figure()
    monkeypatch.setattr(figure, "savefig", lambda path, **kwargs: target.write_bytes(b""))
    with pytest.raises(OSError, match="no data"):
        export_figure(figure, target)
    assert not target.exists()


def test_a_read_only_target_reports_the_real_write_error(tmp_path):
    import os
    import stat

    target = tmp_path / "locked.png"
    target.write_bytes(b"locked")
    os.chmod(target, stat.S_IREAD)
    try:
        with pytest.raises(OSError):
            export_figure(real_figure(), target)
        assert target.read_bytes() == b"locked"
    finally:
        os.chmod(target, stat.S_IWRITE | stat.S_IREAD)


# --- overwriting is the UI's decision, not ours ------------------------------


def test_an_existing_file_is_overwritten_because_the_ui_already_confirmed(tmp_path):
    target = tmp_path / "out.png"
    target.write_bytes(b"old")
    export_figure(real_figure(), target)
    assert target.read_bytes().startswith(PNG_MAGIC)


# --- an empty figure is still a figure ---------------------------------------


def test_a_figure_with_no_axes_still_exports(tmp_path):
    target = tmp_path / "blank.png"
    export_figure(new_figure("light"), target)
    assert target.read_bytes().startswith(PNG_MAGIC)
