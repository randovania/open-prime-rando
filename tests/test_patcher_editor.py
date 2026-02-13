import re

import pytest
from retro_data_structures.formats.scan import Scan
from retro_data_structures.formats.strg import Strg
from retro_data_structures.properties.echoes.objects import ScannableObjectInfo

from open_prime_rando.patcher_editor import PatcherEditor


def test_create_strg(prime2_editor: PatcherEditor) -> None:
    simple_id_1, simple = prime2_editor.create_strg("MyName", "Some Little Text")
    assert simple.strings == ("Some Little Text",)

    simple_id_2, simple_2 = prime2_editor.create_strg("MyName", "Some Little Text")
    assert simple_id_2 == simple_id_1
    assert simple_2 is simple

    with pytest.raises(
        ValueError,
        match=re.escape(
            r"STRG named 'MyName' already exists with contents `('Some Little Text',)`, expected `('Different Text',)`"
        ),
    ):
        prime2_editor.create_strg("MyName", "Different Text")

    _, c = prime2_editor.create_strg("Complex", ["Block 1", "Block 2"])
    assert c.strings == ("Block 1", "Block 2")


def test_create_simple_scan_one_box(prime2_editor: PatcherEditor) -> None:
    scan_id = prime2_editor.create_simple_scan("FooBar")

    scan = prime2_editor.get_file(scan_id, Scan)
    assert scan.scannable_object_info.get_properties() == ScannableObjectInfo(
        string=0x713FD71A,  # hash of the name
    )

    strg = prime2_editor.get_file(0x713FD71A, Strg)
    assert strg.strings == ("FooBar",)

    # Again gives the same scan
    assert prime2_editor.create_simple_scan("FooBar") == scan_id
