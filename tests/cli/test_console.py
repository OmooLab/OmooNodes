import io
from contextlib import redirect_stdout

import pytest

from omoonodes.console import done, progress


@pytest.mark.parametrize("failed", [False, True])
def test_terminal_progress_keeps_diagnostics_and_marks_only_success(failed):
    output = io.StringIO()
    output.isatty = lambda: True
    with redirect_stdout(output):
        try:
            with progress("Example.blend", indent="  "):
                print("diagnostic")
                if failed:
                    raise ValueError("failure")
        except ValueError:
            assert failed
    text = output.getvalue()
    assert "  Example.blend ..." in text and "\r" in text
    assert "diagnostic" in text
    assert ("  ✔ Example.blend" in text) == (not failed)


def test_done_lists_output_directories(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    done([tmp_path / "workspaces/b45/O_Essentials", tmp_path / "workspaces/b45/O_Extra"])
    assert capsys.readouterr().out == "Done\n  - workspaces/b45/O_Essentials\n  - workspaces/b45/O_Extra\n"
