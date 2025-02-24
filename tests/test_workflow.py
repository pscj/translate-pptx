def test_workflow():
    import os
    from translate_pptx._terminal import command_line_interface

    command_line_interface(["translate_pptx", "tests/test.pptx", "french", "tests/test_french.pptx", "nop"])
    assert os.path.exists("tests/test_french.pptx")

