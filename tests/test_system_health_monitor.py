import sys, pathlib, logging
from unittest import mock
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "scripts"))
import system_health_monitor as m

def run(cpu, mem, disk, procs):
    with mock.patch.object(m.psutil, "cpu_percent", return_value=cpu), \
         mock.patch.object(m.psutil, "virtual_memory", return_value=mock.Mock(percent=mem)), \
         mock.patch.object(m.psutil, "disk_usage", return_value=mock.Mock(percent=disk)), \
         mock.patch.object(m.psutil, "pids", return_value=list(range(procs))), \
         mock.patch.object(m.psutil, "process_iter", return_value=[]):
        return m.check(logging.getLogger("t"))

def test_all_healthy(): assert run(10, 20, 30, 100) == []
def test_cpu_boundary_80_no_alert(): assert run(80.0, 0, 0, 0) == []
def test_cpu_above_threshold(): assert run(80.1, 0, 0, 0)[0].startswith("cpu")
def test_multiple_alerts(): assert len(run(95, 95, 95, 500)) == 4
