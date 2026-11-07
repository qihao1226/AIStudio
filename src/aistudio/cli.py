"""AIStudio Command Line Interface for AG_SOP_04."""

import sys
import argparse
from pathlib import Path
from .config import DEFAULT_PROJECTS_DIR, PROJECT_SUBDIRS
from .inventory import scan_inventory
from .manifest import validate_manifest
from .assembler import assemble_assets

def init_project(project_id: str, base_dir: Path = DEFAULT_PROJECTS_DIR):
    project_path = base_dir / project_id
    project_path.mkdir(parents=True, exist_ok=True)
    for subdir in PROJECT_SUBDIRS:
        (project_path / subdir).mkdir(parents=True, exist_ok=True)
    print(f"✅ 项目目录初始化成功: {project_path}")
    return project_path

def main():
    parser = argparse.ArgumentParser(description="AIStudio AG_SOP_04 Pipeline CLI")
    subparsers = parser.add_subparsers(dest="command")

    # init
    init_parser = subparsers.add_parser("init", help="初始化 AG_SOP_04 项目标准目录结构")
    init_parser.add_argument("project_id", help="项目ID (如: 20261107_demo)")

    # scan
    scan_parser = subparsers.add_parser("scan", help="扫描 01_raw_assets 资产")
    scan_parser.add_argument("project_dir", help="项目根路径")

    # assemble
    assemble_parser = subparsers.add_parser("assemble", help="组装 assets_hub 并执行机器门禁检测")
    assemble_parser.add_argument("project_dir", help="项目根路径")

    args = parser.parse_args()

    if args.command == "init":
        init_project(args.project_id)
    elif args.command == "scan":
        inv = scan_inventory(Path(args.project_dir))
        print(f"✅ 扫描完成！共计发现 {inv['total_files']} 个原始文件。")
    elif args.command == "assemble":
        res = assemble_assets(Path(args.project_dir))
        if res["is_ready"]:
            print(f"🎉 资产组装与机器门禁全绿通过！共组装 {res['assembled_count']} 个核心资产。")
        else:
            print(f"⚠️ 资产组装未通过，错误列表: {res['errors']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
