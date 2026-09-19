from pathlib import Path

from tools.check_text_hygiene import check_text_bytes


PATH = Path("example.txt")


def messages(data: bytes) -> list[str]:
    return [diagnostic.message for diagnostic in check_text_bytes(PATH, data)]


def test_valid_utf8_lf_file_passes() -> None:
    assert check_text_bytes(PATH, b"hello\n") == []


def test_missing_final_newline_is_reported() -> None:
    assert messages(b"hello") == ["missing final newline"]


def test_empty_file_passes() -> None:
    assert check_text_bytes(PATH, b"") == []


def test_crlf_line_ending_is_reported() -> None:
    assert messages(b"hello\r\n") == ["CRLF line ending; expected LF"]


def test_bare_cr_line_ending_is_reported() -> None:
    assert messages(b"hello\r") == [
        "missing final newline",
        "bare CR line ending; expected LF",
    ]


def test_trailing_spaces_are_reported() -> None:
    assert messages(b"hello   \n") == ["trailing whitespace"]


def test_trailing_tab_is_reported() -> None:
    assert messages(b"hello\t\n") == ["trailing whitespace"]


def test_invalid_utf8_is_reported() -> None:
    assert messages(b"\xff\n") == ["invalid UTF-8"]


def test_nul_containing_file_is_treated_as_binary() -> None:
    assert check_text_bytes(PATH, b"\0not text") == []
