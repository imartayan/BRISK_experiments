use bincode::{deserialize_from, serialize_into};
use cbl::kmer::{IntKmer, Kmer};
use clap::{Args, Parser, Subcommand};
use needletail::parse_fastx_file;
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, BufWriter};

// Loads runtime-provided constants for which declarations
// will be generated at `$OUT_DIR/constants.rs`.
pub mod constants {
    include!(concat!(env!("OUT_DIR"), "/constants.rs"));
}

use constants::{K, KT};

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Command,
}

#[derive(Subcommand, Debug)]
enum Command {
    Build(BuildArgs),
    Query(QueryArgs),
    Insert(UpdateArgs),
    Remove(UpdateArgs),
}

#[derive(Args, Debug)]
struct BuildArgs {
    /// Input file (FASTA/Q, possibly gzipped)
    input: String,
    /// Output file (defaults to <input>.hash)
    #[arg(short, long)]
    output: Option<String>,
}

#[derive(Args, Debug)]
struct QueryArgs {
    /// Index file (Hash format)
    index: String,
    /// Input file to query (FASTA/Q, possibly gzipped)
    input: String,
}

#[derive(Args, Debug)]
struct UpdateArgs {
    /// Index file (Hash format)
    index: String,
    /// Input file to query (FASTA/Q, possibly gzipped)
    input: String,
    /// Output file (otherwise overwrite the index file)
    #[arg(short, long)]
    output: Option<String>,
}

fn main() {
    let args = Cli::parse();
    match args.command {
        Command::Build(args) => {
            let input_filename = args.input.as_str();
            let output_filename = if let Some(filename) = args.output {
                filename
            } else {
                input_filename.to_owned() + ".hash"
            };

            let mut map = HashMap::new();
            let mut reader = parse_fastx_file(input_filename)
                .unwrap_or_else(|_| panic!("Failed to open {input_filename}"));
            eprintln!("Building the index of {K}-mers contained in {input_filename}");
            while let Some(record) = reader.next() {
                let seqrec = record.unwrap_or_else(|_| panic!("Invalid record"));
                for kmer in IntKmer::<K, KT>::iter_from_nucs(seqrec.seq().iter()) {
                    map.entry(kmer)
                        .and_modify(|c: &mut u8| *c = c.saturating_add(1))
                        .or_insert(1u8);
                }
            }

            let output = File::create(output_filename.as_str())
                .unwrap_or_else(|_| panic!("Failed to open {output_filename}"));
            let mut writer = BufWriter::new(output);
            eprintln!("Writing the index to {output_filename}");
            serialize_into(&mut writer, &map).unwrap();
        }
        Command::Query(args) => {
            let index_filename = args.index.as_str();
            let input_filename = args.input.as_str();

            let index = File::open(index_filename)
                .unwrap_or_else(|_| panic!("Failed to open {index_filename}"));
            let reader = BufReader::new(index);
            eprintln!("Reading the index stored in {index_filename}");
            let map: HashMap<IntKmer<K, KT>, u8> = deserialize_from(reader).unwrap();

            let mut reader = parse_fastx_file(input_filename)
                .unwrap_or_else(|_| panic!("Failed to open {input_filename}"));
            eprintln!("Querying the {K}-mers contained in {input_filename}");
            let mut total = 0usize;
            let mut positive = 0usize;
            while let Some(record) = reader.next() {
                let seqrec = record.unwrap_or_else(|_| panic!("Invalid record"));
                total += seqrec.seq().len();
                for kmer in IntKmer::<K, KT>::iter_from_nucs(seqrec.seq().iter()) {
                    if map.contains_key(&kmer) {
                        positive += 1;
                    }
                }
            }
            eprintln!("# queries: {total}");
            eprintln!(
                "# positive queries: {positive} ({:.2}%)",
                (positive * 100) as f64 / total as f64
            );
        }
        Command::Insert(args) => {
            let index_filename = args.index.as_str();
            let input_filename = args.input.as_str();
            let output_filename = if let Some(filename) = args.output {
                filename
            } else {
                index_filename.to_owned()
            };

            let index = File::open(index_filename)
                .unwrap_or_else(|_| panic!("Failed to open {index_filename}"));
            let reader = BufReader::new(index);
            eprintln!("Reading the index stored in {index_filename}");
            let mut map: HashMap<IntKmer<K, KT>, u8> = deserialize_from(reader).unwrap();

            let mut reader = parse_fastx_file(input_filename)
                .unwrap_or_else(|_| panic!("Failed to open {input_filename}"));
            eprintln!("Adding the {K}-mers contained in {input_filename} to the index");
            while let Some(record) = reader.next() {
                let seqrec = record.unwrap_or_else(|_| panic!("Invalid record"));
                for kmer in IntKmer::<K, KT>::iter_from_nucs(seqrec.seq().iter()) {
                    map.entry(kmer)
                        .and_modify(|c: &mut u8| *c = c.saturating_add(1))
                        .or_insert(1u8);
                }
            }

            let output = File::create(output_filename.as_str())
                .unwrap_or_else(|_| panic!("Failed to open {output_filename}"));
            let mut writer = BufWriter::new(output);
            eprintln!("Writing the updated index to {output_filename}");
            serialize_into(&mut writer, &map).unwrap();
        }
        Command::Remove(args) => {
            let index_filename = args.index.as_str();
            let input_filename = args.input.as_str();
            let output_filename = if let Some(filename) = args.output {
                filename
            } else {
                index_filename.to_owned()
            };

            let index = File::open(index_filename)
                .unwrap_or_else(|_| panic!("Failed to open {index_filename}"));
            let reader = BufReader::new(index);
            eprintln!("Reading the index stored in {index_filename}");
            let mut map: HashMap<IntKmer<K, KT>, u8> = deserialize_from(reader).unwrap();

            let mut reader = parse_fastx_file(input_filename)
                .unwrap_or_else(|_| panic!("Failed to open {input_filename}"));
            eprintln!("Removing the {K}-mers contained in {input_filename} to the index");
            while let Some(record) = reader.next() {
                let seqrec = record.unwrap_or_else(|_| panic!("Invalid record"));
                for kmer in IntKmer::<K, KT>::iter_from_nucs(seqrec.seq().iter()) {
                    let entry = map
                        .entry(kmer)
                        .and_modify(|c: &mut u8| *c = c.saturating_sub(1));
                    if let Entry::Occupied(e) = entry {
                        if *e.get() == 0 {
                            e.remove();
                        }
                    }
                }
            }

            let output = File::create(output_filename.as_str())
                .unwrap_or_else(|_| panic!("Failed to open {output_filename}"));
            let mut writer = BufWriter::new(output);
            eprintln!("Writing the updated index to {output_filename}");
            serialize_into(&mut writer, &map).unwrap();
        }
    }
}
