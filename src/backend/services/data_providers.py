"""
Data providers: Load Stock and MRP data from Excel files
"""
import os
import pandas as pd
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

class ExcelDataProvider:
    """Load data from Excel files for Stock and MRP simulation"""
    
    STOCK_FILE = "data/stock.xlsx"
    MRP_FILE = "data/mrp.xlsx"
    CONSUMPTION_FILE = "data/consumo_historico.xlsx"
    
    @classmethod
    def _get_file_path(cls, filename: str) -> str:
        """Get full path to data file"""
        base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_path, filename)
    
    @classmethod
    def file_exists(cls, filename: str) -> bool:
        """Check if data file exists"""
        return os.path.exists(cls._get_file_path(filename))
    
    @classmethod
    def load_stock(cls, material_codigo: str = None) -> Dict:
        """Load stock data from Excel"""
        try:
            filepath = cls._get_file_path(cls.STOCK_FILE)
            if not os.path.exists(filepath):
                return cls._generate_sample_stock(material_codigo)
            
            df = pd.read_excel(filepath)
            
            if material_codigo:
                row = df[df['codigo'] == material_codigo].to_dict('records')
                return row[0] if row else cls._generate_sample_stock(material_codigo)
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading stock: {e}")
            return cls._generate_sample_stock(material_codigo)
    
    @classmethod
    def load_mrp(cls, material_codigo: str = None) -> Dict:
        """Load MRP data from Excel"""
        try:
            filepath = cls._get_file_path(cls.MRP_FILE)
            if not os.path.exists(filepath):
                return cls._generate_sample_mrp(material_codigo)
            
            df = pd.read_excel(filepath)
            
            if material_codigo:
                row = df[df['codigo'] == material_codigo].to_dict('records')
                return row[0] if row else cls._generate_sample_mrp(material_codigo)
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading MRP: {e}")
            return cls._generate_sample_mrp(material_codigo)
    
    @classmethod
    def load_consumption_history(cls, material_codigo: str = None, days: int = 90) -> List[Dict]:
        """Load consumption history from Excel"""
        try:
            filepath = cls._get_file_path(cls.CONSUMPTION_FILE)
            if not os.path.exists(filepath):
                return cls._generate_sample_consumption(material_codigo, days)
            
            df = pd.read_excel(filepath)
            
            if material_codigo:
                df_filtered = df[df['codigo'] == material_codigo]
                return df_filtered.to_dict('records')
            
            return df.to_dict('records')
        except Exception as e:
            print(f"Error loading consumption: {e}")
            return cls._generate_sample_consumption(material_codigo, days)
    
    @staticmethod
    def _generate_sample_stock(material_codigo: str = None) -> Dict:
        """Generate sample stock data"""
        return {
            "codigo": material_codigo or "MAT-001",
            "centro": "CC-10",
            "almacen": "ALM-A",
            "cantidad_disponible": 1250,
            "cantidad_reservada": 180,
            "cantidad_libre": 1070,
            "unidad_medida": "KG",
            "punto_reorden": 500,
            "lote_minimo": 100,
            "estado": "disponible",
            "ultima_actualizacion": datetime.now().isoformat()
        }
    
    @staticmethod
    def _generate_sample_mrp(material_codigo: str = None) -> Dict:
        """Generate sample MRP data"""
        return {
            "codigo": material_codigo or "MAT-001",
            "centro": "CC-10",
            "demanda_semana1": 500,
            "demanda_semana2": 480,
            "demanda_semana3": 520,
            "demanda_semana4": 490,
            "stock_proyectado": 1070,
            "necesidad_produccion": 0,
            "fecha_disponibilidad": (datetime.now() + timedelta(days=7)).isoformat(),
            "lead_time_dias": 3,
            "proveedor": "PROV-ABC",
            "estado_orden": "ninguna",
            "recomendacion": "Stock suficiente para 2+ semanas"
        }
    
    @staticmethod
    def _generate_sample_consumption(material_codigo: str = None, days: int = 90) -> List[Dict]:
        """Generate sample consumption history"""
        data = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            data.append({
                "codigo": material_codigo or "MAT-001",
                "centro": "CC-10",
                "fecha": date.strftime("%Y-%m-%d"),
                "cantidad_consumida": round(50 + (i % 30), 2),
                "turno": "T1"
            })
        return data


def create_sample_excel_files():
    """Create sample Excel files for testing"""
    base_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "data"
    )
    os.makedirs(base_path, exist_ok=True)
    
    # Stock data
    stock_data = {
        "codigo": ["MAT-001", "MAT-002", "MAT-003"],
        "descripcion": ["Material A", "Material B", "Material C"],
        "centro": ["CC-10", "CC-10", "CC-20"],
        "almacen": ["ALM-A", "ALM-B", "ALM-A"],
        "cantidad_disponible": [1250, 850, 2100],
        "cantidad_reservada": [180, 120, 300],
        "cantidad_libre": [1070, 730, 1800],
        "unidad_medida": ["KG", "UN", "KG"],
        "punto_reorden": [500, 300, 800],
        "lote_minimo": [100, 50, 200],
        "estado": ["disponible", "bajo", "disponible"],
    }
    df_stock = pd.DataFrame(stock_data)
    df_stock.to_excel(os.path.join(base_path, "stock.xlsx"), index=False)
    
    # MRP data
    mrp_data = {
        "codigo": ["MAT-001", "MAT-002", "MAT-003"],
        "centro": ["CC-10", "CC-10", "CC-20"],
        "demanda_semana1": [500, 200, 800],
        "demanda_semana2": [480, 210, 820],
        "demanda_semana3": [520, 190, 810],
        "demanda_semana4": [490, 220, 795],
        "stock_proyectado": [1070, 730, 1800],
        "necesidad_produccion": [0, 500, 0],
        "lead_time_dias": [3, 5, 2],
        "proveedor": ["PROV-ABC", "PROV-XYZ", "PROV-ABC"],
        "estado_orden": ["ninguna", "pendiente", "entregada"],
        "recomendacion": ["Stock OK", "Ordenar urgente", "Stock OK"],
    }
    df_mrp = pd.DataFrame(mrp_data)
    df_mrp.to_excel(os.path.join(base_path, "mrp.xlsx"), index=False)
    
    print(f"✅ Sample Excel files created in {base_path}")


if __name__ == "__main__":
    create_sample_excel_files()
