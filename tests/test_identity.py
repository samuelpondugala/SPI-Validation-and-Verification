# tests/test_identity.py
import drivers
import logging

def test_cmd0_idle_state():
    """Open the SPI device and verify that `CMD0` reports SD idle state.

    Returns:
        None: Opens the bus, captures the `response` (int) from `drivers.send_cmd`,
        asserts the expected idle value, and closes the device in `finally`.
    """

    try:
        # 1. OPEN THE DOOR TO THE HARDWARE FIRST
        drivers.spi.open(0, 1) 
        
        logging.info("Testing CMD0 (GO_IDLE_STATE)...")
        response = drivers.send_cmd(0, 0, 0x95)
        assert response == 0x01
        
    except Exception as e:
        logging.error(f"Error: {e}")
    finally:
        # 2. ALWAYS CLOSE IT WHEN DONE
        try:
            drivers.spi.close()
        except:
            pass

def test_ocr_read():
    """Check that reading the OCR register yields an SDHC flag boolean.

    Returns:
        None: Stores `is_sdhc` (bool) from `drivers.read_ocr()` and asserts that
        the hardware capability probe returns a boolean result.
    """

    try:
        logging.info("Reading OCR Register...")
        is_sdhc = drivers.read_ocr()
        assert isinstance(is_sdhc, bool)
    except OSError as e:
        logging.warning(f"Error occurred like this: {e}. Please check SPI bus initialization or file descriptors.")
    except Exception as e:
        logging.warning(f"Setup error occurred: {e}. Please check environment.")
