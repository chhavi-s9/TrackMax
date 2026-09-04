"""Populate MySQL with internally consistent synthetic demo data."""

from __future__ import annotations

import json
from datetime import date, datetime, timedelta
from pathlib import Path

from sqlalchemy import delete, select, text

from app.database import SessionLocal, ensure_database, engine
from app.ml.risk_model import train_demo_model
from app.models.asset import Asset
from app.models.department import Department
from app.models.maintenance_block import MaintenanceBlock
from app.models.maintenance_task import MaintenanceTask
from app.models.resource import Resource
from app.models.train import Train
from app.models.train_schedule import TrainSchedule
from app.models.weather import WeatherRecord
from app.services.external_data import DATA_DIR, load_defect_sources, load_json

SECTIONS = ["JP-AII", "JP-GAD", "AII-MJ", "JP-BKI"]
AS_OF = date(2026, 9, 5)


def _wipe(db) -> None:
    db.execute(delete(MaintenanceTask))
    db.execute(delete(TrainSchedule))
    db.execute(delete(WeatherRecord))
    db.execute(delete(Resource))
    db.execute(delete(Asset))
    db.execute(delete(MaintenanceBlock))
    db.execute(delete(Train))
    db.execute(delete(Department))
    db.commit()


def seed() -> None:
    ensure_database()
    db = SessionLocal()
    try:
        _wipe(db)
        departments = _departments(db)
        assets = _assets(db, departments)
        _resources(db, departments)
        trains = _trains(db)
        _schedules(db, trains)
        blocks = _blocks(db)
        _tasks(db, departments, assets, blocks)
        _weather(db)
        db.commit()
        print("Departments inserted")
        print("Assets inserted")
        print("Maintenance tasks inserted")
        print("Resources inserted")
        print("Trains inserted")
        print("Schedules inserted")
        print("Blocks inserted")
    finally:
        db.close()
    train_demo_model()
    print("Demonstration risk model trained (synthetic data only)")


def _departments(db) -> dict[str, Department]:
    rows = [
        Department(name="Engineering / Track", code="ENG", description="Permanent way and works"),
        Department(name="Signal & Telecommunication", code="SNT", description="Signalling and telecom"),
        Department(name="Traction / Electrical", code="TRD", description="OHE and traction distribution"),
        Department(name="Mechanical", code="MECH", description="Rolling stock and workshops"),
    ]
    db.add_all(rows)
    db.flush()
    return {row.code: row for row in rows}


def _assets(db, departments: dict[str, Department]) -> dict[str, Asset]:
    specs = [
        ("TRK-JP-AII-12", "track", "Up line km 12-18", "JP-AII", "ENG", "HIGH", 62, 4),
        ("TRK-JP-AII-18", "drainage", "Cutting drain km 18", "JP-AII", "ENG", "CRITICAL", 48, 6),
        ("TRK-JP-GAD-04", "track", "Curve km 7-9", "JP-GAD", "ENG", "MEDIUM", 71, 2),
        ("TRK-AII-MJ-09", "embankment", "Embankment km 9", "AII-MJ", "ENG", "HIGH", 58, 3),
        ("TRK-JP-BKI-03", "rail", "Plain track km 3-6", "JP-BKI", "ENG", "HIGH", 64, 2),
        ("SIG-JP-AII-P12", "point_machine", "Point Machine P12", "JP-AII", "SNT", "CRITICAL", 41, 7),
        ("SIG-JP-AII-H04", "signal", "Home signal H04", "JP-AII", "SNT", "HIGH", 55, 3),
        ("SIG-JP-GAD-T02", "track_circuit", "Track circuit T02", "JP-GAD", "SNT", "MEDIUM", 73, 1),
        ("SIG-JP-BKI-C01", "telecom", "Control cable C01", "JP-BKI", "SNT", "MEDIUM", 80, 1),
        ("SIG-AII-MJ-P07", "point_machine", "Point Machine P07", "AII-MJ", "SNT", "HIGH", 52, 5),
        ("OHE-JP-AII-22", "ohe", "OHE stagger km 22", "JP-AII", "TRD", "HIGH", 60, 3),
        ("OHE-JP-AII-11", "isolator", "Isolator 11", "JP-AII", "TRD", "MEDIUM", 77, 1),
        ("OHE-JP-GAD-05", "contact_wire", "Contact wire km 5", "JP-GAD", "TRD", "LOW", 85, 0),
        ("TSS-AII-MJ-01", "substation", "TSS Ajmer approach", "AII-MJ", "TRD", "HIGH", 66, 2),
        ("OHE-JP-BKI-08", "section_insulator", "Section insulator 8", "JP-BKI", "TRD", "MEDIUM", 74, 1),
        ("RSM-JP-AII-01", "coach", "IOH spare rake", "JP-AII", "MECH", "MEDIUM", 70, 2),
        ("RSM-JP-GAD-02", "wagon", "Freight examination", "JP-GAD", "MECH", "LOW", 82, 0),
        ("TRK-JP-AII-05", "points", "Turnout 05", "JP-AII", "ENG", "HIGH", 57, 4),
        ("SIG-JP-GAD-S08", "signal", "Starter S08", "JP-GAD", "SNT", "MEDIUM", 69, 2),
        ("OHE-AII-MJ-14", "ohe", "OHE portal 14", "AII-MJ", "TRD", "HIGH", 61, 3),
    ]
    assets: dict[str, Asset] = {}
    for i, (code, atype, name, section, dept, crit, cond, fails) in enumerate(specs):
        asset = Asset(
            asset_code=code,
            asset_type=atype,
            name=name,
            section=section,
            location=f"{section} km marker {i + 1}",
            department_id=departments[dept].id,
            installation_date=date(2008 + (i % 12), 3, 1),
            last_maintenance_date=AS_OF - timedelta(days=20 + i * 7),
            next_maintenance_due=AS_OF + timedelta(days=(i % 15) - 4),
            condition_score=cond,
            failure_count=fails,
            criticality=crit,
            status="DEGRADED" if cond < 60 else "OPERATIONAL",
        )
        db.add(asset)
        assets[code] = asset
    db.flush()
    return assets


def _resources(db, departments: dict[str, Department]) -> None:
    rows = [
        ("RES-ENG-AII-1", "Track machine gang A", "track_gang", "ENG", "JP-AII"),
        ("RES-ENG-GAD-1", "P.Way gang B", "track_gang", "ENG", "JP-GAD"),
        ("RES-SNT-AII-1", "S&T team 1", "snt_team", "SNT", "JP-AII"),
        ("RES-SNT-BKI-1", "S&T team 2", "snt_team", "SNT", "JP-BKI"),
        ("RES-TRD-AII-1", "OHE tower wagon", "tower_wagon", "TRD", "JP-AII"),
        ("RES-TRD-MJ-1", "TRD maintenance squad", "trd_squad", "TRD", "AII-MJ"),
        ("RES-MECH-AII-1", "Mechanical fitters", "mech_gang", "MECH", "JP-AII"),
        ("RES-ENG-MJ-1", "Engineering gang C", "track_gang", "ENG", "AII-MJ"),
        ("RES-SNT-GAD-1", "S&T team 3", "snt_team", "SNT", "JP-GAD"),
        ("RES-TRD-BKI-1", "OHE team Bandikui", "tower_wagon", "TRD", "JP-BKI"),
    ]
    start = datetime(2026, 9, 1, 0, 0, 0)
    end = datetime(2026, 9, 30, 23, 59, 0)
    for code, name, rtype, dept, section in rows:
        db.add(
            Resource(
                resource_code=code,
                name=name,
                resource_type=rtype,
                department_id=departments[dept].id,
                section=section,
                capacity=1,
                status="AVAILABLE",
                available_from=start,
                available_until=end,
            )
        )
    db.flush()


def _trains(db) -> list[Train]:
    specs = [
        ("12956", "Jaipur Superfast", "EXPRESS", "HIGH"),
        ("12015", "Shatabdi", "EXPRESS", "CRITICAL"),
        ("19707", "Aravali Express", "EXPRESS", "HIGH"),
        ("12413", "Pooja Express", "EXPRESS", "HIGH"),
        ("54807", "Jaipur Passenger", "PASSENGER", "MEDIUM"),
        ("59705", "Ajmer Passenger", "PASSENGER", "MEDIUM"),
        ("04801", "Bandikui Passenger", "PASSENGER", "LOW"),
        ("12307", "Howrah Jodhpur", "EXPRESS", "HIGH"),
        ("19666", "Udaipur Express", "EXPRESS", "MEDIUM"),
        ("22987", "Ajmer SF", "EXPRESS", "HIGH"),
        ("16507", "Jodhpur Express", "EXPRESS", "MEDIUM"),
        ("G-JP-01", "Container freight", "FREIGHT", "MEDIUM"),
        ("G-AII-02", "Coal rake", "FREIGHT", "LOW"),
        ("G-BKI-03", "Mixed freight", "FREIGHT", "LOW"),
        ("02985", "Special", "OTHER", "LOW"),
    ]
    trains = [
        Train(
            train_number=num,
            train_name=name,
            train_type=ttype,
            priority=prio,
            operating_status="ACTIVE",
        )
        for num, name, ttype, prio in specs
    ]
    db.add_all(trains)
    db.flush()
    return trains


def _schedules(db, trains: list[Train]) -> None:
    """Generate 100+ internally consistent section movements."""
    # Leave night/afternoon gaps so maintenance windows exist.
    patterns = {
        "JP-AII": [(6, 15), (8, 40), (11, 20), (16, 10), (18, 45), (20, 30)],
        "JP-GAD": [(6, 40), (9, 10), (12, 0), (17, 20), (19, 50)],
        "AII-MJ": [(7, 5), (10, 15), (15, 40), (19, 10), (21, 0)],
        "JP-BKI": [(5, 50), (8, 5), (11, 50), (16, 55), (20, 5)],
    }
    count = 0
    for day_offset in range(8):
        day = AS_OF + timedelta(days=day_offset)
        for section, slots in patterns.items():
            for idx, (hour, minute) in enumerate(slots):
                train = trains[(count + idx) % len(trains)]
                arrival = datetime(day.year, day.month, day.day, hour, minute, 0)
                dwell = 12 if train.train_type != "FREIGHT" else 20
                db.add(
                    TrainSchedule(
                        train_id=train.id,
                        section=section,
                        arrival_time=arrival,
                        departure_time=arrival + timedelta(minutes=dwell),
                        schedule_date=day,
                    )
                )
                count += 1
    db.flush()
    assert count >= 100


def _blocks(db) -> list[MaintenanceBlock]:
    rows = []
    specs = [
        ("BLK-JP-AII-01", "JP-AII", datetime(2026, 9, 5, 1, 0), datetime(2026, 9, 5, 3, 0), "APPROVED"),
        ("BLK-JP-AII-02", "JP-AII", datetime(2026, 9, 6, 22, 30), datetime(2026, 9, 6, 23, 50), "PROPOSED"),
        ("BLK-JP-GAD-01", "JP-GAD", datetime(2026, 9, 5, 2, 0), datetime(2026, 9, 5, 4, 0), "APPROVED"),
        ("BLK-JP-GAD-02", "JP-GAD", datetime(2026, 9, 8, 14, 0), datetime(2026, 9, 8, 16, 0), "PROPOSED"),
        ("BLK-AII-MJ-01", "AII-MJ", datetime(2026, 9, 5, 1, 30), datetime(2026, 9, 5, 4, 0), "ACTIVE"),
        ("BLK-AII-MJ-02", "AII-MJ", datetime(2026, 9, 9, 12, 30), datetime(2026, 9, 9, 14, 30), "PROPOSED"),
        ("BLK-JP-BKI-01", "JP-BKI", datetime(2026, 9, 5, 2, 0), datetime(2026, 9, 5, 4, 30), "APPROVED"),
        ("BLK-JP-BKI-02", "JP-BKI", datetime(2026, 9, 7, 15, 0), datetime(2026, 9, 7, 17, 0), "PROPOSED"),
        ("BLK-JP-AII-03", "JP-AII", datetime(2026, 9, 10, 13, 0), datetime(2026, 9, 10, 15, 0), "PROPOSED"),
        ("BLK-JP-GAD-03", "JP-GAD", datetime(2026, 9, 11, 0, 30), datetime(2026, 9, 11, 3, 30), "PROPOSED"),
    ]
    for code, section, start, end, status in specs:
        block = MaintenanceBlock(
            block_code=code,
            section=section,
            start_time=start,
            end_time=end,
            duration_minutes=int((end - start).total_seconds() // 60),
            status=status,
            block_type="MAINTENANCE",
        )
        db.add(block)
        rows.append(block)
    db.flush()
    return rows


def _resource_type_for(source: str, dept_code: str) -> str:
    if dept_code == "SNT":
        return "snt_team"
    if dept_code == "TRD":
        return "tower_wagon"
    if dept_code == "MECH":
        return "mech_gang"
    return "track_gang"


def _tasks(db, departments, assets: dict[str, Asset], blocks: list[MaintenanceBlock]) -> None:
    defects = load_defect_sources()
    extra = [
        {
            "task_code": "INT-JP-AII-M01",
            "section": "JP-AII",
            "asset_code": "RSM-JP-AII-01",
            "task_type": "mechanical inspection",
            "description": "Coach IOH related pit attention",
            "priority": "LOW",
            "duration_minutes": 60,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-AII-E01",
            "section": "JP-AII",
            "asset_code": "TRK-JP-AII-05",
            "task_type": "turnout inspection",
            "description": "Turnout 05 geometry and welding check",
            "priority": "HIGH",
            "duration_minutes": 90,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-GAD-S01",
            "section": "JP-GAD",
            "asset_code": "SIG-JP-GAD-S08",
            "task_type": "signal visibility",
            "description": "Starter signal visibility in fog-prone stretch",
            "priority": "MEDIUM",
            "duration_minutes": 45,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-AII-MJ-O01",
            "section": "AII-MJ",
            "asset_code": "OHE-AII-MJ-14",
            "task_type": "OHE tension check",
            "description": "Portal 14 stagger and tension",
            "priority": "HIGH",
            "duration_minutes": 100,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-BKI-T01",
            "section": "JP-BKI",
            "asset_code": "TRK-JP-BKI-03",
            "task_type": "track inspection",
            "description": "Routine inspection plus temperature watch",
            "priority": "MEDIUM",
            "duration_minutes": 80,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-GAD-M01",
            "section": "JP-GAD",
            "asset_code": "RSM-JP-GAD-02",
            "task_type": "wagon examination",
            "description": "Freight examination siding",
            "priority": "LOW",
            "duration_minutes": 50,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-AII-D01",
            "section": "JP-AII",
            "asset_code": "TRK-JP-AII-18",
            "task_type": "track stability",
            "description": "Follow-up after drainage complaint",
            "priority": "CRITICAL",
            "duration_minutes": 110,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-AII-MJ-S01",
            "section": "AII-MJ",
            "asset_code": "SIG-AII-MJ-P07",
            "task_type": "S&T inspection",
            "description": "Repeat failure investigation",
            "priority": "HIGH",
            "duration_minutes": 95,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-BKI-E01",
            "section": "JP-BKI",
            "asset_code": "OHE-JP-BKI-08",
            "task_type": "electrical insulation",
            "description": "Insulation resistance after rain",
            "priority": "MEDIUM",
            "duration_minutes": 70,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-JP-GAD-G01",
            "section": "JP-GAD",
            "asset_code": "TRK-JP-GAD-04",
            "task_type": "hot work welding",
            "description": "Thermit welding on curve (weather-sensitive)",
            "priority": "MEDIUM",
            "duration_minutes": 140,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "TMS-JP-AII-003",
            "section": "JP-AII",
            "asset_code": "TRK-JP-AII-12",
            "task_type": "track inspection",
            "description": "Additional inspection due after failure count rise",
            "priority": "HIGH",
            "duration_minutes": 75,
            "source_system": "TMS",
        },
        {
            "task_code": "SMMS-JP-AII-003",
            "section": "JP-AII",
            "asset_code": "SIG-JP-AII-P12",
            "task_type": "point machine inspection",
            "description": "Detection media replacement",
            "priority": "CRITICAL",
            "duration_minutes": 85,
            "source_system": "SMMS",
        },
        {
            "task_code": "TDMS-JP-GAD-002",
            "section": "JP-GAD",
            "asset_code": "OHE-JP-GAD-05",
            "task_type": "OHE tension check",
            "description": "Seasonal tension adjustment",
            "priority": "MEDIUM",
            "duration_minutes": 90,
            "source_system": "TDMS",
        },
        {
            "task_code": "INT-JP-AII-F01",
            "section": "JP-AII",
            "asset_code": "SIG-JP-AII-H04",
            "task_type": "signal visibility",
            "description": "Fog-related aspect check",
            "priority": "HIGH",
            "duration_minutes": 55,
            "source_system": "INTERNAL",
        },
        {
            "task_code": "INT-AII-MJ-D01",
            "section": "AII-MJ",
            "asset_code": "TRK-AII-MJ-09",
            "task_type": "drainage",
            "description": "Catchwater drain desilting",
            "priority": "HIGH",
            "duration_minutes": 120,
            "source_system": "INTERNAL",
        },
    ]
    all_defects = defects + extra
    dept_by_asset = {}
    for asset in assets.values():
        dept_by_asset[asset.asset_code] = asset

    existing_block = next(b for b in blocks if b.block_code == "BLK-JP-AII-01")
    created = 0
    for i, item in enumerate(all_defects):
        asset = dept_by_asset[item["asset_code"]]
        dept_code = next(code for code, dep in departments.items() if dep.id == asset.department_id)
        status = "PENDING"
        block_id = None
        if item["task_code"] == "TMS-JP-AII-001":
            status = "SCHEDULED"
            block_id = existing_block.id
        db.add(
            MaintenanceTask(
                task_code=item["task_code"],
                asset_id=asset.id,
                department_id=asset.department_id,
                source_system=item["source_system"],
                task_type=item["task_type"],
                description=item["description"],
                section=item["section"],
                priority=item["priority"],
                estimated_duration_minutes=item["duration_minutes"],
                due_date=AS_OF + timedelta(days=(i % 12) - 3),
                status=status,
                required_resource_type=_resource_type_for(item["source_system"], dept_code),
                block_id=block_id,
            )
        )
        created += 1
    db.flush()
    assert created >= 30


def _weather(db) -> None:
    for fname, wtype in [
        ("weather_normal.json", "NORMAL"),
        ("weather_heavy_rain.json", "HEAVY_RAIN"),
        ("weather_heatwave.json", "HEATWAVE"),
    ]:
        payload = load_json(fname)
        for row in payload["sections"]:
            if wtype != "NORMAL" and row["section"] != "JP-AII":
                continue
            if wtype != "NORMAL":
                continue
            db.add(
                WeatherRecord(
                    section=row["section"],
                    date=date.fromisoformat(row["date"]),
                    weather_type=payload["weather_type"],
                    severity=row["severity"],
                    rainfall=row.get("rainfall"),
                    temperature=row.get("temperature"),
                    visibility=row.get("visibility"),
                    description=row.get("description"),
                )
            )
    db.add(
        WeatherRecord(
            section="JP-AII",
            date=AS_OF,
            weather_type="FOG",
            severity=45,
            rainfall=0,
            temperature=16,
            visibility=0.4,
            description="Synthetic fog scenario stored for demo",
        )
    )
    db.flush()


def main() -> None:
    seed()


if __name__ == "__main__":
    main()
