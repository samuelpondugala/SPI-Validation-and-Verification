# CardLink: SPI FAT32 Reliability Harness

CardLink is a Python-based SD card validation and FAT32 exploration project built for Raspberry Pi SPI environments. It combines low-level SPI command handling, lightweight FAT32 navigation helpers, a pytest-driven validation suite, and a few standalone hardware scripts for fault injection, loopback checks, and SPI display playback.

This repository is useful if you want to:

- validate SD card behavior over SPI
- exercise FAT32 read/write paths from Python
- run hardware-aware regression and fault-injection tests
- demonstrate embedded validation work on a resume or GitHub profile

## Resume-Friendly Project Name

Recommended project title:

`CardLink: SPI FAT32 Reliability Harness`

It stays explicit about the domain while still sounding polished enough for a resume, portfolio, or GitHub project heading.

## What The Project Covers

The codebase is centered around three layers:

1. `drivers.py` implements the core SPI, SD-card, and FAT32 helper logic.
2. `tests/` contains pytest scenarios for identity checks, negative testing, preflight hardware simulation, FAT32 edge cases, controller stress, and raw data integrity.
3. Standalone scripts such as `run_tests.py`, `run_power_loss.py`, `loopback.py`, `spi_test.py`, `spi_testcases.py`, and `spi_display.py` provide direct hardware exercises outside pytest.

At a high level, the workflow is:

1. Open the SPI device.
2. Initialize the SD card using `CMD0`, `CMD8`, `CMD55`, and `ACMD41`.
3. Read the OCR register to determine SDHC behavior.
4. Read the MBR and FAT32 boot sector.
5. Compute FAT and data-region offsets.
6. Read or write raw sectors.
7. Traverse directories, create files, delete files, and manipulate FAT entries.
8. Run test scenarios that simulate wiring faults, protocol faults, filesystem churn, and controller edge cases.

## Tech Stack

- Python 3
- `pytest` for automated validation
- `pytest-html` for HTML report generation
- `spidev` for Linux SPI access on Raspberry Pi
- `RPi.GPIO` for display control pins
- `Pillow` for image loading and RGB conversion
- Built-in Python modules such as `logging`, `datetime`, `os`, `sys`, `time`, `glob`, and `unittest.mock`
- FAT32 on top of SD-card SPI protocol primitives

## Repository Structure

- `drivers.py`
  Core SD-card SPI driver plus FAT32 helpers for block reads, block writes, directory parsing, file creation, file deletion, directory creation, and recursive deletion.

- `run_tests.py`
  Launches the pytest suite, creates a `logs/` folder, configures logging, and emits a timestamped HTML report.

- `run_power_loss.py`
  Stress script that continuously rewrites the same FAT entry so power can be cut during a metadata update.

- `spi_test.py`
  Minimal JEDEC-style SPI probe script for quick bus sanity checking.

- `spi_testcases.py`
  Small SD-card initialization prototype showing command packet construction and early bring-up flow.

- `loopback.py`
  SPI loopback script that sends known patterns and compares echoed bytes.

- `spi_display.py`
  Separate SPI display utility that initializes an LCD-like panel and streams JPEG frames.

- `tests/conftest.py`
  Session fixture that opens the SPI bus, initializes the SD card, parses key FAT32 geometry values, and shares them with tests.

- `tests/test_preflight_hardware.py`
  Mock-based crash-proof preflight tests for loopback behavior, floating bus detection, device identity, and hot-swap rejection.

- `tests/test_identity.py`
  Identity and initialization checks such as `CMD0` idle-state response and OCR access.

- `tests/test_negative.py`
  Negative scenarios such as invalid commands, out-of-range block reads, and delete attempts on missing files.

- `tests/test_hardware.py`
  Fault-oriented scenarios such as SPI mode mismatch, MISO timeout behavior, and chip-select glitch recovery.

- `tests/test_integrity.py`
  Raw block write/read pattern checks using repeated data values such as `0xAA`, `0x55`, `0xFF`, and `0x00`.

- `tests/test_controller.py`
  Controller-oriented scenarios that simulate wear-leveling latency, read-after-write hazards, and hot-swap identity changes.

- `tests/test_fat32.py`
  FAT32 edge-case exercises such as fragmentation setup, directory boundary pressure, free-cluster exhaustion, and zero-byte directory entries.

- `tests/test_margins.py`
  SPI clock-margin sweep behavior using a higher SPI frequency during a read attempt.

- `tests/test_stress.py`
  Small churn scenario that creates and looks up a stress-test file.

## Key Functional Areas

### 1. SD Card Bring-Up

`drivers.py` performs the basic SPI-side initialization sequence:

- `send_cmd()` builds a 6-byte SD command packet.
- `init_sd()` performs slow-speed initialization and retries `ACMD41`.
- `read_ocr()` checks the OCR register and derives the SDHC flag.

### 2. Raw Sector Access

The project can access storage at the 512-byte sector level:

- `read_block()` reads one data block with `CMD17`
- `write_block()` writes one data block with `CMD24`

These functions are the foundation for everything higher level in the project.

### 3. FAT32 Parsing And Navigation

The code uses simple FAT32 helpers to move between filesystem structures:

- `read_fat_entry()`
- `cluster_to_sector()`
- `read_directory()`
- `list_files()`
- `read_file()`

Together, these functions let the project inspect directory contents and retrieve file data from a FAT32-formatted SD card.

### 4. FAT32 Modification

The project also includes lightweight filesystem write helpers:

- `find_free_cluster()`
- `write_fat_entry()`
- `create_dir_entry()`
- `create_file()`
- `find_file()`
- `delete_file()`
- `create_directory()`
- `delete_directory()`
- `delete_directory_recursive()`

This makes the repository more than a read-only test harness. It can actively create, delete, and stress filesystem metadata.

### 5. Validation Strategy

The tests mix software-only and hardware-facing scenarios:

- Mock-driven tests prevent hard crashes when hardware is absent.
- Session-scoped setup tries to mount the SD environment once for all tests.
- Negative tests verify failure handling.
- Integrity tests exercise repeated block patterns.
- FAT32 and stress tests poke directory and allocation logic.
- Controller tests simulate behavior that matters in reliability work, not just simple functional success.

## Prerequisites

Typical environment assumptions for this project:

- Raspberry Pi or another Linux board with `/dev/spidev*`
- SPI enabled in the OS
- An SD card connected over SPI
- Python 3 installed
- For `spi_display.py`, a compatible SPI display plus GPIO wiring

Python packages commonly needed:

```bash
pip install pytest pytest-html spidev RPi.GPIO pillow
```

## How To Run

Run the full validation suite:

```bash
python run_tests.py
```

Run pytest directly:

```bash
pytest -v -s tests/
```

Run the power-loss stress script:

```bash
python run_power_loss.py
```

Run the SPI loopback utility:

```bash
python loopback.py
```

Run the minimal SPI probe:

```bash
python spi_test.py
```

Run the SD initialization prototype:

```bash
python spi_testcases.py
```

Run the display player:

```bash
python spi_display.py
```

## Logging And Reports

- `run_tests.py` creates a `logs/` directory automatically.
- Runtime logs are written to `logs/spi_validation.log`.
- HTML test reports are written as timestamped files such as `logs/spi_report_YYYYMMDD_HHMMSS.html`.

## Important Implementation Notes

This project is already strong as a validation/demo platform, but the current code is intentionally lightweight rather than production-hardened. A few honest notes are worth keeping in the README:

- The FAT32 manipulation code is simplified and mostly geared toward single-cluster examples.
- File creation currently assumes small payloads and does not build long cluster chains for large files.
- Several tests use hardcoded sectors or dummy geometry values so they can still exercise code paths even when a full mounted environment is not available.
- `tests/conftest.py` opens the SD-card SPI device on bus `0`, chip select `1`, while some standalone scripts use chip select `0`.
- Some hardware tests are best interpreted as lab exercises or smoke tests rather than strict production qualification.

## Why This Project Stands Out

This repository demonstrates a nice combination of:

- low-level embedded communication
- filesystem-aware validation
- automated testing with pytest
- fault-injection thinking
- practical Raspberry Pi hardware interfacing

That combination makes it a strong portfolio piece for embedded software, validation engineering, firmware test, storage validation, or Python-based hardware automation roles.
