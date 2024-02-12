use needletail::parse_fastx_file;
use std::env::args;

// Loads runtime-provided constants for which declarations
// will be generated at `$OUT_DIR/constants.rs`.
pub mod constants {
    include!(concat!(env!("OUT_DIR"), "/constants.rs"));
}

use constants::K;

fn main() {
    let args: Vec<String> = args().collect();
    let input_filename = args.get(1).expect("No argument given");
    let mut reader = parse_fastx_file(input_filename).unwrap();
    let mut kmer_count = 0usize;
    while let Some(record) = reader.next() {
        let seqrec = record.expect("Invalid record");
        kmer_count += seqrec.num_bases() - K + 1;
    }
    println!("{kmer_count}");
}
