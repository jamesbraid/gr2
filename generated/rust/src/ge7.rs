// @generated from devices/ge7/registers.toml by defs-gen - do not edit, change the source
// SPDX-License-Identifier: BSD-3-Clause
// defs-gen 5
// input sha256 e30b0fdf775c51b8fdeab63c9fca6fbdcc7b0ebfdb6d0844c750cd3ef14767df
// GE7 geometry engines: host window and microcode load registers
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// Shared data RAM below the ready flag. [binary] The microcode loader copies the constants block into its first words and reads them back; its error tex (established)
pub mod shared_ram {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x0;
    pub const COUNT: u32 = 32767;
    pub const STRIDE: u64 = 4;
}
/// Last word of the shared RAM, used as a flag. [binary] The driver stores 1 after the built-in console microcode loads and 0 when a load fails; the cons (established)
pub mod ucode_ready {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x1fffc;
}
/// Engine 0 storage below the microcode window. [binary] The engine probe takes slot 0 as present and tests only slots 1 to 7, so ordinary storage here i (inferred)
pub mod slot0_ram {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x68000;
    pub const COUNT: u32 = 248;
    pub const STRIDE: u64 = 4;
}
/// Microword column 0, lowest. [binary] The loader writes record bytes 20 to 23 here and reads them back unmasked. One window serving every populated eng (established)
pub mod ucode_d0 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x683e0;
}
/// Microword column 1. [binary] The loader writes record bytes 16 to 19 here and reads them back unmasked. qtest: a full 32-bit value reads back. (established)
pub mod ucode_d1 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x683e4;
}
/// Microword column 2. [binary] The loader writes record bytes 12 to 15 here and reads them back unmasked. qtest: a full 32-bit value reads back. (established)
pub mod ucode_d2 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x683e8;
}
/// Microword column 3. [binary] The loader writes record bytes 8 to 11 here; the verify masks both sides to seven bits, so only seven bits are stored. qt (established)
pub mod ucode_d3 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x683ec;
    pub mod stored { // bits 6:0, established
        pub const SHIFT: u32 = 0;
        pub const MASK: u32 = 0x7f;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// GE7 revision. [binary] The kernel driver and the PROM probe write zero, read the word back and keep bits 7:5 of the low byte. [public] NetBSD reads an (established)
pub mod revision {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x683f4;
    pub mod rev { // bits 7:5, inferred
        pub const SHIFT: u32 = 5;
        pub const MASK: u32 = 0x7;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
}
/// Engine slots 1 to 7, 1 KiB each. [binary] The engine probe writes five words per slot at slot offsets 0x0, 0x7c, 0xfc, 0x17c and 0x1fc and reads them  (established)
pub mod slot_ram {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x68400;
    pub const COUNT: u32 = 1792;
    pub const STRIDE: u64 = 4;
}
