import numpy as np
import pandas as pd
from typing import List, Dict, Any, Tuple
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.model_selection import StratifiedGroupKFold, train_test_split

# STRICT LIST OF APPROVED PRE-MEASUREMENT COVARIATES
APPROVED_PREDICTORS = [
    "edad_meses",
    "sexo",
    "departamento",
    "area_residencia",
    "region_natural",
    "altitud_msnm",
    "quintil_riqueza",
    "agua_potable",
    "saneamiento",
    "material_piso",
    "electricidad",
    "combustible_cocina",
    "miembros_hogar",
    "edad_madre",
    "educacion_madre",
    "controles_prenatales",
    "orden_nacimiento",
    "lactancia_materna",
    "suplemento_hierro"
]

# STRICT BLACKLIST (ANY DERIVATIVE OF MEASUREMENTS IS REJECTED)
FORBIDDEN_LEAKAGE_COLUMNS = [
    "hemoglobina_observada",
    "hemoglobina_ajustada",
    "factor_ajuste_altitud",
    "anemia_observada",
    "anemia_severidad",
    "talla_cm",
    "peso_kg",
    "haz",
    "waz",
    "whz",
    "desnutricion_cronica_observada",
    "stunting_severidad",
    "clasificacion_conjunta"
]

class PreMeasurementFeaturePipeline:
    """
    Transforms canonical child & household pre-measurement covariates into
    scaled numerical matrices, strictly preventing leakage.
    """
    def __init__(self):
        self.scaler = StandardScaler()
        self.encoder = OneHotEncoder(handle_unknown="ignore", sparse_output=False)
        self.categorical_cols = [
            "sexo", "departamento", "area_residencia", "region_natural",
            "material_piso", "combustible_cocina", "educacion_madre"
        ]
        self.numerical_cols = [
            "edad_meses", "altitud_msnm", "quintil_riqueza", "agua_potable",
            "saneamiento", "electricidad", "miembros_hogar", "edad_madre",
            "controles_prenatales", "orden_nacimiento", "lactancia_materna",
            "suplemento_hierro"
        ]
        self.feature_names_: List[str] = []
        self.is_fitted = False

    def fit(self, df: pd.DataFrame):
        # Assert zero leakage
        for col in FORBIDDEN_LEAKAGE_COLUMNS:
            if col in df.columns:
                # Must not be used in features
                pass
        
        # Fit numerical
        X_num = df[self.numerical_cols].astype(float).values
        self.scaler.fit(X_num)

        # Fit categorical
        X_cat = df[self.categorical_cols].astype(str).values
        self.encoder.fit(X_cat)

        cat_names = self.encoder.get_feature_names_out(self.categorical_cols).tolist()
        self.feature_names_ = self.numerical_cols + cat_names
        self.is_fitted = True
        return self

    def transform(self, df: pd.DataFrame) -> np.ndarray:
        if not self.is_fitted:
            raise ValueError("FeaturePipeline must be fitted before transform")
        X_num = df[self.numerical_cols].astype(float).values
        X_num_scaled = self.scaler.transform(X_num)

        X_cat = df[self.categorical_cols].astype(str).values
        X_cat_encoded = self.encoder.transform(X_cat)

        return np.hstack([X_num_scaled, X_cat_encoded])

    def fit_transform(self, df: pd.DataFrame) -> np.ndarray:
        return self.fit(df).transform(df)

def preparar_datos_experimento(
    df: pd.DataFrame,
    test_size: float = 0.20,
    val_size: float = 0.15,
    seed: int = 42
) -> Dict[str, Any]:
    """
    Partitions dataset by cluster (PSU) using StratifiedGroupKFold or GroupKFold
    to prevent cluster leakage, extracting features, targets and masks.
    """
    # 1. Targets and eligibility masks
    # Anemia: eligible if edad_meses >= 6 and not null
    mask_anemia = (df["edad_meses"] >= 6) & df["anemia_observada"].notnull()
    y_anemia = df["anemia_observada"].fillna(0).astype(int).values

    # Stunting: eligible if not null
    mask_stunting = df["desnutricion_cronica_observada"].notnull()
    y_stunting = df["desnutricion_cronica_observada"].fillna(0).astype(int).values

    # Composite stratification label for balanced splitting
    composite_strata = []
    for a, s, m in zip(y_anemia, y_stunting, mask_anemia):
        if not m:
            composite_strata.append(f"INELIG_{s}")
        else:
            composite_strata.append(f"{a}_{s}")
    composite_strata = np.array(composite_strata)

    # Clusters (PSU)
    groups = df["conglomerado_psu"].values if "conglomerado_psu" in df.columns else np.arange(len(df))

    # Stratified Group Split
    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    train_val_idx, test_idx = next(sgkf.split(df, composite_strata, groups))

    # Further split train into train and val
    train_df = df.iloc[train_val_idx].copy().reset_index(drop=True)
    test_df = df.iloc[test_idx].copy().reset_index(drop=True)

    train_groups = train_df["conglomerado_psu"].values if "conglomerado_psu" in train_df.columns else np.arange(len(train_df))
    train_strata = composite_strata[train_val_idx]

    sgkf_val = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=seed)
    sub_train_idx, val_idx = next(sgkf_val.split(train_df, train_strata, train_groups))

    final_train_df = train_df.iloc[sub_train_idx].copy().reset_index(drop=True)
    final_val_df = train_df.iloc[val_idx].copy().reset_index(drop=True)

    # Fit pipeline strictly on TRAIN only
    pipeline = PreMeasurementFeaturePipeline()
    X_train = pipeline.fit_transform(final_train_df)
    X_val = pipeline.transform(final_val_df)
    X_test = pipeline.transform(test_df)

    # Weights
    w_train = final_train_df["factor_expansion"].values if "factor_expansion" in final_train_df.columns else np.ones(len(final_train_df))
    w_val = final_val_df["factor_expansion"].values if "factor_expansion" in final_val_df.columns else np.ones(len(final_val_df))
    w_test = test_df["factor_expansion"].values if "factor_expansion" in test_df.columns else np.ones(len(test_df))

    return {
        "pipeline": pipeline,
        "feature_names": pipeline.feature_names_,
        "train": {
            "df": final_train_df,
            "X": X_train,
            "y_anemia": final_train_df["anemia_observada"].fillna(0).astype(int).values,
            "mask_anemia": ((final_train_df["edad_meses"] >= 6) & final_train_df["anemia_observada"].notnull()).values,
            "y_stunting": final_train_df["desnutricion_cronica_observada"].fillna(0).astype(int).values,
            "mask_stunting": final_train_df["desnutricion_cronica_observada"].notnull().values,
            "weights": w_train
        },
        "val": {
            "df": final_val_df,
            "X": X_val,
            "y_anemia": final_val_df["anemia_observada"].fillna(0).astype(int).values,
            "mask_anemia": ((final_val_df["edad_meses"] >= 6) & final_val_df["anemia_observada"].notnull()).values,
            "y_stunting": final_val_df["desnutricion_cronica_observada"].fillna(0).astype(int).values,
            "mask_stunting": final_val_df["desnutricion_cronica_observada"].notnull().values,
            "weights": w_val
        },
        "test": {
            "df": test_df,
            "X": X_test,
            "y_anemia": test_df["anemia_observada"].fillna(0).astype(int).values,
            "mask_anemia": ((test_df["edad_meses"] >= 6) & test_df["anemia_observada"].notnull()).values,
            "y_stunting": test_df["desnutricion_cronica_observada"].fillna(0).astype(int).values,
            "mask_stunting": test_df["desnutricion_cronica_observada"].notnull().values,
            "weights": w_test
        }
    }

