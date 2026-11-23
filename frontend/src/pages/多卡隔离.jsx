import React, { useEffect, useState } from "react";
import { 取, 递 } from "../api.js";

const 夹具 = ["多卡隔离-A进B出", "多卡隔离-A进A出", "多卡隔离-并发双卡"];

export default function 多卡隔离() {
  const [行, 设行] = useState([]);
  const [架, 设架] = useState(null);
  const [讯, 设讯] = useState("");
  const 刷 = () => {
    取("/多卡隔离").then(设行);
    取("/多卡隔离/架构").then(设架);
  };
  useEffect(() => { 刷(); }, []);
  const 灌 = async (名) => {
    设讯("装载中…");
    try {
      const r = await 递(`/多卡隔离/装载/夹具?名=${encodeURIComponent(名)}`);
      设讯(
        `批次 ${r.批次编号}〔${r.架构}·批命运=${r.批命运}〕：` +
        `入流${r.入流} 开腿${r.开腿} 成对${r.成对} 旁路${r.旁路} 跨卡隔离${r.跨卡隔离}`
      );
      await 刷();
    } catch (e) {
      设讯(String(e.message || e));
    }
  };
  return (
    <div>
      <h1 className="题">多卡隔离</h1>
      <p className="述">
        出站只匹配<strong>本卡</strong>在途开腿，跨卡不得成对。卡A在途时灌卡B出站：
        B同票进旁路匣（跨卡无开腿），A开腿仍在途，批命运=继续。
      </p>
      {架 && (
        <div className="提示条">
          全局架构：<strong>{架.架构}</strong>（只贯彻一种）· {架.口径}
        </div>
      )}
      <div className="行">
        {夹具.map((n) => (
          <button key={n} className="次 亮片" onClick={() => 灌(n)}>{n}</button>
        ))}
        <button className="次" onClick={刷}>刷新</button>
      </div>
      {讯 && <p className="讯">{讯}</p>}
      {!行.length ? (
        <div className="空态">尚无隔离判定。灌「多卡隔离-A进B出」看跨卡出站旁路。</div>
      ) : (
        <table>
          <thead>
            <tr>
              <th>#</th><th>批次</th><th>出站事件</th><th>出站卡</th><th>候选开腿卡</th>
              <th>批命运</th><th>旁路或回滚证据</th><th>valid</th><th>时刻</th>
            </tr>
          </thead>
          <tbody>
            {行.map((r) => (
              <tr key={r.编号}>
                <td>{r.编号}</td><td>{r.批次编号}</td><td>{r.出站事件编号}</td>
                <td>{r.出站卡}</td>
                <td>
                  {r.候选开腿卡 || "—"}
                  {r.候选开腿卡 && r.候选开腿卡 !== r.出站卡 && (
                    <span className="徽章 败" style={{ marginLeft: "0.4rem" }}>跨卡</span>
                  )}
                </td>
                <td>{r.批命运}</td>
                <td style={{ maxWidth: 360, wordBreak: "break-all" }}>{r.证据}</td>
                <td><span className={`徽章 ${r.valid ? "通" : "败"}`}>{r.valid ? "valid" : "invalid"}</span></td>
                <td>{r.时刻}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
