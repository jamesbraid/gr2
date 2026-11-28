// @generated from devices/xmap5/registers.toml by defs-gen - do not edit, change the source
// SPDX-License-Identifier: BSD-3-Clause
// defs-gen 5
// input sha256 a3ae4415635c74b4ea2e6ed3456ce65a38f3c1efd9e9288d8614427fef7f9c11
// XMAP5 multimode colour mapper (five per Express board)
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// Miscellaneous register file, written through one port after the address pair is set; the diagnostic sizes it at six bytes. Init writes 0, 0, 0, 14, 0  (inferred)
pub mod misc {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x0;
}
/// Mode table port. The target entry is chosen by addrlo (byte address 4 * display ID, addrhi 0) before each write; init writes entry 0 and the retrace a (established)
pub mod mode {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x4;
}
/// Colour table data port. Entry n is selected by addrhi = (n >> 8) & 0x1f and addrlo = n & 0xff; three byte writes (red, green, blue) store one entry an (established)
pub mod clut {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x8;
}
/// Named CRC by NetBSD. Never accessed by the Indigo driver or PROM. Unknown. (unknown)
pub mod crc {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0xc;
}
/// Low address byte for the mode, colour table and misc ports. Readable: the retrace handler reads chip 0's pair and writes it back through the broadcast (established)
pub mod addrlo {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x10;
}
/// High address byte (five bits used for the colour table). Same rules as addrlo. [binary] (established)
pub mod addrhi {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x14;
}
/// Named byte count by NetBSD. Never accessed by shipped drivers. Unknown. (unknown)
pub mod bytecount {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x18;
}
/// Status of the write FIFO in front of the chip (name from NetBSD [public]). Bit 0 set means busy: callers poll until it clears before mode, colour tabl (established)
pub mod fifostatus {
    pub const WIDTH: u32 = 8;
    pub const OFFSET: u64 = 0x1c;
    pub mod overflow { // bits 2:2, unknown
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod room { // bits 1:1, established
        pub const SHIFT: u32 = 1;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod busy { // bits 0:0, established
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
/// Mode table word, one per display ID, written through the mode port at byte address 4 * ID. Field boundaries are [source] the IRIX diagnostic program's (established)
pub mod mode_word {
    pub const WIDTH: u32 = 32;
    pub mod pix_page { // bits 31:27, established
        pub const SHIFT: u32 = 27;
        pub const MASK: u32 = 0x1f;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod pix_mode { // bits 26:24, established
        pub const SHIFT: u32 = 24;
        pub const MASK: u32 = 0x7;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod overlay_enable { // bits 23:20, established
        pub const SHIFT: u32 = 20;
        pub const MASK: u32 = 0xf;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod alt_video { // bits 19:18, established
        pub const SHIFT: u32 = 18;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod pd_mode { // bits 17:16, established
        pub const SHIFT: u32 = 16;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod popup_flags { // bits 15:14, inferred
        pub const SHIFT: u32 = 14;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod aux_page { // bits 13:9, established
        pub const SHIFT: u32 = 9;
        pub const MASK: u32 = 0x1f;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod underlay_enable { // bits 8:8, established
        pub const SHIFT: u32 = 8;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod popup_mode { // bits 6:5, inferred
        pub const SHIFT: u32 = 5;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod popup_page { // bits 4:0, inferred
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x1f;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
pub const BOOT_MODE_WORD_DID0: u32 = 0x82000000; // established
pub const CHIP_COUNT: u32 = 0x5; // established
pub const CLUT_ENTRIES: u32 = 0x2000; // established
pub const MODE_ENTRIES: u32 = 0x20; // established
pub const TEXTPORT_CLUT_BASE: u32 = 0x1000; // established
pub const WINDOW_SIZE: u32 = 0x20; // inferred
