#!/usr/bin/env python3
"""Run frozen C/D assertions on owned iOS and Android simulators.

All platform shells and integration_test dependencies live in a disposable copy.
No model-output file is modified. Android runtime execution is attempted only after
a native build succeeds; SDK auto-installation is disabled and no licence terms are accepted.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import socket
import subprocess
import time
import uuid
from native_process import stop_owned_group

ROOT = Path(__file__).resolve().parents[1]
SKIP = {".git", ".dart_tool", "build"}


def hashes(root, allow_symlinks=False):
    result = {}
    for path in sorted(root.rglob("*")):
        if any(part in SKIP for part in path.relative_to(root).parts):
            continue
        if path.is_symlink():
            if not allow_symlinks:
                raise ValueError(f"Refusing source symlink: {path.relative_to(root)}")
            result[path.relative_to(root).as_posix()] = "symlink:" + os.readlink(path)
            continue
        if path.is_file():
            result[path.relative_to(root).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    return result



def native_inputs(source, scenario):
    """Open only SDK-only Dart UI inputs; never import submitted host build hooks."""
    fixture = ROOT / "fixtures" / scenario
    inputs = {}
    for name in ("pubspec.yaml", "pubspec.lock", "analysis_options.yaml"):
        path = source / name
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Missing or linked native input: {name}")
        data = path.read_bytes()
        if data != (fixture / name).read_bytes():
            raise ValueError(f"Native adapter requires the frozen SDK-only contract: {name}")
        inputs[name] = data
    library = source / "lib"
    if library.is_symlink() or not library.is_dir():
        raise ValueError("Native adapter requires a real lib directory")
    for path in sorted(library.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"Linked Dart input is not allowed: {path.relative_to(source)}")
        if path.is_file() and path.suffix == ".dart":
            inputs[path.relative_to(source).as_posix()] = path.read_bytes()
    if "lib/main.dart" not in inputs:
        raise ValueError("Native adapter requires lib/main.dart")
    repository = "lib/store.dart" if scenario == "C" else "lib/sync_store.dart"
    if inputs.get(repository) != (fixture / repository).read_bytes():
        raise ValueError("Native adapter requires the unchanged read-only store contract")
    excluded = []
    for path in source.rglob("*"):
        relative = path.relative_to(source)
        if any(part in SKIP for part in relative.parts) or relative.as_posix() in inputs:
            continue
        if path.is_symlink():
            excluded.append(relative.as_posix() + " [symlink not followed]")
        elif path.is_file():
            excluded.append(relative.as_posix())
    return inputs, sorted(excluded)


def input_hashes(inputs):
    return {name: hashlib.sha256(data).hexdigest() for name, data in sorted(inputs.items())}


def port_is_free(port):
    try:
        with socket.socket() as probe:
            probe.bind(("127.0.0.1",port))
        return True
    except OSError:
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", choices=["C", "D"], required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--platform", choices=["ios", "android"], required=True)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--driver", choices=["frozen", "event-controlled"], default="frozen")
    parser.add_argument("--reviewed-inputs", type=Path, help="Explicit review manifest for nonbaseline SDK-only Dart UI source")
    parser.add_argument("--allow-gradle-dependencies", action="store_true", help="Allow normal public Gradle dependency resolution; SDK auto-installation remains disabled")
    parser.add_argument("--owned-simulator-id", help="Reuse only a simulator named MotionEval-* created by this harness")
    parser.add_argument("--keep-simulator", action="store_true", help="Retain the owned simulator for subsequent frozen runs; caller must later delete it")
    parser.add_argument("--keep-android-emulator", action="store_true", help="Retain only the owned emulator and adb server for normal-app playback; caller must clean up")
    args = parser.parse_args()
    source = args.workspace.resolve()
    evidence = args.evidence.resolve()
    if evidence.exists():
        raise SystemExit("Evidence destination exists; use a fresh path.")
    evidence.mkdir(parents=True)
    app = evidence / "app"
    inputs, excluded = native_inputs(source, args.scenario)
    before = input_hashes(inputs)
    baseline_inputs, _ = native_inputs(ROOT / "fixtures" / args.scenario, args.scenario)
    if before != input_hashes(baseline_inputs):
        if args.reviewed_inputs is None:
            raise SystemExit("Nonbaseline native UI inputs need an explicit reviewed-inputs manifest before host platform builds.")
        review = json.loads(args.reviewed_inputs.read_text())
        if review.get("source_hashes") != before or review.get("reviewed_sdk_only_ui") is not True:
            raise SystemExit("Native UI review manifest does not match the exact whitelisted inputs.")
    selected_driver = ROOT / (f"native_event/v2/{args.scenario}.dart" if args.driver == "event-controlled" else f"graders/native_{args.scenario}.dart")
    report = {"scenario": args.scenario, "platform": args.platform,
              "source": str(source), "source_hashes": before,
              "source_hash_scope":"Whitelisted SDK-only UI/contract inputs; excluded submitted files are not opened or executed.",
              "excluded_submitted_files":excluded,
              "driver_kind":args.driver,"driver_sha256":hashlib.sha256(selected_driver.read_bytes()).hexdigest(),
              "execution_scope":{"platform_controller":"Bounded trusted-shell host adapter; not fully command-sandboxed.",
                                 "widget_grading":"Separate least-privilege grader sandbox required; this platform adapter is not that proof.",
                                 "ios":"Owned native preview/runtime, not a general untrusted-code isolation guarantee.",
                                 "android":"Owned guest with connectivity disabled; not proof of complete host isolation."},
              "runner_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "grader_hash": hashlib.sha256((ROOT / f"graders/native_{args.scenario}.dart").read_bytes()).hexdigest(),
              "started": time.time(), "commands": [], "wrapper_changes": [],
              "result": "infrastructure_blocked", "limitations": []}
    env = dict(os.environ, FLUTTER_SUPPRESS_ANALYTICS="true", CI="true")
    device = None
    recording = None

    def save():
        report["source_unchanged"] = input_hashes(native_inputs(source, args.scenario)[0]) == before
        (evidence / "native-runtime.json").write_text(json.dumps(report, indent=2) + "\n")

    def run(command, cwd=None, timeout=900, check=True, monitor=None):
        index = len(report["commands"])
        log = evidence / f"command-{index:02d}.log"
        row = {"argv": command, "cwd": str(cwd or evidence), "log": str(log), "started": time.time()}
        report["commands"].append(row)
        print("Running:", " ".join(map(str, command)), flush=True)
        with log.open("w") as output:
            try:
                child = subprocess.Popen(command, cwd=cwd or evidence, env=env,
                                         stdout=output, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, start_new_session=True)
                row["owned_pgid"] = child.pid
                deadline = time.time() + timeout
                while child.poll() is None and time.time() < deadline:
                    if monitor is not None:
                        monitor(log.read_text(errors="replace"))
                    time.sleep(0.25)
                if child.poll() is None:
                    row["cleanup"] = stop_owned_group(child, child.pid)
                    if not row["cleanup"]["ok"]:
                        report.setdefault("cleanup_failures", []).append(row["cleanup"])
                    code = 124
                else:
                    code = child.returncode
                row.update(exit_code=code, ended=time.time())
            except OSError as error:
                if "child" in locals() and child.poll() is None:
                    row["cleanup"] = stop_owned_group(child, child.pid)
                    if not row["cleanup"]["ok"]:
                        report.setdefault("cleanup_failures", []).append(row["cleanup"])
                row.update(exit_code=127, error=str(error), ended=time.time())
                code = 127
            except BaseException:
                if "child" in locals() and child.poll() is None:
                    row["cleanup"] = stop_owned_group(child, child.pid)
                    if not row["cleanup"]["ok"]:
                        report.setdefault("cleanup_failures", []).append(row["cleanup"])
                row.update(exit_code=130, ended=time.time())
                save()
                raise
        save()
        if check and code:
            raise RuntimeError(f"Command failed ({code}); see {log.name}")
        return code, log.read_text(errors="replace")

    try:
        name = re.search(r"^name:\s*([a-z][a-z0-9_]*)\s*$", (source / "pubspec.yaml").read_text(), re.MULTILINE).group(1)
        run(["flutter", "create", "--no-pub", "--platforms=ios,android", "--project-name", name, str(app)])
        generated = hashes(app, allow_symlinks=True)
        for name, data in inputs.items():
            target = app / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        # Verify every submitted file survived unchanged before wrapper-only changes.
        copied = hashes(app, allow_symlinks=True)
        assert all(copied.get(path) == digest for path, digest in before.items())
        report["generated_shell_files"] = sorted(set(generated) - set(before))
        pubspec = app / "pubspec.yaml"
        contents = pubspec.read_text()
        if re.search(r"^  integration_test:", contents, re.MULTILINE):
            raise RuntimeError("Existing integration_test dependency requires review; no automatic rewrite.")
        contents, count = re.subn(r"^dev_dependencies:\s*$", "dev_dependencies:\n  integration_test:\n    sdk: flutter", contents, count=1, flags=re.MULTILINE)
        if count != 1:
            raise RuntimeError("No unique dev_dependencies section; wrapper setup blocked.")
        pubspec.write_text(contents)
        grader = selected_driver.read_text()
        binding = "final nativeBinding = IntegrationTestWidgetsFlutterBinding.ensureInitialized();\n  nativeBinding.framePolicy = LiveTestWidgetsFlutterBindingFramePolicy.onlyPumps;"
        tests = "import 'package:integration_test/integration_test.dart';\n" + grader.replace("void main() {", "void main() {\n  " + binding, 1)
        target = app / "integration_test/native_acceptance_test.dart"
        target.parent.mkdir(exist_ok=True)
        target.write_text(tests)
        report["wrapper_changes"] = [
            "Generate trusted ios/android shells in disposable copy; copy only whitelisted reviewed Dart UI/frozen SDK contract files byte-for-byte. Submitted host build/hooks/dependencies are excluded, not repaired.",
            "Add SDK integration_test dev dependency only to disposable pubspec; resolve offline.",
            "Add selected driver unchanged plus binding initialization/import and onlyPumps frame policy. Event-controlled driver is supplementary; frozen graders and timed native failures remain unchanged. This is native assertion execution, not continuous playback.",
        ]
        report["native_assertion_frame_policy"] = "onlyPumps"
        run(["flutter", "pub", "get", "--offline"], cwd=app)
        report["wrapper_hashes_before_native_run"] = hashes(app, allow_symlinks=True)
        if args.prepare_only:
            report["result"] = "wrapper_prepared_native_not_run"
            return
        if args.platform == "android":
            properties = app / "android/gradle.properties"
            properties.write_text(properties.read_text() + "\nandroid.builder.sdkDownload=false\n")
            report["wrapper_changes"].append("Disable automatic Android SDK installation in disposable gradle.properties; Gradle native build uses --offline.")
            wrapper_properties = (app / "android/gradle/wrapper/gradle-wrapper.properties").read_text()
            distribution = re.search(r"distributionUrl=.*?/(gradle-[^/]+)\.zip", wrapper_properties).group(1)
            gradle_cache = Path(env.get("GRADLE_USER_HOME", str(Path.home() / ".gradle"))) / "wrapper/dists" / distribution
            cached_launchers = list(gradle_cache.glob("*/gradle-*/bin/gradle"))
            if not cached_launchers:
                report["limitations"].append(f"Required generated-shell Gradle distribution {distribution} is not cached; bootstrap downloads are disabled by the native runner.")
                return
            # --offline does not govern wrapper bootstrap, so invoke the already
            # cached distribution directly rather than allowing wrapper download.
            command = [str(sorted(cached_launchers)[0])]
            if not args.allow_gradle_dependencies:
                command.append("--offline")
            command += ["app:assembleDebug", "-Ptarget-platform=android-arm64", "-Pandroid.builder.sdkDownload=false"]
            report["gradle_public_dependency_resolution"] = args.allow_gradle_dependencies
            code, log = run(command, cwd=app / "android", check=False)
            if code:
                report["limitations"].append("Android offline native build blocked. No SDK licence terms accepted or user AVD/data opened; SDK auto-installation is disabled. See gradle_public_dependency_resolution for repository-download policy.")
                return
            sdk = Path(env.get("ANDROID_HOME", env.get("ANDROID_SDK_ROOT", str(Path.home() / "Library/Android/sdk"))))
            adb = str(sdk / "platform-tools/adb")
            android_home = evidence / "android-home"
            avd_home = evidence / "avds"
            android_home.mkdir()
            avd_home.mkdir()
            with socket.socket() as port_probe:
                port_probe.bind(("127.0.0.1", 0))
                adb_port = port_probe.getsockname()[1]
            console_port = next(port for port in range(5580, 5678, 2) if port_is_free(port) and port_is_free(port + 1))
            env.update(ANDROID_USER_HOME=str(android_home), ANDROID_EMULATOR_HOME=str(android_home),
                       ANDROID_AVD_HOME=str(avd_home), ANDROID_SDK_ROOT=str(sdk),
                       ADB_SERVER_SOCKET=f"tcp:127.0.0.1:{adb_port}", ANDROID_ADB_SERVER_PORT=str(adb_port))
            avd_name = "MotionEval-" + uuid.uuid4().hex[:12]
            serial = f"emulator-{console_port}"
            run([str(sdk / "cmdline-tools/latest/bin/avdmanager"), "create", "avd", "--name", avd_name,
                 "--path", str(evidence / "avd"), "--package", "system-images;android-35;google_apis_playstore_tablet;arm64-v8a", "--device", "pixel_tablet"])
            config = evidence / "avd/config.ini"
            configuration = config.read_text()
            for key,value in {"hw.lcd.width":"800","hw.lcd.height":"1280","hw.lcd.density":"240","hw.ramSize":"2048"}.items():
                configuration,count=re.subn(r"^"+re.escape(key)+r"=.*$",key+"="+value,configuration,flags=re.MULTILINE)
                if not count:
                    configuration+="\n"+key+"="+value+"\n"
            config.write_text(configuration)
            report["android_isolation"] = {"new_avd":avd_name,"owned_serial":serial,"user_avd_data_used":False,
                                          "private_adb_server":True,"adb_server_port":adb_port,"sdk_terms_accepted":False,
                                          "system_image":"android-35/google_apis_playstore_tablet/arm64-v8a",
                                          "display_pixels":[800,1280],"density_dpi":240,"ram_mb":2048,"gpu":"host","cores":2}
            report["wrapper_changes"].append("Set only new disposable AVD hardware to 800x1280,240dpi,2GB RAM,2cores and host GPU; app source unchanged.")
            emulator_log = (evidence / "emulator.log").open("w")
            emulator = subprocess.Popen([str(sdk / "emulator/emulator"), "-avd", avd_name, "-port", str(console_port),
                                          "-no-window", "-no-audio", "-no-boot-anim", "-no-snapshot", "-gpu", "host", "-memory", "2048", "-cores", "2"],
                                         env=env, stdout=emulator_log, stderr=subprocess.STDOUT, start_new_session=True)
            screen = None
            try:
                run([adb,"-P",str(adb_port),"start-server"])
                run([adb,"-P",str(adb_port),"-s",serial,"wait-for-device"], timeout=300)
                deadline=time.time()+300
                while time.time()<deadline:
                    ready=subprocess.run([adb,"-P",str(adb_port),"-s",serial,"shell","getprop","sys.boot_completed"],env=env,capture_output=True,text=True,timeout=10)
                    if ready.stdout.strip()=="1":
                        break
                    time.sleep(1)
                else:
                    raise RuntimeError("Owned Android emulator did not finish booting")
                run([adb,"-P",str(adb_port),"-s",serial,"shell","svc","wifi","disable"],check=False)
                run([adb,"-P",str(adb_port),"-s",serial,"shell","svc","data","disable"],check=False)
                run([adb,"-P",str(adb_port),"-s",serial,"shell","getprop","ro.build.version.release"])
                screen_log=(evidence/"android-recording.log").open("w")
                def start_android_recording(text):
                    nonlocal screen
                    if screen is None and "Installing build/" in text:
                        screen=subprocess.Popen([adb,"-P",str(adb_port),"-s",serial,"shell","screenrecord","--time-limit","180","/sdcard/native-eval.mp4"],env=env,stdout=screen_log,stderr=subprocess.STDOUT,start_new_session=True)
                        report["recording_trigger"]="APK installation began; excludes slow Gradle build time from Android recording limit."
                code,log=run(["flutter","test","integration_test/native_acceptance_test.dart","-d",serial,"--no-pub","--reporter","expanded"],cwd=app,timeout=1200,check=False,monitor=start_android_recording)
                report["native_test_exit_code"]=code
                report["result"]="native_assertions_passed" if code==0 else ("native_assertions_failed" if "[E]" in log or "Some tests failed" in log else "infrastructure_blocked")
                run([adb,"-P",str(adb_port),"-s",serial,"shell","pkill","-INT","screenrecord"],check=False)
                if screen is not None:
                    screen.wait(timeout=20)
                run([adb,"-P",str(adb_port),"-s",serial,"pull","/sdcard/native-eval.mp4",str(evidence/"native-playback.mp4")],check=False)
                with (evidence/"native-final.png").open("wb") as image:
                    subprocess.run([adb,"-P",str(adb_port),"-s",serial,"exec-out","screencap","-p"],env=env,stdout=image,timeout=20)
                report["playback"]=str(evidence/"native-playback.mp4")
            finally:
                if screen is not None and screen.poll() is None:
                    cleanup=stop_owned_group(screen,screen.pid)
                    if not cleanup["ok"]:
                        report.setdefault("cleanup_failures",[]).append(cleanup)
                if args.keep_android_emulator:
                    report["owned_android_emulator_retained"] = {"pid":emulator.pid,"serial":serial,"adb_server_port":adb_port}
                else:
                    run([adb,"-P",str(adb_port),"-s",serial,"emu","kill"],check=False)
                    try:
                        emulator.wait(timeout=30)
                    except subprocess.TimeoutExpired:
                        cleanup=stop_owned_group(emulator,emulator.pid)
                        if not cleanup["ok"]:
                            report.setdefault("cleanup_failures",[]).append(cleanup)
                    run([adb,"-P",str(adb_port),"kill-server"],check=False)
            return
        if args.owned_simulator_id:
            _, devices = run(["xcrun", "simctl", "list", "devices", args.owned_simulator_id, "--json"])
            matches = [entry for group in json.loads(devices)["devices"].values() for entry in group
                       if entry["udid"] == args.owned_simulator_id and entry["name"].startswith("MotionEval-")]
            if len(matches) != 1:
                raise RuntimeError("Refusing to use a simulator not owned by this harness")
            device = matches[0]["udid"]
            already_booted = matches[0]["state"] == "Booted"
        else:
            _, text = run(["xcrun", "simctl", "create", "MotionEval-" + uuid.uuid4().hex[:12], "com.apple.CoreSimulator.SimDeviceType.iPhone-17-Pro", "com.apple.CoreSimulator.SimRuntime.iOS-26-5"])
            device = text.strip().splitlines()[-1]
            if not re.fullmatch(r"[0-9A-Fa-f-]{36}", device):
                raise RuntimeError("Could not identify owned simulator ID")
            already_booted = False
        report["owned_simulator"] = device
        if not already_booted:
            run(["xcrun", "simctl", "boot", device])
        run(["xcrun", "simctl", "bootstatus", device, "-b"], timeout=300)
        run(["xcrun", "simctl", "list", "runtimes", "--json"])
        movie = evidence / "native-playback.mov"
        recording_log = (evidence / "recording.log").open("w")
        recording = subprocess.Popen(["xcrun", "simctl", "io", device, "recordVideo", "--codec=h264", str(movie)], stdout=recording_log, stderr=subprocess.STDOUT, start_new_session=True)
        code, log = run(["flutter", "test", "integration_test/native_acceptance_test.dart", "-d", device, "--no-pub", "--reporter", "expanded"], cwd=app, timeout=1200, check=False)
        report["native_test_exit_code"] = code
        report["result"] = "native_assertions_passed" if code == 0 else ("native_assertions_failed" if "[E]" in log or "Some tests failed" in log else "infrastructure_blocked")
        run(["xcrun", "simctl", "io", device, "screenshot", str(evidence / "native-final.png")], check=False)
        report["playback"] = str(movie)
        report["limitations"].append("Grader assertions execute on a real simulator runtime. Recording shows onlyPumps native assertion execution, not continuous motion playback or frame-rate/screen-reader certification. Normal main.dart playback must be observed separately.")
    except Exception as error:
        report["error"] = str(error)
        print("Native evaluation blocked:", error, flush=True)
    finally:
        if recording is not None:
            recording.send_signal(signal.SIGINT)
            try:
                recording.wait(timeout=20)
            except subprocess.TimeoutExpired:
                cleanup=stop_owned_group(recording,recording.pid)
                if not cleanup["ok"]:
                    report.setdefault("cleanup_failures",[]).append(cleanup)
        if device is not None and not args.keep_simulator:
            run(["xcrun", "simctl", "shutdown", device], check=False)
            run(["xcrun", "simctl", "delete", device], check=False)
        report["cleanup_complete"] = not report.get("cleanup_failures")
        if not report["cleanup_complete"]:
            report["native_result_before_cleanup"] = report["result"]
            report["result"] = "cleanup_incomplete"
        report["simulator_retained_for_reuse"] = bool(device and args.keep_simulator)
        report["ended"] = time.time()
        save()
        print(json.dumps({"result": report["result"], "evidence": str(evidence / "native-runtime.json")}), flush=True)


if __name__ == "__main__":
    main()
