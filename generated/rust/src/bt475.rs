// @generated from devices/bt475/registers.toml by defs-gen - do not edit, change the source
// defs-gen 3
// input sha256 e092e289cdf7071aaa43ac066a8157c9ebaf1861cc18de50147bf970a5c6e882
// Brooktree Bt475 and Bt477 RAMDAC: datasheet port map only, no Express use found
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

pub const SEL_ADDR_READ: u32 = 0x3; // established
pub const SEL_ADDR_WRITE: u32 = 0x0; // established
pub const SEL_COMMAND: u32 = 0x6; // established
pub const SEL_OVERLAY_DATA: u32 = 0x5; // established
pub const SEL_OVERLAY_READ: u32 = 0x7; // established
pub const SEL_OVERLAY_WRITE: u32 = 0x4; // established
pub const SEL_PALETTE: u32 = 0x1; // established
pub const SEL_READ_MASK: u32 = 0x2; // established
