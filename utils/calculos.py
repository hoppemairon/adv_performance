import pandas as pd
import numpy as np

def calcular_resultado(advogados_df, processos_df, total_custo_fixo, qtd_rateio, aliquota_imposto=0.0):
    # Garante que df_proc tenha as colunas esperadas mesmo se estiver vazio
    if processos_df.empty or "valor_recebido" not in processos_df.columns:
        resultados = []
        for _, adv in advogados_df.iterrows():
            custo_direto = adv["custo_direto_anual"]
            custo_fixo = total_custo_fixo / qtd_rateio
            receita = 0.0
            imposto = 0.0
            resultado_liquido = - (custo_direto + custo_fixo)
            receita_necessaria_positivo = (custo_direto + custo_fixo) / (1 - aliquota_imposto / 100) if resultado_liquido < 0 else 0.0
            resultados.append({
                "advogado_id": adv["advogado_id"],
                "nome": adv["nome"],
                "receita_advogado": receita,
                "imposto": imposto,
                "custo_direto_anual": custo_direto,
                "custo_fixo_rateado": custo_fixo,
                "resultado_liquido": resultado_liquido,
                "receita_necessaria_positivo": receita_necessaria_positivo
            })
        return pd.DataFrame(resultados)

    # Aplicar imposto
    processos_df["valor_recebido_liquido"] = processos_df["valor_recebido"] * (1 - aliquota_imposto / 100)

    # Receita por advogado
    processos_df["receita_advogado"] = processos_df["valor_recebido_liquido"] * (processos_df["participacao (%)"] / 100)
    receita_por_advogado = processos_df.groupby("advogado_id")["receita_advogado"].sum().reset_index()

    # Merge com advogados
    df = advogados_df.merge(receita_por_advogado, on="advogado_id", how="left")
    df["receita_advogado"] = df["receita_advogado"].fillna(0)

    # Custo fixo rateado
    custo_fixo_por_advogado = total_custo_fixo / qtd_rateio
    df["custo_fixo_rateado"] = custo_fixo_por_advogado

    # Resultado líquido
    df["resultado_liquido"] = df["receita_advogado"] - (df["custo_direto_anual"] + df["custo_fixo_rateado"])

    # Valor necessário para equilibrar
    df["valor_necessario_para_equilibrar"] = np.where(
        df["resultado_liquido"] < 0,
        (df["custo_direto_anual"] + df["custo_fixo_rateado"]) / (1 - aliquota_imposto / 100),
        np.nan
    )

    # Calcula imposto e receita necessária para ficar positivo
    df["imposto"] = df["receita_advogado"] * (aliquota_imposto / 100)
    df["receita_necessaria_positivo"] = np.where(
        df["resultado_liquido"] < 0,
        (df["custo_direto_anual"] + df["custo_fixo_rateado"]) / (1 - aliquota_imposto / 100),
        0.0
    )

    return df