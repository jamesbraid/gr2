// @generated from devices/re3/registers.toml by defs-gen - do not edit, change the source
// defs-gen 4
// input sha256 e559fb7a2c82246cdc738e1fe92d4bcc43e2ea7556f489b4fc11622933bb8317
// RE3 raster engine: host-visible register banks
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// First word of the bank [public] a public driver's memory map calls the 27-bit registers. Extent, register names and reset values unknown. No shipped p (unknown)
pub mod bank_27bit {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6c200;
}
/// First word of the bank [public] a public driver's memory map calls the 24-bit registers. Extent, register names and reset values unknown; no shipped p (unknown)
pub mod bank_24bit {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6c280;
}
/// First word of the bank [public] a public driver's memory map calls the 32-bit registers. Extent, register names and reset values unknown; no shipped p (unknown)
pub mod bank_32bit {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6c600;
}
