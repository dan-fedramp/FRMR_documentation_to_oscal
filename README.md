# FedRAMP Documentation to OSCAL Catalog Converter

This project provides a script to generate an [OSCAL](https://pages.nist.gov/OSCAL/) compliant catalog from the FedRAMP Machine-Readable Documentation (FRMR) JSON.

## Overview

The primary purpose of this tool is to automate the conversion of FedRAMP documentation into a standardized OSCAL JSON format, specifically focusing on requirements that affect Providers.

The script performs the following actions:
1.  Fetches the latest `FRMR.documentation.json` from the [FedRAMP documentation repository](https://github.com/FedRAMP/docs).
2.  Filters and collects requirements using an ID pattern (e.g., `XXX-XXX-XXX`).
3.  Maps each requirement to an OSCAL control structure (including statements, definitions, updates, and notes).
4.  Outputs the final OSCAL catalog to `frmr.catalog.oscal.json`.

## Requirements

-   **Python 3.7+**
-   **Dependencies:**
    -   `requests`: Used for fetching the remote JSON data.
    -   `json`, `uuid`, `datetime`, `os`, `re`: Standard library modules.

## Setup

1.  Clone the repository.
2.  (Optional but recommended) Create and activate a virtual environment:
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```
3.  Install the required dependencies:
    ```bash
    pip install requests
    ```

## Usage

To generate the OSCAL catalog, run the following command:

```bash
python generate_oscal_catalog.py
```

Upon successful execution, the file `frmr.catalog.oscal.json` will be created in the project root.

## Tests

-   **TODO:** No automated tests are currently implemented.
-   **TODO:** Add unit tests for `item_to_control` and `collect_requirements`.
-   **TODO:** Add integration tests for the full conversion pipeline with mocked network requests.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

