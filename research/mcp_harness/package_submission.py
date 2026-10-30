"""Package the submission files and a clean repository snapshot; standard library only."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]


def package(output):
    output = Path(output).resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    excluded = {"__pycache__", ".pytest_cache", ".git", "figures", "results_local"}
    files = {}
    for p in sorted(REPO.rglob("*")):
        parts = p.relative_to(REPO).parts
        if not p.is_file() or p.resolve() == output or any(s in excluded or s.endswith(".egg-info") for s in parts):
            continue
        files["repository/"+p.relative_to(REPO).as_posix()] = p.read_bytes()
    files["Corporate_Groups_SSRN_EN.pdf"] = (ROOT/"artifacts/Corporate_Groups_SSRN_EN.pdf").read_bytes()
    files["SSRN_GUIDE_RU.docx"] = (ROOT/"submission/SSRN_GUIDE_RU.docx").read_bytes()
    for p in sorted((ROOT/"submission").glob("*.txt")):
        files["form_fields/"+p.name] = p.read_bytes()
    files["START_HERE.txt"] = ("ПАКЕТ ПОДАЧИ НА SSRN — ВЕРСИЯ 1.2\n\n"
        "1. Откройте SSRN_GUIDE_RU.docx: инструкция и все поля формы.\n"
        "2. На SSRN загружайте Corporate_Groups_SSRN_EN.pdf из корня архива.\n"
        "3. Тексты для копирования находятся в form_fields. Файлы 08 и 09 — условные декларации; используйте только при соответствии фактам.\n"
        "4. Проверьте аффилиацию, финансирование, конфликт интересов и права на загрузку; выберите лицензию.\n"
        "5. Прочитайте рукопись перед окончательным Submit. Подача в этом пакете не выполнена.\n\n"
        "Русская версия и редактируемые Word-файлы:\n"
        "repository/research/mcp_harness/artifacts/\n\n"
        "Данные, исходники, тесты и отчет об аудите:\n"
        "repository/research/mcp_harness/\n\n"
        "Для проверки расчетов без дополнительных библиотек:\n"
        "cd repository/research/mcp_harness\n"
        "python3 -m unittest -v test_research.py\n"
        "python3 verify_release.py\n\n"
        "GitHub: https://github.com/dmkkazakov/group-data-copilot\n").encode("utf-8")
    hashes = {name: hashlib.sha256(data).hexdigest() for name,data in files.items()}
    files["PACKAGE_SHA256.json"] = (json.dumps(hashes, ensure_ascii=False, indent=2)+"\n").encode("utf-8")
    with zipfile.ZipFile(output,"w",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(files.items()):
            info=zipfile.ZipInfo(name, (2026,10,30,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            z.writestr(info,data)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        for name, digest in hashes.items():
            assert hashlib.sha256(z.read(name)).hexdigest() == digest, name
    print(json.dumps({"archive":str(output),"files":len(files),"size_bytes":output.stat().st_size,"sha256":hashlib.sha256(output.read_bytes()).hexdigest()}))


if __name__ == "__main__":
    parser=argparse.ArgumentParser();parser.add_argument("--output",required=True)
    package(parser.parse_args().output)
