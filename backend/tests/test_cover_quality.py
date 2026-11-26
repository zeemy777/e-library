from tools import fetch_public_domain_covers as covers


def jpeg_bytes(width, height, padding=5000):
    segment = (
        b"\xff\xc0"
        + (17).to_bytes(2, "big")
        + b"\x08"
        + height.to_bytes(2, "big")
        + width.to_bytes(2, "big")
        + b"\x03\x01\x11\x00\x02\x11\x01\x03\x11\x01"
    )
    return b"\xff\xd8" + segment + b"\xff\xda" + b"0" * padding + b"\xff\xd9"


def test_jpeg_size_reads_scan_dimensions():
    assert covers.jpeg_size(jpeg_bytes(300, 500)) == (300, 500)


def test_real_cover_requires_scan_dimensions():
    assert covers.is_real_cover(jpeg_bytes(300, 500, 20000))
    assert not covers.is_real_cover(jpeg_bytes(32, 58, 1100))
    assert not covers.is_real_cover(b"not a jpeg")


def test_cover_state_flags_placeholders_and_fallbacks(tmp_path, monkeypatch):
    cover_dir = tmp_path / "covers"
    cover_dir.mkdir()
    monkeypatch.setattr(covers, "COVER_DIR", cover_dir)

    (cover_dir / "tiny.jpg").write_bytes(jpeg_bytes(32, 58, 1100))
    (cover_dir / "small.jpg").write_bytes(jpeg_bytes(128, 193, 8000))
    (cover_dir / "good.jpg").write_bytes(jpeg_bytes(300, 500, 20000))

    assert covers.cover_state(
        {"cover_image": "covers/tiny.jpg"}
    ) == "placeholder"
    assert covers.cover_state(
        {"cover_image": "covers/small.jpg"}
    ) == "lowres"
    assert covers.cover_state(
        {"cover_image": "covers/good.jpg"}
    ) == "real"
    assert covers.cover_state(
        {"cover_image": "covers/fallback.svg"}
    ) == "generated"
    assert covers.cover_state({"cover_image": ""}) == "missing"
