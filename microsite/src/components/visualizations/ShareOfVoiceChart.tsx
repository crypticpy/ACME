import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { ShareOfVoiceCategory } from '@/types/analysis'

interface ShareOfVoiceChartProps {
  data: ShareOfVoiceCategory[]
  width?: number
  height?: number
}

export default function ShareOfVoiceChart({ 
  data, 
  width = 400, 
  height = 400 
}: ShareOfVoiceChartProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!data.length || !svgRef.current) return

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove()

    const radius = Math.min(width, height) / 2
    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${width / 2}, ${height / 2})`)

    // Color scale
    const color = d3.scaleOrdinal()
      .domain(data.map(d => d.name))
      .range(['#2563eb', '#7c3aed', '#06b6d4'])

    // Pie generator
    const pie = d3.pie<ShareOfVoiceCategory>()
      .value(d => d.value)
      .sort(null)

    // Arc generator
    const arc = d3.arc<d3.PieArcDatum<ShareOfVoiceCategory>>()
      .innerRadius(radius * 0.4)
      .outerRadius(radius * 0.8)

    // Label arc
    const labelArc = d3.arc<d3.PieArcDatum<ShareOfVoiceCategory>>()
      .innerRadius(radius * 0.9)
      .outerRadius(radius * 0.9)

    // Create pie slices
    const arcs = g.selectAll('.arc')
      .data(pie(data))
      .enter().append('g')
      .attr('class', 'arc')

    // Add paths
    arcs.append('path')
      .attr('d', arc)
      .attr('fill', d => color(d.data.name) as string)
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .style('opacity', 0)
      .transition()
      .duration(800)
      .style('opacity', 1)
      .attrTween('d', function(d) {
        const interpolate = d3.interpolate({ startAngle: 0, endAngle: 0 }, d)
        return function(t) {
          return arc(interpolate(t)) || ''
        }
      })

    // Add labels
    arcs.append('text')
      .attr('transform', d => `translate(${labelArc.centroid(d)})`)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('font-weight', '600')
      .style('opacity', 0)
      .transition()
      .delay(800)
      .duration(400)
      .style('opacity', 1)
      .text(d => `${d.data.percentage.toFixed(1)}%`)

    // Add center text
    const centerText = g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '-0.5em')
      .style('font-size', '16px')
      .style('font-weight', '700')
      .text('Share of Voice')

    g.append('text')
      .attr('text-anchor', 'middle')
      .attr('dy', '1em')
      .style('font-size', '14px')
      .style('fill', '#6b7280')
      .text(`${data.reduce((sum, d) => sum + d.value, 0)} Total`)

    // Add legend
    const legend = svg.append('g')
      .attr('transform', `translate(${width - 120}, 20)`)

    const legendItems = legend.selectAll('.legend-item')
      .data(data)
      .enter().append('g')
      .attr('class', 'legend-item')
      .attr('transform', (d, i) => `translate(0, ${i * 25})`)

    legendItems.append('rect')
      .attr('width', 16)
      .attr('height', 16)
      .attr('fill', d => color(d.name) as string)
      .attr('rx', 2)

    legendItems.append('text')
      .attr('x', 24)
      .attr('y', 12)
      .style('font-size', '12px')
      .text(d => d.name)

  }, [data, width, height])

  return <svg ref={svgRef} className="w-full h-full" />
}