// @generated from devices/bt457/registers.toml by defs-gen - do not edit, change the source
// SPDX-License-Identifier: BSD-3-Clause
// defs-gen 5
// input sha256 e70d1735c70ebfb40a10bdbfae82173a37248264f8277909d1c208d56f73f0dc
// Brooktree Bt457 RAMDAC as wired on the Express board (three chips, one per colour)
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// Address register. Written before every register or palette access; after a palette or overlay access it advances (palette wraps to 0 after 255, overla (established)
pub mod addr {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x0;
}
/// Colour palette RAM data. The three chips are addressed separately, so the board uses the datasheet's normal mode: one byte write stores one colour com (established)
pub mod palette {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x4;
}
/// Control register data: the register picked by addr (read mask, blink mask, command, test) is read or written here and addr does not advance. [public]  (established)
pub mod ctrl {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x8;
}
/// Overlay colour data, entries 0 to 3 selected by addr. Init writes four bytes 0 to 3 after setting addr to 0. [public] [binary] (established)
pub mod overlay {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0xc;
}
/// Command register fields, from the datasheet. The board writes 0xc1. (established)
pub mod command {
    pub const WIDTH: u32 = 8;
    pub mod mux_select { // bits 7:7, established
        pub const SHIFT: u32 = 7;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod ram_enable { // bits 6:6, established
        pub const SHIFT: u32 = 6;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod blink_rate { // bits 5:4, established
        pub const SHIFT: u32 = 4;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod overlay1_blink { // bits 3:3, established
        pub const SHIFT: u32 = 3;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod overlay0_blink { // bits 2:2, established
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod overlay1_display { // bits 1:1, established
        pub const SHIFT: u32 = 1;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod overlay0_display { // bits 0:0, established
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
pub const ADDR_BLINK_MASK: u32 = 0x5; // established
pub const ADDR_COMMAND: u32 = 0x6; // established
pub const ADDR_READ_MASK: u32 = 0x4; // established
pub const ADDR_TEST: u32 = 0x7; // established
pub const INIT_COMMAND: u32 = 0xc1; // established
pub const INIT_READ_MASK: u32 = 0x0; // established
pub const OVERLAY_ENTRIES: u32 = 0x4; // established
pub const PALETTE_ENTRIES: u32 = 0x100; // established
pub const UNBLANK_READ_MASK: u32 = 0xff; // established
