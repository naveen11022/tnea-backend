from sqlalchemy import text
from sqlalchemy.orm import Session
from typing import List, Optional


def build_in_clause(values, prefix):
    if not values:
        return "", {}
    placeholders = ", ".join(f":{prefix}_{i}" for i in range(len(values)))
    params = {f"{prefix}_{i}": v for i, v in enumerate(values)}
    return placeholders, params


def build_filter_parts(years, districts, college_types, branch_categories):
    conditions = []
    params = {}

    if years:
        ph, p = build_in_clause(years, "year")
        conditions.append(f"ca.year IN ({ph})")
        params.update(p)

    if districts:
        ph, p = build_in_clause(districts, "district")
        conditions.append(f"c.location IN ({ph})")
        params.update(p)

    if college_types:
        ph, p = build_in_clause(college_types, "ct")
        conditions.append(f"c.college_type IN ({ph})")
        params.update(p)

    if branch_categories:
        ph, p = build_in_clause(branch_categories, "bc")
        conditions.append(f"b.category IN ({ph})")
        params.update(p)

    where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
    return where, params


def get_all_districts(db: Session):
    sql = text("SELECT DISTINCT location FROM colleges WHERE location IS NOT NULL ORDER BY location ASC")
    rows = db.execute(sql).fetchall()
    return [r[0] for r in rows]


def get_branch_trends(db: Session, years, districts, college_types, branch_categories, top_n):
    where, params = build_filter_parts(years, districts, college_types, branch_categories)
    params["top_n"] = top_n

    sql = text(f"""
        WITH base AS (
            SELECT
                ca.year,
                ca.branch_code,
                b.branch_name,
                COUNT(*) AS demand_count,
                ROUND(AVG(ca.aggr_mark)::numeric, 2) AS avg_cutoff
            FROM candidate_allotment ca
            JOIN branch b ON ca.branch_code = b.branch_code
            JOIN colleges c ON ca.college_code::text = c.college_code::text
            {where}
            GROUP BY ca.year, ca.branch_code, b.branch_name
        ),
        ranked AS (
            SELECT *,
                RANK() OVER (PARTITION BY year ORDER BY demand_count DESC) AS rnk
            FROM base
        )
        SELECT year, branch_code, branch_name, demand_count, avg_cutoff, rnk
        FROM ranked
        WHERE rnk <= :top_n
        ORDER BY year ASC, demand_count DESC
    """)

    rows = db.execute(sql, params).fetchall()
    return [
        {
            "year": r.year,
            "branch_code": r.branch_code,
            "branch_name": r.branch_name,
            "demand_count": r.demand_count,
            "avg_cutoff": float(r.avg_cutoff) if r.avg_cutoff else 0.0,
            "rank": r.rnk,
        }
        for r in rows
    ]


def get_top_district_branches(db: Session, years, districts, college_types, branch_categories, top_n):
    where, params = build_filter_parts(years, districts, college_types, branch_categories)
    params["top_n"] = top_n

    sql = text(f"""
        WITH base AS (
            SELECT
                c.location AS district,
                ca.branch_code,
                b.branch_name,
                COUNT(*) AS demand_count,
                ROUND(AVG(ca.aggr_mark)::numeric, 2) AS avg_cutoff
            FROM candidate_allotment ca
            JOIN branch b ON ca.branch_code = b.branch_code
            JOIN colleges c ON ca.college_code::text = c.college_code::text
            {where}
            GROUP BY c.location, ca.branch_code, b.branch_name
        ),
        ranked AS (
            SELECT *,
                RANK() OVER (PARTITION BY district ORDER BY demand_count DESC) AS rank_in_district
            FROM base
        )
        SELECT district, branch_code, branch_name, demand_count, avg_cutoff, rank_in_district
        FROM ranked
        WHERE rank_in_district <= :top_n
        ORDER BY district ASC, rank_in_district ASC
    """)

    rows = db.execute(sql, params).fetchall()
    return [
        {
            "district": r.district,
            "branch_code": r.branch_code,
            "branch_name": r.branch_name,
            "demand_count": r.demand_count,
            "avg_cutoff": float(r.avg_cutoff) if r.avg_cutoff else 0.0,
            "rank_in_district": r.rank_in_district,
        }
        for r in rows
    ]


def get_top_year_branches(db: Session, years, districts, college_types, branch_categories, top_n):
    where, params = build_filter_parts(years, districts, college_types, branch_categories)
    params["top_n"] = top_n

    sql = text(f"""
        WITH base AS (
            SELECT
                ca.year,
                ca.branch_code,
                b.branch_name,
                COUNT(*) AS demand_count,
                ROUND(AVG(ca.aggr_mark)::numeric, 2) AS avg_cutoff
            FROM candidate_allotment ca
            JOIN branch b ON ca.branch_code = b.branch_code
            JOIN colleges c ON ca.college_code::text = c.college_code::text
            {where}
            GROUP BY ca.year, ca.branch_code, b.branch_name
        ),
        ranked AS (
            SELECT *,
                RANK() OVER (PARTITION BY year ORDER BY demand_count DESC) AS rank_in_year
            FROM base
        )
        SELECT year, branch_code, branch_name, demand_count, avg_cutoff, rank_in_year
        FROM ranked
        WHERE rank_in_year <= :top_n
        ORDER BY year DESC, rank_in_year ASC
    """)

    rows = db.execute(sql, params).fetchall()
    return [
        {
            "year": r.year,
            "branch_code": r.branch_code,
            "branch_name": r.branch_name,
            "demand_count": r.demand_count,
            "avg_cutoff": float(r.avg_cutoff) if r.avg_cutoff else 0.0,
            "rank_in_year": r.rank_in_year,
        }
        for r in rows
    ]


def get_top_college_branches(db: Session, years, districts, college_types, branch_categories, top_n):
    where, params = build_filter_parts(years, districts, college_types, branch_categories)
    params["top_n"] = top_n

    sql = text(f"""
        WITH base AS (
            SELECT
                c.college_code,
                c.college_name,
                c.location AS district,
                c.college_type,
                ca.branch_code,
                b.branch_name,
                COUNT(*) AS demand_count,
                ROUND(AVG(ca.aggr_mark)::numeric, 2) AS avg_cutoff,
                MIN(ca.aggr_mark) AS min_cutoff,
                MAX(ca.aggr_mark) AS max_cutoff
            FROM candidate_allotment ca
            JOIN branch b ON ca.branch_code = b.branch_code
            JOIN colleges c ON ca.college_code::text = c.college_code::text
            {where}
            GROUP BY c.college_code, c.college_name, c.location, c.college_type, ca.branch_code, b.branch_name
        ),
        ranked AS (
            SELECT *,
                RANK() OVER (PARTITION BY college_code ORDER BY demand_count DESC) AS rank_in_college
            FROM base
        )
        SELECT college_code, college_name, district, college_type, branch_code, branch_name,
               demand_count, avg_cutoff, min_cutoff, max_cutoff, rank_in_college
        FROM ranked
        WHERE rank_in_college <= :top_n
        ORDER BY college_name ASC, rank_in_college ASC
    """)

    rows = db.execute(sql, params).fetchall()
    return [
        {
            "college_code": str(r.college_code),
            "college_name": r.college_name,
            "district": r.district,
            "college_type": r.college_type,
            "branch_code": r.branch_code,
            "branch_name": r.branch_name,
            "demand_count": r.demand_count,
            "avg_cutoff": float(r.avg_cutoff) if r.avg_cutoff else 0.0,
            "min_cutoff": float(r.min_cutoff) if r.min_cutoff else 0.0,
            "max_cutoff": float(r.max_cutoff) if r.max_cutoff else 0.0,
            "rank_in_college": r.rank_in_college,
        }
        for r in rows
    ]


def get_dashboard_summary(db: Session):
    sql = text("""
        SELECT
            COUNT(*) AS total_allotments,
            (SELECT COUNT(DISTINCT college_code) FROM colleges) AS total_colleges,
            (SELECT COUNT(DISTINCT branch_code) FROM branch) AS total_branches,
            (SELECT COUNT(DISTINCT year) FROM candidate_allotment) AS total_years,
            ROUND(AVG(aggr_mark)::numeric, 2) AS avg_cutoff
        FROM candidate_allotment
    """)

    top_branch_sql = text("""
        SELECT b.branch_name
        FROM candidate_allotment ca
        JOIN branch b ON ca.branch_code = b.branch_code
        GROUP BY b.branch_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    top_district_sql = text("""
        SELECT c.location
        FROM candidate_allotment ca
        JOIN colleges c ON ca.college_code::text = c.college_code::text
        WHERE ca.college_code ~ '^[0-9]+$'
        GROUP BY c.location
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    top_college_sql = text("""
        SELECT c.college_name
        FROM candidate_allotment ca
        JOIN colleges c ON ca.college_code::text = c.college_code::text
        WHERE ca.college_code ~ '^[0-9]+$'
        GROUP BY c.college_name
        ORDER BY COUNT(*) DESC
        LIMIT 1
    """)

    row = db.execute(sql).fetchone()
    top_branch = db.execute(top_branch_sql).scalar()
    top_district = db.execute(top_district_sql).scalar()
    top_college = db.execute(top_college_sql).scalar()

    return {
        "total_allotments": row.total_allotments,
        "total_colleges": row.total_colleges,
        "total_branches": row.total_branches,
        "total_years": row.total_years,
        "avg_cutoff": float(row.avg_cutoff) if row.avg_cutoff else 0.0,
        "top_branch": top_branch or "",
        "top_district": top_district or "",
        "top_college": top_college or "",
    }


def get_seat_filling_speed(db: Session, years, districts, college_types, branch_categories):
    where, params = build_filter_parts(years, districts, college_types, branch_categories)

    sql = text(f"""
        WITH round_data AS (
            SELECT
                ca.year,
                ca.branch_code,
                b.branch_name,
                CAST(ca.college_code AS VARCHAR) AS college_code,
                c.college_name,
                c.location AS district,
                c.college_type,
                ca.round,
                COUNT(*) AS allotments_in_round,
                ROUND(AVG(ca.aggr_mark)::numeric, 2) AS avg_cutoff_round,
                MAX(ca.aggr_mark) AS max_cutoff_round,
                MIN(ca.aggr_mark) AS min_cutoff_round
            FROM candidate_allotment ca
            JOIN branch b ON ca.branch_code = b.branch_code
            JOIN colleges c ON ca.college_code::text = c.college_code::text
            {where}
            GROUP BY ca.year, ca.branch_code, b.branch_name, ca.college_code, c.college_name,
                     c.location, c.college_type, ca.round
        ),
        branch_totals AS (
            SELECT
                year,
                branch_code,
                branch_name,
                SUM(allotments_in_round) AS total_allotments
            FROM round_data
            GROUP BY year, branch_code, branch_name
        ),
        with_cumulative AS (
            SELECT
                rd.*,
                bt.total_allotments,
                SUM(rd.allotments_in_round) OVER (
                    PARTITION BY rd.year, rd.branch_code
                    ORDER BY rd.round
                    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
                ) AS cumulative_allotments,
                RANK() OVER (
                    PARTITION BY rd.year, rd.branch_code
                    ORDER BY rd.round
                ) AS round_number
            FROM round_data rd
            JOIN branch_totals bt
                ON rd.year = bt.year AND rd.branch_code = bt.branch_code
        )
        SELECT
            year,
            branch_code,
            branch_name,
            college_code,
            college_name,
            district,
            college_type,
            round,
            round_number,
            allotments_in_round,
            cumulative_allotments,
            total_allotments,
            avg_cutoff_round,
            max_cutoff_round,
            min_cutoff_round,
            ROUND(cumulative_allotments::numeric / NULLIF(total_allotments, 0) * 100, 2) AS fill_pct
        FROM with_cumulative
        ORDER BY year DESC, total_allotments DESC, round_number ASC
    """)

    rows = db.execute(sql, params).fetchall()
    return [
        {
            "year": r.year,
            "branch_code": r.branch_code,
            "branch_name": r.branch_name,
            "college_code": r.college_code,
            "college_name": r.college_name,
            "district": r.district,
            "college_type": r.college_type,
            "round": r.round,
            "round_number": r.round_number,
            "allotments_in_round": r.allotments_in_round,
            "cumulative_allotments": r.cumulative_allotments,
            "total_allotments": r.total_allotments,
            "avg_cutoff_round": float(r.avg_cutoff_round) if r.avg_cutoff_round else 0.0,
            "max_cutoff_round": float(r.max_cutoff_round) if r.max_cutoff_round else 0.0,
            "min_cutoff_round": float(r.min_cutoff_round) if r.min_cutoff_round else 0.0,
            "fill_pct": float(r.fill_pct) if r.fill_pct else 0.0,
            "cumulative_allotments": int(r.cumulative_allotments) if r.cumulative_allotments else 0,
            "total_allotments": int(r.total_allotments) if r.total_allotments else 0,
        }
        for r in rows
    ]


def get_training_data_for_branch(db: Session, branch_code: str, district: Optional[str], college_type: Optional[str]):
    conditions = ["ca.branch_code = :branch_code"]
    params: dict = {"branch_code": branch_code}

    if district:
        conditions.append("c.location = :district")
        params["district"] = district

    if college_type:
        conditions.append("c.college_type = :college_type")
        params["college_type"] = college_type

    where = "WHERE " + " AND ".join(conditions)

    sql = text(f"""
        SELECT
            ca.year,
            ca.branch_code,
            c.location AS district,
            c.college_type,
            COUNT(*) AS allotment_count,
            ROUND(AVG(ca.aggr_mark)::numeric, 2) AS avg_cutoff
        FROM candidate_allotment ca
        JOIN colleges c ON ca.college_code::text = c.college_code::text
        {where}
        GROUP BY ca.year, ca.branch_code, c.location, c.college_type
        ORDER BY ca.year ASC
    """)

    rows = db.execute(sql, params).fetchall()
    return [
        {
            "year": r.year,
            "branch_code": r.branch_code,
            "region": r.district,
            "college_type": r.college_type,
            "allotment_count": r.allotment_count,
            "avg_cutoff": float(r.avg_cutoff) if r.avg_cutoff else 0.0,
        }
        for r in rows
    ]


def get_branch_name_by_code(db: Session, branch_code: str) -> str:
    sql = text("SELECT branch_name FROM branch WHERE branch_code = :code LIMIT 1")
    result = db.execute(sql, {"code": branch_code}).scalar()
    return result or branch_code

