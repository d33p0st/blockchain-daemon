mod blockchain;

use pyo3::prelude::*;

#[pymodule]
#[pyo3(name = "rust")]
fn rust(_py: Python<'_>, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_class::<blockchain::BlockChainGenerator>()?;
    // m.add_function(wrap_pyfunction!(blockchain::))
    Ok(())
}