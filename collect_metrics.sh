# Script para recolectar métricas de Docker en un CSV
# Uso: ./collect_metrics.sh DURACION_EN_SEGUNDOS

DURATION=$1   
INTERVAL=5 
OUTPUT="metrics.csv"

if [ -z "$DURATION" ]; then
  echo "Uso: $0 DURACION_EN_SEGUNDOS"
  exit 1
fi

echo "timestamp,container,cpu,mem" > $OUTPUT

END=$((SECONDS+DURATION))
while [ $SECONDS -lt $END ]; do
  docker stats --no-stream --format "{{.Name}},{{.CPUPerc}},{{.MemUsage}}" |   awk -v date="$(date +%s)" '{print date","$0}' >> $OUTPUT
  sleep $INTERVAL
done

echo "Métricas guardadas en $OUTPUT"
