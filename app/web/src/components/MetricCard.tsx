interface MetricCardProps {
  label: string
  value: string | number
  accent?: string
}

export const MetricCard = ({ label, value, accent = '#2563eb' }: MetricCardProps) => {
  return (
    <div className="metric-card" style={{ borderColor: accent + '33' }}>
      <h3>{label}</h3>
      <p>{value}</p>
    </div>
  )
}
