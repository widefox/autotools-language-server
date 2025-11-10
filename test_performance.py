#!/usr/bin/env python3
"""Test performance of the make language server on large files with resource monitoring."""

import os
import sys
import time
import signal
import psutil
import subprocess
from pathlib import Path
from threading import Thread, Event

# Configuration
MAX_MEMORY_MB = 2048  # 2GB max memory
MAX_TIME_SECONDS = 60  # 60 seconds timeout
CHECK_INTERVAL = 0.1  # Check resources every 100ms

class ResourceMonitor:
    """Monitor resource usage of a process."""

    def __init__(self, pid, max_memory_mb, max_time_seconds):
        self.pid = pid
        self.max_memory_mb = max_memory_mb
        self.max_time_seconds = max_time_seconds
        self.stop_event = Event()
        self.stats = {
            'peak_memory_mb': 0,
            'elapsed_time': 0,
            'killed': False,
            'kill_reason': None
        }

    def monitor(self):
        """Monitor the process in a separate thread."""
        try:
            process = psutil.Process(self.pid)
            start_time = time.time()

            while not self.stop_event.is_set():
                try:
                    # Get memory usage
                    mem_info = process.memory_info()
                    memory_mb = mem_info.rss / (1024 * 1024)

                    # Update peak memory
                    self.stats['peak_memory_mb'] = max(
                        self.stats['peak_memory_mb'],
                        memory_mb
                    )

                    # Check elapsed time
                    elapsed = time.time() - start_time
                    self.stats['elapsed_time'] = elapsed

                    # Check if we exceeded limits
                    if memory_mb > self.max_memory_mb:
                        print(f"\n⚠ Memory limit exceeded: {memory_mb:.1f}MB > {self.max_memory_mb}MB", file=sys.stderr)
                        self.stats['killed'] = True
                        self.stats['kill_reason'] = f'memory_exceeded_{memory_mb:.1f}MB'
                        process.kill()
                        break

                    if elapsed > self.max_time_seconds:
                        print(f"\n⚠ Time limit exceeded: {elapsed:.1f}s > {self.max_time_seconds}s", file=sys.stderr)
                        self.stats['killed'] = True
                        self.stats['kill_reason'] = f'time_exceeded_{elapsed:.1f}s'
                        process.kill()
                        break

                    time.sleep(CHECK_INTERVAL)

                except psutil.NoSuchProcess:
                    break

        except Exception as e:
            print(f"Monitor error: {e}", file=sys.stderr)

    def stop(self):
        """Stop monitoring."""
        self.stop_event.set()


def test_file(filepath, max_memory_mb=MAX_MEMORY_MB, max_time_seconds=MAX_TIME_SECONDS):
    """Test language server on a file with resource monitoring."""

    print(f"\n{'='*70}")
    print(f"Testing: {filepath}")
    print(f"Limits: {max_memory_mb}MB memory, {max_time_seconds}s timeout")
    print(f"{'='*70}")

    # Get file size
    file_size = os.path.getsize(filepath)
    print(f"File size: {file_size / 1024:.1f} KB")

    # Count lines
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        lines = sum(1 for _ in f)
    print(f"Lines: {lines:,}")

    # Start the language server check
    start_time = time.time()

    try:
        # Use --check to run diagnostics on the file
        proc = subprocess.Popen(
            [sys.executable, '-m', 'make_language_server', '--check', filepath],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Start monitoring
        monitor = ResourceMonitor(proc.pid, max_memory_mb, max_time_seconds)
        monitor_thread = Thread(target=monitor.monitor, daemon=True)
        monitor_thread.start()

        # Wait for completion
        stdout, stderr = proc.communicate()
        elapsed = time.time() - start_time

        # Stop monitoring
        monitor.stop()
        monitor_thread.join(timeout=1)

        # Print results
        print(f"\n{'─'*70}")
        print(f"Results:")
        print(f"  Exit code: {proc.returncode}")
        print(f"  Elapsed time: {elapsed:.2f}s")
        print(f"  Peak memory: {monitor.stats['peak_memory_mb']:.1f}MB")

        if monitor.stats['killed']:
            print(f"  Status: KILLED ({monitor.stats['kill_reason']})")
        else:
            print(f"  Status: COMPLETED")

        if stdout.strip():
            print(f"\nStdout:\n{stdout}")
        if stderr.strip():
            print(f"\nStderr:\n{stderr}")

        return {
            'file': filepath,
            'success': not monitor.stats['killed'] and proc.returncode == 0,
            'elapsed': elapsed,
            'peak_memory_mb': monitor.stats['peak_memory_mb'],
            'killed': monitor.stats['killed'],
            'kill_reason': monitor.stats['kill_reason'],
            'returncode': proc.returncode
        }

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return {
            'file': filepath,
            'success': False,
            'error': str(e)
        }


def main():
    """Main function."""

    # Test files
    test_files = [
        'examples/Linux/Makefile',
        'examples/Linux/scripts/Makefile.lib',
        'examples/Linux/drivers/gpu/drm/Makefile',
    ]

    results = []

    for filepath in test_files:
        full_path = Path(filepath)
        if not full_path.exists():
            print(f"⚠ File not found: {filepath}")
            continue

        result = test_file(str(full_path))
        results.append(result)

    # Summary
    print(f"\n{'='*70}")
    print("SUMMARY")
    print(f"{'='*70}")

    for result in results:
        file = result['file']
        if result.get('success'):
            print(f"✓ {file}: {result['elapsed']:.2f}s, {result['peak_memory_mb']:.1f}MB")
        elif result.get('killed'):
            print(f"✗ {file}: KILLED ({result['kill_reason']})")
        else:
            print(f"✗ {file}: FAILED (code={result.get('returncode', 'N/A')})")

    return 0 if all(r.get('success') for r in results) else 1


if __name__ == '__main__':
    sys.exit(main())
