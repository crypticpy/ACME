import { useEffect, useRef } from 'react'
import * as d3 from 'd3'
import { Theme } from '@/types/analysis'

interface ThemeBarChartProps {
  data: Theme[]
  width?: number
  height?: number
}

export default function ThemeBarChart({ 
  data, 
  width = 800, 
  height = 400 
}: ThemeBarChartProps) {
  const svgRef = useRef<SVGSVGElement>(null)

  useEffect(() => {
    if (!data.length || !svgRef.current) return

    // Clear previous chart
    d3.select(svgRef.current).selectAll('*').remove()

    const margin = { top: 20, right: 30, bottom: 100, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    const svg = d3.select(svgRef.current)
      .attr('width', width)
      .attr('height', height)

    const g = svg.append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`)

    // Scales
    const x = d3.scaleBand()
      .domain(data.map(d => d.name))
      .range([0, innerWidth])
      .padding(0.1)

    const y = d3.scaleLinear()
      .domain([0, d3.max(data, d => d.count) || 0])
      .nice()
      .range([innerHeight, 0])

    // Color scale based on sentiment
    const colorScale = d3.scaleOrdinal()
      .domain(['positive', 'negative', 'neutral', 'mixed'])
      .range(['#10b981', '#ef4444', '#6b7280', '#f59e0b'])

    // X axis
    g.append('g')
      .attr('transform', `translate(0,${innerHeight})`)
      .call(d3.axisBottom(x))
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end')
      .style('font-size', '12px')

    // Y axis
    g.append('g')
      .call(d3.axisLeft(y))
      .append('text')
      .attr('transform', 'rotate(-90)')
      .attr('y', -40)
      .attr('x', -innerHeight / 2)
      .attr('text-anchor', 'middle')
      .style('font-size', '14px')
      .style('fill', '#374151')
      .text('Number of Mentions')

    // Bars
    const bars = g.selectAll('.bar')
      .data(data)
      .enter().append('rect')
      .attr('class', 'bar')
      .attr('x', d => x(d.name) || 0)
      .attr('width', x.bandwidth())
      .attr('y', innerHeight)
      .attr('height', 0)
      .attr('fill', d => colorScale(d.sentiment) as string)
      .attr('rx', 4)
      .style('cursor', 'pointer')

    // Animate bars
    bars.transition()
      .duration(800)
      .delay((d, i) => i * 50)
      .attr('y', d => y(d.count))
      .attr('height', d => innerHeight - y(d.count))

    // Add value labels
    g.selectAll('.label')
      .data(data)
      .enter().append('text')
      .attr('class', 'label')
      .attr('x', d => (x(d.name) || 0) + x.bandwidth() / 2)
      .attr('y', d => y(d.count) - 5)
      .attr('text-anchor', 'middle')
      .style('font-size', '12px')
      .style('font-weight', '600')
      .style('opacity', 0)
      .text(d => d.count)
      .transition()
      .delay(800)
      .duration(400)
      .style('opacity', 1)

    // Tooltip
    const tooltip = d3.select('body').append('div')
      .attr('class', 'tooltip')
      .style('position', 'absolute')
      .style('padding', '12px')
      .style('background', 'rgba(0, 0, 0, 0.8)')
      .style('color', 'white')
      .style('border-radius', '6px')
      .style('font-size', '14px')
      .style('pointer-events', 'none')
      .style('opacity', 0)

    // Bar hover effects
    bars
      .on('mouseover', (event, d) => {
        tooltip.transition()
          .duration(200)
          .style('opacity', 0.9)
        
        tooltip.html(`
          <strong>${d.name}</strong><br/>
          Count: ${d.count}<br/>
          Percentage: ${d.percentage.toFixed(1)}%<br/>
          Sentiment: ${d.sentiment}<br/>
          Urgency: ${d.urgency}
        `)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px')
      })
      .on('mouseout', () => {
        tooltip.transition()
          .duration(500)
          .style('opacity', 0)
      })

    // Cleanup
    return () => {
      d3.select('body').selectAll('.tooltip').remove()
    }

  }, [data, width, height])

  return <svg ref={svgRef} className="w-full h-full" />
}