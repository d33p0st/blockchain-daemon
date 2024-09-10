// use core::num;
use std::io::{BufRead, Write};

// use pyo3::marshal::VERSION;/
use rustypath::RPath;
use serde::{Serialize, Deserialize};
// use serde_json::map::Entry;
use sha2::{Sha256, Digest};
use chrono::prelude::*;
// use chrono::{Datelike, Timelike, Local, NaiveDateTime};
// use std::{fmt, time};
use pyo3::prelude::*;
// use pyo3::types::PyBytes;

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Block {
    index: usize,
    timestamp: String,
    filename: String,
    original_loc: String,
    data: Data,
    encrypted: bool,
    previous_hash: String,
    hash: String,
    nonce: u64,
}

#[derive(Serialize, Deserialize, Debug, Clone)]
struct Data {
    data: Vec<u8>,
}

impl Data {
    fn new() -> Self {
        Data {
            data: Vec::new(),
        }
    }

    fn make(data: Vec<u8>) -> Self {
        Self { data }
    }

    fn get(&self) -> Vec<u8> {
        self.data.clone()
    }
}

struct BlockChain {
    chain: Vec<Block>,
    difficulty: usize,
}

impl Block {
    fn new(index: usize, filename: String, original_loc: String, data: Data, previous_hash: String, encrypted: bool) -> Self {
        let ist = Utc::now() + chrono::Duration::hours(5) + chrono::Duration::minutes(30);
        let timestamp = ist.to_rfc3339();

        let nonce = 0;

        let mut block = Block {
            index,
            timestamp,
            filename,
            original_loc,
            data,
            encrypted,
            previous_hash: previous_hash.clone(),
            hash: String::new(),
            nonce,
        };

        block.hash = block.calculate_hash();

        block
    }

    fn calculate_hash(&self) -> String {
        let block_data = serde_json::to_string(&self).unwrap_or_else(|_e| {
            eprintln!("Failed to generate hash for block: {}", self.index);
            std::process::exit(1);
        });

        let mut hasher = Sha256::new();
        hasher.update(block_data);
        format!("{:x}", hasher.finalize())
    }

    fn mine_block(&mut self, difficulty: usize) {
        let target = "0".repeat(difficulty);
        while &self.hash[..difficulty] != target {
            self.nonce += 1;
            self.hash = self.calculate_hash();
        }
    }
}

impl BlockChain {
    fn new(difficulty: usize) -> Self {
        let mut blockchain = BlockChain {
            chain: Vec::new(),
            difficulty,
        };
        blockchain.create_genesis();
        blockchain
    }

    fn create_genesis(&mut self) {
        let genesis = Block::new(0, "".to_string(), "".to_string(), Data::new(), String::from("0"), false);
        self.chain.push(genesis);
    }

    fn get_latest(&self) -> &Block {
        self.chain.last().unwrap()
    }

    fn len(&self) -> usize {
        self.chain.len() - 1
    }

    fn add_block(&mut self, filename: String, original_loc: String, data: Data, encrypted: bool) {
        let prevhash = self.get_latest().hash.clone();
        let mut block = Block::new(self.chain.len(), filename, original_loc, data, prevhash, encrypted);
        block.mine_block(self.difficulty);
        self.chain.push(block);
    }

    fn chain_valid(&self) -> bool {
        for i in 1..self.chain.len() {
            let current_b = &self.chain[i];
            let prev_b = &self.chain[i-1];

            if current_b.hash != current_b.calculate_hash() {
                return false;
            }

            if current_b.previous_hash != prev_b.hash {
                return false;
            }
        }

        true
    }
}

#[pyclass]
pub struct BlockChainGenerator {
    blockchain: BlockChain,
}

#[pymethods]
impl BlockChainGenerator {
    #[new]
    pub fn new(difficulty: usize) -> PyResult<Self> {
        Ok(Self { blockchain: BlockChain::new(difficulty) })
    }

    pub fn add_block(&mut self, filename: String, loc: String, data: &[u8], encryption: bool) -> PyResult<()> {

        let dat = Data::make(data.to_owned());

        self.blockchain.add_block(filename, loc, dat, encryption);

        Ok(())
    }

    pub fn len(&self) -> PyResult<usize> {
        Ok(self.blockchain.len())
    }

    pub fn iterate_and_write(&self, filename_or_index: String, loc: String) -> PyResult<()> {
        let mut data = Vec::new();
        for chain in &self.blockchain.chain {
            if chain.filename == filename_or_index {
                data = chain.data.get().clone();
                break;
            } else if chain.index.to_string() == filename_or_index {
                data = chain.data.get().clone();
                break;
            }
        }

        if ! data.is_empty() {
            // write the data to the file
            let mut file = std::fs::OpenOptions::new().write(true).create(true).truncate(true).open(loc)?;
            file.write_all(&data)?;
            Ok(())
        } else {
            Err(pyo3::exceptions::PyFileNotFoundError::new_err(format!("No file found: {}", filename_or_index)))
        }
    }

    pub fn valid(&self) -> PyResult<bool> {
        Ok(self.blockchain.chain_valid())
    }

    pub fn load_backup(&mut self, loc: &str) -> PyResult<()> {
        let backup = get_latest_backup(loc)?;
        // println!("{}", backup);

        if ! backup.is_empty() {
            let file = std::fs::File::open(RPath::from(loc).join(&backup).convert_to_string())?;
            let reader = std::io::BufReader::new(file);

            let mut lines = reader.lines();
            // let mut index = 0;
            // let mut is_reading = true;

            while let (Some(filename_line), Some(loc_line), Some(data_line), Some(encrypted_line)) = (lines.next(), lines.next(), lines.next(), lines.next()) {
                let filename_line = filename_line?;
                let data_line = data_line?;
                let encrypted_line = encrypted_line?;
                let loc_line = loc_line?;

                let filename = if filename_line.starts_with("filename: ") {
                    let mid = filename_line.strip_prefix("filename: ").unwrap_or("").trim().to_string();
                    mid.replace("\n", "")
                } else {
                    // eprintln!("Failed to get backup data.");
                    Err(pyo3::exceptions::PyException::new_err("Failed to get filename from backup"))?
                };

                let original_loc = if loc_line.starts_with("original_loc: ") {
                    let mid = loc_line.strip_prefix("original_loc: ").unwrap_or("").trim().to_string();
                    mid.replace("\n", "")
                } else {
                    Err(pyo3::exceptions::PyException::new_err("Failed to get original_location from backup"))?
                };

                let data = if data_line.starts_with("data: ") {
                    let mid = data_line.strip_prefix("data: ").unwrap_or("").trim().to_string();
                    string_to_bytes(&mid.replace("\n", "")).unwrap_or_else(|e| {
                        eprintln!("Failed to convert data back to bytes: {}", e);
                        std::process::exit(1);
                    })
                } else {
                    Err(pyo3::exceptions::PyException::new_err("Failed to parse vector<u8> [RUST] from string representation to vec<u8>"))?
                };

                let encrypted = if encrypted_line.starts_with("encrypted: ") {
                    let mid = encrypted_line.strip_prefix("encrypted: ").unwrap_or("").trim().to_string();
                    mid.replace("\n", "")
                } else {
                    Err(pyo3::exceptions::PyException::new_err("Failed to fetch encrypted status"))?
                };

                if filename.is_empty() || data.is_empty() || encrypted.is_empty() {
                    Err(pyo3::exceptions::PyException::new_err("Failed to get data for file."))?
                } else {
                    let mut encryption = false;
                    if encrypted.to_lowercase() == "true" {
                        encryption = true;
                    }

                    match self.add_block(filename.clone(), original_loc, data.as_slice(), encryption) {
                        Ok(()) => {},
                        Err(_e) => {
                            eprintln!("failed to add block for file \'{}\': {}", filename, _e);
                        },
                    }
                }
            }
            
        }

        Ok(())
    }

    pub fn exit_protocol(&self, loc: String) -> PyResult<bool> {
        if self.blockchain.len() > 0 {

            let mut backup = std::fs::File::create(RPath::from(&loc).join(&("bcDaemon_".to_string() + &(match get_latest_number(&loc) {
                Ok(val) => val,
                Err(e) => {
                    eprintln!("Error: {e}");
                    String::from("100")
                },
            }))).convert_to_string())?;

            for chain in &self.blockchain.chain {
                if chain.index == 0 {
                    continue;
                }
                let filename = format!("filename: {}\n", chain.filename);
                let original_loc = format!("original_loc: {}\n", chain.original_loc);
                let data = format!("data: {:?}\n", chain.data.get());
                let encrypted = format!("encrypted: {}\n", chain.encrypted);
                // println!("{}", format!("{} {} {} {}", filename, original_loc, data, encrypted));
                backup.write(filename.as_bytes())?;
                backup.write(original_loc.as_bytes())?;
                backup.write(data.as_bytes())?;
                backup.write(encrypted.as_bytes())?;
            }
        }

        Ok(true)
    }

    pub fn list(&self) -> PyResult<Vec<String>> {
        let mut list: Vec<String> = Vec::new();
        let mut count = 0;
        for chain in &self.blockchain.chain {
            if count == 0 {
                count += 1;
                continue;
            }
            list.push(chain.filename.clone());
        }

        Ok(list)
    }
}

// use regex::Regex;

// function to get latest number
fn get_latest_number(loc: &str) -> std::io::Result<String> {
    let mut number: usize = 1;
    for entry in RPath::from(loc).read_dir()? {
        let entry = entry?;
        let filename_os_str = entry.file_name();
        let mut filename = filename_os_str.to_str().unwrap();
        if filename.starts_with("bcDaemon_") {
            filename = filename.strip_prefix("bcDaemon_").unwrap();
            let number_: usize = filename.parse().unwrap_or_else(|e| {
                eprintln!("Failed to parse interger from backups: {}", e);
                0
            });
            if number_ == 0 {
                continue;
            } else if number_ > number {
                number = number_
            }
        } else {
            continue;
        }
    }

    Ok(number.to_string())
}

// function to get the latest backup name
fn get_latest_backup(loc: &str) -> std::io::Result<String> {
    let path = RPath::from(loc);
    let mut number: usize = 1;
    for entry in path.read_dir()? {
        let entry = entry?;
        let filename_os_str = entry.file_name();
        let mut filename = filename_os_str.to_str().unwrap();

        if filename.starts_with("bcDaemon_") {
            filename = filename.strip_prefix("bcDaemon_").unwrap();
            let num_: usize = filename.parse().unwrap_or_else(|e| {
                eprintln!("Failed to parse integer from backup file.: {e}");
                0
            });

            if num_ == 0 {
                continue;
            } else if num_ > number {
                number = num_
            }
        } else {
            continue;
        }
    }
    if path.join(&("bcDaemon_".to_string() + &number.to_string())).exists() {
        Ok("bcDaemon_".to_string() + &number.to_string())
    } else {
        Ok(String::new())
    }
    
}


// function to create bytes back from string representation
fn string_to_bytes(input: &str) -> Result<Vec<u8>, Box<dyn std::error::Error>> {
    let trimmed = input.trim_matches(|c| c == '[' || c == ']');
    let bytes: Result<Vec<u8>, _> = trimmed.split(',').map(|s| s.trim().parse::<u8>()).collect();
    bytes.map_err(|e| e.into())
}