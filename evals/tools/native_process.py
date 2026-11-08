"""Bounded cleanup for process groups this adapter created with a new session."""
import os
import signal
import subprocess
import time


def _group_exists(pgid):
    try:
        os.killpg(pgid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_owned_group(process, owned_pgid, term_grace=2.0, kill_grace=2.0, drain_grace=1.0):
    """TERM, then KILL, drain and reap only a recorded owned process group.

    Callers must create this Popen with start_new_session=True and retain its
    original pid as owned_pgid. No process-name searches or unrelated PIDs are
    accepted. A failed cleanup is explicit in the returned report.
    """
    if owned_pgid != process.pid or owned_pgid <= 1:
        raise ValueError("Refusing a process group not recorded from this owned child")
    if process.poll() is None and os.getpgid(process.pid) != owned_pgid:
        raise ValueError("Refusing to signal a child outside its recorded owned group")
    report = {"owned_pgid": owned_pgid, "term_sent": False, "kill_sent": False,
              "leader_reaped": False, "pipes_drained": False, "group_gone": False,
              "errors": []}

    def send(sig, field):
        try:
            os.killpg(owned_pgid, sig)
            report[field] = True
        except ProcessLookupError:
            pass
        except OSError as error:
            report["errors"].append(f"signal {sig}: {error}")

    def wait_group(seconds):
        deadline = time.monotonic() + seconds
        last_error = None
        while time.monotonic() < deadline:
            process.poll()  # Reap our direct child promptly.
            try:
                if not _group_exists(owned_pgid):
                    return True, None
            except OSError as error:
                # macOS can briefly return EPERM while a killed group exits.
                # Retry within the same bound; never interpret denial as gone.
                last_error = str(error)
            time.sleep(0.05)
        return False, last_error

    send(signal.SIGTERM, "term_sent")
    gone, observation_error = wait_group(term_grace)
    if not gone:
        send(signal.SIGKILL, "kill_sent")
        gone, observation_error = wait_group(kill_grace)
    try:
        process.wait(timeout=drain_grace)
        report["leader_reaped"] = True
    except subprocess.TimeoutExpired:
        report["errors"].append("Owned child could not be reaped within the final bound")
    if process.stdout is not None or process.stderr is not None:
        try:
            process.communicate(timeout=drain_grace)
            report["pipes_drained"] = True
        except subprocess.TimeoutExpired:
            report["errors"].append("Owned output pipes did not close within the drain bound")
            for stream in (process.stdout, process.stderr):
                if stream is not None:
                    stream.close()
    else:
        report["pipes_drained"] = True
    report["group_gone"] = gone
    if not gone:
        if observation_error:
            report["errors"].append(f"group check: {observation_error}")
        report["errors"].append("Owned process group still exists after TERM/KILL bounds")
    report["ok"] = all(report[key] for key in ("leader_reaped", "pipes_drained", "group_gone")) and not report["errors"]
    return report
