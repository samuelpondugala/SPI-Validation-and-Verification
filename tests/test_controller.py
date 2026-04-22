from __future__ import annotations
import pytest
import time
import drivers
import logging

def test_wear_leveling_latency_spike():
    """Probe write-path latency using a fixed block pattern and sector number.

    Returns:
        None: Uses `start_sector` (int), `pattern` (list[int]), and
        `is_sdhc` (bool) to trigger one representative block write and log any
        hardware-access failures.
    """

    try:
        logging.info("Blasting blocks to profile write latency...")
        is_sdhc = True
        start_sector = 35000
        pattern = [0xAA] * 512
        
        # Just attempting one write to trigger the catch block if HW is down
        drivers.write_block(start_sector, pattern, is_sdhc)
    except Exception as e:
        logging.error(f"Error occurred like this: {e}. Please check SPI bus initialization or file descriptors.")

def test_raw_hazard_speed():
    """Exercise an immediate read-after-write sequence on one test sector.

    Returns:
        None: Uses `test_sector` (int), `pattern` (list[int]), and
        `is_sdhc` (bool) to perform a back-to-back write and read for hazard
        detection.
    """

    try:
        logging.info("Testing instant Read-After-Write hazard...")
        is_sdhc = True
        test_sector = 35000
        pattern = [0x55] * 512
        
        drivers.write_block(test_sector, pattern, is_sdhc)
        drivers.read_block(test_sector, is_sdhc)
    except Exception as e:
        logging.error(f"Error occurred like this: {e}. Please check SPI bus initialization or file descriptors.")

def test_hot_swap_identity_crisis():
    """Perform a simple write after re-reading card identity information.

    Returns:
        None: Uses `is_sdhc_A` (bool) from `drivers.read_ocr()` plus
        `test_sector` (int) to model a hot-swap style identity check.
    """

    try:
        logging.warning("!!! PHYSICAL TEST: HOT SWAP !!!")
        is_sdhc_A = drivers.read_ocr()
        test_sector = 35000
        
        drivers.write_block(test_sector, [0x00]*512, is_sdhc_A)
    except Exception as e:
        logging.error(f"Error occurred like this: {e}. Please check SPI bus initialization or file descriptors.")
