import os
import json
import time
import urllib.request
from fastapi import FastAPI, BackgroundTasks, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI(title="Villa Inspector Proxy & Sync")

DEFAULT_GAS_URL = "https://script.google.com/macros/s/AKfycbzSHV9lCQxvSNii1_5g3q_S0bvsWV7Z4TXMPLqgS2JJtKWxxY6cegy5MSaylHuoDStQqw/exec"
DATA_FILE = "/app/data/villas.json"

# Khoi tao cache tu disk neu co
villas_cache = {
    "status": "success",
    "total": 0,
    "villas": {},
    "last_synced": 0
}

def load_disk_cache():
    global villas_cache
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                villas_cache = json.load(f)
        except Exception as e:
            print("Error loading disk cache:", e)

def save_disk_cache():
    try:
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(villas_cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print("Error saving disk cache:", e)

load_disk_cache()

def fetch_gas_villas():
    global villas_cache
    try:
        req = urllib.request.Request(DEFAULT_GAS_URL, headers={"User-Agent": "Creek-VPS/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("status") == "success" and "villas" in data:
                villas_cache["status"] = "success"
                villas_cache["total"] = data.get("total", len(data["villas"]))
                villas_cache["villas"] = data["villas"]
                villas_cache["last_synced"] = int(time.time())
                save_disk_cache()
                print(f"Synced {villas_cache['total']} villas from Google Sheets.")
    except Exception as e:
        print("Error fetching from GAS:", e)

@app.on_event("startup")
def startup_event():
    # Sync ngay khi server khoi dong
    fetch_gas_villas()

@app.get("/api/villas")
def get_villas(background_tasks: BackgroundTasks):
    # Tra ve cache RAM ngay lap tuc (0.01 giay)
    # Neu cache da cu hon 60 giay thi trigger background sync tu Google Sheet
    now = int(time.time())
    if now - villas_cache.get("last_synced", 0) > 60:
        background_tasks.add_task(fetch_gas_villas)
    return villas_cache

@app.post("/api/sync-now")
def sync_now():
    fetch_gas_villas()
    return villas_cache

@app.post("/api/upload")
async def proxy_upload(request: Request, background_tasks: BackgroundTasks):
    # Nhan anh tu client, forward sang Google Apps Script
    try:
        body = await request.body()
        req = urllib.request.Request(
            DEFAULT_GAS_URL,
            data=body,
            headers={"Content-Type": "text/plain;charset=utf-8"}
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            if result.get("status") == "success":
                # Cap nhat luon vao RAM cache cua VPS
                villa_id_str = result.get("villaId", "")
                num_match = villa_id_str.replace("Villa", "").strip()
                try:
                    num = str(int(num_match))
                    v_type = result.get("type", "before")
                    file_url = result.get("fileUrl", "")
                    
                    if num not in villas_cache["villas"]:
                        villas_cache["villas"][num] = {
                            "before": None, "beforeTime": None,
                            "after": None, "afterTime": None,
                            "status": "Chưa hoàn thành"
                        }
                    
                    v_entry = villas_cache["villas"][num]
                    v_entry[v_type] = file_url
                    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
                    v_entry[f"{v_type}Time"] = now_str
                    if v_entry.get("before") and v_entry.get("after"):
                        v_entry["status"] = "Hoàn Thành"
                    
                    villas_cache["total"] = len(villas_cache["villas"])
                    save_disk_cache()
                except Exception as ex:
                    print("Error updating local cache:", ex)
                
                # Sync them background de dong bo day du
                background_tasks.add_task(fetch_gas_villas)

            return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})

# Mount static files (Frontend HTML)
app.mount("/", StaticFiles(directory="/app/public", html=True), name="public")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)
