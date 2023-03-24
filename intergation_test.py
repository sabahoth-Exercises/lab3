# pylint: disable=missing-class-docstring     # чтобы не быть Капитаном Очевидностью
# pylint: disable=missing-function-docstring  # чтобы не быть Капитаном Очевидностью
# pylint: disable=line-too-long               # строки с ожидаемым выводом

""" Интеграционные тесты транслятора и машины """

import contextlib
import io
import logging
import os
import tempfile
import pytest

import machine
import translator


@pytest.mark.golden_test("golden/cat.yml")
def test_cat(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        source = os.path.join(tmp_dir_name, "cat.js")
        input_stream = os.path.join(tmp_dir_name, "input.txt")
        target = os.path.join(tmp_dir_name, "cat_out.txt")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input"])
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main([source, target])
            print("============================================================")
            machine.main([target, input_stream])

        with open(target, encoding="utf-8") as file:
            instructions = file.read()

        assert instructions == golden.out["code"]
        assert stdout.getvalue() == golden.out["output"]
        assert caplog.text == golden.out["log"]


@pytest.mark.golden_test("golden/prob2.yml")
def test_prob(golden, caplog):
    caplog.set_level(logging.DEBUG)

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        source = os.path.join(tmp_dir_name, "prob2.js")
        input_stream = os.path.join(tmp_dir_name, "in.txt")
        target = os.path.join(tmp_dir_name, "prob_out.txt")

        with open(source, "w", encoding="utf-8") as file:
            file.write(golden["source"])
        with open(input_stream, "w", encoding="utf-8") as file:
            file.write(golden["input"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            translator.main([source, target])
            print("============================================================")
            machine.main([target, input_stream])

        with open(target, encoding="utf-8") as file:
            instructions = file.read()

        assert instructions == golden.out["code"]
        assert stdout.getvalue() == golden.out["output"]
        assert caplog.text == golden.out["log"]
