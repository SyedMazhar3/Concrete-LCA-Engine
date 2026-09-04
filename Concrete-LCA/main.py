import math
from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class EnvironmentalImpactFactors:
    """Embodied Carbon Coefficients (kg CO2e per kg material) - Cradle to Gate."""
    opc: float = 0.820       # Ordinary Portland Cement (EN 15804 baseline)
    ggbs: float = 0.080      # Ground Granulated Blast-furnace Slag
    fly_ash: float = 0.020   # Fly Ash
    silica_fume: float = 0.028
    coarse_agg: float = 0.005
    fine_agg: float = 0.003
    water: float = 0.0003
    superplasticizer: float = 1.500
    rebar: float = 1.990     # Reinforcing steel per kg


@dataclass
class TransportDistance:
    """Distances in km and emission factors in kg CO2e / tonne-km."""
    distance_km: float
    mode_factor: float = 0.105  # Standard heavy-goods vehicle (HGV)


class ConcreteLCACalculator:
    def __init__(
        self,
        mix_design: Dict[str, float],  # kg/m3
        transport_distances: Dict[str, TransportDistance],
        volume_m3: float = 1.0,
        exposure_class: str = "XC3",    # Exposure condition (e.g., XC3 = Moderate Humidity/Carbonation)
        service_life_years: int = 50,
        exposed_surface_area_m2: float = 10.0
    ):
        self.mix = mix_design
        self.transport = transport_distances
        self.volume = volume_m3
        self.exposure_class = exposure_class
        self.service_life = service_life_years
        self.surface_area = exposed_surface_area_m2
        self.factors = EnvironmentalImpactFactors()

    def calculate_cradle_to_gate(self) -> Tuple[float, Dict[str, float]]:
        """A1-A3: Raw Material Extraction, Transport to Factory, and Manufacturing."""
        breakdown = {}
        total_a1_a3 = 0.0
        
        for material, weight in self.mix.items():
            factor = getattr(self.factors, material, 0.0)
            embodied = weight * factor * self.volume
            breakdown[material] = round(embodied, 2)
            total_a1_a3 += embodied
            
        return round(total_a1_a3, 2), breakdown

    def calculate_transport_emissions(self) -> Tuple[float, Dict[str, float]]:
        """A4: Transport to Construction Site."""
        breakdown = {}
        total_a4 = 0.0
        
        for material, weight in self.mix.items():
            if material in self.transport:
                dist_info = self.transport[material]
                tonnes = (weight * self.volume) / 1000.0
                emissions = tonnes * dist_info.distance_km * dist_info.mode_factor
                breakdown[material] = round(emissions, 2)
                total_a4 += emissions
                
        return round(total_a4, 2), breakdown

    def calculate_carbonation_sink(self) -> float:
        """
        B1: Carbonation during Use Phase (Fick's 2nd Law of Diffusion abstraction).
        Estimates uptake of CO2 via concrete carbonation over service life.
        """
        # k factor (mm/year^0.5) based on Eurocode EN 16757 depending on environment
        k_factors = {
            "XC1": 1.5,  # Dry indoor
            "XC2": 2.0,  # Wet, rarely dry
            "XC3": 4.0,  # Moderate humidity (highest uptake rate)
            "XC4": 2.5,  # Cyclic wet and dry
            "XS1": 1.0   # Marine atmospheric
        }
        k = k_factors.get(self.exposure_class, 2.5)
        
        # Depth of carbonation (mm)
        depth_mm = k * math.sqrt(self.service_life)
        depth_m = depth_mm / 1000.0
        
        # CaO content capable of carbonating (approx. 0.65 for OPC)
        opc_content = self.mix.get("opc", 0.0)
        cacao_ratio = 0.65
        
        # Carbonated volume (m3) = surface area * depth
        carbonated_vol = min(self.volume, self.surface_area * depth_m)
        
        # Stoichiometric uptake (~0.49 kg CO2 per kg CaO)
        co2_uptake = carbonated_vol * opc_content * cacao_ratio * 0.491
        return round(co2_uptake, 2)

    def generate_lca_report(self) -> Dict:
        a1_a3, material_breakdown = self.calculate_cradle_to_gate()
        a4, transport_breakdown = self.calculate_transport_emissions()
        b1_sink = self.calculate_carbonation_sink()
        
        net_emissions = a1_a3 + a4 - b1_sink
        intensity_per_m3 = net_emissions / self.volume

        return {
            "Total Cradle-to-Gate (A1-A3) kg CO2e": a1_a3,
            "Total Transport (A4) kg CO2e": a4,
            "Use-Phase Carbonation Sink (B1) kg CO2e": -b1_sink,
            "Net Lifetime Carbon Impact kg CO2e": round(net_emissions, 2),
            "Carbon Intensity (kg CO2e / m3)": round(intensity_per_m3, 2),
            "Material Embodied Breakdown": material_breakdown,
            "Transport Emissions Breakdown": transport_breakdown
        }

    def evaluate_flaws_and_recommendations(self) -> List[str]:
        """Engineered feedback loop identifying environmental risks and flaws."""
        warnings = []
        opc = self.mix.get("opc", 0.0)
        ggbs = self.mix.get("ggbs", 0.0)
        fly_ash = self.mix.get("fly_ash", 0.0)
        total_cementitious = opc + ggbs + fly_ash
        
        # Check OPC replacement ratio
        scm_ratio = (ggbs + fly_ash) / total_cementitious if total_cementitious > 0 else 0
        if scm_ratio < 0.30:
            warnings.append(
                f"[High Embodied Carbon] High OPC ratio ({(1-scm_ratio)*100:.1f}%). "
                "Consider replacing at least 30-50% OPC with GGBS or Fly Ash to drop A1-A3 emissions."
            )
            
        # Water/Binder Ratio Check
        w_b_ratio = self.mix.get("water", 0) / total_cementitious if total_cementitious > 0 else 0
        if w_b_ratio > 0.45 and self.exposure_class in ["XC3", "XC4"]:
            warnings.append(
                f"[Durability Flaw] Water/Binder ratio ({w_b_ratio:.2f}) exceeds 0.45 in a carbonation exposure class ({self.exposure_class}). "
                "Higher porosity speeds up carbonation depth, risking rebar corrosion despite increasing short-term carbon uptake."
            )

        # Transport Logistics Warning
        for mat, dist in self.transport.items():
            if dist.distance_km > 300 and mat in ["coarse_agg", "fine_agg"]:
                warnings.append(
                    f"[Transport Inefficiency] Aggregates ({mat}) are hauled over {dist.distance_km} km. "
                    "Aggregate mass makes transport emissions dominate A4 phase. Source aggregates locally (< 100 km)."
                )

        return warnings


# =====================================================================
# EXAMPLE RUN TIME EXECUTION
# =====================================================================

if __name__ == "__main__":
    # Concrete Mix Design in kg/m3 (C30/37 structural mix)
    mix_c30 = {
        "opc": 375,
        "ggbs": 50,
        "fly_ash": 0,
        "coarse_agg": 1000,
        "fine_agg": 800,
        "water": 175,
        "superplasticizer": 3.7
    }

    # Logistics Inputs (Distance in km)
    logistics = {
        "opc": TransportDistance(distance_km=120),
        "ggbs": TransportDistance(distance_km=250),
        "coarse_agg": TransportDistance(distance_km=350),  # Intentionally long to trigger alert
        "fine_agg": TransportDistance(distance_km=45)
    }

    # Initialize Engine (100 m3 structural slab project)
    calculator = ConcreteLCACalculator(
        mix_design=mix_c30,
        transport_distances=logistics,
        volume_m3=100.0,
        exposure_class="XC3",
        service_life_years=60,
        exposed_surface_area_m2=500.0
    )

    report = calculator.generate_lca_report()
    flaws = calculator.evaluate_flaws_and_recommendations()

    print("=" * 60)
    print("           LCA CO2 CALCULATOR REPORT (BS EN 15804)          ")
    print("=" * 60)
    for key, value in report.items():
        if isinstance(value, dict):
            print(f"\n--- {key} ---")
            for sub_k, sub_v in value.items():
                print(f"  * {sub_k:18s}: {sub_v} kg CO2e")
        else:
            print(f"{key:42s}: {value}")

    print("\n" + "=" * 60)
    print("      TECHNICAL ENVIRONMENTAL FLAWS & RECOMMENDATIONS      ")
    print("=" * 60)
    for i, flaw in enumerate(flaws, 1):
        print(f"{i}. {flaw}")