// ทดสอบ: (1) chess.js ใช้ได้ + เข้าป้อมถูกต้อง  (2) สคริปต์ใน index.html syntax ถูก
import fs from "node:fs";
import path from "node:path";

const D = "E:/Hermes_workbench/50_research/2026-10-10_chess-app";
const { Chess } = await import("file:///" + D + "/lib/chess.js");

const g = new Chess();
console.log("FEN เริ่ม:", g.fen());

// เล่นตามลำดับเพื่อเปิดทางเข้าป้อม (เหมือนที่ผู้ใช้ทำบนจอ)
const seq = ["e4","e5","Nf3","Nc6","Bc4","Bc5"];
for (const s of seq) { const m = g.move(s); if(!m) throw new Error("เดินไม่ได้: "+s); }
console.log("หลัง 6 ตา:", g.fen());

// 1) ตรวจว่าคิง e1 มีช่องเดินได้รวม g1 (เข้าป้อมปีกคิง)
const kingMoves = g.moves({ square: "e1", verbose: true });
const castle = kingMoves.filter(m => m.flags.includes("k") || m.flags.includes("q"));
console.log("เข้าป้อมที่คิงทำได้:", castle.map(m => m.to + " (" + m.flags + ")").join(", ") || "ไม่มี");
console.log("มี g1 =", castle.some(m => m.to === "g1"));

// 2) เดินเข้าป้อมจริง และดูว่า SAN ออกเป็น O-O
const mv = g.move({ from: "e1", to: "g1" });
console.log("เดิน O-O ->", mv.san, "| flags:", mv.flags, "| FEN:", g.fen());
console.log("คิงอยู่ g1 =", g.get("g1") && g.get("g1").type === "k", "| เรืออยู่ f1 =", g.get("f1") && g.get("f1").type === "r");
console.log("ประวัติการเดิน:", g.history().join(" "));

// 3) เข้าป้อมยาว (ดำ) เพื่อความชัวร์
const g2 = new Chess("r3k2r/pppppppp/8/8/8/8/PPPPPPPP/R3K2R b KQkq - 0 1");
const m2 = g2.move({ from: "e8", to: "c8" });
console.log("\nเข้าป้อมยาวดำ:", m2 && m2.san, "| FEN:", g2.fen(), "| คิง c8 =", !!g2.get("c8"));

// 4) syntax ของสคริปต์ใน index.html
const html = fs.readFileSync(path.join(D, "index.html"), "utf8");
const m = html.match(/<script type="module">([\s\S]*?)<\/script>/);
if (!m) { console.log("\nไม่พบสคริปต์ module ✗"); }
else {
  fs.writeFileSync(path.join(D, "_appcheck.mjs"), m[1].replace(/from '\.\/lib\/chess\.js'/, `from 'file:///${D}/lib/chess.js'`));
  console.log("\nเขียน _appcheck.mjs แล้ว (" + m[1].length + " ตัวอักษร) — ตรวจ syntax ด้วย node --check");
}
