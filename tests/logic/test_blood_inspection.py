import json
import pytest
from app.logic.blood_inspection import parse_document, BloodInspectionResult


class TestParseDocument:
    def test_01(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210307_01.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 9
        self.__assert_result(results[0], "WBC", "74", "10^2/uL")
        self.__assert_result(results[1], "RBC", "493L", "10^4/uL")
        self.__assert_result(results[2], "HGB", "11.4L", "g/dL")
        self.__assert_result(results[3], "HCT", "32.9L", "%")
        self.__assert_result(results[4], "MCV", "66.7", "fL")
        self.__assert_result(results[5], "MCH", "23.1", "pg")
        self.__assert_result(results[6], "MCHC", "34.7", "g/dL")
        self.__assert_result(results[7], "PLT", "27.2", "10^4/uL")
        self.__assert_result(
            results[8], "TP", "7.4", "Y/D"
        )  # 本当はitem="TP", unit="g/dl"

    def test_02(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210307_02.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 7
        self.__assert_result(results[0], "Na-PS", "146", "mEq/l")
        self.__assert_result(results[1], "K-PS", "4.3", "mEq/l")
        self.__assert_result(results[2], "CI-PS", "107", "mEq/l")
        self.__assert_result(results[3], "BUN-PS", ">140.0", "mg/dl")
        self.__assert_result(results[4], "CRE-PS", "7.43", "mg/dl")
        self.__assert_result(results[5], "Ca-PS", "11.0", "mg/dl")
        self.__assert_result(results[6], "IP-PS", "14.0", "mg/dl")

    def test_03(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210314_01.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 9
        self.__assert_result(results[0], "WBC", "73", "10^2/uL")
        self.__assert_result(results[1], "RBC", "438L", "10^4/uL")
        self.__assert_result(results[2], "HGB", "10.2L", "g/dL")
        self.__assert_result(results[3], "HCT", "29.5L", "%")
        self.__assert_result(results[4], "MCV", "67.4", "fL")
        self.__assert_result(results[5], "MCH", "23.3", "pg")
        self.__assert_result(results[6], "MCHC", "34.6", "g/dL")
        self.__assert_result(results[7], "PLT", "21.4", "10^4/uL")
        self.__assert_result(
            results[8], "TP7.4", "g/H", ""
        )  # 本当はitem="TP", value="7.4" unit="g/dl"

    def test_04(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210314_02.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 0

    def test_05(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210321_01.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 9
        self.__assert_result(results[0], "WBC", "73", "10^2/uL")
        self.__assert_result(results[1], "RBC", "406L", "10^4/uL")
        self.__assert_result(results[2], "HGB", "9.5L", "g/dL")
        self.__assert_result(results[3], "HCT", "27.6L", "%")
        self.__assert_result(results[4], "MCV", "68.0", "FL")  # 本当はunit="fL"
        self.__assert_result(results[5], "MCH", "23.4", "D8")  # 本当はunit="pg"
        self.__assert_result(results[6], "MCHC", "34.4", "g/cL")  # 本当はunit="g/dL"
        self.__assert_result(results[7], "PLT", "22.7", "10^4/uL")
        self.__assert_result(
            results[8], "TI", "6.8991", ""
        )  # 本当はitem="TP", unit="g/dl"

    def test_06(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210321_02.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 5
        self.__assert_result(results[0], "BUN-PS", "114.2", "mg/dl")
        self.__assert_result(results[1], "CRE-PS", "5.58", "mg/dl")
        self.__assert_result(results[2], "Ca-PS", "13.0", "mg/dl")
        self.__assert_result(results[3], "IP-PS", "5.8", "mg/dl")
        self.__assert_result(results[4], "NH3-PS", "37", "ug/dl")

    def test_07(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210328_01.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 8
        self.__assert_result(results[0], "WBC", "83", "10^2/uL")
        self.__assert_result(results[1], "RBC", "400L", "10^4/uL")
        self.__assert_result(results[2], "HGB", "9.7L", "g/dL")
        self.__assert_result(results[3], "HCT", "27.1L", "%")
        self.__assert_result(results[4], "MCV", "67.8", "fL")
        self.__assert_result(results[5], "MCH", "24.3", "pg")
        self.__assert_result(results[6], "MCHC", "35.8", "g/dL")
        self.__assert_result(results[7], "PLT", "28.5", "10^4/uL")

    def test_08(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210328_02.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 4
        self.__assert_result(results[0], "BUN-PS", "97.3", "mg/dl")
        self.__assert_result(results[1], "CRE-PS", "4.78", "mg/dl")
        self.__assert_result(results[2], "Ca-PS", "12.2", "mg/dl")
        self.__assert_result(results[3], "IP-PS", "5.9", "mg/dl")

    def test_09(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210421_01.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 8
        self.__assert_result(results[0], "WBC", "68", "10^2/uL")
        self.__assert_result(results[1], "RBC", "386L", "10^4/uL")
        self.__assert_result(results[2], "HGB", "9.4L", "g/dL")
        self.__assert_result(results[3], "HCT", "27.1L", "%")
        self.__assert_result(results[4], "MCV", "70.2", "fL")
        self.__assert_result(results[5], "MCH", "24.4", "pg")
        self.__assert_result(results[6], "MCHC", "34.7", "g/dL")
        self.__assert_result(results[7], "PLT", "24.0", "10^4/uL")

    def test_10(self, datadir):
        # -- setup
        document = json.loads((datadir / "luke_20210421_02.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 4
        self.__assert_result(results[0], "BUN-PS", "76.1", "mg/dl")
        self.__assert_result(results[1], "CRE-PS", "3.51", "mg/dl")
        self.__assert_result(results[2], "Ca-PS", "11.6", "mg/dl")
        self.__assert_result(results[3], "IP-PS", "5.7", "mg/dl")

    def test_11(self, datadir):
        # -- setup
        document = json.loads((datadir / "chase_20180921_01.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 8
        self.__assert_result(results[0], "WBC", "90", "10^2/uL")
        self.__assert_result(results[1], "RBC", "577", "10^4/uL")
        self.__assert_result(results[2], "HGB", "14.1", "g/dL")
        self.__assert_result(results[3], "HCT", "41.0", "%")
        self.__assert_result(results[4], "MCV", "71.1", "fL")
        self.__assert_result(results[5], "MCH", "24.4", "pg")
        self.__assert_result(results[6], "MCHC", "34.4", "g/dL")
        self.__assert_result(results[7], "PLT", "21.4", "10^4/uL")

    def test_12(self, datadir):
        # -- setup
        document = json.loads((datadir / "chase_20180921_02.json").read_text())

        # -- exercise
        results = parse_document(document)

        # -- verify
        assert len(results) == 10
        self.__assert_result(results[0], "GLU-PS", "125", "mg/dl")
        self.__assert_result(results[1], "GPT-PS", "53", "U/l")  # 本当はitem="CPT-PS"
        self.__assert_result(results[2], "ALP-PS", "100", "U/l")
        self.__assert_result(results[3], "TCHO-PS", "165", "mg/dl")
        self.__assert_result(results[4], "BUN-PS", "23.3", "mg/dl")
        self.__assert_result(results[5], "CRE-PS", "1.0", "mg/dl")
        self.__assert_result(results[6], "ALB-PS", "3.0", "g/dl")
        self.__assert_result(results[7], "Ca-PS", "9.3", "mg/dl")
        self.__assert_result(results[8], "CPK-PS", "176", "U/l")
        self.__assert_result(results[9], "cCRP", "0.3", "mg/dl")

    def __assert_result(
        self, result: BloodInspectionResult, item: str, value: str, unit: str
    ) -> None:
        assert result.item == item
        assert result.value == value
        assert result.unit == unit
