#!/usr/bin/env python3
"""System health monitor: alerts when CPU/memory/disk/process count cross thresholds.
Usage: python3 system_health_monitor.py [--interval 5] [--once] [--log health.log]"""
import argparse, logging, time
import psutil

THRESHOLDS = {"cpu": 80.0, "memory": 80.0, "disk": 80.0, "processes": 400}

def check(log):
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    procs = len(psutil.pids())
    log.info("CPU=%.1f%% MEM=%.1f%% DISK=%.1f%% PROCS=%d", cpu, mem, disk, procs)
    alerts = []
    for name, val in (("cpu", cpu), ("memory", mem), ("disk", disk), ("processes", procs)):
        if val > THRESHOLDS[name]:
            alerts.append(f"{name} {val} > {THRESHOLDS[name]}")
    for a in alerts:
        log.warning("ALERT: %s", a)
    if alerts:
        top = sorted(psutil.process_iter(["pid", "name", "cpu_percent"]),
                     key=lambda p: p.info["cpu_percent"] or 0, reverse=True)[:5]
        for p in top:
            log.warning("  top proc pid=%s name=%s cpu=%s%%", p.info["pid"], p.info["name"], p.info["cpu_percent"])
    return alerts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--interval", type=int, default=5)
    ap.add_argument("--once", action="store_true")
    ap.add_argument("--log", default="system_health.log")
    a = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s",
                        handlers=[logging.StreamHandler(), logging.FileHandler(a.log)])
    log = logging.getLogger("health")
    while True:
        alerts = check(log)
        if a.once:
            raise SystemExit(1 if alerts else 0)
        time.sleep(a.interval)

if __name__ == "__main__":
    main()
