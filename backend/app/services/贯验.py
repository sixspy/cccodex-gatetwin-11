from app.db import 连接
from app.seed import 此刻


def 跑贯验() -> dict:
    """行程账与刷卡点互证：每笔已成对行程对应两笔已成对刷卡；旁路/开腿命运自洽。"""
    conn = 连接()
    try:
        问题 = []
        刷卡数 = conn.execute("SELECT COUNT(*) FROM 刷卡点").fetchone()[0]
        行程 = conn.execute("SELECT * FROM 行程账 WHERE 状态='已成对'").fetchall()
        开腿数 = conn.execute("SELECT COUNT(*) FROM 开腿账 WHERE 状态='在途'").fetchone()[0]
        旁路数 = conn.execute("SELECT COUNT(*) FROM 旁路匣").fetchone()[0]

        for t in 行程:
            进 = conn.execute(
                "SELECT * FROM 刷卡点 WHERE 事件编号=?", (t["进站事件编号"],)
            ).fetchone()
            出 = conn.execute(
                "SELECT * FROM 刷卡点 WHERE 事件编号=?", (t["出站事件编号"],)
            ).fetchone()
            if not 进 or not 出:
                问题.append(f"行程{t['行程键']}缺刷卡点")
                continue
            if 进["命运"] != "已成对" or 出["命运"] != "已成对":
                问题.append(f"行程{t['行程键']}刷卡命运非已成对")
            if 进["行程键"] != t["行程键"] or 出["行程键"] != t["行程键"]:
                问题.append(f"行程{t['行程键']}刷卡行程键不一致")
            if 进["卡号"] != t["卡号"] or 出["卡号"] != t["卡号"]:
                问题.append(f"行程{t['行程键']}卡号不一致")
            if 进["方向"] != "进站" or 出["方向"] != "出站":
                问题.append(f"行程{t['行程键']}方向不配对")

        成对刷 = conn.execute(
            "SELECT COUNT(*) FROM 刷卡点 WHERE 命运='已成对'"
        ).fetchone()[0]
        if 成对刷 != len(行程) * 2:
            问题.append(f"已成对刷卡{成对刷} ≠ 行程{len(行程)}×2")

        开腿刷 = conn.execute(
            "SELECT COUNT(*) FROM 刷卡点 WHERE 命运='已开腿'"
        ).fetchone()[0]
        if 开腿刷 != 开腿数:
            问题.append(f"已开腿刷卡{开腿刷} ≠ 在途开腿{开腿数}")

        # 多卡隔离协同:行程两端卡号互查(跨卡不得成对) + 隔离判定 valid 全通
        跨卡行程 = conn.execute(
            """SELECT COUNT(*) FROM 行程账 t
               JOIN 刷卡点 a ON a.事件编号=t.进站事件编号
               JOIN 刷卡点 b ON b.事件编号=t.出站事件编号
               WHERE a.卡号<>b.卡号"""
        ).fetchone()[0]
        if 跨卡行程:
            问题.append(f"跨卡成对行程{跨卡行程}笔(两端卡号不一致)")
        隔离判定数 = 0
        if conn.execute(
            "SELECT 1 FROM sqlite_master WHERE type='table' AND name='多卡隔离'"
        ).fetchone():
            隔离判定数 = conn.execute("SELECT COUNT(*) FROM 多卡隔离").fetchone()[0]
            坏 = conn.execute("SELECT COUNT(*) FROM 多卡隔离 WHERE valid=0").fetchone()[0]
            if 坏:
                问题.append(f"多卡隔离valid=0判定{坏}笔(写闸拦截未闭)")

        通过 = 1 if not 问题 else 0
        说明 = "行程账与刷卡点互证通过" if 通过 else "；".join(问题)[:800]
        conn.execute(
            """INSERT INTO 行程贯验(时刻,刷卡数,行程数,开腿数,旁路数,是否通过,说明)
               VALUES (?,?,?,?,?,?,?)""",
            (此刻(), 刷卡数, len(行程), 开腿数, 旁路数, 通过, 说明),
        )
        conn.commit()
        return {
            "是否通过": bool(通过),
            "刷卡数": 刷卡数,
            "行程数": len(行程),
            "开腿数": 开腿数,
            "旁路数": 旁路数,
            "隔离判定数": 隔离判定数,
            "说明": 说明,
            "问题": 问题,
        }
    finally:
        conn.close()
