use bincode::{DefaultOptions, Options};
use cbl::kmer::{IntKmer, Kmer};
use clap::{Args, Parser, Subcommand};
use needletail::{parse_fastx_file, FastxReader};
use serde::{de::DeserializeOwned, Serialize};
use std::collections::hash_map::Entry;
use std::collections::HashMap;
use std::fs::File;
use std::io::{BufReader, BufWriter};
use std::path::Path;

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
    /// Build an index containing the k-mers of a FASTA/Q file
    Build(BuildArgs),
    /// Query an index for every k-mer contained in a FASTA/Q file
    Query(QueryArgs),
    /// Add the k-mers of a FASTA/Q file to an index
    Insert(UpdateArgs),
    /// Remove the k-mers of a FASTA/Q file from an index
    Remove(UpdateArgs),
}

#[derive(Args, Debug)]
struct BuildArgs {
    /// Input file (FASTA/Q, possibly gzipped)
    input: String,
    /// Output file (no serialization by default)
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
    /// Output file (no serialization by default)
    #[arg(short, long)]
    output: Option<String>,
}

fn read_fasta<P: AsRef<Path> + Copy>(path: P) -> Box<dyn FastxReader> {
    parse_fastx_file(path)
        .unwrap_or_else(|_| panic!("Failed to open {}", path.as_ref().to_str().unwrap()))
}

fn read_index<D: DeserializeOwned, P: AsRef<Path> + Copy>(path: P) -> D {
    let index = File::open(path)
        .unwrap_or_else(|_| panic!("Failed to open {}", path.as_ref().to_str().unwrap()));
    let reader = BufReader::new(index);
    eprintln!(
        "Reading the index stored in {}",
        path.as_ref().to_str().unwrap()
    );
    DefaultOptions::new()
        .with_varint_encoding()
        .reject_trailing_bytes()
        .deserialize_from(reader)
        .unwrap()
}

fn write_index<S: Serialize, P: AsRef<Path> + Copy>(index: &S, path: P) {
    let output = File::create(path)
        .unwrap_or_else(|_| panic!("Failed to open {}", path.as_ref().to_str().unwrap()));
    let mut writer = BufWriter::new(output);
    eprintln!("Writing the index to {}", path.as_ref().to_str().unwrap());
    DefaultOptions::new()
        .with_varint_encoding()
        .reject_trailing_bytes()
        .serialize_into(&mut writer, &index)
        .unwrap();
}

fn main() {
    let args = Cli::parse();
    match args.command {
        Command::Build(args) => {
            let input_filename = args.input.as_str();
            let mut map = HashMap::new();
            let mut reader = read_fasta(input_filename);
            eprintln!("Building the index of {K}-mers contained in {input_filename}");
            while let Some(record) = reader.next() {
                let seqrec = record.unwrap_or_else(|_| panic!("Invalid record"));
                for kmer in IntKmer::<K, KT>::iter_from_nucs(seqrec.seq().iter()) {
                    map.entry(kmer)
                        .and_modify(|c: &mut u8| *c = c.saturating_add(1))
                        .or_insert(1u8);
                }
            }
            if let Some(output_filename) = args.output {
                write_index(&map, output_filename.as_str());
            }
        }
        Command::Query(args) => {
            let index_filename = args.index.as_str();
            let input_filename = args.input.as_str();
            let map: HashMap<IntKmer<K, KT>, u8> = read_index(index_filename);
            let mut reader = read_fasta(input_filename);
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
            let mut map: HashMap<IntKmer<K, KT>, u8> = read_index(index_filename);
            let mut reader = read_fasta(input_filename);
            eprintln!("Adding the {K}-mers contained in {input_filename} to the index");
            while let Some(record) = reader.next() {
                let seqrec = record.unwrap_or_else(|_| panic!("Invalid record"));
                for kmer in IntKmer::<K, KT>::iter_from_nucs(seqrec.seq().iter()) {
                    map.entry(kmer)
                        .and_modify(|c: &mut u8| *c = c.saturating_add(1))
                        .or_insert(1u8);
                }
            }
            if let Some(output_filename) = args.output {
                write_index(&map, output_filename.as_str());
            }
        }
        Command::Remove(args) => {
            let index_filename = args.index.as_str();
            let input_filename = args.input.as_str();
            let mut map: HashMap<IntKmer<K, KT>, u8> = read_index(index_filename);
            let mut reader = read_fasta(input_filename);
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
            if let Some(output_filename) = args.output {
                write_index(&map, output_filename.as_str());
            }
        }
    }
}
