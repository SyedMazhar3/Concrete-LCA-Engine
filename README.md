# Concrete LCA Calculator

A lightweight Python calculator for estimating the embodied carbon and lifetime carbon impact of concrete mixes. It combines material quantities, transport distances, and a simplified carbonation uptake model to help engineers identify practical carbon-reduction opportunities early in the design process.

## Sales Pitch

Concrete teams should not have to wait for a specialist LCA study to spot obvious carbon hotspots. **Concrete LCA Calculator turns a mix design into an actionable environmental snapshot in seconds.**

Use it to:

- compare the carbon contribution of cement, supplementary cementitious materials, aggregates, water, admixtures, and reinforcement;
- quantify the effect of delivery distances on transport emissions;
- estimate the use-phase carbonation sink over a chosen service life; and
- surface design risks such as high OPC content, excessive water-to-binder ratio, and long-haul aggregate logistics.

The result is a transparent, editable starting point for lower-carbon concrete decisions: reduce clinker where performance allows, source heavy aggregates closer to site, and investigate durability trade-offs before they become expensive project changes.

## Features

- Cradle-to-gate emissions for common concrete constituents (A1-A3)
- Construction-site transport emissions (A4)
- Simplified use-phase carbonation uptake estimate (B1)
- Total net lifetime carbon impact and carbon intensity per m³
- Material-by-material and transport-by-transport breakdowns
- Rule-based engineering warnings and recommendations
- No external dependencies; runs with the Python standard library

## Quick Start

Requirements: Python 3.9 or newer.

Run the included C30/37 example:

```bash
python main.py
```

The example evaluates a 100 m³ structural slab and prints the report and recommendations to the console.

## Basic Usage

```python
from main import ConcreteLCACalculator, TransportDistance

mix = {
    "opc": 300,
    "ggbs": 150,
    "fly_ash": 0,
    "coarse_agg": 1000,
    "fine_agg": 800,
    "water": 165,
    "superplasticizer": 4,
}

transport = {
    "opc": TransportDistance(distance_km=80),
    "ggbs": TransportDistance(distance_km=150),
    "coarse_agg": TransportDistance(distance_km=60),
    "fine_agg": TransportDistance(distance_km=40),
}

calculator = ConcreteLCACalculator(
    mix_design=mix,
    transport_distances=transport,
    volume_m3=25,
    exposure_class="XC3",
    service_life_years=50,
    exposed_surface_area_m2=120,
)

print(calculator.generate_lca_report())
print(calculator.evaluate_flaws_and_recommendations())
```

## Inputs

`mix_design` contains material quantities in **kg/m³**. Supported material keys include:

- `opc`
- `ggbs`
- `fly_ash`
- `silica_fume`
- `coarse_agg`
- `fine_agg`
- `water`
- `superplasticizer`
- `rebar`

`transport_distances` maps material names to `TransportDistance` values. Distance is in kilometres and the default transport factor is `0.105 kg CO2e / tonne-km`.

## Calculation Scope

The calculator currently covers:

- **A1-A3:** material embodied carbon using the coefficients in `EnvironmentalImpactFactors`;
- **A4:** transport from supplier to construction site; and
- **B1:** an estimated carbonation sink based on exposure class, service life, exposed area, and OPC content.

The recommendation engine checks OPC replacement, water-to-binder ratio for XC3/XC4 exposure, and aggregate haulage distance.

## Important Limitations

This is an early-stage estimation tool, not a certified Environmental Product Declaration or project carbon assessment. Results depend on the default factors and simplified assumptions in `main.py`. In particular:

- material factors are generic defaults and should be replaced with verified supplier or EPD data;
- carbonation is an abstraction and does not replace a durability or structural assessment;
- the model does not yet cover all EN 15804 modules, construction activities, maintenance, demolition, recycling, or end-of-life benefits; and
- input validation and uncertainty analysis are not currently included.

Use the output for option screening and design conversations, then validate important decisions with project-specific data and a qualified LCA practitioner.

## Project Structure

```text
.
├── main.py     # Calculator, example inputs, and console report
└── README.md   # Project documentation
```

## License

No license has been specified yet.