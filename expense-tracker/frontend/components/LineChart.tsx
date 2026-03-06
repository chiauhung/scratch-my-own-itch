import React from 'react'

interface LineChartProps {
  data: Array<{
    date: string
    amount: number
  }>
  height?: number
}

export function LineChart({ data, height = 200 }: LineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-pastel-600">
        No spending data to display
      </div>
    )
  }

  // Get max value for scaling
  const maxAmount = Math.max(...data.map(d => d.amount), 1)
  const minAmount = 0

  // Calculate dimensions
  const width = 800
  const padding = { top: 20, right: 40, bottom: 40, left: 60 }
  const chartWidth = width - padding.left - padding.right
  const chartHeight = height - padding.top - padding.bottom

  // Create points for the line
  const points = data.map((item, index) => {
    const x = padding.left + (index / (data.length - 1 || 1)) * chartWidth
    const y = padding.top + chartHeight - ((item.amount - minAmount) / (maxAmount - minAmount || 1)) * chartHeight
    return { x, y, ...item }
  })

  // Create path string
  const pathData = points.map((point, index) =>
    `${index === 0 ? 'M' : 'L'} ${point.x} ${point.y}`
  ).join(' ')

  // Create area path (filled under the line)
  const areaPath = pathData +
    ` L ${points[points.length - 1].x} ${padding.top + chartHeight}` +
    ` L ${points[0].x} ${padding.top + chartHeight} Z`

  // Format date for display
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr)
    return `${date.getMonth() + 1}/${date.getDate()}`
  }

  // Y-axis labels
  const yAxisSteps = 4
  const yAxisLabels = Array.from({ length: yAxisSteps + 1 }, (_, i) => {
    const value = maxAmount - (i * maxAmount / yAxisSteps)
    return {
      value,
      y: padding.top + (i * chartHeight / yAxisSteps)
    }
  })

  return (
    <div className="w-full overflow-x-auto">
      <svg viewBox={`0 0 ${width} ${height}`} className="w-full" style={{ minWidth: '600px' }}>
        {/* Grid lines */}
        {yAxisLabels.map((label, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              y1={label.y}
              x2={width - padding.right}
              y2={label.y}
              stroke="#F0E5F5"
              strokeWidth="1"
              strokeDasharray="4 4"
            />
            <text
              x={padding.left - 10}
              y={label.y}
              textAnchor="end"
              className="text-xs fill-pastel-800"
              dominantBaseline="middle"
            >
              {Math.round(label.value)}
            </text>
          </g>
        ))}

        {/* Area under line */}
        <path
          d={areaPath}
          fill="url(#pastelGradient)"
          opacity="0.4"
        />

        {/* Line */}
        <path
          d={pathData}
          fill="none"
          stroke="#FFAFCC"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {points.map((point, index) => (
          <g key={index}>
            <circle
              cx={point.x}
              cy={point.y}
              r="5"
              fill="white"
              stroke="#FFAFCC"
              strokeWidth="2"
              className="hover:r-7 transition-all cursor-pointer"
            />
            <title>{`${formatDate(point.date)}: RM ${point.amount.toFixed(2)}`}</title>
          </g>
        ))}

        {/* X-axis labels */}
        {points.map((point, index) => {
          // Show every nth label to avoid crowding
          const showLabel = data.length <= 10 || index % Math.ceil(data.length / 10) === 0
          if (!showLabel && index !== data.length - 1) return null

          return (
            <text
              key={`label-${index}`}
              x={point.x}
              y={height - padding.bottom + 20}
              textAnchor="middle"
              className="text-xs fill-pastel-800"
            >
              {formatDate(point.date)}
            </text>
          )
        })}

        {/* Gradient definition */}
        <defs>
          <linearGradient id="pastelGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#FFAFCC" stopOpacity="0.8" />
            <stop offset="50%" stopColor="#FFC8DD" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#CDB4DB" stopOpacity="0.2" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  )
}
