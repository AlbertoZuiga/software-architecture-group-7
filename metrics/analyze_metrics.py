import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Directorio donde están los CSV
data_dir = Path("./metrics/proxy")  # cambia si están en otra ruta
output_dir = data_dir / "graphs"
output_dir.mkdir(exist_ok=True)

# Escenarios que esperamos
scenarios = [1, 10, 100, 1000, 5000]

# Función para métricas de contenedor
def parse_container_metrics(file_path):
    df = pd.read_csv(file_path)
    # limpiar CPU
    df["cpu"] = df["cpu"].astype(str).str.replace("%", "").str.replace(",", ".").astype(float)
    # limpiar Memoria
    df["mem"] = df["mem"].astype(str).str.split("/").str[0]
    df["mem"] = df["mem"].str.replace("MiB", "").str.replace("GiB", "000").str.replace(",", ".").str.strip()
    df["mem"] = pd.to_numeric(df["mem"], errors="coerce")
    return df

# Función para métricas JMeter (en español)
def parse_jmeter_results(file_path):
    df = pd.read_csv(file_path)
    # Tomar la fila "Total"
    total = df[df["Etiqueta"] == "Total"].iloc[0]
    stats = {
        "samples": int(total["# Muestras"]),
        "avg_latency_ms": float(str(total["Media"]).replace(",", ".")),
        "min_latency_ms": float(str(total["Mín"]).replace(",", ".")),
        "max_latency_ms": float(str(total["Máx"]).replace(",", ".")),
        "stddev": float(str(total["Desv. Estándar"]).replace(",", ".")),
        "error_rate": str(total["% Error"]),
        "throughput_req_s": float(str(total["Rendimiento"]).replace(",", ".")),
        "kb_per_sec": float(str(total["Kb/sec"]).replace(",", ".")),
    }
    return stats

container_summary = []
jmeter_summary = []

for sc in scenarios:
    container_file = data_dir / f"proxy_metrics_{sc}.csv"
    jmeter_file = data_dir / f"jmeter-proxy-{sc}.csv"

    if container_file.exists():
        cdf = parse_container_metrics(container_file)
        cpu_avg = cdf.groupby("container")["cpu"].mean()
        mem_avg = cdf.groupby("container")["mem"].mean()
        for cont in cpu_avg.index:
            container_summary.append({
                "scenario": sc,
                "container": cont,
                "avg_cpu": round(cpu_avg[cont], 4),
                "avg_mem": round(mem_avg[cont], 4)
            })

    if jmeter_file.exists():
        stats = parse_jmeter_results(jmeter_file)
        stats = {k: round(v, 4) if isinstance(v, float) else v for k, v in stats.items()}
        stats["scenario"] = sc
        jmeter_summary.append(stats)

# Crear DataFrame comparativo para contenedores
if container_summary:
    df_cont = pd.DataFrame(container_summary)
    for container in df_cont['container'].unique():
        cont_df = df_cont[df_cont['container'] == container].set_index('scenario').reindex([1, 10, 100, 1000, 5000])
        cont_df = cont_df[['avg_cpu', 'avg_mem']].round(4)
        fig, ax = plt.subplots(figsize=(8, 2 + len(cont_df) * 0.5))
        col_labels = ['Avg CPU (%)', 'Avg Mem (MB)']
        table_data = cont_df.values.tolist()
        row_labels = cont_df.index.tolist()
        ax.axis('off')
        table = ax.table(cellText=table_data, rowLabels=row_labels, colLabels=col_labels, loc='center', cellLoc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1, 1.5)
        plt.title(f"Comparative Table for Container: {container}", fontsize=14)
        plt.tight_layout()
        plt.savefig(output_dir / f"container_{container}_comparative_table.png")
        plt.close()

# Crear DataFrame comparativo para JMeter
if jmeter_summary:
    jmeter_df = pd.DataFrame(jmeter_summary)
    jmeter_df = jmeter_df.set_index("scenario").reindex([1, 10, 100, 1000, 5000])
    jmeter_df = jmeter_df.round(4)
    fig, ax = plt.subplots(figsize=(16, 2 + len(jmeter_df) * 0.5))
    col_labels = [col.replace('_', ' ').title() for col in jmeter_df.columns]
    table_data = jmeter_df.values.tolist()
    row_labels = jmeter_df.index.tolist()
    ax.axis('off')
    table = ax.table(cellText=table_data, rowLabels=row_labels, colLabels=col_labels, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    plt.title("JMeter Comparative Table by Scenario", fontsize=14)
    plt.tight_layout()
    plt.savefig(output_dir / "jmeter_comparative_table.png")
    plt.close()

# Guardar resúmenes
pd.DataFrame(container_summary).to_csv(data_dir / "container_summary.csv", index=False)
pd.DataFrame(jmeter_summary).to_csv(data_dir / "jmeter_summary.csv", index=False)

print("✅ Análisis completo.")
print(f"- Imágenes de tablas guardadas en: {output_dir}")
print("- container_summary.csv")
print("- jmeter_summary.csv")
