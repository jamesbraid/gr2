// @generated from devices/vc1-express/registers.toml by defs-gen - do not edit, change the source
// SPDX-License-Identifier: BSD-3-Clause
// defs-gen 5
// input sha256 25734a17818e96cd0d8d228db9bbafb76b5aba73b4daabd22058b0bf5bc47127
// VC1 video timing, cursor and display-ID controller on the Express board
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// Internal register data port. Set the address pair to an internal register number, then write half-words; the address advances by two after each (curso (established)
pub mod command {
    pub const WIDTH: u32 = 16;
    pub const OFFSET: u64 = 0x6c040;
}
/// Window to a display-mode table inside the VC1 (the Entry board's equivalent holds the mode words). Express keeps display modes in the XMAP5 chips inst (unknown)
pub mod xmapmode {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c044;
}
/// External SRAM data port. The SRAM is addressed by byte; each half-word transfer advances the address pair by two. Written from timing images and displ (established)
pub mod sram {
    pub const WIDTH: u32 = 16;
    pub const OFFSET: u64 = 0x6c048;
}
/// Revision read: after addrhi = 0 and addrlo = 5, the low three bits are stored as the VC1 revision. gfxinfo decodes 1 as A and 2 as B and every capture (established)
pub mod testreg {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c04c;
    pub mod revision { // bits 2:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x7;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// Low byte of the 16-bit address pair used by command and sram. Readable: the retrace shadow reads it back to save and restore the pair around interrupt (established)
pub mod addrlo {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c050;
}
/// High byte of the address pair. Readable. [binary] (established)
pub mod addrhi {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c054;
}
/// System control byte; readable (read-modify-write by the retrace handler and Gr2SetMonitor). Bit roles are NetBSD names [public] except as noted: 0 int (established)
pub mod sysctl {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x6c058;
    pub mod video { // bits 7:7, unknown
        pub const SHIFT: u32 = 7;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod genlock { // bits 6:6, inferred
        pub const SHIFT: u32 = 6;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod cursor_display { // bits 5:5, established
        pub const SHIFT: u32 = 5;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod cursor { // bits 4:4, inferred
        pub const SHIFT: u32 = 4;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod did { // bits 3:3, inferred
        pub const SHIFT: u32 = 3;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod core { // bits 2:2, inferred
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod timing { // bits 1:1, unknown
        pub const SHIFT: u32 = 1;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod interrupt { // bits 0:0, inferred
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
pub const CURSOR_X_THRESHOLD: u32 = 0x20; // established
pub const REG_BLACKOUT: u32 = 0x60; // inferred
pub const REG_CURSOR_EP: u32 = 0x20; // established
pub const REG_CURSOR_MODE: u32 = 0x26; // inferred
pub const REG_CURSOR_X: u32 = 0x22; // established
pub const REG_CURSOR_Y: u32 = 0x24; // established
pub const REG_DID_DIV: u32 = 0x44; // established
pub const REG_DID_END: u32 = 0x42; // established
pub const REG_DID_EP: u32 = 0x40; // established
pub const REG_REVISION: u32 = 0x5; // established
pub const REG_VID_ENABLE: u32 = 0x14; // inferred
pub const REG_VID_EP: u32 = 0x0; // established
pub const SRAM_CURSOR_FRAME_TABLE: u32 = 0x900; // established
pub const SRAM_CURSOR_GLYPH: u32 = 0xa00; // established
pub const SRAM_CURSOR_LINE_LIST: u32 = 0x400; // established
pub const SRAM_DID_FRAME_TABLE: u32 = 0xb00; // established
pub const SRAM_DID_LINE_DEFAULT: u32 = 0x1400; // established
pub const SRAM_FRAME_TABLE: u32 = 0x800; // established
pub const SRAM_INTERLACED: u32 = 0x9f0; // established
pub const SRAM_LINE_LIST: u32 = 0x0; // established
pub const SRAM_SCREENWIDTH: u32 = 0x9f2; // established
pub const SYSCTL_CURSOR_DISPLAY: u32 = 0x20; // established
pub const SYSCTL_GENSYNC: u32 = 0x40; // inferred
pub const SYSCTL_LOAD: u32 = 0x3; // established
pub const SYSCTL_VC1_DID: u32 = 0xc; // established
