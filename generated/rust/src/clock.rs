// @generated from devices/clock/registers.toml by defs-gen - do not edit, change the source
// SPDX-License-Identifier: BSD-3-Clause
// defs-gen 5
// input sha256 467273ff471ddf2134ff68f52c6be88c8ce534408f7b0b63cc8677a1cd2e2738
// Express board configuration ports and pixel clock control
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// Read: board revision and, on revision 4 and up, the monitor code. Bits 3:0 read back inverted (board revision is the complement, zero means no board). (established)
pub mod port0 {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c000;
    pub mod monitor_code_rev4 { // bits 7:4, established
        pub const SHIFT: u32 = 4;
        pub const MASK: u32 = 0xf;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod board_rev_n { // bits 3:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0xf;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// Read below revision 4: bit 0 is monitor code bit 0; bits 3:2 both set mean no Z buffer. Read at revision 4 and up: bits 1:0 backend revision as read ( (established)
pub mod port1 {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c004;
    pub mod z_present_rev4 { // bits 5:5, established
        pub const SHIFT: u32 = 5;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod depth24_rev4 { // bits 4:4, established
        pub const SHIFT: u32 = 4;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod no_z_rev3 { // bits 3:2, established
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod low2 { // bits 1:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// Board revision below 4 only. Bits 3:2 read back inverted as the backend revision (zero fails the probe); bits 1:0 are monitor code bits 2:1. Not read  (established)
pub mod port2 {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c008;
    pub mod backend_rev_n { // bits 3:2, established
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod monitor_code_hi { // bits 1:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// Board revision below 4 only: frame-buffer memory slot presence; a slot is empty when both of its bits are set (slot A bits 1:0, slot B bits 3:2, slot  (established)
pub mod port3 {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c00c;
    pub mod slot_c_empty { // bits 5:4, established
        pub const SHIFT: u32 = 4;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod slot_b_empty { // bits 3:2, established
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod slot_a_empty { // bits 1:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// Pixel clock serial or command port. Board revision below 4: 17 command bytes. Revision 4 and up: 56 single-bit writes (bit 0 is the data bit, bit 1 se (established)
pub mod data {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c020;
    pub mod last { // bits 1:1, established
        pub const SHIFT: u32 = 1;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod bit { // bits 0:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
pub const BOARD_REV_SPLIT: u32 = 0x4; // established
pub const COMMAND_BYTES_REV3: u32 = 0x11; // established
pub const EXTRA_BYTE_REV3: u32 = 0xa5; // established
pub const LOAD_REV3: u32 = 0x40; // inferred
pub const SEL_60HZ: u32 = 0x1; // inferred
pub const SEL_72HZ: u32 = 0x2; // inferred
pub const SEL_OTHER: u32 = 0x4; // inferred
pub const SEL_REV4: u32 = 0x7; // established
pub const SERIAL_BYTES_REV4: u32 = 0x7; // established
