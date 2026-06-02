# P&C Loss Reserving & IBNR Estimation Engine

A production-ready, interactive Property & Casualty (P&C) loss reserving engine built inside Jupyter Notebook using pure Pandas and NumPy. This application transforms flat regulatory NAIC Schedule P transaction logs into structured actuarial loss development triangles to calculate required Incurred But Not Reported (IBNR) cash reserves.

---

## 📂 Repository Layout
```text
pc-loss-reserving-engine/
├── README.md                 # Project Documentation & Methodology
├── Project_P_and_C.ipynb     # Interactive Actuarial Engine & Jupyter Dashboard
└── Data.csv       # Casualty Actuarial Society Data File (Schedule P Profile)
```

---

## 🌐 Background & Data Origin
This application utilizes authentic, cleaned run-off data compiled by the **Casualty Actuarial Society (CAS) Reserve Research Working Group** in collaboration with S&P Global Market Intelligence. 

The underlying data originates from **Schedule P (Analysis of Losses and Loss Expenses)** within the National Association of Insurance Commissioners (NAIC) database. It captures 10 distinct accident years (1998–2007) across U.S. property-casualty insurers, tracking both paid cash triangles and case reserve estimates.

---

## 📊 Core Functionalities & Features

- **Actuarial Diagonal Filtering**: Maps raw transaction records to their distinct calendar valuation years (`AccidentYear + DevelopmentLag - 1`) and applies a moving diagonal evaluation wall up to Year 2007. This isolates historical development patterns and leaves recent accident cohorts open for mathematical prediction.
- **Chain-Ladder Estimation Framework (CL)**: Computes volume-weighted Age-to-Age Development Factors (Link Ratios) across historical insurance records to project ultimate outstanding claims liabilities.
- **Bornhuetter-Ferguson Framework (BF)**: Integrates an adjustable Initial Expected Loss Ratio (IELR) runtime modifier to regularize and stabilize reserving targets for highly volatile, early-stage accident years.
- **In-Notebook UI Dashboard**: Uses `ipywidgets` and `matplotlib` to generate a live-updating user interface directly inside the notebook cell layout, eliminating the need for external web servers or open port configurations.

---

## 💾 Core Dataset Variables Handled
The engine parses and structures several regulatory columns from the original schema:
*   `GRNAME` / `GRCODE`: NAIC Insurance Company/Group name and unique numeric identifying code.
*   `AccidentYear` / `DevelopmentLag`: The year the claim occurred and its relative chronological growth age.
*   `CumPaidLoss`: Cumulative paid net losses and allocated expenses (Cash out the door).
*   `IncurLosses`: Incurred net losses and allocated expenses (Paid losses + outstanding adjuster case reserves).
*   `EarnedPremDIR`: Underwriting Net Direct and Assumed Earned Premiums used as risk exposure bases for the BF method.

---

## 🧮 Mathematical Architecture Implemented

### 1. Volume-Weighted Age-to-Age Link Ratio ($f_k$)
Calculates the historical claims growth progression factor from maturity period $k$ to $k+1$:
$$f_k = \frac{\sum_{i} C_{i, k+1}}{\sum_{i} C_{i, k}}$$

### 2. Cumulative Development Factor (CDF)
Determines the compound multiplier required to advance current cumulative losses ($C_{i,k}$) to final ultimate maturity:
$$\text{CDF}_k = \prod_{j=k}^{n-1} f_j$$

### 3. Bornhuetter-Ferguson IBNR Reserve Allocation
Dampens projection volatility in young accident years by utilizing pricing exposures alongside the mathematical percent of claims left unreported:
$$\text{IBNR}_{\text{BF}} = (\text{Earned Premium} \times \text{IELR}) \times \left(1 - \frac{1}{\text{CDF}_k}\right)$$

---

## 🚀 System Setup & Execution

### 1. Requirements Setup
Clone this repository to your local computer and ensure you have the core data science libraries installed:
```bash
git clone https://github.com
cd pc-loss-reserving-engine
pip install pandas numpy matplotlib ipywidgets
```

### 2. Dashboard Execution
1. Open your terminal environment and launch your environment: `jupyter notebook`
2. Open **`Project_P_and_C.ipynb`**.
3. Select **Cell ➔ Run All** to render the interactive UI dropdown menus and the live slider widget.



---

## 📈 Dataset Reference & Citation
The execution layer maps columns matching the official **Casualty Actuarial Society (CAS) Loss Reserving Database** (Commercial Auto Liability profile). Data units are scaled and presented in thousands ($K).

*   **Official Source**: [CAS Loss Reserving Data Pulled from NAIC Schedule P](https://www.casact.org/publications-research/research/research-resources/loss-reserving-data-pulled-naic-schedule-p)
