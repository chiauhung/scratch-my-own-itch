import React from 'react'

interface PieChartProps {
  data: Array<{
    label: string
    value: number
    color: string
  }>
}

export function PieChart({ data }: PieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0)

  if (total === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-custom">
        No data to display
      </div>
    )
  }

  let currentAngle = -90 // Start at top

  const slices = data.map((item, index) => {
    const percentage = (item.value / total) * 100
    const angle = (percentage / 100) * 360
    const startAngle = currentAngle
    const endAngle = currentAngle + angle

    currentAngle = endAngle

    // Calculate path for pie slice
    const startRad = (startAngle * Math.PI) / 180
    const endRad = (endAngle * Math.PI) / 180

    const x1 = 100 + 90 * Math.cos(startRad)
    const y1 = 100 + 90 * Math.sin(startRad)
    const x2 = 100 + 90 * Math.cos(endRad)
    const y2 = 100 + 90 * Math.sin(endRad)

    const largeArc = angle > 180 ? 1 : 0

    const pathData = [
      `M 100 100`,
      `L ${x1} ${y1}`,
      `A 90 90 0 ${largeArc} 1 ${x2} ${y2}`,
      `Z`
    ].join(' ')

    return { pathData, color: item.color, label: item.label, value: item.value, percentage }
  })

  return (
    <div className="flex flex-col items-center space-y-6">
      {/* SVG Pie Chart */}
      <svg viewBox="0 0 200 200" className="w-64 h-64">
        {slices.map((slice, index) => (
          <g key={index}>
            <path
              d={slice.pathData}
              fill={slice.color}
              className="transition-all hover:opacity-80 cursor-pointer"
              style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.1))' }}
            />
          </g>
        ))}
        {/* Center circle for donut effect */}
        <circle cx="100" cy="100" r="50" fill="white" />
        <text
          x="100"
          y="95"
          textAnchor="middle"
          className="text-xs font-semibold fill-[hsl(var(--heading-section))]"
        >
          Total
        </text>
        <text
          x="100"
          y="110"
          textAnchor="middle"
          className="text-sm font-bold fill-[hsl(var(--text-body))]"
        >
          RM {total.toFixed(0)}
        </text>
      </svg>

      {/* Legend */}
      <div className="grid grid-cols-2 gap-3 w-full">
        {slices.map((slice, index) => (
          <div key={index} className="flex items-center space-x-2">
            <div
              className="w-4 h-4 rounded-sm flex-shrink-0"
              style={{ backgroundColor: slice.color }}
            />
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium heading-section truncate">
                {slice.label}
              </p>
              <p className="text-xs text-muted-custom">
                {slice.percentage.toFixed(1)}% • RM {slice.value.toFixed(0)}
              </p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
