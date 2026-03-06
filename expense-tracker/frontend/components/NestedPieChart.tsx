import React, { useState } from 'react'

interface NestedPieChartProps {
  data: Array<{
    category: string
    subcategory: string
    total: number
  }>
  categoryColors: Record<string, string>
}

export function NestedPieChart({ data, categoryColors }: NestedPieChartProps) {
  const [hoveredItem, setHoveredItem] = useState<{ type: 'category' | 'subcategory'; label: string; value: number; percentage: number } | null>(null)

  const total = data.reduce((sum, item) => sum + item.total, 0)

  if (total === 0) {
    return (
      <div className="flex items-center justify-center h-64 text-muted-custom">
        No data to display
      </div>
    )
  }

  // Group by category for inner ring
  const categoryTotals = data.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + item.total
    return acc
  }, {} as Record<string, number>)

  // Count subcategories per category for gradient calculation
  const subcategoryCount = data.reduce((acc, item) => {
    acc[item.category] = (acc[item.category] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  // Track subcategory index within each category
  const subcategoryIndexMap = new Map<string, number>()

  // Calculate inner ring (categories) - using DARKER colors
  let currentAngle = -90
  const innerSlices = Object.entries(categoryTotals).map(([category, value]) => {
    const percentage = (value / total) * 100
    const angle = (percentage / 100) * 360
    const startAngle = currentAngle
    const endAngle = currentAngle + angle
    currentAngle = endAngle

    const startRad = (startAngle * Math.PI) / 180
    const endRad = (endAngle * Math.PI) / 180

    const innerRadius = 55
    const outerRadius = 75

    const x1Inner = 100 + innerRadius * Math.cos(startRad)
    const y1Inner = 100 + innerRadius * Math.sin(startRad)
    const x2Inner = 100 + innerRadius * Math.cos(endRad)
    const y2Inner = 100 + innerRadius * Math.sin(endRad)

    const x1Outer = 100 + outerRadius * Math.cos(startRad)
    const y1Outer = 100 + outerRadius * Math.sin(startRad)
    const x2Outer = 100 + outerRadius * Math.cos(endRad)
    const y2Outer = 100 + outerRadius * Math.sin(endRad)

    const largeArc = angle > 180 ? 1 : 0

    const pathData = [
      `M ${x1Inner} ${y1Inner}`,
      `L ${x1Outer} ${y1Outer}`,
      `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2Outer} ${y2Outer}`,
      `L ${x2Outer} ${y2Outer}`,
      `L ${x2Inner} ${y2Inner}`,
      `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x1Inner} ${y1Inner}`,
      `Z`
    ].join(' ')

    // Lighten the base color for parent category (lightest)
    const baseColor = categoryColors[category] || '#CCC'
    const lightestColor = lightenColor(baseColor, 0.5)

    return { pathData, color: lightestColor, category, value, percentage }
  })

  // Calculate outer ring (subcategories) - ALIGNED with inner ring
  // Group data by category first
  const dataByCategory = data.reduce((acc, item) => {
    if (!acc[item.category]) acc[item.category] = []
    acc[item.category].push(item)
    return acc
  }, {} as Record<string, typeof data>)

  const outerSlices: Array<{
    pathData: string
    color: string
    category: string
    subcategory: string
    value: number
    percentage: number
  }> = []

  // For each category, calculate subcategories within that category's angle range
  currentAngle = -90
  Object.entries(categoryTotals).forEach(([category, categoryTotal]) => {
    const categoryPercentage = (categoryTotal / total) * 100
    const categoryAngle = (categoryPercentage / 100) * 360
    const categoryStartAngle = currentAngle
    const categoryEndAngle = currentAngle + categoryAngle

    // Get subcategories for this category
    const subcategories = dataByCategory[category] || []
    let subcategoryAngle = categoryStartAngle

    subcategories.forEach((item, index) => {
      // Calculate this subcategory's proportion within its parent category
      const subPercentageInCategory = (item.total / categoryTotal) * 100
      const subAngle = (subPercentageInCategory / 100) * categoryAngle

      const startAngle = subcategoryAngle
      const endAngle = subcategoryAngle + subAngle
      subcategoryAngle = endAngle

      const startRad = (startAngle * Math.PI) / 180
      const endRad = (endAngle * Math.PI) / 180

      const innerRadius = 78
      const outerRadius = 95

      const x1Inner = 100 + innerRadius * Math.cos(startRad)
      const y1Inner = 100 + innerRadius * Math.sin(startRad)
      const x2Inner = 100 + innerRadius * Math.cos(endRad)
      const y2Inner = 100 + innerRadius * Math.sin(endRad)

      const x1Outer = 100 + outerRadius * Math.cos(startRad)
      const y1Outer = 100 + outerRadius * Math.sin(startRad)
      const x2Outer = 100 + outerRadius * Math.cos(endRad)
      const y2Outer = 100 + outerRadius * Math.sin(endRad)

      const largeArc = subAngle > 180 ? 1 : 0

      const pathData = [
        `M ${x1Inner} ${y1Inner}`,
        `L ${x1Outer} ${y1Outer}`,
        `A ${outerRadius} ${outerRadius} 0 ${largeArc} 1 ${x2Outer} ${y2Outer}`,
        `L ${x2Outer} ${y2Outer}`,
        `L ${x2Inner} ${y2Inner}`,
        `A ${innerRadius} ${innerRadius} 0 ${largeArc} 0 ${x1Inner} ${y1Inner}`,
        `Z`
      ].join(' ')

      // Generate gradient color based on subcategory index within category
      const baseColor = categoryColors[category] || '#CCC'
      const totalSubcategories = subcategories.length
      // Create darker shades - from medium to darkest
      const darknessFactor = 0.1 + (index / totalSubcategories) * 0.4
      const gradientColor = darkenColor(baseColor, darknessFactor)

      outerSlices.push({
        pathData,
        color: gradientColor,
        category: item.category,
        subcategory: item.subcategory,
        value: item.total,
        percentage: (item.total / total) * 100
      })
    })

    currentAngle = categoryEndAngle
  })

  return (
    <div className="flex flex-col items-center">
      {/* SVG Nested Donut Chart */}
      <svg viewBox="0 0 200 200" className="w-80 h-80">
        {/* Inner ring - Categories */}
        {innerSlices.map((slice, index) => (
          <g key={`inner-${index}`}>
            <path
              d={slice.pathData}
              fill={slice.color}
              className="transition-all hover:opacity-90 cursor-pointer"
              style={{ filter: 'drop-shadow(0 2px 4px rgba(0,0,0,0.15))' }}
              onMouseEnter={() => setHoveredItem({
                type: 'category',
                label: slice.category,
                value: slice.value,
                percentage: slice.percentage
              })}
              onMouseLeave={() => setHoveredItem(null)}
            />
          </g>
        ))}

        {/* Outer ring - Subcategories */}
        {outerSlices.map((slice, index) => (
          <g key={`outer-${index}`}>
            <path
              d={slice.pathData}
              fill={slice.color}
              className="transition-all hover:opacity-90 cursor-pointer"
              style={{ filter: 'drop-shadow(0 1px 2px rgba(0,0,0,0.1))' }}
              onMouseEnter={() => setHoveredItem({
                type: 'subcategory',
                label: slice.subcategory,
                value: slice.value,
                percentage: slice.percentage
              })}
              onMouseLeave={() => setHoveredItem(null)}
            />
          </g>
        ))}

        {/* Center circle */}
        <circle cx="100" cy="100" r="52" fill="white" />

        {/* Display hovered item or total */}
        {hoveredItem ? (
          <>
            <text
              x="100"
              y="90"
              textAnchor="middle"
              className="text-xs font-medium fill-[hsl(var(--text-body))]"
            >
              {hoveredItem.type === 'category' ? '📂' : '📄'} {hoveredItem.label}
            </text>
            <text
              x="100"
              y="105"
              textAnchor="middle"
              className="text-sm font-bold fill-[hsl(var(--heading-section))]"
            >
              RM {hoveredItem.value.toFixed(0)}
            </text>
            <text
              x="100"
              y="118"
              textAnchor="middle"
              className="text-xs fill-[hsl(var(--text-muted))]"
            >
              {hoveredItem.percentage.toFixed(1)}%
            </text>
          </>
        ) : (
          <>
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
          </>
        )}
      </svg>

      {/* Category Legend */}
      <div className="mt-6 flex flex-wrap justify-center gap-3">
        {Object.entries(categoryTotals).map(([category, _]) => (
          <div key={category} className="flex items-center space-x-2">
            <div
              className="w-3 h-3 rounded-sm flex-shrink-0"
              style={{ backgroundColor: lightenColor(categoryColors[category] || '#CCC', 0.5) }}
            />
            <span className="text-xs text-body">{category}</span>
          </div>
        ))}
      </div>

      {/* Hover instruction */}
      <p className="text-xs text-muted-custom mt-3 text-center">
        Hover over segments to see details
      </p>
    </div>
  )
}

// Helper function to darken a hex color
function darkenColor(color: string, factor: number): string {
  const hex = color.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)

  // Darken by moving towards black
  const newR = Math.round(r * (1 - factor))
  const newG = Math.round(g * (1 - factor))
  const newB = Math.round(b * (1 - factor))

  const toHex = (n: number) => {
    const hex = n.toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }

  return `#${toHex(newR)}${toHex(newG)}${toHex(newB)}`
}

// Helper function to lighten a hex color
function lightenColor(color: string, factor: number): string {
  const hex = color.replace('#', '')
  const r = parseInt(hex.substring(0, 2), 16)
  const g = parseInt(hex.substring(2, 4), 16)
  const b = parseInt(hex.substring(4, 6), 16)

  // Lighten by moving towards white
  const newR = Math.round(r + (255 - r) * factor)
  const newG = Math.round(g + (255 - g) * factor)
  const newB = Math.round(b + (255 - b) * factor)

  const toHex = (n: number) => {
    const hex = n.toString(16)
    return hex.length === 1 ? '0' + hex : hex
  }

  return `#${toHex(newR)}${toHex(newG)}${toHex(newB)}`
}
