// @generated from devices/hq2/registers.toml by defs-gen - do not edit, change the source
// defs-gen 4
// input sha256 cba5637da661ab8b8f3e475b328cfed1722aba88cfb3d1a80e1228cd43c13f30
// HQ2 command engine: FIFO window, microstore and host registers
#![allow(dead_code)]
#![allow(clippy::doc_markdown)]
#![cfg_attr(rustfmt, rustfmt_skip)]

/// Graphics FIFO window, 128 KiB. A store is a command: bits 10:2 of the address select a microcode entry, bits 15:12 and bit 16 select an attribute shap (established)
pub mod fifo_window {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x40000;
    pub const COUNT: u32 = 32768;
    pub const STRIDE: u64 = 4;
}
/// HQ2 microstore, one 32-bit word per address, address = word index from the window base. [binary] Gr2DownloadHQ2 writes each loaded word and reads it b (established)
pub mod ucode_store {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x60000;
    pub const COUNT: u32 = 8192;
    pub const STRIDE: u64 = 4;
}
/// Attribute jump table, 16 words. [binary] The loader writes 16 words from image offset 0xfc and reads them back (Gr2DownloadHQ2); the ide register menu (established)
pub mod attr_jump {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a000;
    pub const COUNT: u32 = 16;
    pub const STRIDE: u64 = 4;
}
/// Status word. The diagnostic program names it the HQ2 version register and prints the fields below; the kernel and PROMs read it by word load and use t (established)
pub mod status {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a040;
    pub mod version { // bits 31:23, established
        pub const SHIFT: u32 = 23;
        pub const MASK: u32 = 0x1ff;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod ge_ptr { // bits 22:20, established
        pub const SHIFT: u32 = 20;
        pub const MASK: u32 = 0x7;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod ge_ctr { // bits 19:16, established
        pub const SHIFT: u32 = 16;
        pub const MASK: u32 = 0xf;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod zero { // bits 15:14, established
        pub const SHIFT: u32 = 14;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod fifo_lowater { // bits 13:13, established
        pub const SHIFT: u32 = 13;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod fifo_count { // bits 12:6, established
        pub const SHIFT: u32 = 6;
        pub const MASK: u32 = 0x7f;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod fifo_overflow { // bits 5:5, established
        pub const SHIFT: u32 = 5;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod dma_sync_src { // bits 4:3, established
        pub const SHIFT: u32 = 3;
        pub const MASK: u32 = 0x3;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod finish_flag1 { // bits 2:2, established
        pub const SHIFT: u32 = 2;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod finish_flag2 { // bits 1:1, established
        pub const SHIFT: u32 = 1;
        pub const MASK: u32 = 0x1;
        pub const fn get(v: u32) -> u32 {
            (v >> SHIFT) & MASK
        }
        pub const fn set(v: u32, x: u32) -> u32 {
            (v & !(MASK << SHIFT)) | ((x & MASK) << SHIFT)
        }
    }
    pub mod finish_flag3 { // bits 0:0, established
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
/// Number of geometry engines. [binary] The kernel and PROM write the probed count (bit 4 also set when the count is 8); ide writes it and checks it ('Wr (established)
pub mod numge {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a044;
}
/// Finish flag 1 (ide, NetBSD FIN1). A store sets the flag to the stored value; the diagnostic program writes 0 before each DMA test and 1 or 0 from its  (established)
pub mod fin1 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a048;
}
/// Finish flag 2 (ide, NetBSD FIN2). The kernel writes 0 before every context-switch, microcode-start and DMA command and then polls status bit 1. [binar (established)
pub mod fin2 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a04c;
}
/// DMA sync source select (ide DMA sync source, NetBSD DMASYNC): 0 vertical interrupt, 1 video sync, 2 clear, 3 set. The ide menu warns not to write it t (established)
pub mod dmasync {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a050;
}
/// FIFO full timeout. Written 100 by kernel and both PROMs. Unit and effect unknown. [binary] _Gr2HQ2RegInit. (established)
pub mod fifo_full_timeout {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a054;
}
/// FIFO empty timeout. Written 255 by the kernel and 10 by the 4.0.5D PROM. Unit and effect unknown. [binary] (established)
pub mod fifo_empty_timeout {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a058;
}
/// FIFO full threshold. Written 40 at init. The INT2 FIFO line (GIO line 0) is asserted while the fill count is at or above it, inferred from the PROM's  (established)
pub mod fifo_full {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a05c;
}
/// FIFO empty (low water) threshold. Written 1. Effect unknown; status bit 13 is the likely consumer (inferred). [binary] (established)
pub mod fifo_empty {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a060;
}
/// GE7 microcode load word (the fifth word of each record; see devices/ge7). Read back with mask 0x03dfffff. [binary] Gr2DownloadGE7; ide reads and write (established)
pub mod ge7_load_ucode {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a064;
}
/// GE DMA port. The MC's graphics DMA engine addresses this location as the GIO slave address of every board DMA (its physical address, 0x1f06a068 on the (established)
pub mod gedma {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a068;
}
/// HQ to GE7 program counter. The diagnostic program reads it and prints 'Currently, can't read - hw bug - HQ_GE7 PC'. The kernel reads it twice: gr2_err (inferred)
pub mod hq_gepc {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a06c;
}
/// GE microstore address (ide: pc used for loading GE7 microcode, NetBSD GEPC). Written with each record's address by the loaders and with 0 by Gr2TpSetu (established)
pub mod gepc {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a070;
}
/// Interrupt bit register. The diagnostic program calls it 'Intr bit (cleared by host)' and offers a write. No IRIX or PROM driver code touches it. Which (inferred)
pub mod intr {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a074;
}
/// Unstall HQ and GE (ide), NetBSD UNSTALL. Written 0 after microcode load by Gr2TpSetup and the PROM; the diagnostic program has an 'unstall HQ2/GE7 and (established)
pub mod unstall {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a078;
}
/// Probe word, always 0xdeadbeef. ide prints it as MYSTERY ADDRESS. [binary] Gr2Probe, PROM probe. qtest: a word read returns 0xdeadbeef before and after (established)
pub mod probe_word {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a07c;
}
/// Refresh register. Written 16 by the kernel and both PROMs; the diagnostic program writes it from its menu. Effect unknown. [binary] (established)
pub mod refresh {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a080;
}
/// NetBSD names the fin3_netbsd offset FIN3. No shipped program touches it; the third finish flag is written at the finish3 register in every shipped pro (unknown)
pub mod fin3_netbsd {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6a100;
}
/// Finish flag 3 write port (ide Finish Flag 3). The kernel and X server store 0 to clear status bit 0 before a command and poll the bit afterwards; Gr2P (established)
pub mod finish3 {
    pub const WIDTH: u32 = 32;
    pub const OFFSET: u64 = 0x6b000;
}
pub const FIFO_DEPTH_LIMIT: u32 = 0x3f; // inferred
pub const FIFO_FULL_INIT: u32 = 0x28; // established
pub const FIFO_SPACE_CHECK: u32 = 0x23; // established
pub const PROBE_WORD: u32 = 0xdeadbeef; // established
