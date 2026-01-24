"""
Unit tests for heat exchanger calculations
"""

import pytest
import numpy as np
from src.calculations import HeatExchanger, calculate_effectiveness_from_ntu
from src.fluid_properties import FluidProperties


class TestHeatExchangerLMTD:
    """Tests for LMTD method"""
    
    def test_basic_lmtd_counter_flow(self):
        """Test basic LMTD calculation for counter flow"""
        hx = HeatExchanger(flow_arrangement='Counter Flow')
        
        results = hx.calculate_lmtd(
            T_hot_in=90,
            T_hot_out=50,
            T_cold_in=25,
            T_cold_out=45,
            m_hot=2.0,
            m_cold=3.0,
            fluid_hot='Water',
            fluid_cold='Water',
            U_value=500
        )
        
        # Check that heat transfer is positive
        assert results['Q'] > 0
        
        # Check that area is positive and reasonable
        assert results['area'] > 0
        assert results['area'] < 1000  # Sanity check
        
        # Check effectiveness is between 0 and 1
        assert 0 < results['effectiveness'] < 1
        
        # Check energy balance (should be close to equal)
        assert abs(results['Q_hot'] - results['Q_cold']) / results['Q_hot'] < 0.01
    
    def test_lmtd_parallel_flow(self):
        """Test LMTD calculation for parallel flow"""
        hx = HeatExchanger(flow_arrangement='Parallel Flow')
        
        results = hx.calculate_lmtd(
            T_hot_in=90,
            T_hot_out=60,
            T_cold_in=25,
            T_cold_out=40,
            m_hot=2.0,
            m_cold=3.0,
            fluid_hot='Water',
            fluid_cold='Water',
            U_value=500
        )
        
        assert results['Q'] > 0
        assert results['area'] > 0
        assert 0 < results['effectiveness'] < 1
    
    def test_lmtd_invalid_temperatures(self):
        """Test that invalid temperatures raise error"""
        hx = HeatExchanger(flow_arrangement='Counter Flow')
        
        with pytest.raises(ValueError):
            # Hot outlet colder than cold inlet (violates 2nd law)
            hx.calculate_lmtd(
                T_hot_in=50,
                T_hot_out=20,
                T_cold_in=25,
                T_cold_out=45,
                m_hot=2.0,
                m_cold=3.0,
                fluid_hot='Water',
                fluid_cold='Water',
                U_value=500
            )


class TestHeatExchangerNTU:
    """Tests for NTU method"""
    
    def test_basic_ntu_counter_flow(self):
        """Test basic NTU calculation for counter flow"""
        hx = HeatExchanger(flow_arrangement='Counter Flow')
        
        results = hx.calculate_ntu(
            T_hot_in=90,
            T_cold_in=25,
            m_hot=2.0,
            m_cold=3.0,
            fluid_hot='Water',
            fluid_cold='Water',
            U_value=500,
            Area=15.0
        )
        
        # Check that heat transfer is positive
        assert results['Q'] > 0
        
        # Check outlet temperatures are reasonable
        assert results['T_hot_out'] < results['T_hot_in']
        assert results['T_cold_out'] > results['T_cold_in']
        
        # Check effectiveness is between 0 and 1
        assert 0 < results['effectiveness'] < 1
        
        # Check NTU is positive
        assert results['NTU'] > 0
    
    def test_ntu_parallel_flow(self):
        """Test NTU calculation for parallel flow"""
        hx = HeatExchanger(flow_arrangement='Parallel Flow')
        
        results = hx.calculate_ntu(
            T_hot_in=90,
            T_cold_in=25,
            m_hot=2.0,
            m_cold=3.0,
            fluid_hot='Water',
            fluid_cold='Water',
            U_value=500,
            Area=15.0
        )
        
        assert results['Q'] > 0
        assert results['T_hot_out'] < results['T_hot_in']
        assert results['T_cold_out'] > results['T_cold_in']


class TestFluidProperties:
    """Tests for fluid properties"""
    
    def test_water_properties(self):
        """Test water property retrieval"""
        water = FluidProperties('Water')
        
        # Test at 25°C
        props = water.get_all_properties(25)
        
        # Density should be close to 1000 kg/m³
        assert 990 < props['density'] < 1010
        
        # Specific heat should be close to 4180 J/(kg·K)
        assert 4100 < props['specific_heat'] < 4250
        
        # Prandtl number should be reasonable for water
        assert 0.5 < props['prandtl'] < 15
    
    def test_air_properties(self):
        """Test air property retrieval"""
        air = FluidProperties('Air')
        
        props = air.get_all_properties(25)
        
        # Density should be close to 1.2 kg/m³
        assert 1.0 < props['density'] < 1.5
        
        # Specific heat should be close to 1005 J/(kg·K)
        assert 1000 < props['specific_heat'] < 1020
    
    def test_invalid_fluid(self):
        """Test that invalid fluid name raises error"""
        with pytest.raises(ValueError):
            FluidProperties('InvalidFluid')


class TestEffectivenessNTU:
    """Tests for effectiveness-NTU relationships"""
    
    def test_counter_flow_effectiveness(self):
        """Test effectiveness calculation for counter flow"""
        NTU = 2.0
        C_ratio = 0.5
        
        eff = calculate_effectiveness_from_ntu(NTU, C_ratio, 'Counter Flow')
        
        # Effectiveness should be between 0 and 1
        assert 0 < eff < 1
        
        # For counter flow with NTU=2, C_ratio=0.5, eff should be around 0.7-0.8
        assert 0.65 < eff < 0.85
    
    def test_parallel_flow_effectiveness(self):
        """Test effectiveness calculation for parallel flow"""
        NTU = 2.0
        C_ratio = 0.5
        
        eff = calculate_effectiveness_from_ntu(NTU, C_ratio, 'Parallel Flow')
        
        # Effectiveness should be between 0 and 1
        assert 0 < eff < 1
        
        # Parallel flow should have lower effectiveness than counter flow
        eff_counter = calculate_effectiveness_from_ntu(NTU, C_ratio, 'Counter Flow')
        assert eff < eff_counter


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
