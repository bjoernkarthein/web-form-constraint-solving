import cProfile
import io
import json
import pandas as pd
import pstats
import requests
import shutil

from pathlib import Path
from typing import Dict

from src.proxy.interception import decode_bytes
from src.utility.helpers import split_on_newline, write_to_file, admin_controller


class EvaluationStub:
    def __getattr__(self, _):
        def any_method(*args, **kwargs):
            pass

        return any_method


class Evaluation:
    def __init__(
        self, pr: cProfile.Profile | None = None, file: str | None = None
    ) -> None:
        self.__pr = pr
        self.__file = file
        self.__stats = {}

    def save_stat(self, variable: str, value) -> None:
        self.__stats[variable] = value

    def write_stats_to_file(self) -> None:
        write_to_file(f"evaluation/{self.__file}_stats.json", self.__stats)

    def start_profiling(self) -> None:
        self.__pr.enable()

    def save_profiling(self) -> None:
        self.__pr.disable()
        csv = self.__prof_to_csv(self.__pr)
        with open(
            f"evaluation/{self.__file}_stats_time.csv", "w+", encoding="utf-8"
        ) as f:
            f.write(csv)

        self.__clean_csv(f"evaluation/{self.__file}_stats_time")
        self.__get_isla_csv(f"evaluation/{self.__file}_stats_time")

    def save_specification(self) -> None:
        if Path("specification").is_dir:
            return

        shutil.copytree(
            "specification",
            f"evaluation/specifications/{self.__file}",
            dirs_exist_ok=True,
        )
        shutil.rmtree("specification", ignore_errors=True)

    def get_service_stats(self) -> Dict:
        url = f"{admin_controller}/getStats"
        res: requests.Response = requests.get(url)
        res_string = decode_bytes(res.content)
        print(res_string)
        return json.loads(res_string)

    def merge_stats(self, service_stats: Dict) -> None:
        self.__stats = self.__stats | service_stats

    def __prof_to_csv(self, pr: cProfile.Profile) -> None:
        out_stream = io.StringIO()
        stats = pstats.Stats(pr, stream=out_stream)
        stats.sort_stats(pstats.SortKey.CUMULATIVE)
        stats.print_stats()
        result = out_stream.getvalue()

        result = "ncalls" + result.split("ncalls")[-1]
        lines = [
            ",".join(line.rstrip().split(None, 5)) for line in split_on_newline(result)
        ]
        lines = list(filter(lambda l: l != "", lines))
        return "\n".join(lines)

    def __clean_csv(self, file: str) -> None:
        df = pd.read_csv(f"{file}.csv", encoding="utf-8")
        my_functions = df["filename:lineno(function)"].str.contains(
            "invariant-based-web-form-testing"
        )
        df = df[my_functions]
        df.reset_index(drop=True, inplace=True)

        df.to_csv(f"{file}_clean.csv", index=False)

    def __get_isla_csv(self, file: str) -> None:
        df = pd.read_csv(f"{file}.csv", encoding="utf-8")
        my_functions = df["filename:lineno(function)"].str.contains("isla")
        df = df[my_functions]
        df.reset_index(drop=True, inplace=True)

        df.to_csv(f"{file}_isla.csv", index=False)
