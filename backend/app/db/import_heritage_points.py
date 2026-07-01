import argparse
import re
import zipfile
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional
from xml.etree import ElementTree as ET

from app.db.database import Base, SessionLocal, engine
from app.models.attraction import Attraction
from app.models.route import Route
from app.models.route_attraction import RouteAttraction


XLSX_NAMESPACE = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
DEFAULT_INPUT_FILE = Path(__file__).resolve().parents[2] / "input" / "美丽中原.xlsx"
RESOURCE_ROUTE_PREFIX = "水利遗产资源"
MAX_POINTS_PER_ROUTE = 12


def normalize_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def parse_float(value: object) -> Optional[float]:
    text = normalize_text(value)
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def column_index(cell_ref: str) -> int:
    letters = re.match(r"[A-Z]+", cell_ref)
    if not letters:
        return 0

    index = 0
    for char in letters.group(0):
        index = index * 26 + ord(char) - ord("A") + 1
    return index - 1


def read_shared_strings(archive: zipfile.ZipFile) -> List[str]:
    if "xl/sharedStrings.xml" not in archive.namelist():
        return []

    root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
    strings = []
    for item in root.findall("main:si", XLSX_NAMESPACE):
        texts = [node.text or "" for node in item.findall(".//main:t", XLSX_NAMESPACE)]
        strings.append("".join(texts))
    return strings


def read_first_sheet_rows(file_path: Path) -> Iterable[List[str]]:
    with zipfile.ZipFile(file_path) as archive:
        shared_strings = read_shared_strings(archive)
        sheet_name = sorted(
            name for name in archive.namelist() if name.startswith("xl/worksheets/sheet")
        )[0]
        root = ET.fromstring(archive.read(sheet_name))

        for row in root.findall(".//main:sheetData/main:row", XLSX_NAMESPACE):
            values: Dict[int, str] = {}
            for cell in row.findall("main:c", XLSX_NAMESPACE):
                ref = cell.attrib.get("r", "A")
                value_node = cell.find("main:v", XLSX_NAMESPACE)
                value = ""
                if value_node is not None:
                    value = value_node.text or ""
                    if cell.attrib.get("t") == "s":
                        value = shared_strings[int(value)]
                values[column_index(ref)] = normalize_text(value)

            if values:
                yield [values.get(index, "") for index in range(max(values.keys()) + 1)]


def build_description(row: Dict[str, str]) -> str:
    location_parts = [row["province"], row["city"], row["county"]]
    location = "".join(part for part in location_parts if part)
    return f"{row['name']}位于{location}，资源类型为{row['heritage_type']}。"


def clean_rows(file_path: Path) -> List[Dict[str, object]]:
    rows = list(read_first_sheet_rows(file_path))
    if not rows:
        return []

    header = rows[0]
    field_map = {
        "名称": "name",
        "遗产类型": "heritage_type",
        "省份": "province",
        "市": "city",
        "县": "county",
        "经度": "longitude",
        "维度": "latitude",
    }

    column_map = {
        field_map[column_name]: index
        for index, column_name in enumerate(header)
        if column_name in field_map
    }

    required_fields = {"name", "heritage_type", "city", "county", "longitude", "latitude"}
    missing_fields = required_fields - set(column_map)
    if missing_fields:
        raise ValueError(f"Excel 缺少必要字段: {', '.join(sorted(missing_fields))}")

    cleaned_rows = []
    seen_keys = set()
    for source_row in rows[1:]:
        row = {
            field: normalize_text(source_row[index] if index < len(source_row) else "")
            for field, index in column_map.items()
        }
        row["province"] = normalize_text(
            source_row[column_map.get("province", -1)]
            if column_map.get("province", -1) < len(source_row)
            else ""
        )

        longitude = parse_float(row["longitude"])
        latitude = parse_float(row["latitude"])
        if not row["name"] or not row["city"] or longitude is None or latitude is None:
            continue

        unique_key = (row["name"], row["city"], row["county"], longitude, latitude)
        if unique_key in seen_keys:
            continue
        seen_keys.add(unique_key)

        row["longitude"] = longitude
        row["latitude"] = latitude
        row["address"] = "".join(
            part for part in [row["province"], row["city"], row["county"], row["name"]] if part
        )
        row["description"] = build_description(row)
        row["tags"] = ",".join(part for part in [row["heritage_type"], row["city"], row["county"]] if part)
        cleaned_rows.append(row)

    return cleaned_rows


def route_name(city: str, heritage_type: str, index: int, total: int) -> str:
    base_name = f"{city}{heritage_type}资源路线"
    if total == 1:
        return base_name
    return f"{base_name} {index}"


def route_description(city: str, heritage_type: str, count: int) -> str:
    return f"整合{city}{count}处{heritage_type}资源点，适合按地图位置串联探访河南水利遗产。"


def chunk_rows(rows: List[Dict[str, object]], size: int) -> Iterable[List[Dict[str, object]]]:
    for index in range(0, len(rows), size):
        yield rows[index : index + size]


def clear_existing_resource_routes(db) -> None:
    routes = db.query(Route).filter(Route.description.like(f"%{RESOURCE_ROUTE_PREFIX}%")).all()
    route_ids = [route.id for route in routes]
    if route_ids:
        db.query(RouteAttraction).filter(RouteAttraction.route_id.in_(route_ids)).delete(synchronize_session=False)
        db.query(Route).filter(Route.id.in_(route_ids)).delete(synchronize_session=False)

    db.query(Attraction).filter(Attraction.tags.like("%水利遗产资源点%")).delete(synchronize_session=False)


def clear_display_data(db) -> None:
    db.query(RouteAttraction).delete(synchronize_session=False)
    db.query(Route).delete(synchronize_session=False)
    db.query(Attraction).delete(synchronize_session=False)


def import_resource_points(
    file_path: Path,
    clear_existing: bool = True,
    replace_all_display_data: bool = True,
) -> Dict[str, int]:
    rows = clean_rows(file_path)
    db = SessionLocal()

    try:
        Base.metadata.create_all(bind=engine)
        if replace_all_display_data:
            clear_display_data(db)
            db.flush()
        elif clear_existing:
            clear_existing_resource_routes(db)
            db.flush()

        grouped_rows = defaultdict(list)
        for row in rows:
            grouped_rows[(row["city"], row["heritage_type"])].append(row)

        route_count = 0
        attraction_count = 0
        for (city, heritage_type), group in sorted(grouped_rows.items()):
            group.sort(key=lambda item: (str(item["county"]), str(item["name"])))
            chunks = list(chunk_rows(group, MAX_POINTS_PER_ROUTE))
            for chunk_index, chunk in enumerate(chunks, start=1):
                route = Route(
                    name=route_name(city, heritage_type, chunk_index, len(chunks)),
                    description=f"{RESOURCE_ROUTE_PREFIX}：{route_description(city, heritage_type, len(chunk))}",
                    region=city,
                    route_type=heritage_type,
                    duration="1天",
                    difficulty="简单",
                )
                db.add(route)
                db.flush()
                route_count += 1

                for order, row in enumerate(chunk, start=1):
                    attraction = Attraction(
                        name=row["name"],
                        description=row["description"],
                        address=row["address"],
                        latitude=row["latitude"],
                        longitude=row["longitude"],
                        tags=f"水利遗产资源点,{row['tags']}",
                    )
                    db.add(attraction)
                    db.flush()
                    db.add(
                        RouteAttraction(
                            route_id=route.id,
                            attraction_id=attraction.id,
                            order=order,
                        )
                    )
                    attraction_count += 1

        db.commit()
        return {"routes": route_count, "attractions": attraction_count, "source_rows": len(rows)}
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="导入美丽中原资源点 Excel 数据")
    parser.add_argument("--file", type=Path, default=DEFAULT_INPUT_FILE, help="Excel 文件路径")
    parser.add_argument("--keep-existing", action="store_true", help="保留已导入的资源点路线")
    parser.add_argument(
        "--append",
        action="store_true",
        help="追加导入，不清空现有路线、景点和关联数据",
    )
    args = parser.parse_args()

    result = import_resource_points(
        args.file,
        clear_existing=not args.keep_existing,
        replace_all_display_data=not args.append,
    )
    print(
        f"导入完成：读取 {result['source_rows']} 条资源点，"
        f"生成 {result['routes']} 条路线，导入 {result['attractions']} 个景点。"
    )


if __name__ == "__main__":
    main()
