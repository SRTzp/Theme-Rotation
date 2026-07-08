# US Sector & Theme Rotation Tracker

Dashboard ติดตาม rotation ของ 25 ธีม + 11 Sector ETFs เทียบ SPY — Rotation Map (custom RS-Ratio/RS-Momentum), Heatmap ผลตอบแทน, Momentum Playbook, Breadth & Volume — ข้อมูลอัปเดตอัตโนมัติทุกวันทำการผ่าน GitHub Actions

## โครงสร้าง

| ไฟล์ | หน้าที่ |
|---|---|
| `index.html` | หน้าเว็บทั้งหมด (self-contained ไม่มี dependency) |
| `universe.json` | รายชื่อธีม/หุ้น/ETF — **แก้ที่นี่ที่เดียว** ทั้ง pipeline และหน้าเว็บอ่านไฟล์นี้ |
| `fetch_data.py` | ดึงราคา (yfinance, adjusted close) → เขียน `data.json` |
| `.github/workflows/update-data.yml` | รัน fetch_data.py ทุกวันทำการ 22:30 UTC แล้ว commit กลับ |
| `data.json` | ราคา 220 วันทำการล่าสุด (สร้างโดย workflow ไม่ต้องแก้เอง) |

## Setup ครั้งแรก (~5 นาที)

1. สร้าง repo ใหม่บน GitHub (public) แล้วอัปโหลดไฟล์ทั้งหมดในโฟลเดอร์นี้ — โครงสร้างโฟลเดอร์ `.github/workflows/` ต้องคงไว้ตามเดิม
2. **Settings → Pages** → Source: `Deploy from a branch` → Branch: `main` / `(root)` → Save
3. **Actions tab** → ถ้ามีปุ่มให้ enable workflows ให้กด → เลือก workflow **Update data** → กด **Run workflow** (รันครั้งแรกด้วยมือเพื่อสร้าง data.json)
4. รอ workflow เขียว (~1–2 นาที) แล้วเปิด `https://<username>.github.io/<repo-name>/`

ถ้ายังไม่มี data.json หน้าเว็บจะ fallback เป็น Demo mode ให้อัตโนมัติพร้อมข้อความบอก

## แก้ universe (เพิ่ม/ลดธีม เปลี่ยนหุ้นในตะกร้า)

แก้ `universe.json` ไฟล์เดียวจบ:

```json
{ "name": "ชื่อธีม", "etfs": [["TICKER", "คำอธิบาย"]], "stocks": ["AAA", "BBB", "CCC"] }
```

commit แล้วรอรอบ workflow ถัดไป (หรือกด Run workflow เอง) — หน้าเว็บจะเห็นธีมใหม่ทันทีที่ data.json มีข้อมูลครบ ticker ที่ yfinance ไม่มีข้อมูลจะถูกตัดออกจากตะกร้าอัตโนมัติ (โชว์ `(4/5)` ท้ายชื่อ)

## ข้อควรรู้

- **Scheduled workflow ใน repo ที่ไม่มี activity 60 วันจะถูก GitHub ปิดอัตโนมัติ** — เข้า Actions tab กด re-enable เป็นครั้งคราว หรือ commit อะไรก็ได้เล็กๆ
- ตะกร้าธีมเป็น equal-weight daily-rebalanced (analytical basket) — ไม่ใช่ผลตอบแทน ETF จริง และ ETF จริงส่วนใหญ่ถ่วง market cap
- สูตร Rotation Map เป็น custom (SMA63 / ROC10) ไม่ใช่ JdK มาตรฐานของ Bloomberg/StockCharts
- เครื่องมือประกอบการวิเคราะห์ ไม่ใช่คำแนะนำซื้อขาย
